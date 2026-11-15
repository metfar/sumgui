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

COMMANDS = [
    ("Tab", "Move focus to the next widget."),
    ("Shift+Tab", "Move focus to the previous widget."),
    ("Enter / Space", "Activate focused buttons or selected actions."),
    ("Ctrl+C / Ctrl+Insert", "Copy text from focused text widget."),
    ("Ctrl+X / Shift+Delete", "Cut text from focused text widget."),
    ("Ctrl+V / Shift+Insert", "Paste text into focused text widget."),
    ("Arrows", "Move cursor, list selection, grid cursor, sliders or chart points."),
    ("Home / End", "Jump to first/last position where supported."),
    ("PageUp / PageDown", "Move by pages where supported."),
    ("Escape", "Close demos/dialogs or exit app."),
];


def command_help():
    return "\n".join(key + " : " + desc for key, desc in COMMANDS);


def command_list():
    return COMMANDS[:];
