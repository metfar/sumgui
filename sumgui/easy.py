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
from .display import set_default_icon;

from .charts import ChartView;
from .graphics import GraphicsSurface;
from sumui import modern_mode;
from .dialogs import input_box, message_box;
from .keyrepeat import enable_key_repeat, get_events;
from .eventbridge import is_focus_loss, touch_to_mouse_event;
from .display import fit_window_size;
from .scale import Scale;
from .theme import DEFAULT_THEME, make_theme;
from .commands import command_help, command_list;
from .widgets import Button, CanvasArea, Label, Panel, Slider, TextArea, TextInput, TerminalArea, Widget, draw_clipped_text;

_app = None;


def graphics(width=640, height=480, mode=None, scaling="fit", background=(0, 0, 0, 255)):
    resolved = mode if mode is not None else modern_mode(width, height, scaling=scaling);
    return GraphicsSurface(resolved, background=background);


def _alpha_value(value, default=255):
    if value is None:
        return int(default);
    if isinstance(value, float) and 0.0 <= value <= 1.0:
        return int(round(value * 255.0));
    try:
        return max(0, min(255, int(value)));
    except (TypeError, ValueError):
        return int(default);


class AlertBox(Widget):
    def __init__(self, rect, title, message, font, big_font, theme, on_close=None, dialog_alpha=255, curtain_alpha=120):
        super().__init__(rect, focusable=True);
        self.title = str(title);
        self.message = str(message);
        self.font = font;
        self.big_font = big_font;
        self.theme = theme;
        self.on_close = on_close;
        self.dialog_alpha = _alpha_value(dialog_alpha, 255);
        self.curtain_alpha = _alpha_value(curtain_alpha, 120);
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

    def _draw_curtain(self, screen):
        if self.curtain_alpha <= 0:
            return None;
        if self.curtain_alpha >= 255:
            pygame.draw.rect(screen, (0, 0, 0), self.rect);
            return None;
        overlay = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA);
        overlay.fill((0, 0, 0, self.curtain_alpha));
        screen.blit(overlay, self.rect.topleft);
        return None;

    def _draw_box(self, screen, offset_x=0, offset_y=0):
        box = self.box_rect().move(-offset_x, -offset_y);
        ok = self.ok_rect().move(-offset_x, -offset_y);

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
        return None;

    def draw(self, screen):
        self._draw_curtain(screen);
        if self.dialog_alpha >= 255:
            self._draw_box(screen);
            return None;
        if self.dialog_alpha <= 0:
            return None;
        box = self.box_rect();
        dialog_surface = pygame.Surface((box.width, box.height), pygame.SRCALPHA);
        self._draw_box(dialog_surface, box.x, box.y);
        dialog_surface.set_alpha(self.dialog_alpha);
        screen.blit(dialog_surface, box.topleft);
        return None;


class EasyApp:
    def __init__(self, title="SumGUI", width=720, height=720, font_name="monospace", font_size=18, font_scale=1.0, theme=None, base_width=720, base_height=720, scale_mode="fit", fullscreen=False, fit_display=True):
        pygame.init();
        set_default_icon();
        self.title = title;
        self.requested_width = int(width);
        self.requested_height = int(height);
        self.width = self.requested_width;
        self.height = self.requested_height;
        self.base_width = int(base_width);
        self.base_height = int(base_height);
        self.scale_mode = scale_mode;
        self.fullscreen = bool(fullscreen);
        self.fit_display = bool(fit_display);
        self.theme = make_theme(theme) if isinstance(theme, str) else (theme or DEFAULT_THEME);
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN);
            self.width, self.height = self.screen.get_size();
        else:
            if self.fit_display:
                self.width, self.height = fit_window_size(self.width, self.height);
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
                if is_focus_loss(event):
                    self.panel.cancel_pointer_capture();
                    if self.modal is not None:
                        cancel = getattr(self.modal, "cancel_pointer", None);
                        if cancel is not None:
                            cancel();
                    continue;
                if event.type in (getattr(pygame, "FINGERDOWN", -101), getattr(pygame, "FINGERMOTION", -102), getattr(pygame, "FINGERUP", -103)):
                    event = touch_to_mouse_event(event, self.screen.get_size());
                elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION) and getattr(event, "touch", False):
                    # Pygame may synthesize a mouse event for the same native
                    # touch event.  Native FINGER events are our source of truth.
                    continue;
                if event.type == pygame.QUIT:
                    self.panel.cancel_pointer_capture();
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


def window(title="SumGUI", width=720, height=720, font_name="monospace", font_size=18, font_scale=1.0, theme=None, base_width=720, base_height=720, scale_mode="fit", fullscreen=False, fit_display=True):
    global _app;
    _app = EasyApp(title, width, height, font_name, font_size, font_scale, theme, base_width, base_height, scale_mode, fullscreen, fit_display);
    return _app;


def screen(title="SumGUI", width=720, height=720, font_name="monospace", font_size=18, font_scale=1.0, theme=None, base_width=720, base_height=720, scale_mode="fit", fullscreen=False, fit_display=True):
    return window(title, width, height, font_name, font_size, font_scale, theme, base_width, base_height, scale_mode, fullscreen, fit_display);


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


def inputline(x, y, w, h, text="", placeholder="", font_size=None, max_length=-1, show_h_scrollbar=False,
              confirm_at_limit=True, validator=None, validation_error="Invalid value", on_validation_error=None,
              on_submit=None, valid_values=(), case_sensitive=False, char_filter=None, clear_on_first_edit=False, spec=None):
    current = app();
    if spec is not None:
        from sumui import FieldSpec;
        field = spec if isinstance(spec, FieldSpec) else FieldSpec.from_dict(spec);
        text = str(field.default if field.default is not None else "");
        placeholder = field.placeholder or placeholder;
        max_length = -1 if field.max_length is None else field.max_length;
        confirm_at_limit = field.confirm;
        valid_values = field.valid_values;
        case_sensitive = field.case_sensitive;
        validation_error = field.validation_error;
    use_font = current.make_font(font_size or current.font_size);
    return current.add(TextInput(
        current.rect(x, y, w, h), use_font, text=text, placeholder=placeholder, max_length=max_length,
        theme=current.theme, show_h_scrollbar=show_h_scrollbar, confirm_at_limit=confirm_at_limit,
        validator=validator, validation_error=validation_error, on_validation_error=on_validation_error,
        on_submit=on_submit, valid_values=valid_values, case_sensitive=case_sensitive, char_filter=char_filter,
        clear_on_first_edit=clear_on_first_edit,
    ));


def textinput(x, y, w, h, text="", placeholder="", font_size=None, max_length=-1, show_h_scrollbar=False, **kwargs):
    return inputline(x, y, w, h, text=text, placeholder=placeholder, font_size=font_size, max_length=max_length, show_h_scrollbar=show_h_scrollbar, **kwargs);


def textarea(x, y, w, h, text="", font_size=None, accepts_tab=True, tab_size=4, syntax=None, show_v_scrollbar=True, show_h_scrollbar=True):
    current = app();
    use_font = current.make_font(font_size or current.font_size);
    return current.add(TextArea(current.rect(x, y, w, h), use_font, text, True, True, True, -1, -1, current.theme, show_v_scrollbar=show_v_scrollbar, show_h_scrollbar=show_h_scrollbar, accepts_tab=accepts_tab, tab_size=tab_size, syntax=syntax));


def canvas(x, y, w, h, interactive=True, auto_redraw=True, on_event=None, on_draw=None):
    current = app();
    return current.add(CanvasArea(current.rect(x, y, w, h), theme=current.theme, on_event=on_event, on_draw=on_draw, interactive=interactive, auto_redraw=auto_redraw));


def chart(spec, x, y, w, h, font_size=None):
    current = app();
    use_font = current.make_font(font_size or current.font_size);
    return current.add(ChartView(current.rect(x, y, w, h), spec, use_font, current.theme));



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

def alert(message, title="SumGUI", on_close=None, dialog_alpha=255, curtain_alpha=120, alpha=None, opacity=None):
    current = app();
    if alpha is not None:
        dialog_alpha = alpha;
    if opacity is not None:
        dialog_alpha = opacity;
    dialog = AlertBox(
        pygame.Rect(0, 0, current.width, current.height),
        title,
        message,
        current.font,
        current.big_font,
        current.theme,
        on_close,
        dialog_alpha=dialog_alpha,
        curtain_alpha=curtain_alpha,
    );
    dialog.owner = current;
    current.show_modal(dialog);
    return dialog;


def message(message, title="SumGUI", on_close=None, dialog_alpha=255, curtain_alpha=120, alpha=None, opacity=None):
    return alert(message, title, on_close, dialog_alpha, curtain_alpha, alpha, opacity);


def ask(title="Input", message="", default_text="", max_length=-1):
    current = app();
    return input_box(current.screen, current.clock, title, message, default_text, current.theme, max_length=max_length);


def commands():
    return command_list();


def keymap_help():
    return command_help();


def start():
    app().run();
