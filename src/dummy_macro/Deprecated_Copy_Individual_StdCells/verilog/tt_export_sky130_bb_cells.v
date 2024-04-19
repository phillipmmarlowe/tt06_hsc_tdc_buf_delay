`timescale 1ns / 1ps
`default_nettype none

(* blackbox *)
module tt_export_sky130_fd_sc_hd__fa_1 (
    `ifdef USE_POWER_PINS
        VPWR,
        VGND,
        VPB ,
        VNB,
    `endif  // USE_POWER_PINS
    COUT,
    SUM ,
    A   ,
    B   ,
    CIN
);

    output COUT;
    output SUM ;
    input  A   ;
    input  B   ;
    input  CIN ;
    `ifdef USE_POWER_PINS
        input  VPWR;
        input  VGND;
        input  VPB ;
        input  VNB ;
    `endif  // USE_POWER_PINS
endmodule

(* blackbox *)
module tt_export_sky130_fd_sc_hd__edfxtp_1 (
    `ifdef USE_POWER_PINS
        VPWR,
        VGND,
        VPB ,
        VNB,
    `endif  // USE_POWER_PINS
    Q   ,
    CLK ,
    D   ,
    DE
);

    output Q   ;
    input  CLK ;
    input  D   ;
    input  DE  ;
    `ifdef USE_POWER_PINS
        input  VPWR;
        input  VGND;
        input  VPB ;
        input  VNB ;
    `endif  // USE_POWER_PINS
endmodule

(* blackbox *)
module tt_export_sky130_fd_sc_hd__and2_1 (
    `ifdef USE_POWER_PINS
        VPWR,
        VGND,
        VPB ,
        VNB,
    `endif  // USE_POWER_PINS    
    X   ,
    A   ,
    B
);

    output X   ;
    input  A   ;
    input  B   ;
    `ifdef USE_POWER_PINS
        input  VPWR;
        input  VGND;
        input  VPB ;
        input  VNB ;
    `endif  // USE_POWER_PINS
endmodule
