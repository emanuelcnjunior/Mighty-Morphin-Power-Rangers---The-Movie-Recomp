# Initial ROM map

The validated dump is a 12-Mbit LoROM image with no copier header.

| CPU address | File offset | Meaning |
| --- | ---: | --- |
| `$00:8000` | `$000000` | Reset entry point |
| `$00:FFC0` | `$007FC0` | Internal SNES header |
| `$00:FFEA` | `$007FEA` | Native-mode interrupt vectors |
| `$00:FFF4` | `$007FF4` | Emulation-mode interrupt vectors |

For normal LoROM ROM addresses (`$xx:8000-$xx:FFFF`), the conversion used is:

```text
file_offset = ((bank & $7F) << 15) | (address & $7FFF)
```

The reset vector stored at file offset `$007FFC` is `$8000`, which maps to the
first byte in the image. Mapping mirrored banks is handled by masking bank bit
7 in the conversion.

## Known header values

| Field | Value |
| --- | --- |
| Internal title | `POWER RANGERS MOVIE` |
| Map mode | `$20` (slow LoROM) |
| ROM type | `$00` |
| ROM size code | `$0B` |
| SRAM size code | `$00` |
| Checksum complement | `$0DF4` |
| Checksum | `$F20B` |

The checksum and complement XOR to `$FFFF`.

## Reset path (`$00:8000`)

The first pass identifies the following initialization sequence. Labels are
provisional until control-flow analysis covers all callers.

```asm
Reset_008000:
    sei
    cld
    clc
    xce                 ; enter native 65816 mode
    sep #$20            ; 8-bit accumulator
    rep #$10            ; 16-bit index registers
    stz $4200           ; disable NMI, IRQ and auto joypad read
    ldx #$1FFF
    txs
    ldx #$0000
    phx
    pld                 ; direct page = $0000
    lda #$00
    pha
    plb                 ; data bank = $00
    lda #$80
    sta $2100           ; forced blank
    stz $2106
    lda #$80
    sta $2115           ; VRAM increment mode
    stz $2123
    stz $2124
    stz $2125
    stz $2126
    stz $2127
    stz $2128
    stz $2129
    stz $212A
    stz $212B
    lda #$30
    sta $2130
    lda #$00
    sta $2131
    lda #$E0
    sta $2132
    lda #$00
    sta $2133
    lda #$FF
    sta $4201
    stz $420B
    stz $420C
    stz $420D
    ldx #$0000
.clear_low_wram:
    stz $00,x
    inx
    cpx #$1F00
    bne .clear_low_wram
    jsr Init_0080B3
```

This establishes a useful first subsystem boundary: `Init_0080B3` runs after
CPU/PPU baseline setup and after clearing `$0000-$1EFF` in low WRAM.
