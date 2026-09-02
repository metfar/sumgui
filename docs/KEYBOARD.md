# SumGUI keyboard and Unicode notes

SumGUI text widgets use `pygame.TEXTINPUT` for printable text. This is important for dead keys and composed characters such as:

```text
á é í ó ú à è ì ò ù â ê î ô û ä ë ï ö ü ñ ç Ñ Ç ¿ ¡ Ω σ λ μ
```

The keymap is related to https://github.com/metfar/myXmodmap .

Raw `KEYDOWN` events are used for control/navigation keys only: arrows, Backspace, Delete, Enter, Home, End, PageUp, PageDown, Tab, Escape and shortcuts.

The SumGUI key repeater avoids generating printable text directly from `KEYDOWN.unicode`; instead it repeats the last `TEXTINPUT` associated with the physical key. This avoids breaking dead-key composition on international keyboard layouts.

For focus traversal:

- `Tab` moves to the next focusable widget.
- `Shift+Tab` moves to the previous focusable widget.
- `TextArea(..., accepts_tab=True)` inserts a tab character instead of changing focus.
- `sumgdialog` follows the same focus ring: entries, other focusable controls and buttons participate in `Tab` / `Shift+Tab` traversal.


<p align=center><b>- oOo -</b></p>
