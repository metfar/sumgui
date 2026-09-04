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
"""sumGUI implementation helpers for the shared dynamic text-grid contract.""";

from sumui import CursorState, TextScreen, coerce_cursor_state;


class GuiTextScreen(TextScreen):
    """Translate a pixel viewport into terminal-like rows/columns.

    ``viewport_provider`` returns ``(width_px, height_px)`` and
    ``cell_provider`` returns ``(cell_width_px, cell_height_px)``.  Both are
    queried for every call, so resize/orientation/font changes are immediate.
    ``cursor_target`` may expose ``set_cursor_state(state)``.
    """;
    def __init__(self, viewport_provider, cell_provider, cursor_target=None, fallback=(80,25)):
        self.viewport_provider = viewport_provider;
        self.cell_provider = cell_provider;
        self.cursor_target = cursor_target;
        super().__init__(size_provider=self._grid_size, cursor_setter=self._set_cursor, fallback=fallback);

    def _grid_size(self):
        width, height = self.viewport_provider();
        cell_width, cell_height = self.cell_provider();
        return max(1, int(width) // max(1, int(cell_width))), max(1, int(height) // max(1, int(cell_height)));

    def _set_cursor(self, state):
        state = coerce_cursor_state(state);
        target = self.cursor_target;
        setter = getattr(target, "set_cursor_state", None) if target is not None else None;
        if callable(setter): setter(state);
        return state;


__all__ = ["GuiTextScreen"];
