# 08 · Hoot, the fridge reminder owl: SPEC

## Who it's for, and the use case

Anyone who has ever stood in the kitchen wondering "did I take my pills this morning?", and anyone who
forgets to drink water: people on daily medication, their carers, students, desk workers, older
parents (a thoughtful gift from their kids). It lives on the fridge door, the one place everybody passes
several times a day, and it answers two questions at a glance: meds done today? had water lately?

## The cute concept

A yellow owl with big gold-ringed eyes, a gold beak and folded wings. Each wing is a button: the left wing
says "meds" (a pill), the right wing "water" (a drop). Press a wing when you've done the thing and that
eye glows "thank you". When the reminder comes due, that eye starts blinking at you until you press its
wing again. A quiet owl means you're all done; a blinking owl is looking at you.

## Features

| | |
|---|---|
| Meds reminder | left wing and left eye; every 24 h, or every 12 h (hold the wing 3 s to switch; one slow flash = 24 h, two = 12 h) |
| Water reminder | right wing and right eye; every 2 h |
| Due | that eye flashes 30 ms every 2 s; with both due, the eyes take turns (the owl looks left and right) |
| Unanswered | after an hour the eye dozes to one flash every 10 s, so a missed reminder is still visible but cheap; a press on either wing wakes it |
| Setting the time | insert the cell: both eyes say hello and both reminders start due; press each wing right after you next do the thing |
| MCU | ATtiny412, asleep in power-down; the RTC wakes it once a second, a wing press wakes it at once |
| Power | one CR2032 in a Keystone 3034 holder in the owl's belly |
| Board | 2 layers, yellow mask, black silk, ENIG eye rings and beak; 10 SMT parts on the front, flat back for magnets |
| Programming | three UPDI pads (VCC, UPDI, GND) on the owl's chin; firmware in [`firmware/`](firmware/) |

## Power budget and battery life

Assumptions (datasheet typical values, rounded up, as for 01): ATtiny412 in power-down with the RTC's
periodic interrupt ≈ 1.5 µA budgeted; awake at 3.33 MHz ≈ 1 mA; an orange LED (Vf ≈ 2.0 V) through
220 Ω from 3.0 V ≈ 4.5 mA. A 30 ms flash, LED plus CPU, is 0.17 mC.

| What | How often | Average |
|---|---|---|
| Sleep (power-down + RTC) | always | 1.5 µA |
| Counting the second (≈ 20 µs awake) | every 1 s | 0.02 µA |
| A due eye blinking (30 ms flash) | every 2 s | 83 µA while it blinks |
| A dozing eye (30 ms flash) | every 10 s | 17 µA while it dozes |
| A press: "thank you" glow (≈ 0.34 s) | per press | 1.1 mC |

A typical day, an assumption: up 07:00-23:00, water pressed about every 2 h 20 min, so it blinks about
20 min before each of 7 presses (2.3 h); after the last press of the evening it is due at 01:00, blinks
an hour and dozes until morning (5 h); meds blink about 15 min a day; 8 presses.

- Blinking 3.6 h x 83 µA = 298 µAh; dozing 5 h x 17 µA = 83 µAh; sleep and counting 37 µAh; presses
  2 µAh: **≈ 420 µAh a day, 17.5 µA on average → about 14 months** on the ≈ 180 mAh usable in a CR2032.
- **Nobody home** (both eyes dozing all the time): 35 µA → about 7 months.
- Nothing due at all: 1.5 µA, the cell's shelf life.

Design estimates; no Hoot has been built.

Timekeeping comes from the ATtiny's internal 32 kHz ultra-low-power oscillator, not a crystal, so the
reminders run a few percent fast or slow. Each press restarts its timer, so the error never adds up past
one interval.

## BOM (100 units, live JLC/LCSC prices read 2026-10-05)

| Refs | Value | Qty | LCSC | MPN | Class | Unit @100 | Line |
|---|---|---|---|---|---|---|---|
| BT1 | CR2032 holder | 1 | C5213768 | 3034TR | extended | $0.3602 | $0.3602 |
| C1 | 10uF | 1 | C15850 | CL21A106KAYNNNE | basic | $0.0773 | $0.0773 |
| C2 | 100nF | 1 | C14663 | CC0603KRX7R9BB104 | basic | $0.0106 | $0.0106 |
| D1, D2 | Orange (eyes) | 2 | C965800 | XL-1608UOC-06 | extended | $0.0071 | $0.0142 |
| R1, R2 | 220 | 2 | C22962 | 0603WAF2200T5E | basic | $0.0014 | $0.0028 |
| SW1, SW2 | TS-1187A (wings) | 2 | C318884 | TS-1187A-B-A-B | basic | $0.0152 | $0.0304 |
| U1 | ATtiny412 | 1 | C1337190 | ATTINY412-SSNR | extended | $0.5060 | $0.5060 |
| | **Parts** | | | | | | **$1.00** |
| | Extended-part loading fee ($3 x 3 / 100 boards) | | | | | | $0.09 |
| | **BOM per board @100** | | | | | | **$1.09** |

Not in the BOM: the PCB (2 layers, ENIG, 42.1 x 53.3 mm), assembly labour, the CR2032, and the two
disc magnets (packed loose; not a JLC assembly part, so not priced from the catalogue). TP1-TP3 are
DNP copper pads, not parts. Machine-readable: [`bom_cost.json`](bom_cost.json).

## Dimensions

42.1 x 53.3 mm (Edge.Cuts bounding box, pcbnew), 17.3 cm², 1.6 mm FR4. Tallest part: the cell in its
holder, about 4 mm; the back is flat. Weight, estimated: about 10 g with the cell.

## Mounting plan (no enclosure)

Two 8 x 2 mm neodymium disc magnets, self-adhesive, go on the two rings printed on the back (behind the
eyes, clear of the QR code and the instructions). Two of them hold about 10 g on a painted steel door
with plenty to spare, and pressing a wing only pushes the owl harder against the door. Stainless fridge
doors are often non-magnetic: check with any fridge magnet first. On a non-steel surface, a strip of
removable mounting tape on the back works too.

## Safety

3 V coin cell only, no mains, no LiPo. Every corner of the outline is rounded (1.4 mm minimum, the ear
tufts included). The LEDs are 220 Ω-limited; nothing gets warm.

**Coin cell, launch blocker.** This lives in a kitchen, within reach of children, and a swallowed coin
cell is a medical emergency. In the US, Reese's Law (16 CFR part 1263, in force since March 2024)
requires a consumer product's button or coin cell to be secured so that it takes a tool, or two
independent simultaneous hand movements, to remove, and it adds warning-label and packaging
requirements. A bare Keystone 3034 holder does not meet that: the cell slides out with a fingernail.
Before selling Hoot assembled with a cell, add a screwed retainer over the cell (rev B: two M2 holes
beside the holder and a small cover plate) or an equivalent, and have the product and its labels
reviewed for compliance. Not done in rev A.

## Verification (measured by KiCad 10.0.6 on the files in this folder)

ERC 0 errors / 0 warnings · netlist round trip identical (9 nets) · routing 24 → 0 open (105 tracks,
13 vias) · DRC 0 errors / 0 warnings / 0 unconnected / 0 parity · DFM `jlcpcb_2layer` 0 errors (1
warning: stock footprint silk at 0.12 mm, printed at the fab's 0.15 mm) · fab gate ready · QR modules
0.345 mm. Firmware: 1,544 B text + 26 B data of 4,096 B, built under `-Wall -Wextra -Werror`. Full
numbers: [`report.json`](report.json), [`measured.json`](measured.json).

**Not built yet.** Not fabricated, assembled or powered. On the first prototypes, measure the sleep
current (it should be under 2 µA), time a 2 h water reminder against a clock to see how far the internal
oscillator is off, and check the magnets' hold with a cell in.
