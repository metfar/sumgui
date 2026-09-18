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

class KeyMap:
    def __init__(self):
        self.bindings = {};

    def bind(self, action, keys):
        self.bindings[action] = list(keys);

    def match(self, event, action):
        return event.type == pygame.KEYDOWN and event.key in self.bindings.get(action, []);

    def actions_for_event(self, event):
        if event.type != pygame.KEYDOWN:
            return [];
        return [action for action, keys in self.bindings.items() if event.key in keys];


def default_voxel_keymap():
    keymap = KeyMap();
    keymap.bind("move_y_neg", [pygame.K_w, pygame.K_KP8]);
    keymap.bind("move_y_pos", [pygame.K_x, pygame.K_KP2]);
    keymap.bind("move_x_neg", [pygame.K_a, pygame.K_KP4]);
    keymap.bind("move_x_pos", [pygame.K_d, pygame.K_KP6]);
    keymap.bind("move_z_pos", [pygame.K_e, pygame.K_KP9]);
    keymap.bind("move_z_neg", [pygame.K_z, pygame.K_KP1]);
    keymap.bind("confirm", [pygame.K_RETURN, pygame.K_SPACE]);
    keymap.bind("cancel", [pygame.K_ESCAPE]);
    return keymap;
