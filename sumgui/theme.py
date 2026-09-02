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

SPECTRUM_COLORS = [
    (0, 0, 0), (0, 0, 205), (205, 0, 0), (205, 0, 205),
    (0, 205, 0), (0, 205, 205), (205, 205, 0), (205, 205, 205),
    (22, 22, 22), (0, 0, 255), (255, 0, 0), (255, 0, 255),
    (0, 255, 0), (0, 255, 255), (255, 255, 0), (255, 255, 255),
];

C64_COLORS = [
    (0, 0, 0), (255, 255, 255), (136, 0, 0), (170, 255, 238),
    (204, 68, 204), (0, 204, 85), (0, 0, 170), (238, 238, 119),
    (221, 136, 85), (102, 68, 0), (255, 119, 119), (51, 51, 51),
    (119, 119, 119), (170, 255, 102), (0, 136, 255), (187, 187, 187),
];

MSX_COLORS = [
    (0, 0, 0), (0, 0, 0), (33, 200, 66), (94, 220, 120),
    (84, 85, 237), (125, 118, 252), (212, 82, 77), (66, 235, 245),
    (252, 85, 84), (255, 121, 120), (212, 193, 84), (230, 206, 128),
    (33, 176, 59), (201, 91, 186), (204, 204, 204), (255, 255, 255),
];

DOS_COLORS = [
    (0, 0, 0), (0, 0, 170), (0, 170, 0), (0, 170, 170),
    (170, 0, 0), (170, 0, 170), (170, 85, 0), (170, 170, 170),
    (85, 85, 85), (85, 85, 255), (85, 255, 85), (85, 255, 255),
    (255, 85, 85), (255, 85, 255), (255, 255, 85), (255, 255, 255),
];

class Theme:
    def __init__(self, name="dark", bg=(10, 30, 32), panel=(28, 48, 54), line=(55, 75, 85), text=(235, 245, 250), muted=(130, 150, 155), button=(140, 220, 40), button_alt=(60, 100, 120), button_text=(10, 25, 30), error=(255, 100, 100), cursor=(255, 255, 0), palette=None, font_name="monospace", selection_bg=None, selection_text=None, title=None, viewer_bg=None, viewer_text=None):
        self.name = name;
        self.bg = bg;
        self.panel = panel;
        self.line = line;
        self.text = text;
        self.muted = muted;
        self.button = button;
        self.button_alt = button_alt;
        self.button_text = button_text;
        self.error = error;
        self.cursor = cursor;
        self.palette = list(palette or SPECTRUM_COLORS);
        self.font_name = font_name;
        self.selection_bg = selection_bg or button_alt;
        self.selection_text = selection_text or (255, 255, 255);
        self.title = title or cursor;
        self.viewer_bg = viewer_bg or bg;
        self.viewer_text = viewer_text or text;

    def copy(self):
        return Theme(self.name, self.bg, self.panel, self.line, self.text, self.muted, self.button, self.button_alt, self.button_text, self.error, self.cursor, self.palette[:], self.font_name, self.selection_bg, self.selection_text, self.title, self.viewer_bg, self.viewer_text);

    def role_color(self, role, background=False):
        """Resolve the semantic SumTUI editor/theme role to an RGB color.""";
        role = str(role or "text");
        if background:
            if role in ("viewer", "editor", "editor_gutter"):
                return self.viewer_bg;
            if role in ("selection", "menu_selection", "input_focus", "control_focus"):
                return self.selection_bg;
            return self.bg;
        if role in ("editor_gutter", "editor_whitespace", "editor_space"):
            return self.muted;
        if role == "editor_tab":
            return self.title;
        if role == "editor_eol":
            return self.button;
        if role in ("editor_control", "syntax_error"):
            return self.error;
        if role == "syntax_keyword":
            return self.palette[11 % len(self.palette)];
        if role in ("syntax_function", "syntax_builtin", "syntax_constant", "syntax_attribute"):
            return self.palette[14 % len(self.palette)];
        if role in ("syntax_type", "syntax_number", "syntax_label"):
            return self.palette[13 % len(self.palette)];
        if role == "syntax_string":
            return self.palette[10 % len(self.palette)];
        if role == "syntax_comment":
            return self.muted;
        if role in ("syntax_heading", "syntax_markup", "syntax_tag"):
            return self.title;
        if role == "syntax_deleted":
            return self.muted;
        if role == "selection":
            return self.selection_text;
        return self.viewer_text if role.startswith("syntax_") else self.text;


def make_theme(name="ZX"):
    key = str(name).strip().casefold();
    if key in ("zx", "spectrum", "sinclair"):
        return Theme("ZX", (0, 0, 0), (0, 0, 90), (0, 255, 255), (255, 255, 255), (0, 205, 205), (255, 255, 0), (0, 0, 205), (0, 0, 0), (255, 80, 80), (255, 255, 0), SPECTRUM_COLORS);
    if key in ("dos", "pc", "turbo"):
        return Theme("DOS", (0, 0, 0), (0, 0, 170), (170, 170, 170), (255, 255, 255), (170, 170, 170), (170, 170, 170), (0, 0, 170), (0, 0, 0), (255, 85, 85), (255, 255, 85), DOS_COLORS);
    if key in ("rar", "rar-dos", "rar2"):
        return Theme("RAR", (0, 0, 170), (0, 0, 170), (170, 170, 170), (255, 255, 255), (170, 170, 170), (0, 170, 170), (0, 0, 170), (0, 0, 0), (255, 85, 85), (255, 255, 85), DOS_COLORS);
    if key in ("dbase", "dbase3", "dbaseiii"):
        return Theme("DBASE", (0, 0, 170), (0, 0, 170), (170, 170, 170), (255, 255, 85), (170, 170, 170), (170, 170, 170), (0, 170, 170), (0, 0, 0), (255, 85, 85), (255, 255, 255), DOS_COLORS, selection_bg=(170, 0, 0), selection_text=(255, 255, 255), title=(255, 255, 85));
    if key in ("fox", "foxpro"):
        return Theme("FOXPRO", (0, 0, 170), (0, 170, 170), (255, 255, 255), (0, 0, 0), (85, 85, 85), (170, 170, 170), (170, 0, 170), (0, 0, 0), (255, 255, 85), (255, 255, 255), DOS_COLORS, selection_bg=(0, 0, 170), selection_text=(255, 255, 255), title=(255, 255, 85));
    if key in ("xbase", "sumx"):
        return Theme("XBASE", (0, 0, 170), (0, 170, 170), (170, 170, 170), (0, 0, 0), (85, 85, 85), (170, 170, 170), (0, 0, 170), (0, 0, 0), (255, 85, 85), (255, 255, 85), DOS_COLORS, selection_bg=(0, 0, 170), selection_text=(255, 255, 255), title=(255, 255, 85));
    if key in ("c64", "commodore"):
        return Theme("C64", (64, 49, 141), (112, 94, 181), (170, 255, 238), (255, 255, 255), (187, 187, 187), (238, 238, 119), (0, 0, 170), (64, 49, 141), (255, 119, 119), (238, 238, 119), C64_COLORS);
    if key == "msx":
        return Theme("MSX", (0, 0, 0), (33, 33, 96), (66, 235, 245), (255, 255, 255), (204, 204, 204), (94, 220, 120), (84, 85, 237), (0, 0, 0), (252, 85, 84), (255, 255, 255), MSX_COLORS);
    if key == "light":
        return Theme("Light", (245, 245, 245), (255, 255, 255), (80, 80, 80), (20, 20, 20), (90, 90, 90), (70, 130, 220), (220, 220, 220), (255, 255, 255), (200, 40, 40), (0, 90, 180), SPECTRUM_COLORS);
    if key == "dark":
        return Theme("Dark", (10, 30, 32), (28, 48, 54), (55, 75, 85), (235, 245, 250), (130, 150, 155), (140, 220, 40), (60, 100, 120), (10, 25, 30), (255, 100, 100), (255, 255, 0), SPECTRUM_COLORS);
    return Theme("ZX", (0, 0, 0), (0, 0, 90), (0, 255, 255), (255, 255, 255), (0, 205, 205), (255, 255, 0), (0, 0, 205), (0, 0, 0), (255, 80, 80), (255, 255, 0), SPECTRUM_COLORS);


THEMES = {
    "ZX": make_theme("ZX"),
    "DOS": make_theme("DOS"),
    "RAR": make_theme("RAR"),
    "DBASE": make_theme("DBASE"),
    "FOXPRO": make_theme("FOXPRO"),
    "XBASE": make_theme("XBASE"),
    "C64": make_theme("C64"),
    "MSX": make_theme("MSX"),
    "Dark": make_theme("Dark"),
    "Light": make_theme("Light"),
};

DEFAULT_THEME = THEMES["ZX"];
