# ZX Spectrum-like UDG Painter - SumGUI rewrite

This is the UDG Painter rewritten to use the local `sumgui` toolkit instead of the older project-local Pygame GUI helpers.

## Run

```bash
python udg_painter_sumgui.py
```

Optional dependency for ICO load/save:

```bash
python -m pip install --user pillow
```

## Controls

- Mouse/touch drag: paint or erase cells.
- Arrow keys: move cursor.
- Shift + arrows: shift the image with wraparound.
- Space: toggle current pixel.
- 0..7: select normal Spectrum colors.
- Shift + 0..7: select bright colors.
- + / -: resize canvas.
- Shift + + / Shift + -: scale image from a stable reference.
- S / L: save / load.
- M: cycle save format.

## Formats

- COLOR `.udg`
- BINARY `.bin`
- XPM `.xpm`
- ICO `.ico`

The internal palette keeps color index 8 as bright black `(22, 22, 22)`.

## 2026-06 input dialog fix

The save filename dialog now uses SumGUI key repeat through `get_events()` and clips/scrolls the visible input window around the cursor. Holding printable keys scrolls the visible text; holding Backspace/Delete repeats as expected.

<p align=center><b>- oOo -</b></p>


