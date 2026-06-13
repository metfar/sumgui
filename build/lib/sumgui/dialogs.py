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
from .widgets import draw_clipped_text, with_clip;


def message_box(screen, clock, title, message, theme=None):
    theme = theme or DEFAULT_THEME;
    width, height = screen.get_size();
    font_big = pygame.font.SysFont("monospace", max(18, height // 32), bold=True);
    font_small = pygame.font.SysFont("monospace", max(14, height // 48), bold=True);
    rect = pygame.Rect(width // 10, height // 3, width * 8 // 10, height // 3);
    ok_rect = pygame.Rect(rect.centerx - width // 8, rect.bottom - height // 12, width // 4, height // 16);
    while True:
        for event in pygame.event.get():
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
