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

<p align=center><b>- oOo -<b></p>
