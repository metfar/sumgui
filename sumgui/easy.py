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

from .dialogs import input_box, message_box;
from .keyrepeat import enable_key_repeat, get_events;
from .scale import Scale;
from .theme import DEFAULT_THEME, make_theme;
from .commands import command_help, command_list;
from .widgets import Button, CanvasArea, Label, Panel, Slider, TextArea, TextInput, TerminalArea, Widget, draw_clipped_text;

_app = None;


class AlertBox(Widget):
    def __init__(self, rect, title, message, font, big_font, theme, on_close=None):
        super().__init__(rect, focusable=True);
        self.title = str(title);
        self.message = str(message);
        self.font = font;
        self.big_font = big_font;
        self.theme = theme;
        self.on_close = on_close;
        self.closed = False;
        self.ok_pressed = False;

    def close(self):
        if self.closed:
            return True;
        self.closed = True;
        owner = getattr(self, "owner", None);
        if owner is not None:
            owner.close_modal();
        if self.on_close is not None:
            self.on_close(self);
        return True;

    def box_rect(self):
        width = max(240, int(self.rect.width * 0.78));
        height = max(170, int(self.rect.height * 0.28));
        return pygame.Rect(
            self.rect.centerx - width // 2,
            self.rect.centery - height // 2,
            width,
            height,
        );

    def ok_rect(self):
        box = self.box_rect();
        w = max(90, int(box.width * 0.28));
        h = max(40, int(box.height * 0.22));
        return pygame.Rect(box.centerx - w // 2, box.bottom - h - 18, w, h);

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE, pygame.K_SPACE):
                return self.close();
            return True;
        if event.type == pygame.TEXTINPUT:
            return True;
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.ok_pressed = self.ok_rect().collidepoint(event.pos);
            return True;
        if event.type == pygame.MOUSEBUTTONUP:
            ok = self.ok_rect();
            was_pressed = self.ok_pressed;
            self.ok_pressed = False;
            if was_pressed and ok.collidepoint(event.pos):
                return self.close();
            return True;
        if event.type in (pygame.MOUSEMOTION, pygame.MOUSEWHEEL):
            return True;
        return True;

    def update(self, dt):
        return None;

    def draw(self, screen):
        overlay = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA);
        overlay.fill((0, 0, 0, 120));
        screen.blit(overlay, self.rect.topleft);

        box = self.box_rect();
        ok = self.ok_rect();

        pygame.draw.rect(screen, self.theme.panel, box, border_radius=8);
        pygame.draw.rect(screen, self.theme.line, box, 3, border_radius=8);

        title_rect = pygame.Rect(box.x + 18, box.y + 14, box.width - 36, self.big_font.get_height() + 8);
        draw_clipped_text(screen, self.big_font, self.title, self.theme.text, title_rect);

        body_rect = pygame.Rect(box.x + 18, title_rect.bottom + 10, box.width - 36, ok.y - title_rect.bottom - 18);
        y = body_rect.y;
        line_h = self.font.get_height() + 4;
        previous_clip = screen.get_clip();
        screen.set_clip(body_rect);
        for line in self.message.split("\n"):
            if y + line_h > body_rect.bottom:
                break;
            draw_clipped_text(screen, self.font, line, self.theme.text, pygame.Rect(body_rect.x, y, body_rect.width, line_h));
            y += line_h;
        screen.set_clip(previous_clip);

        color = getattr(self.theme, "accent", self.theme.button) if self.ok_pressed else self.theme.button;
        pygame.draw.rect(screen, color, ok, border_radius=8);
        pygame.draw.rect(screen, self.theme.line, ok, 2, border_radius=8);
        draw_clipped_text(screen, self.big_font, "OK", self.theme.button_text, ok, align="center", valign="middle");


class EasyApp:
    def __init__(self, title="SumGUI", width=720, height=720, font_name="monospace", font_size=18, font_scale=1.0, theme=None, base_width=720, base_height=720, scale_mode="fit", fullscreen=False):
        pygame.init();
        self.title = title;
        self.width = int(width);
        self.height = int(height);
        self.base_width = int(base_width);
        self.base_height = int(base_height);
        self.scale_mode = scale_mode;
        self.fullscreen = bool(fullscreen);
        self.theme = make_theme(theme) if isinstance(theme, str) else (theme or DEFAULT_THEME);
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN);
            self.width, self.height = self.screen.get_size();
        else:
            self.screen = pygame.display.set_mode((self.width, self.height));
        pygame.display.set_caption(title);
        self.clock = pygame.time.Clock();
        self.scale = Scale(self.width, self.height, self.base_width, self.base_height, self.scale_mode);
        self.font_name = font_name;
        self.font_size = int(font_size);
        self.font_scale = float(font_scale);
        self.font = self.make_font(self.font_size);
        self.big_font = self.make_font(self.font_size + 8, bold=True);
        self.panel = Panel(pygame.Rect(0, 0, self.width, self.height), self.theme);
        self.modal = None;
        self.running = False;
        enable_key_repeat(250, 31);

    def make_font(self, size=None, bold=False):
        size = self.font_size if size is None else size;
        return pygame.font.SysFont(self.font_name, max(8, int(self.scale.font_size(size) * self.font_scale)), bold=bold);

    def x(self, value):
        return self.scale.x(value);

    def y(self, value):
        return self.scale.y(value);

    def w(self, value):
        return self.scale.w(value);

    def h(self, value):
        return self.scale.h(value);

    def v(self, value):
        return self.scale.v(value);

    def rect(self, x, y, w, h):
        return self.scale.rect(x, y, w, h);

    def point(self, x, y):
        return self.scale.point(x, y);

    def size(self, w, h):
        return self.scale.size(w, h);

    def to_logical(self, x, y):
        return self.scale.to_logical(x, y);

    def add(self, widget):
        return self.panel.add(widget);

    def show_modal(self, modal):
        self.modal = modal;
        return modal;

    def close_modal(self):
        self.modal = None;
        return True;

    def run(self):
        self.running = True;
        while self.running:
            dt = self.clock.tick(60);
            for event in get_events():
                if event.type == pygame.QUIT:
                    self.running = False;
                elif self.modal is not None:
                    self.modal.handle_event(event);
                else:
                    handled = self.panel.handle_event(event);
                    if not handled and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.running = False;
            self.panel.update(dt);
            if self.modal is not None:
                self.modal.update(dt);
            self.screen.fill(self.theme.bg);
            self.panel.draw(self.screen);
            if self.modal is not None:
                self.modal.draw(self.screen);
            pygame.display.flip();
        pygame.quit();


def window(title="SumGUI", width=720, height=720, font_name="monospace", font_size=18, font_scale=1.0, theme=None, base_width=720, base_height=720, scale_mode="fit", fullscreen=False):
    global _app;
    _app = EasyApp(title, width, height, font_name, font_size, font_scale, theme, base_width, base_height, scale_mode, fullscreen);
    return _app;


def screen(title="SumGUI", width=720, height=720, font_name="monospace", font_size=18, font_scale=1.0, theme=None, base_width=720, base_height=720, scale_mode="fit", fullscreen=False):
    return window(title, width, height, font_name, font_size, font_scale, theme, base_width, base_height, scale_mode, fullscreen);


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
    return current.add(Label(current.rect(x, y, w, h), text, use_font, current.theme));


def label(text, x, y, w=260, h=32, font_size=None, bold=False):
    return say(text, x, y, w, h, font_size, bold);


def button(text, x, y, w=160, h=50, do=None, font_size=None, bold=True):
    current = app();
    use_font = current.make_font(font_size or current.font_size, bold=bold);
    def callback(widget):
        if do is not None:
            do();
    return current.add(Button(current.rect(x, y, w, h), text, use_font, callback, current.theme));


def inputline(x, y, w, h, text="", placeholder="", font_size=None, max_length=-1, show_h_scrollbar=False):
    current = app();
    use_font = current.make_font(font_size or current.font_size);
    return current.add(TextInput(current.rect(x, y, w, h), use_font, text=text, placeholder=placeholder, max_length=max_length, theme=current.theme, show_h_scrollbar=show_h_scrollbar));


def textinput(x, y, w, h, text="", placeholder="", font_size=None, max_length=-1, show_h_scrollbar=False):
    return inputline(x, y, w, h, text=text, placeholder=placeholder, font_size=font_size, max_length=max_length, show_h_scrollbar=show_h_scrollbar);


def textarea(x, y, w, h, text="", font_size=None, accepts_tab=True, tab_size=4, syntax=None, show_v_scrollbar=True, show_h_scrollbar=True):
    current = app();
    use_font = current.make_font(font_size or current.font_size);
    return current.add(TextArea(current.rect(x, y, w, h), use_font, text, True, True, True, -1, -1, current.theme, show_v_scrollbar=show_v_scrollbar, show_h_scrollbar=show_h_scrollbar, accepts_tab=accepts_tab, tab_size=tab_size, syntax=syntax));


def canvas(x, y, w, h, interactive=True, auto_redraw=True, on_event=None, on_draw=None):
    current = app();
    return current.add(CanvasArea(current.rect(x, y, w, h), theme=current.theme, on_event=on_event, on_draw=on_draw, interactive=interactive, auto_redraw=auto_redraw));



def terminal(x, y, w, h, text="", font_size=None, show_v_scrollbar=True, show_h_scrollbar=True):
    current = app();
    use_font = current.make_font(font_size or current.font_size);
    return current.add(TerminalArea(current.rect(x, y, w, h), use_font, text=text, theme=current.theme, show_v_scrollbar=show_v_scrollbar, show_h_scrollbar=show_h_scrollbar));


def slider(label_text, x, y, w, h, minimum=0.0, maximum=1.0, value=0.0, orientation="horizontal", step=None, do=None, font_size=None):
    current = app();
    use_font = current.make_font(font_size or current.font_size);
    return current.add(Slider(current.rect(x, y, w, h), minimum, maximum, value, orientation, step, do, use_font, label_text, current.theme));


def rect(x, y, w, h):
    return app().rect(x, y, w, h);


def point(x, y):
    return app().point(x, y);


def size(w, h):
    return app().size(w, h);


def logical_pos(x, y):
    return app().to_logical(x, y);

def alert(message, title="SumGUI", on_close=None):
    current = app();
    dialog = AlertBox(
        pygame.Rect(0, 0, current.width, current.height),
        title,
        message,
        current.font,
        current.big_font,
        current.theme,
        on_close,
    );
    dialog.owner = current;
    current.show_modal(dialog);
    return dialog;


def message(message, title="SumGUI", on_close=None):
    return alert(message, title, on_close);


def ask(title="Input", message="", default_text="", max_length=-1):
    current = app();
    return input_box(current.screen, current.clock, title, message, default_text, current.theme, max_length=max_length);


def commands():
    return command_list();


def keymap_help():
    return command_help();


def start():
    app().run();
