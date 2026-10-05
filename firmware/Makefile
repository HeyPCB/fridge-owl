# Hoot firmware: ATtiny412, avr-gcc with tinyAVR 1-series support (avr-libc's iotn412.h).
#   make                 build hoot.hex
#   make flash PORT=/dev/tty.usbserial-XXXX     program over SerialUPDI (avrdude 7+)
AVR_PREFIX ?=
CC      = $(AVR_PREFIX)avr-gcc
OBJCOPY = $(AVR_PREFIX)avr-objcopy
SIZE    = $(AVR_PREFIX)avr-size
MCU     = attiny412
F_CPU   = 3333333UL
CFLAGS  = -mmcu=$(MCU) -DF_CPU=$(F_CPU) -Os -std=gnu11 -Wall -Wextra -Werror \
          -ffunction-sections -fdata-sections
LDFLAGS = -mmcu=$(MCU) -Wl,--gc-sections
PORT   ?= /dev/ttyUSB0

all: hoot.hex

hoot.elf: main.c
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $<
	$(SIZE) $@

hoot.hex: hoot.elf
	$(OBJCOPY) -O ihex -R .eeprom $< $@

flash: hoot.hex
	avrdude -c serialupdi -P $(PORT) -p t412 -U flash:w:hoot.hex:i

clean:
	rm -f hoot.elf hoot.hex

.PHONY: all flash clean
