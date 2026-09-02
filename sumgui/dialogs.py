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


