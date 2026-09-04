#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301
#  
#  Copyright 2018- William Martinez Bas <metfar@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
"""r20.2 demo: shared text-grid cursor, graphics plane and patterned BORDER.

Requires Pygame.  Q/Escape/window-close exits; otherwise it closes after ten
seconds so it is also convenient as a quick physical-device smoke test.
""";

import time;
import pygame;

from sumgui import GraphicsWindow, GuiTextScreen;
from sumui import GraphicsCommand, spectrum_mode;


PATTERN = (0b11110000, 0b11110000, 0b00001111, 0b00001111,
           0b11110000, 0b11110000, 0b00001111, 0b00001111);


def main():
    # In a real widget this provider is bound to the live viewport/cell size.
    viewport = [800, 600];
    cell = [10, 20];
    text = GuiTextScreen(lambda: tuple(viewport), lambda: tuple(cell));
    print("sumGUI TextGrid:", text.cols, "x", text.rows);
    print("cursor:", text.cursor(False).value, "->", text.cursor(True).value, "->", text.cursor("block").value);
    text.cursor(True);

    # Native active-surface scaling deliberately leaves a visible four-sided
    # physical frame so the BORDER tile is obvious in this standalone demo.
    window = GraphicsWindow(title="SUM r20.2 - layers / patterned BORDER", window_size=(800, 600), fit_display=False);
    window.handle(spectrum_mode(scaling="native"));
    window.handle(GraphicsCommand("paper", (0,)));
    window.handle(GraphicsCommand("border", (1,)));
    window.handle(GraphicsCommand("border_paper", (1,)));
    window.handle(GraphicsCommand("border_ink", (5,)));
    window.handle(GraphicsCommand("border_pattern", (PATTERN,)));
    window.handle(GraphicsCommand("text", (24, 62, "GRAPHICS plane / GPRINT",), (("color", 7), ("size", 18))));
    window.handle(GraphicsCommand("text", (24, 92, "BORDER is an independent layer",), (("color", 5), ("size", 16))));
    window.handle(GraphicsCommand("sort_layers", (("GRAPHICS", "TEXT"), "ASC")));

    deadline = time.monotonic() + 10.0;
    clock = pygame.time.Clock();
    while not window.closed and time.monotonic() < deadline:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                window.close();
                break;
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_q):
                window.close();
                break;
        if window.closed: break;
        window.surface.scroll_border(1, 0);
        window.present();
        clock.tick(30);
    window.close();
    return 0;


if __name__ == "__main__":
    raise SystemExit(main());
