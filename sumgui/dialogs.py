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
from .widgets import TextInput, draw_clipped_text, with_clip;
from .keyrepeat import get_events;


def message_box(screen, clock, title, message, theme=None):
    theme = theme or DEFAULT_THEME;
    width, height = screen.get_size();
    font_big = pygame.font.SysFont("monospace", max(18, height // 32), bold=True);
    font_small = pygame.font.SysFont("monospace", max(14, height // 48), bold=True);
    rect = pygame.Rect(width // 10, height // 3, width * 8 // 10, height // 3);
    ok_rect = pygame.Rect(rect.centerx - width // 8, rect.bottom - height // 12, width // 4, height // 16);
    while True:
        for event in get_events():
            if event.type == pygame.QUIT:
                return False;
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_SPACE):
                return True;
            if event.type == pygame.MOUSEBUTTONDOWN and ok_rect.collidepoint(event.pos):
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
        pygame.draw.rect(screen, theme.button, ok_rect, border_radius=8);
        pygame.draw.rect(screen, theme.line, ok_rect, 2, border_radius=8);
        draw_clipped_text(screen, font_big, "OK", theme.button_text, ok_rect, align="center", valign="middle");
        pygame.display.flip();
        clock.tick(60);



def input_box(screen, clock, title, message="", default_text="", theme=None, max_length=-1):
    theme = theme or DEFAULT_THEME;
    width, height = screen.get_size();
    font_big = pygame.font.SysFont("monospace", max(18, height // 32), bold=True);
    font_small = pygame.font.SysFont("monospace", max(14, height // 48), bold=True);
    rect = pygame.Rect(width // 10, height // 4, width * 8 // 10, height // 2);
    input_rect = pygame.Rect(rect.x + 20, rect.y + height // 7, rect.width - 40, height // 14);
    ok_rect = pygame.Rect(rect.x + rect.width // 10, rect.bottom - height // 12, rect.width * 35 // 100, height // 16);
    cancel_rect = pygame.Rect(rect.right - rect.width * 45 // 100, rect.bottom - height // 12, rect.width * 35 // 100, height // 16);
    field = TextInput(input_rect, font_big, text=default_text, placeholder="", max_length=max_length, theme=theme);
    field.set_focus(True);
    while True:
        dt = clock.tick(60);
        for event in get_events():
            if event.type == pygame.QUIT:
                field.set_focus(False);
                return None;
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    field.set_focus(False);
                    return None;
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    field.set_focus(False);
                    return field.value();
            if event.type == pygame.MOUSEBUTTONDOWN:
                if ok_rect.collidepoint(event.pos):
                    field.set_focus(False);
                    return field.value();
                if cancel_rect.collidepoint(event.pos):
                    field.set_focus(False);
                    return None;
            field.handle_event(event);
        field.update(dt);
        pygame.draw.rect(screen, theme.panel, rect, border_radius=8);
        pygame.draw.rect(screen, theme.line, rect, 3, border_radius=8);
        title_rect = pygame.Rect(rect.x + 20, rect.y + 16, rect.width - 40, font_big.get_height() + 6);
        draw_clipped_text(screen, font_big, title, theme.text, title_rect);
        if message:
            message_rect = pygame.Rect(rect.x + 20, rect.y + 66, rect.width - 40, font_small.get_height() + 8);
            draw_clipped_text(screen, font_small, message, theme.text, message_rect);
        field.draw(screen);
        pygame.draw.rect(screen, theme.button, ok_rect, border_radius=8);
        pygame.draw.rect(screen, theme.line, ok_rect, 2, border_radius=8);
        draw_clipped_text(screen, font_big, "OK", theme.button_text, ok_rect, align="center", valign="middle");
        pygame.draw.rect(screen, theme.button, cancel_rect, border_radius=8);
        pygame.draw.rect(screen, theme.line, cancel_rect, 2, border_radius=8);
        draw_clipped_text(screen, font_big, "CANCEL", theme.button_text, cancel_rect, align="center", valign="middle");
        pygame.display.flip();
