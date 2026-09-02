# sumGUI 0.2 architecture direction

sumGUI 0.2 is the replacement line for the original experimental Pygame toolkit. The old 0.1 code remains a donor of useful widgets, canvas work and compatibility ideas, but the new architecture converges on the same backend-neutral contracts used by sumTUI.

The first shared contract is `sumui.ChartSpec`: the same chart description can be rendered as ASCII/Unicode/Braille by sumTUI or as pixels by sumGUI.

The next convergence milestones are:

1. backend-neutral event/focus contracts;
2. compatible core widget semantics (`Button`, `TextInput`, containers, validation, `CONFIRM`);
3. graphical `sumgdialog` compatible with `sumdialog`;
4. portable `Canvas`/graphics primitives with arbitrary logical `m x n` modes;
5. adapters for sumBASIC, sumC, sumCPP, sumASM, sumPY and sumR.

Pygame is the graphical backend. NumPy may be used as an optional accelerator later; pandas is not a toolkit dependency.

## Physical display versus logical layout

sumGUI must never assume that the requested logical demo size is available as a physical desktop window. `desktop_size()` queries SDL/Pygame before window creation and `fit_window_size()` reduces oversized windows while preserving aspect ratio. The Easy API keeps widget coordinates in the logical `base_width x base_height` space, so the same application can fit a 768-pixel-high notebook, a tablet, Android, or a larger desktop.

This is a backend responsibility, not a BASIC-specific rule. Future sumC/sumCPP/sumASM/sumPY/sumR applications receive the same behavior.

## Shared chart interchange

`sumchart` is the neutral command-line dispatcher for `sum.chart/1`. Language examples can emit one JSON contract and choose rendering only at execution time (`--backend=tui` or `--backend=gui`). This is the reference pattern for future native language bindings.

<p align=center><b>- oOo -<b></p>
