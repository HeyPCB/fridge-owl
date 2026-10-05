/*
 * Hoot, the fridge reminder owl - firmware for the ATtiny412 (heypcb.ai merch 08).
 *
 * What it does
 *   - Two reminders. The left wing is "meds" (every 24 h, or every 12 h), the right wing "water" (every
 *     2 h). Press a wing when you have done the thing: that eye glows "thank you" and its timer restarts.
 *   - When a reminder comes due, its eye blinks at you (a 30 ms flash every 2 s) until you press its wing.
 *     The left eye flashes on even seconds and the right on odd ones, so with both due the owl looks
 *     left and right.
 *   - An eye that has blinked for an hour unanswered dozes: one flash every 10 s, a fifth of the current,
 *     so a missed reminder is still there when you walk past (the night, a day out). Pressing either wing
 *     wakes it: somebody is home, so it blinks properly again.
 *   - Hold the meds wing 3 s to switch meds between 24 h and 12 h (the left eye answers with one slow
 *     flash for 24 h, two for 12 h). The choice is kept in EEPROM; the hold also counts as a press.
 *   - Putting the cell in: both eyes say hello and both reminders start due. Press each wing right after
 *     you next do the thing; that sets its time of day.
 *   - The rest of the time it sleeps in power-down. The RTC's periodic interrupt (1.024 kHz internal
 *     ultra-low-power oscillator) wakes it once a second to count; a wing press wakes it at once (PA2 and
 *     PA6 are the port's fully asynchronous pins, so a falling edge on them wakes power-down).
 *
 * Pins (from the board's netlist; KiCad symbol MCU_Microchip_ATtiny:ATtiny412-SS)
 *   PA1 (pin 4)  EYE_L  output, the left eye: orange LED through 220 ohm, high = on
 *   PA3 (pin 7)  EYE_R  output, the right eye
 *   PA6 (pin 2)  MEDS   input with pull-up, the left wing button to GND
 *   PA2 (pin 5)  WATER  input with pull-up, the right wing button to GND
 *   PA7 (pin 3)  not connected: pull-up on, so it never floats
 *   PA0 (pin 6)  UPDI   programming only
 *
 * Timekeeping: the internal oscillator is not a crystal, so the reminders run a few percent fast or
 * slow. Every press restarts its timer, so the error never adds up past one interval.
 *
 * Power budget (see SPEC.md for the arithmetic): about 17 uA on an average day, over a year on a CR2032.
 *
 * Build: make      (avr-gcc with ATtiny412 support; see README.md)
 */
#include <avr/eeprom.h>
#include <avr/interrupt.h>
#include <avr/io.h>
#include <avr/sleep.h>
#include <stdint.h>
#include <util/delay.h>

#define EYE_L PIN1_bm
#define WATER PIN2_bm
#define EYE_R PIN3_bm
#define MEDS PIN6_bm
#define SPARE PIN7_bm

#define HOUR 3600UL
#define NAG_S (1 * HOUR)      /* a due eye blinks every 2 s for an hour ... */
#define DOZE_EVERY_S 10u      /* ... then once every 10 s until somebody presses a wing */
#define FLASH_MS 30u
#define HOLD_MS 3000u

/* EEPROM: 1 = meds every 12 h; anything else (0xFF on a new chip) = every 24 h */
#define EE_MEDS_12H ((uint8_t *)0)

struct reminder {
    uint32_t every;     /* its interval, s */
    uint32_t left;      /* s until it is due; 0 = due */
    uint32_t nagged;    /* s it has blinked since it came due (or since a press woke it) */
    uint8_t eye;        /* its LED */
};

static struct reminder meds = {24 * HOUR, 0, 0, EYE_L};
static struct reminder water = {2 * HOUR, 0, 0, EYE_R};

static volatile uint8_t ticks;      /* seconds the RTC has counted that main() has not handled */
static volatile uint8_t pressed;    /* wings whose pin fell that main() has not handled */

ISR(RTC_PIT_vect)
{
    RTC.PITINTFLAGS = RTC_PI_bm;
    ticks++;
}

ISR(PORTA_PORT_vect)
{
    uint8_t f = PORTA.INTFLAGS;
    PORTA.INTFLAGS = f;
    pressed |= f & (MEDS | WATER);
}

static void count_second(struct reminder *r)
{
    if (r->left)
        r->left--;
    else if (r->nagged < NAG_S)
        r->nagged++;
}

/* Does this reminder's eye flash in second `s` (0..59)? Left eye on even seconds, right eye on odd. */
static uint8_t flashes(const struct reminder *r, uint8_t s)
{
    uint8_t odd = (r->eye == EYE_R);
    if (r->left)
        return 0;
    if (r->nagged < NAG_S)
        return (s & 1u) == odd;
    return s % DOZE_EVERY_S == (odd ? 5u : 0u);
}

static void flash(uint8_t pin, uint16_t ms)
{
    PORTA.OUTSET = pin;
    while (ms--)
        _delay_ms(1);
    PORTA.OUTCLR = pin;
}

/* A soft fade (software PWM at about 1 kHz): `steps_ms` steps of about 1 ms from one level to the other. */
static void glow(uint8_t pin, uint8_t from, uint8_t to, uint8_t steps_ms)
{
    for (uint8_t t = 0; t < steps_ms; t++) {
        uint8_t level = from + (int16_t)(to - from) * t / steps_ms;     /* 0..32 */
        for (uint8_t k = 0; k < 32; k++) {
            if (k < level)
                PORTA.OUTSET = pin;
            else
                PORTA.OUTCLR = pin;
            _delay_us(30);
        }
    }
    PORTA.OUTCLR = pin;
}

static void thanks(uint8_t eye)
{
    glow(eye, 0, 32, 120);
    glow(eye, 32, 0, 200);
}

static void restart(struct reminder *r)
{
    r->left = r->every;
    r->nagged = 0;
}

/* Somebody pressed a wing: an eye that dozed off over an unanswered reminder blinks properly again. */
static void wake(struct reminder *r)
{
    if (!r->left)
        r->nagged = 0;
}

static void set_meds(uint8_t twelve) { meds.every = (twelve ? 12u : 24u) * HOUR; }

static void on_press(uint8_t wing)
{
    _delay_ms(20);                          /* debounce */
    if (PORTA.IN & wing)
        return;                             /* a bounce, or the release of an earlier press */
    struct reminder *r = (wing == MEDS) ? &meds : &water;
    wake(&meds);
    wake(&water);
    thanks(r->eye);
    uint16_t held = 340;                    /* the debounce and the glow */
    while (!(PORTA.IN & wing) && held < HOLD_MS) {
        _delay_ms(10);
        held += 10;
    }
    if (wing == MEDS && held >= HOLD_MS) {
        uint8_t twelve = (meds.every != 12u * HOUR);                    /* switch it */
        eeprom_update_byte(EE_MEDS_12H, twelve);
        set_meds(twelve);
        for (uint8_t i = 0; i <= twelve; i++) {
            flash(EYE_L, 250);
            _delay_ms(250);
        }
        for (uint16_t t = 0; !(PORTA.IN & MEDS) && t < 1000; t++)
            _delay_ms(10);                  /* wait for the release (10 s at most) */
    }
    restart(r);
}

static void sleep_now(void)
{
    set_sleep_mode(SLEEP_MODE_PWR_DOWN);
    sleep_enable();
    sleep_cpu();
    sleep_disable();
}

int main(void)
{
    /* eyes off; the wings' pull-ups and wake-up edges; the unconnected pin pulled up */
    PORTA.DIRSET = EYE_L | EYE_R;
    PORTA.OUTCLR = EYE_L | EYE_R;
    PORTA.PIN6CTRL = PORT_PULLUPEN_bm | PORT_ISC_FALLING_gc;
    PORTA.PIN2CTRL = PORT_PULLUPEN_bm | PORT_ISC_FALLING_gc;
    PORTA.PIN7CTRL = PORT_PULLUPEN_bm;

    set_meds(eeprom_read_byte(EE_MEDS_12H) == 1);

    /* RTC periodic interrupt: 1.024 kHz internal ULP oscillator, 1024 cycles = 1 s */
    while (RTC.STATUS > 0)
        ;
    RTC.CLKSEL = RTC_CLKSEL_INT1K_gc;
    while (RTC.PITSTATUS > 0)
        ;
    RTC.PITINTCTRL = RTC_PI_bm;
    RTC.PITCTRLA = RTC_PERIOD_CYC1024_gc | RTC_PITEN_bm;
    sei();

    thanks(EYE_L);                          /* hello: left, then right */
    thanks(EYE_R);

    uint8_t s = 0;                          /* the second, 0..59, that picks which eye flashes */
    for (;;) {
        sleep_now();

        cli();
        uint8_t w = pressed;
        pressed = 0;
        uint8_t n = ticks;
        ticks = 0;
        sei();

        if (w & MEDS)
            on_press(MEDS);
        if (w & WATER)
            on_press(WATER);
        if (!n)
            continue;
        while (n--) {
            count_second(&meds);
            count_second(&water);
            s = (s + 1u) % 60u;
        }
        if (flashes(&meds, s))
            flash(EYE_L, FLASH_MS);
        if (flashes(&water, s))
            flash(EYE_R, FLASH_MS);
    }
}
