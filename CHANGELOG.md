# Changelog

## 0.2.0a4 - 2026-09-02

- Restored **UDG Painter Reborn** to the distributable package after it was accidentally omitted from the r11 final artifact; the installed `sumudg` command launches the packaged application and its UDG/image/icon resources are included in wheel/sdist builds.
- Added the generic `GraphicsWindow` renderer for backend-neutral `sumui.GraphicsMode` / `GraphicsCommand` streams, providing the concrete Pygame target used by sumBASIC graphics.
- Added Spectrum palette state for `INK`, `PAPER`, `BORDER`, `BRIGHT`, `FLASH`, `INVERSE` and `OVER` while preserving arbitrary modern RGB colours.
- Fixed `examples/demo_full.py`: its logical canvas is 720x1280, matching the actual layout instead of scaling a 720x720 logical square. This removes the large top offset and keeps the lower controls inside the fitted window.

## 0.2.0a3 - 2026-09-02

- Added `sumgui.display.desktop_size()` and `fit_window_size()`; the Easy API now checks the physical display before creating a non-fullscreen window and scales large logical layouts down to fit.
- Corrected oversized examples, including the Canvas/BGI demo that requested 1074x2102 despite using only about 700 logical rows.
- Added compact component examples for Label, Button, TextInput, TextArea, Slider, Canvas, ChartView, TerminalArea and an integrated sampler.
- Added `sumgdialog --demo`, an interactive graphical launcher analogous to the existing `sumdialog --demo` role for currently implemented GUI dialog modes.
- `sumgdialog` and direct-Pygame examples now also use physical-display fitting.
- Added coverage for the 1366x768 case to prevent future examples from creating multi-screen-height windows.

## 0.2.0a2 - 2026-09-02

- Coordinated sumGUI with the first sumUI contracts, shared ChartSpec, Android-safe event bridge, logical graphics surface and initial sumgdialog frontend.

<p align=center><b>- oOo -<b></p>
