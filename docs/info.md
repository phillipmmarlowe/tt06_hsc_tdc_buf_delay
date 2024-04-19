<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

A tiny TDC

## How to test

Setup VCS on you local machine, cd to test run:
```make SIM=vcs GATES=yes```

## External hardware

To begin, there are seven input pins: 

pg_in (user controlled pulse input), 

tog_in (constant oscillating square wave at a quarter of clock speed),

pg_src (to select between pg_in and pg_src), 

valid_in (valid protocol for streaming interface), 

clk_l (launch clock), clk_c (capture clock), and

reg (named pg_bypass in the top level module and can be used to bypass a register stage used to synchronize the timing of streamed data)

Along with 8 output pins: 

hw_out[6:0] (Hamming weight decoder output), and

valid_out (valid protocol for streaming interface). 

The input pins are intended to be controlled by an external FPGA which will also handle the data received from the output pins. The actual delay line location can be seen by the module with triangle shaped symbols (similar to a line of interconnected standard buffer symbols).
The following schematic describes this visually.

![Pin Handling and Abstracted Inner TDC Modules Schematic](./tdc.png)
