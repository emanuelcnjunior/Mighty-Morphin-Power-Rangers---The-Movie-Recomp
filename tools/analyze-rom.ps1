[CmdletBinding()]
param(
    [string] $RomPath,
    [switch] $AllowUnknownHash
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$expectedHash = 'C706B70097C679F6F0CED6F77A30620807D0B2555FC3C683C0EC2FC791176039'
$repoRoot = Split-Path -Parent $PSScriptRoot

if (-not $RomPath) {
    $candidates = @(Get-ChildItem -LiteralPath (Join-Path $repoRoot 'rom') -File |
        Where-Object { $_.Extension -ieq '.sfc' })
    if ($candidates.Count -ne 1) {
        throw "Expected exactly one .sfc file under rom/, found $($candidates.Count). Pass -RomPath explicitly."
    }
    $RomPath = $candidates[0].FullName
}

$resolvedRom = (Resolve-Path -LiteralPath $RomPath).Path
$rom = [System.IO.File]::ReadAllBytes($resolvedRom)
$hash = (Get-FileHash -LiteralPath $resolvedRom -Algorithm SHA256).Hash

if (($hash -ne $expectedHash) -and (-not $AllowUnknownHash)) {
    throw "Unexpected ROM SHA-256: $hash (expected $expectedHash)"
}
if (($rom.Length % 0x8000) -ne 0) {
    throw "ROM size is not aligned to a LoROM bank: $($rom.Length) bytes"
}

$headerOffset = 0x7FC0
if ($rom.Length -lt ($headerOffset + 0x40)) {
    throw 'ROM is too small to contain an SNES LoROM header.'
}

function Read-U16([int] $Offset) {
    return [BitConverter]::ToUInt16($rom, $Offset)
}

function Convert-LoRomAddressToOffset([int] $Bank, [int] $Address) {
    if ($Address -lt 0x8000) {
        throw ('Address ${0:X2}:{1:X4} is outside the normal LoROM ROM window.' -f $Bank, $Address)
    }
    return (($Bank -band 0x7F) -shl 15) -bor ($Address -band 0x7FFF)
}

$title = [Text.Encoding]::ASCII.GetString($rom, $headerOffset, 21).TrimEnd()
$complement = Read-U16 ($headerOffset + 0x1C)
$checksum = Read-U16 ($headerOffset + 0x1E)
$resetVector = Read-U16 ($headerOffset + 0x3C)
$resetOffset = Convert-LoRomAddressToOffset 0 $resetVector
$previewLength = [Math]::Min(16, $rom.Length - $resetOffset)
$resetBytes = ($rom[$resetOffset..($resetOffset + $previewLength - 1)] |
    ForEach-Object { '{0:X2}' -f $_ }) -join ' '

[pscustomobject]@{
    Path                  = $resolvedRom
    SizeBytes             = $rom.Length
    SHA256                = $hash
    Title                 = $title
    MapMode               = '0x{0:X2}' -f $rom[$headerOffset + 0x15]
    RomType               = '0x{0:X2}' -f $rom[$headerOffset + 0x16]
    RomSizeCode           = '0x{0:X2}' -f $rom[$headerOffset + 0x17]
    SramSizeCode          = '0x{0:X2}' -f $rom[$headerOffset + 0x18]
    Checksum              = '0x{0:X4}' -f $checksum
    ChecksumComplement    = '0x{0:X4}' -f $complement
    ChecksumPairValid     = (($checksum -bxor $complement) -eq 0xFFFF)
    ResetVector           = '00:{0:X4}' -f $resetVector
    ResetFileOffset       = '0x{0:X6}' -f $resetOffset
    ResetBytes            = $resetBytes
} | Format-List
