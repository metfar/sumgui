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
from .theme import DEFAULT_THEME;
from .widgets import Button, Panel, TextInput, draw_clipped_text, with_clip;
from .keyrepeat import get_events;
from .eventbridge import is_focus_loss, touch_to_mouse_event;


def message_box(screen, clock, title, message, theme=None):
    theme = theme or DEFAULT_THEME;
    width, height = screen.get_size();
    font_big = pygame.font.SysFont("monospace", max(18, height // 32), bold=True);
    font_small = pygame.font.SysFont("monospace", max(14, height // 48), bold=True);
    rect = pygame.Rect(width // 10, height // 3, width * 8 // 10, height // 3);
    ok_rect = pygame.Rect(rect.centerx - width // 8, rect.bottom - height // 12, width // 4, height // 16);
    state = {"done": False};

    def close(unused_button=None):
        state["done"] = True;

    focus = Panel(rect, theme=theme);
    ok_button = focus.add(Button(ok_rect, "OK", font_big, close, theme=theme, tab_index=0));
    while True:
        for event in _dialog_events(screen):
            if event.type == pygame.QUIT:
                return False;
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return True;
            focus.handle_event(event);
            if state["done"]:
                return True;
        pygame.draw.rect(screen, theme.panel, rect, border_radius=8);
        pygame.draw.rect(screen, theme.line, rect, 3, border_radius=8);
        title_rect = pygame.Rect(rect.x + 20, rect.y + 16, rect.width - 40, font_big.get_height() + 6);
        draw_clipped_text(screen, font_big, title, theme.text, title_rect);
        body_rect = pygame.Rect(rect.x + 20, rect.y + 66, rect.width - 40, ok_rect.y - rect.y - 82);
        def draw_body():
            y = body_rect.y;
            line_h = font_small.get_height() + 4;
            for line in message.split("\n"):
                if y + line_h > body_rect.bottom:
                    break;
                draw_clipped_text(screen, font_small, line, theme.text, pygame.Rect(body_rect.x, y, body_rect.width, line_h));
                y += line_h;
        with_clip(screen, body_rect, draw_body);
        ok_button.draw(screen);
        pygame.display.flip();
        clock.tick(60);


def _dialog_events(screen):
    for event in get_events():
        if is_focus_loss(event):
            continue;
        if event.type in (getattr(pygame, "FINGERDOWN", -101), getattr(pygame, "FINGERMOTION", -102), getattr(pygame, "FINGERUP", -103)):
            yield touch_to_mouse_event(event, screen.get_size());
            continue;
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION) and getattr(event, "touch", False):
            continue;
        yield event;


def question_box(screen, clock, title, message, theme=None, yes_label="YES", no_label="NO"):
    theme = theme or DEFAULT_THEME;
    width, height = screen.get_size();
    font_big = pygame.font.SysFont("monospace", max(18, height // 32), bold=True);
    font_small = pygame.font.SysFont("monospace", max(14, height // 48), bold=True);
    rect = pygame.Rect(width // 10, height // 3, width * 8 // 10, height // 3);
    yes_rect = pygame.Rect(rect.x + rect.width // 10, rect.bottom - height // 12, rect.width * 35 // 100, height // 16);
    no_rect = pygame.Rect(rect.right - rect.width * 45 // 100, rect.bottom - height // 12, rect.width * 35 // 100, height // 16);
    state = {"done": False, "value": False};

    def choose(value):
        def callback(unused_button=None):
            state["done"] = True;
            state["value"] = bool(value);
        return callback;

    focus = Panel(rect, theme=theme);
    yes_button = focus.add(Button(yes_rect, yes_label, font_big, choose(True), theme=theme, tab_index=0));
    no_button = focus.add(Button(no_rect, no_label, font_big, choose(False), theme=theme, tab_index=1));
    while True:
        for event in _dialog_events(screen):
            if event.type == pygame.QUIT:
                return False;
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True;
                if event.key in (pygame.K_ESCAPE, pygame.K_n):
                    return False;
            focus.handle_event(event);
            if state["done"]:
                return state["value"];
        pygame.draw.rect(screen, theme.panel, rect, border_radius=8);
        pygame.draw.rect(screen, theme.line, rect, 3, border_radius=8);
        title_rect = pygame.Rect(rect.x + 20, rect.y + 16, rect.width - 40, font_big.get_height() + 6);
        draw_clipped_text(screen, font_big, title, theme.text, title_rect);
        body_rect = pygame.Rect(rect.x + 20, rect.y + 66, rect.width - 40, yes_rect.y - rect.y - 82);
        def draw_body():
            y = body_rect.y;
            line_h = font_small.get_height() + 4;
            for line in str(message).split("\n"):
                if y + line_h > body_rect.bottom:
                    break;
                draw_clipped_text(screen, font_small, line, theme.text, pygame.Rect(body_rect.x, y, body_rect.width, line_h));
                y += line_h;
        with_clip(screen, body_rect, draw_body);
        yes_button.draw(screen);
        no_button.draw(screen);
        pygame.display.flip();
        clock.tick(60);


def input_box(screen, clock, title, message="", default_text="", theme=None, max_length=-1,
              confirm=True, valid_values=(), validation_error="Invalid value", case_sensitive=False):
    theme = theme or DEFAULT_THEME;
    width, height = screen.get_size();
    font_big = pygame.font.SysFont("monospace", max(18, height // 32), bold=True);
    font_small = pygame.font.SysFont("monospace", max(14, height // 48), bold=True);
    rect = pygame.Rect(width // 10, height // 4, width * 8 // 10, height // 2);
    input_rect = pygame.Rect(rect.x + 20, rect.y + height // 7, rect.width - 40, height // 14);
    error_rect = pygame.Rect(input_rect.x, input_rect.bottom + 8, input_rect.width, font_small.get_height() + 8);
    ok_rect = pygame.Rect(rect.x + rect.width // 10, rect.bottom - height // 12, rect.width * 35 // 100, height // 16);
    cancel_rect = pygame.Rect(rect.right - rect.width * 45 // 100, rect.bottom - height // 12, rect.width * 35 // 100, height // 16);
    state = {"accepted": False, "cancelled": False, "value": None};

    def accepted(value):
        state["accepted"] = True;
        state["value"] = value;

    def accept_button(unused_button=None):
        field.submit();

    def cancel_button(unused_button=None):
        state["cancelled"] = True;

    focus = Panel(rect, theme=theme);
    field = focus.add(TextInput(
        input_rect, font_big, text=default_text, placeholder="", max_length=max_length, theme=theme,
        confirm_at_limit=confirm, valid_values=valid_values, validation_error=validation_error,
        case_sensitive=case_sensitive, on_submit=accepted, tab_index=0,
    ));
    ok_button = focus.add(Button(ok_rect, "OK", font_big, accept_button, theme=theme, tab_index=1));
    cancel_button_widget = focus.add(Button(cancel_rect, "CANCEL", font_big, cancel_button, theme=theme, tab_index=2));
    focus.set_focus_widget(field);
    while True:
        dt = clock.tick(60);
        for event in _dialog_events(screen):
            if event.type == pygame.QUIT:
                focus.set_focus_widget(None);
                return None;
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                focus.set_focus_widget(None);
                return None;
            focus.handle_event(event);
            if state["cancelled"]:
                focus.set_focus_widget(None);
                return None;
            if state["accepted"]:
                focus.set_focus_widget(None);
                return state["value"];
        focus.update(dt);
        pygame.draw.rect(screen, theme.panel, rect, border_radius=8);
        pygame.draw.rect(screen, theme.line, rect, 3, border_radius=8);
        title_rect = pygame.Rect(rect.x + 20, rect.y + 16, rect.width - 40, font_big.get_height() + 6);
        draw_clipped_text(screen, font_big, title, theme.text, title_rect);
        if message:
            message_rect = pygame.Rect(rect.x + 20, rect.y + 66, rect.width - 40, font_small.get_height() + 8);
            draw_clipped_text(screen, font_small, message, theme.text, message_rect);
        field.draw(screen);
        if field.last_validation_message:
            draw_clipped_text(screen, font_small, field.last_validation_message, getattr(theme, "error", theme.cursor), error_rect);
        ok_button.draw(screen);
        cancel_button_widget.draw(screen);
        pygame.display.flip();




def form_box(screen, clock, spec, theme=None):
    """Render a backend-neutral ``sumui.DialogSpec(kind='form')``.

    The first graphical bridge intentionally keeps the widget vocabulary
    small and portable: text fields use ``TextInput`` while option/boolean
    fields use cycling buttons.  Validation and required-field semantics are
    taken from the shared FieldSpec rather than redefined by the application.
    """;
    from sumui import DialogSpec;
    spec = spec if isinstance(spec, DialogSpec) else DialogSpec.from_dict(spec);
    spec.normalize();
    if spec.kind != "form": raise ValueError("form_box requires a form DialogSpec");
    theme = theme or DEFAULT_THEME;
    width, height = screen.get_size();
    title_font = pygame.font.SysFont("monospace", max(18, min(28, height // 26)), bold=True);
    font = pygame.font.SysFont("monospace", max(14, min(21, height // 34)));
    small = pygame.font.SysFont("monospace", max(12, min(17, height // 42)));
    margin = max(16, min(width, height) // 28);
    rect = pygame.Rect(margin, margin, width - margin * 2, height - margin * 2);
    header_h = title_font.get_height() + (small.get_height() + 6 if spec.text else 0) + 20;
    button_h = max(36, font.get_height() + 14);
    footer_h = button_h + 28;
    field_area_h = max(80, rect.height - header_h - footer_h);
    row_h = max(44, min(62, field_area_h // max(1, len(spec.fields))));
    label_w = max(120, min(rect.width * 34 // 100, max([font.size(str(item.label))[0] + 20 for item in spec.fields] + [120])));
    field_x = rect.x + label_w + 18;
    field_w = max(120, rect.right - field_x - 18);
    state = {"accepted": False, "cancelled": False, "error": ""};
    panel = Panel(rect, theme=theme);
    controls = [];

    def _bool_text(value): return "Yes" if bool(value) else "No";

    for index, field in enumerate(spec.fields):
        y = rect.y + header_h + index * row_h;
        control_rect = pygame.Rect(field_x, y, field_w, max(34, row_h - 10));
        kind = str(field.kind or "entry").lower();
        if kind in ("bool", "boolean", "check", "checkbox"):
            data = {"value": bool(field.default)};
            button = Button(control_rect, _bool_text(data["value"]), font, theme=theme, tab_index=index);
            def click(unused=None, data=data, button=button):
                data["value"] = not data["value"];
                button.text = _bool_text(data["value"]);
            button.on_click = click;
            panel.add(button);
            controls.append((field, "bool", button, data));
        elif field.options or kind in ("combo", "choice", "radio", "select"):
            options = list(field.options or field.valid_values or ());
            if not options: options = [str(field.default or "")];
            default = str(field.default or "");
            try: selected = options.index(default);
            except ValueError: selected = 0;
            data = {"index": selected, "options": options};
            button = Button(control_rect, options[selected] if options else "", font, theme=theme, tab_index=index);
            def cycle(unused=None, data=data, button=button):
                if not data["options"]: return;
                data["index"] = (data["index"] + 1) % len(data["options"]);
                button.text = data["options"][data["index"]];
            button.on_click = cycle;
            panel.add(button);
            controls.append((field, "choice", button, data));
        else:
            valid = field.valid_values or ();
            input_widget = TextInput(
                control_rect, font, text=str(field.default if field.default is not None else ""), placeholder=field.placeholder,
                max_length=(-1 if field.max_length is None else field.max_length), theme=theme, tab_index=index,
                confirm_at_limit=field.confirm, valid_values=valid, case_sensitive=field.case_sensitive,
                validation_error=field.validation_error,
            );
            panel.add(input_widget);
            controls.append((field, "text", input_widget, None));

    def collect_values():
        values = {};
        for field, kind, control, data in controls:
            if kind == "bool": value = bool(data["value"]);
            elif kind == "choice": value = data["options"][data["index"]] if data["options"] else "";
            else:
                if not control.validate():
                    state["error"] = "{}: {}".format(field.label, control.last_validation_message or field.validation_error);
                    panel.set_focus_widget(control);
                    return None;
                value = control.value();
            if field.required and (value is None or str(value).strip() == ""):
                state["error"] = "{} is required".format(field.label);
                panel.set_focus_widget(control);
                return None;
            values[field.name] = value;
        state["error"] = "";
        return values;

    result = {"value": None};
    def accept(unused=None):
        values = collect_values();
        if values is None: return;
        result["value"] = values;
        state["accepted"] = True;
    def cancel(unused=None): state["cancelled"] = True;

    ok_label = spec.ok_label or "OK";
    cancel_label = spec.cancel_label or "Cancel";
    bw = max(110, min(180, rect.width // 4));
    ok_button = panel.add(Button(pygame.Rect(rect.centerx - bw - 8, rect.bottom - button_h - 12, bw, button_h), ok_label, font, accept, theme=theme, tab_index=len(controls)));
    cancel_button = panel.add(Button(pygame.Rect(rect.centerx + 8, rect.bottom - button_h - 12, bw, button_h), cancel_label, font, cancel, theme=theme, tab_index=len(controls) + 1));
    if controls: panel.set_focus_widget(controls[0][2]);
    while True:
        dt = clock.tick(60);
        for event in _dialog_events(screen):
            if event.type == pygame.QUIT: return None;
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: return None;
            panel.handle_event(event);
            if state["cancelled"]: return None;
            if state["accepted"]: return result["value"];
        panel.update(dt);
        screen.fill(theme.bg);
        pygame.draw.rect(screen, theme.panel, rect, border_radius=8);
        pygame.draw.rect(screen, theme.line, rect, 2, border_radius=8);
        draw_clipped_text(screen, title_font, spec.title or "Form", theme.title, pygame.Rect(rect.x + 18, rect.y + 12, rect.width - 36, title_font.get_height() + 4));
        if spec.text:
            draw_clipped_text(screen, small, spec.text, theme.text, pygame.Rect(rect.x + 18, rect.y + 18 + title_font.get_height(), rect.width - 36, small.get_height() + 4));
        for index, (field, kind, control, data) in enumerate(controls):
            y = rect.y + header_h + index * row_h;
            label_rect = pygame.Rect(rect.x + 18, y, label_w - 20, row_h - 8);
            label = "{}{}".format(field.label, " *" if field.required else "");
            draw_clipped_text(screen, font, label, theme.text, label_rect, valign="middle");
            control.draw(screen);
        if state["error"]:
            draw_clipped_text(screen, small, state["error"], theme.error, pygame.Rect(rect.x + 18, rect.bottom - footer_h, rect.width - 36, small.get_height() + 4));
        ok_button.draw(screen);
        cancel_button.draw(screen);
        pygame.display.flip();
