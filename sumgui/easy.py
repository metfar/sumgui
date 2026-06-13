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

from .dialogs import message_box;
from .keyrepeat import enable_key_repeat, get_events;
from .scale import Scale;
from .theme import DEFAULT_THEME, make_theme;
from .commands import command_help, command_list;
from .widgets import Button, CanvasArea, Label, Panel, TextArea;

_app = None;


class EasyApp:
    def __init__(self, title="SumGUI", width=720, height=720, font_name="monospace", font_size=18, font_scale=1.0, theme=None):
        pygame.init();
        self.title = title;
        self.width = int(width);
        self.height = int(height);
        self.theme = make_theme(theme) if isinstance(theme, str) else (theme or DEFAULT_THEME);
        self.screen = pygame.display.set_mode((self.width, self.height));
        pygame.display.set_caption(title);
        self.clock = pygame.time.Clock();
        self.scale = Scale(self.width, self.height);
        self.font_name = font_name;
        self.font_size = int(font_size);
        self.font_scale = float(font_scale);
        self.font = self.make_font(self.font_size);
        self.big_font = self.make_font(self.font_size + 8, bold=True);
        self.panel = Panel(pygame.Rect(0, 0, self.width, self.height), self.theme);
        self.running = False;
        enable_key_repeat(250, 31);

    def make_font(self, size=None, bold=False):
        size = self.font_size if size is None else size;
        return pygame.font.SysFont(self.font_name, max(8, int(size * self.font_scale)), bold=bold);

    def add(self, widget):
        return self.panel.add(widget);

    def run(self):
        self.running = True;
        while self.running:
            dt = self.clock.tick(60);
            for event in get_events():
                if event.type == pygame.QUIT:
                    self.running = False;
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False;
                else:
                    self.panel.handle_event(event);
            self.panel.update(dt);
            self.screen.fill(self.theme.bg);
            self.panel.draw(self.screen);
            pygame.display.flip();
        pygame.quit();


def window(title="SumGUI", width=720, height=720, font_name="monospace", font_size=18, font_scale=1.0, theme=None):
    global _app;
    _app = EasyApp(title, width, height, font_name, font_size, font_scale, theme);
    return _app;


def screen(title="SumGUI", width=720, height=720, font_name="monospace", font_size=18, font_scale=1.0, theme=None):
    return window(title, width, height, font_name, font_size, font_scale, theme);


def app():
    if _app is None:
        return window();
    return _app;


def font(size=18, name=None, scale=None):
    current = app();
    if name is not None:
        current.font_name = name;
    if scale is not None:
        current.font_scale = scale;
    current.font_size = int(size);
    current.font = current.make_font(size);
    current.big_font = current.make_font(size + 8, bold=True);
    return current.font;


def say(text, x, y, w=260, h=32, font_size=None, bold=False):
    current = app();
    use_font = current.make_font(font_size or current.font_size, bold=bold);
    return current.add(Label(pygame.Rect(x, y, w, h), text, use_font, current.theme));


def label(text, x, y, w=260, h=32, font_size=None, bold=False):
    return say(text, x, y, w, h, font_size, bold);


def button(text, x, y, w=160, h=50, do=None, font_size=None, bold=True):
    current = app();
    use_font = current.make_font(font_size or current.font_size, bold=bold);
    def callback(widget):
        if do is not None:
            do();
    return current.add(Button(pygame.Rect(x, y, w, h), text, use_font, callback, current.theme));


def textarea(x, y, w, h, text="", font_size=None, accepts_tab=True, tab_size=4, syntax="plain", code_style=None):
    current = app();
    use_font = current.make_font(font_size or current.font_size);
    return current.add(TextArea(pygame.Rect(x, y, w, h), use_font, text, True, True, True, -1, -1, current.theme, show_v_scrollbar=True, show_h_scrollbar=True, accepts_tab=accepts_tab, tab_size=tab_size, syntax=syntax, code_style=code_style));


def canvas(x, y, w, h, interactive=True, auto_redraw=True, on_event=None, on_draw=None):
    current = app();
    return current.add(CanvasArea(pygame.Rect(x, y, w, h), theme=current.theme, on_event=on_event, on_draw=on_draw, interactive=interactive, auto_redraw=auto_redraw));


def alert(message, title="SumGUI"):
    current = app();
    return message_box(current.screen, current.clock, title, message, current.theme);


def commands():
    return command_list();


def keymap_help():
    return command_help();


def start():
    app().run();
