# Changelog

## 0.2.0a10 - 2026-09-02

- Added BGI-compatible arc/ellipse/text/fill primitive rendering without `.BGI` driver files.
- Added active/visible graphics pages, AUTO/MANUAL presentation, page copy/update and a graphical conio backend.
- Added BGI/conio/stdio Python examples and compact-font dashboard rendering.

## 0.2.0a9 - 2026-09-02
- Added the BASIC-compatible 16-color palette for arbitrary BASIC graphics modes while retaining Spectrum palette semantics for Spectrum profiles.
- `GraphicsSurface` now captures/restores image regions, flood-fills (`PAINT`/`FILL`), saves/loads images, and consumes shared image/table/chart commands.
- Added `TableView`, horizontal bar and radar rendering, chart labels/legends, and `examples/demo_report_dashboard.py`.
- Graphical application windows can export their current rendered image as PNG.
- UDG Painter Reborn remains part of the package.

## 0.2.0a8 - 2026-09-02
- ZX is now the native GUI default theme and the default for sumgdialog and graphical demos.
- Removed the retired third-party-derived colour scheme from the built-in GUI theme registry.
- Unknown theme names fall back to ZX so legacy saved configurations remain launchable.
- The shared-application renderer continues to consume the exact active application theme.

## 0.2.0a6 - 2026-09-02

- Added `GraphicalApplicationBackend`, a Pygame presentation backend for the **same live Sum application tree** used by sumTUI. This is the first Vim/GVim-style convergence milestone: application logic is not reimplemented for graphical mode.
- The backend renders Rich semantic styles into graphical character cells, so existing menus, status/function bars, dialogs, editor syntax highlighting and TUI color schemes immediately carry into graphical presentation.
- Pygame keyboard, text input, mouse press/release/move, drag, wheel and resize events are translated to the application's existing Sum events. Native Android/Pygame FINGER events are translated once and synthesized `touch=True` mouse duplicates are suppressed.
- Added `EditorView`, a native pixel-editor surface for the next renderer stage. It supports line numbers, semantic syntax roles, invisibles/control glyphs, horizontal/vertical scrolling and live syntax-cache invalidation after edits.
- Added GUI theme definitions aligned with the established Sum schemes (`ZX`, `DOS`, `RAR`, `DBASE`, `FOXPRO`, `XBASE`, `C64`, `MSX`, `Dark`, `Light`). ZX is the fresh-install default. The shared application renderer continues to use the exact active sumTUI theme styles.
- Includes the 0.2.0a5 `sumgdialog` Tab/Shift+Tab focus traversal fix and retains UDG Painter Reborn.

## 0.2.0a5 - 2026-09-02

- `sumgdialog` now uses the common focus ring for dialog controls.
- `Tab` moves from an entry to the next focusable field/component/button; `Shift+Tab` moves backwards.
- Entry dialogs traverse `Entry -> OK -> CANCEL -> Entry` cyclically.
- Question/message dialogs and the `sumgdialog --demo` launcher use the same keyboard-focus rules.
- Focused buttons use the existing visual focus border and activate with Enter/Space.

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