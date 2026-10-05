# Hoot firmware (ATtiny412)

One file, [`main.c`](main.c), bare-metal C on avr-libc: no Arduino core, no libraries. The comments at
its top say what it does, pin by pin.

## Build

Any avr-gcc whose avr-libc knows the tinyAVR 1-series (`-mmcu=attiny412`, header `iotn412.h`):

```sh
make                       # or: make AVR_PREFIX=/path/to/avr-gcc/bin/
```

Compiled on 2026-10-05 with avr-gcc 15.1.0 (Microchip AVR 8-bit toolchain 4.0.0, the
`felias-fogg/avr-gcc-15` arm64 macOS build) under `-Wall -Wextra -Werror`:

```
   text    data     bss     dec     hex filename
   1544      26       2    1572     624 hoot.elf
```

1,570 of 4,096 bytes of flash. [`hoot.hex`](hoot.hex) is that build.

## Flash

The owl's chin has three UPDI pads (VCC, UPDI, GND), under the cell holder. Any USB-serial adapter
becomes a UPDI programmer with a 4.7 kΩ resistor from its TX to UPDI and RX tied to UPDI (SerialUPDI).
Take the coin cell out and power the board from the adapter's 3.3 V:

```sh
make flash PORT=/dev/tty.usbserial-XXXX      # avrdude 7+: -c serialupdi -p t412
```

Fuses can stay at their factory values (20 MHz oscillator divided by 6 = 3.33 MHz, which `F_CPU` assumes).

## Using it

1. Put a CR2032 in: both eyes glow hello, and both reminders start due (both eyes blink).
2. Right after you next take your meds, press the left wing; right after your next glass of water, the
   right wing. Each eye glows "thank you" and goes quiet. That sets each reminder's time of day.
3. Meds twice a day? Hold the left wing 3 s: two slow flashes = every 12 h, one = every 24 h.
4. A blinking eye is due. After an hour unanswered it dozes to one flash every 10 s; a press on either
   wing wakes it.

## Status

Compiled, not yet run on hardware: no Hoot has been built. On the first prototypes, measure the sleep
current (under 2 µA expected) and time a 2 h water reminder against a clock. If the internal oscillator
is far off, scale `HOUR` in `main.c` to match.

## License

MIT (see [`LICENSE`](LICENSE)).
