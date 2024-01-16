#!/usr/bin/env python3

import sys
import fileinput

CPU_TARGET="""CPUhartid: cpu@hartid {
      device_type = "cpu";
      status = "okay";
      compatible = "eth,ariane", "riscv";
      clock-frequency = <targetfreq>;
      riscv,isa = "rv64fimadch";
      mmu-type = "riscv,sv39";
      tlb-split;
      reg = <hartid>;
      CPUhartid_intc: interrupt-controller {
        #address-cells = <1>;
        #interrupt-cells = <1>;
        interrupt-controller;
        compatible = "riscv,cpu-intc";
      };
    };
"""

CLINT="""clint@2000000 {
      compatible = "riscv,clint0";
      interrupts-extended = first-interrupt second-interrupt;
      reg = <0x0 0x2000000 0x0 0xc0000>;
      reg-names = "control";
    };
"""
PLIC="""    PLIC0: interrupt-controller@c000000 {
      #address-cells = <0>;
      #interrupt-cells = <1>;
      compatible = "riscv,plic0";
      interrupt-controller;
      interrupts-extended = first-interrupt second-interrupt;
      reg = <0x0 0xc000000 0x0 0x4000000>;
      riscv,max-priority = <7>;
      riscv,ndev = <255>;
    };
"""
DEBUG="""    debug-controller@0 {
      compatible = "riscv,debug-013";
      interrupts-extended = first-interrupt second-interrupt;
      reg = <0x0 0x0 0x0 0x1000>;
      reg-names = "control";
    };"""

def replace_strings(file_path, old_string, new_string):
    with fileinput.FileInput(file_path, inplace=True, backup=".bak") as file:
        for line in file:
            print(line.replace(old_string, new_string), end='')

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python3 dts_gen.py <file-path> <num_harts> <target-freq> <half-freq> <target-baud>")
        sys.exit(1)
    
    # Extract command-line arguments
    file_path = sys.argv[1]
    num_harts = sys.argv[2]
    
    cpu0 = CPU_TARGET.replace("hartid","0")
    cpu1 = CPU_TARGET.replace("hartid","1")

    clint = CLINT.replace("first-interrupt","<&CPU0_intc 3 &CPU0_intc 7>")
    plic = PLIC.replace("first-interrupt","<&CPU0_intc 11 &CPU0_intc 9>")
    debug= DEBUG.replace("first-interrupt","<&CPU0_intc 65535>")

    if(num_harts=="1"):
        clint = clint.replace("second-interrupt","")
        plic = plic.replace("second-interrupt","")
        debug = debug.replace("second-interrupt","")
        replace_strings(file_path,"target_cpus",cpu0)
    else:
        clint = clint.replace("second-interrupt"," , <&CPU1_intc 3 &CPU1_intc 7>")
        plic = plic.replace("second-interrupt"," , <&CPU1_intc 11 &CPU1_intc 9>")
        debug = debug.replace("second-interrupt"," , <&CPU1_intc 65535>")
        replace_strings(file_path,"target_cpus",cpu0+"    "+cpu1)

    replace_strings(file_path,"ariane_peripherals",clint+plic+debug)
    replace_strings(file_path,"targetfreq",sys.argv[3])
    replace_strings(file_path,"halffreq",sys.argv[4])
    replace_strings(file_path,"targetbaud",sys.argv[5])
