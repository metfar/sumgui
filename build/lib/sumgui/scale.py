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
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#

import pygame;

BASE_WIDTH = 720;
BASE_HEIGHT = 720;


class Scale:
    """Logical-to-screen scaler for SumGUI.

    Coordinates are expressed in a logical canvas, by default 720x720.
    The scaler converts them to real pixels for the current display.

    scale_mode values:
        fit     : keep aspect ratio and fit inside the screen.
        fill    : keep aspect ratio and fill the screen, cropping if needed.
        stretch : scale x and y independently.
        height  : old SumGUI behavior, scale everything from height.
        none    : no scaling.
    """;

    def __init__(self, width, height, base_width=BASE_WIDTH, base_height=BASE_HEIGHT, scale_mode="fit"):
        self.width = int(width);
        self.height = int(height);
        self.base_width = int(base_width);
        self.base_height = int(base_height);
        self.scale_mode = scale_mode or "fit";
        self.update(self.width, self.height);

    def update(self, width=None, height=None):
        if width is not None:
            self.width = int(width);
        if height is not None:
            self.height = int(height);

        sx = self.width / max(1, self.base_width);
        sy = self.height / max(1, self.base_height);

        if self.scale_mode == "stretch":
            self.factor_x = sx;
            self.factor_y = sy;
            self.factor = min(sx, sy);
            self.offset_x = 0;
            self.offset_y = 0;
        elif self.scale_mode == "fill":
            self.factor = max(sx, sy);
            self.factor_x = self.factor;
            self.factor_y = self.factor;
            self.offset_x = int(round((self.width - self.base_width * self.factor) / 2.0));
            self.offset_y = int(round((self.height - self.base_height * self.factor) / 2.0));
        elif self.scale_mode == "height":
            self.factor = sy;
            self.factor_x = sy;
            self.factor_y = sy;
            self.offset_x = 0;
            self.offset_y = 0;
        elif self.scale_mode == "none":
            self.factor = 1.0;
            self.factor_x = 1.0;
            self.factor_y = 1.0;
            self.offset_x = 0;
            self.offset_y = 0;
        else:
            self.factor = min(sx, sy);
            self.factor_x = self.factor;
            self.factor_y = self.factor;
            self.offset_x = int(round((self.width - self.base_width * self.factor) / 2.0));
            self.offset_y = int(round((self.height - self.base_height * self.factor) / 2.0));

    def x(self, value):
        return int(round(self.offset_x + value * self.factor_x));

    def y(self, value):
        return int(round(self.offset_y + value * self.factor_y));

    def w(self, value):
        return max(1, int(round(value * self.factor_x)));

    def h(self, value):
        return max(1, int(round(value * self.factor_y)));

    def v(self, value):
        return max(1, int(round(value * self.factor)));

    def point(self, x, y):
        return self.x(x), self.y(y);

    def size(self, w, h):
        return self.w(w), self.h(h);

    def rect(self, x, y, w, h):
        return pygame.Rect(self.x(x), self.y(y), self.w(w), self.h(h));

    def font_size(self, points):
        return max(8, self.v(points));

    def font(self, points, bold=False, name="monospace"):
        return pygame.font.SysFont(name, self.font_size(points), bold=bold);

    def to_logical(self, x, y):
        lx = (x - self.offset_x) / self.factor_x if self.factor_x else x;
        ly = (y - self.offset_y) / self.factor_y if self.factor_y else y;
        return lx, ly;
