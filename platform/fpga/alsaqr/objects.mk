#
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright (C) 2019 FORTH-ICS/CARV
#		Panagiotis Peristerakis <perister@ics.forth.gr>
#

ifndef TARGET_FREQ
  $(error TARGET_FREQ not set - please export TARGET FREQ in Hz)
endif

ifeq ($(shell expr $(TARGET_FREQ) \>= 50000000), 1)
  TARGET_BAUDRATE := 115200
else ifeq ($(shell expr $(TARGET_FREQ) \>= 40000000), 1)
	TARGET_BAUDRATE := 38400
else
	TARGET_BAUDRATE := 9600
endif

platform-genflags-y += -DTARGET_FREQ=$(TARGET_FREQ) -DTARGET_BAUDRATE=$(TARGET_BAUDRATE)

# Compiler flags
platform-cppflags-y =
platform-cflags-y =
platform-asflags-y =
platform-ldflags-y =

# Object to build
platform-objs-y += platform.o

PLATFORM_RISCV_XLEN = 64

# Blobs to build
FW_TEXT_START=0x80000000
FW_JUMP=n

ifeq ($(PLATFORM_RISCV_XLEN), 32)
 # This needs to be 4MB aligned for 32-bit support
 FW_JUMP_ADDR=0x80400000
 else
 # This needs to be 2MB aligned for 64-bit support
 FW_JUMP_ADDR=0x80200000
 endif
FW_JUMP_FDT_ADDR=0x82200000

# Firmware with payload configuration.
FW_PAYLOAD=y

ifeq ($(PLATFORM_RISCV_XLEN), 32)
# This needs to be 4MB aligned for 32-bit support
  FW_PAYLOAD_OFFSET=0x400000
else
# This needs to be 2MB aligned for 64-bit support
  FW_PAYLOAD_OFFSET=0x200000
endif
FW_PAYLOAD_FDT_ADDR=0x81800000
FW_PAYLOAD_ALIGN=0x1000

clean.dts:
	rm -f $(platform_src_dir)/fdt_gen/alsaqr.dts

alsaqr.dts: clean.dts
	$(shell sed 's/targetfreq/$(TARGET_FREQ)/g' $(platform_src_dir)/fdt_gen/alsaqr-template.dts > $(platform_src_dir)/fdt_gen/alsaqr.dts)
	$(shell sed -i 's/targetbaud/$(TARGET_BAUDRATE)/g' $(platform_src_dir)/fdt_gen/alsaqr.dts)

PHONY: clean.dts alsaqr.dts
