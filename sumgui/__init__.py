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

__version__ = "0.2.0a18";

from .contracts import GUI_BACKEND, backend_capabilities;
from .eventbridge import event_to_common, touch_to_mouse_event;
from .application_backend import GraphicalApplicationBackend, run_application;
from .graphics import GraphicsSurface, GraphicsWindow;
from .display import desktop_size, display_size, fit_window_size, set_default_icon, sigma_icon;
from .theme import C64_COLORS, DEFAULT_THEME, DOS_COLORS, SPECTRUM_COLORS, THEMES, Theme, make_theme;
from .scale import Scale;
from .keymap import KeyMap, default_voxel_keymap;
from .widgets import Button, CalendarView, CanvasArea, ColorPicker, DateTimeView, EditorView, GridCell, GridWidget, Label, PaletteWidget, Panel, Slider, StatusBar, TextArea, TextInput, TerminalArea, TimeView, ToolBar, Widget;
from .easy import EasyApp;
from sumui import AxisSpec, BackendCapabilities, ChartSeries, ChartSpec, DialogSpec, FieldSpec, GraphicsCommand, GraphicsMode, GraphicsProgram, ImageSpec, InputSpec, TableSpec, UIEvent, basic_mode, modern_mode, spectrum_mode;
from .charts import BarChart, ChartView, LineChart, PieChart, ScatterChart;
from .chart_backends import available_chart_renderers, render_chart_rgba;
from .tables import TableView;
from .dialogs import input_box, message_box, question_box;
from .clipboard import get_clipboard_text, set_clipboard_text;
from .commands import command_help, command_list;
from .voxel import Voxel, VoxelFace, VoxelGridModel, VoxelGridWidgetSpec;

from .keyrepeat import DOS_FAST_DELAY_MS, DOS_FAST_INTERVAL_MS, KeyRepeatConfig, disable_key_repeat, enable_key_repeat, get_events, process_key_repeat;

from .textscreen import GuiTextScreen;
