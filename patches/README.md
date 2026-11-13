# Local framework fixes

`snesrecomp-display-memory.patch` applies to the pinned SNESRecomp checkout.
CMake applies it idempotently when configuring the game or its runtime tests.
The submodule therefore appears modified; keep the patch with the game until
the change is incorporated into a future framework pin. Unrelated edits are
preserved; an incompatible patch fails configuration instead of overwriting them.

Power Rangers starts uploading the next pose's OAM and tile data in the bottom
forced-blank interval, before the host finishes its CPU frame. Rendering from
live memory combined next-frame attributes with partially uploaded tiles,
producing detached parts, apparent mirroring and intermittent disappearance.

The game opts into a coherent display-memory copy at the field's first unblank,
after its top-border uploads finish. Each raster journal owns that copy; drawing
temporarily uses it and restores all live graphics memory afterwards. Other
hosts retain their previous behavior unless they opt in. This mode assumes
display memory remains stable during the visible playfield; it is not intended
for titles which deliberately replace palettes or tiles between visible bands.

Regression checks, without a ROM:

```powershell
cmake -S tests -B build/runtime-tests -G 'Visual Studio 17 2022' -A x64
cmake --build build/runtime-tests --config Release --parallel 4
ctest --test-dir build/runtime-tests -C Release --output-on-failure
```

The frame-state extension includes these copies, so save states from before
this change are incompatible with the new frame-state size.
