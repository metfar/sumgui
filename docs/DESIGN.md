# SumGUI / ΣGUI alpha design

SumGUI is a small GUI toolkit over Pygame. It is designed for beginners, teachers, hobbyists, Android/PyDroid3, Linux, Raspberry Pi, old PCs, small tools and retro-flavored applications.

## Philosophy

SumGUI is inspired by home computing: short feedback loops, understandable code, sharing, learning and modifying.

## Core principles

- Simple API first.
- Widgets draw inside their own rectangle.
- Text and children must be clipped to their components.
- All printable text should use `pygame.TEXTINPUT` to support composed Unicode characters and dead keys.
- Keyboard repeat should behave like classic DOS/Spectrum-style editing.
- Mouse and touch should use capture while dragging.
- Themes should be swappable.
- Packaging must support user-local installation.

## Themes

Built-in themes:

- ZX
- DOS
- C64
- Dark
- Light

## Text commands

- Ctrl+C / Ctrl+Insert: copy
- Ctrl+X / Shift+Delete: cut
- Ctrl+V / Shift+Insert: paste

## 2D first

The first alpha focuses on 2D.

<p align=center><b>- oOo -</b></p>
