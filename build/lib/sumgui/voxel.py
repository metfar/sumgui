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

from dataclasses import dataclass;

@dataclass
class VoxelFace:
    color: int = -1;
    text: str = "";
    image: object = None;

@dataclass
class Voxel:
    color: int = -1;
    text: str = "";
    image: object = None;
    faces: dict = None;

    def __post_init__(self):
        if self.faces is None:
            self.faces = {
                "top": VoxelFace(),
                "bottom": VoxelFace(),
                "left": VoxelFace(),
                "right": VoxelFace(),
                "front": VoxelFace(),
                "back": VoxelFace(),
            };

class VoxelGridModel:
    def __init__(self, width=8, height=8, depth=8):
        self.width = width;
        self.height = height;
        self.depth = depth;
        self.voxels = [[[Voxel() for _x in range(width)] for _y in range(height)] for _z in range(depth)];

    def inside(self, x, y, z):
        return 0 <= x < self.width and 0 <= y < self.height and 0 <= z < self.depth;

    def get(self, x, y, z):
        if not self.inside(x, y, z):
            return None;
        return self.voxels[z][y][x];

    def set(self, x, y, z, color=-1, text="", image=None):
        if not self.inside(x, y, z):
            return False;
        voxel = self.voxels[z][y][x];
        voxel.color = color;
        voxel.text = text;
        voxel.image = image;
        return True;

class VoxelGridWidgetSpec:
    """Design stub for alpha: render/backend comes in SumGUI 0.2.

    Planned features:
    - isometric 2D render over Pygame, no OpenGL required;
    - cursor in X/Y/Z;
    - remappable keys through KeyMap;
    - optional text/image per voxel or per visible face;
    - Nav3DPad for move/rotate/scale.
    """;
