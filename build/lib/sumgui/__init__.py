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

# PyDroid3 bootstrap: load pygame before SumGUI submodules.
# Some Android/PyDroid3 builds fail if internal widgets import pygame
# before the top-level package has forced pygame to load.
import pygame;

__version__ = "0.0.1a27";

from .theme import C64_COLORS, DEFAULT_THEME, DOS_COLORS, MSX_COLORS, SPECTRUM_COLORS, THEMES, Theme, make_theme;
from .scale import Scale;
from .keymap import KeyMap, default_voxel_keymap;
from .widgets import Button, CanvasArea, ColorPicker, GridCell, GridWidget, Label, PaletteWidget, Panel, Slider, StatusBar, TextArea, TextInput, TerminalArea, ToolBar, Widget;
from .easy import EasyApp;
from .charts import BarChart, LineChart, PieChart, ScatterChart;
from .dialogs import input_box, message_box;
from .clipboard import get_clipboard_text, set_clipboard_text;
from .commands import command_help, command_list;
from .voxel import Voxel, VoxelFace, VoxelGridModel, VoxelGridWidgetSpec;

from .keyrepeat import DOS_FAST_DELAY_MS, DOS_FAST_INTERVAL_MS, KeyRepeatConfig, disable_key_repeat, enable_key_repeat, get_events, process_key_repeat;
