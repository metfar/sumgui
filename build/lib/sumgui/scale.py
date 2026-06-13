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
BASE_HEIGHT = 1280;

class Scale:
    def __init__(self, width, height, base_height=BASE_HEIGHT):
        self.width = width;
        self.height = height;
        self.base_height = base_height;
        self.factor = height / base_height;

    def v(self, value):
        return max(1, int(round(value * self.factor)));

    def rect(self, x, y, w, h):
        return pygame.Rect(self.v(x), self.v(y), self.v(w), self.v(h));

    def font(self, points, bold=False):
        return pygame.font.SysFont("monospace", max(8, self.v(points)), bold=bold);
