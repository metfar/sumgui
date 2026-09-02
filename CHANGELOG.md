# Changelog

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
