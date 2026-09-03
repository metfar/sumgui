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

import pygame;

from sumui import TableSpec;
from .theme import DEFAULT_THEME;
from .widgets import Widget, draw_clipped_text, with_clip;


class TableView(Widget):
    """Pygame renderer for backend-neutral ``sumui.TableSpec`` values.""";
    def __init__(self, rect, spec, font, theme=None, focusable=False, tab_index=0, fonts=None):
        super().__init__(rect, focusable=focusable, tab_index=tab_index);
        self.spec = spec if isinstance(spec, TableSpec) else TableSpec.from_dict(spec);
        self.font = font;
        fonts = dict(fonts or {});
        self.title_font = fonts.get("title", font);
        self.header_font = fonts.get("header", font);
        self.theme = theme or DEFAULT_THEME;

    def set_spec(self, spec):
        self.spec = spec if isinstance(spec, TableSpec) else TableSpec.from_dict(spec);
        return self;

    def draw(self, screen):
        pygame.draw.rect(screen, self.theme.panel, self.rect);
        pygame.draw.rect(screen, self.theme.cursor if self.has_focus else self.theme.line, self.rect, 2);
        top = self.rect.y + 4;
        if self.spec.title:
            title_rect = pygame.Rect(self.rect.x + 6, top, self.rect.width - 12, self.title_font.get_height());
            draw_clipped_text(screen, self.title_font, self.spec.title, self.theme.title, title_rect);
            top += self.title_font.get_height() + 4;
        rows = list(self.spec.rows);
        headers = list(self.spec.headers);
        column_count = max([len(headers)] + [len(row) for row in rows] + [1]);
        row_height = max(self.font.get_height(), self.header_font.get_height()) + 6;
        body = pygame.Rect(self.rect.x + 4, top, self.rect.width - 8, self.rect.bottom - top - 4);
        col_width = max(1, body.width // column_count);
        def draw_inside():
            y = body.y;
            if headers:
                for col in range(column_count):
                    cell = pygame.Rect(body.x + col * col_width, y, col_width if col < column_count - 1 else body.right - (body.x + col * col_width), row_height);
                    pygame.draw.rect(screen, self.theme.button, cell);
                    pygame.draw.rect(screen, self.theme.line, cell, 1);
                    text = headers[col] if col < len(headers) else "";
                    draw_clipped_text(screen, self.header_font, str(text), self.theme.button_text, cell.inflate(-6, -2), valign="middle");
                y += row_height;
            for row_index, row in enumerate(rows):
                if y >= body.bottom:
                    break;
                for col in range(column_count):
                    cell = pygame.Rect(body.x + col * col_width, y, col_width if col < column_count - 1 else body.right - (body.x + col * col_width), row_height);
                    if row_index % 2:
                        pygame.draw.rect(screen, self.theme.bg, cell);
                    pygame.draw.rect(screen, self.theme.line, cell, 1);
                    value = row[col] if col < len(row) else "";
                    draw_clipped_text(screen, self.font, str(value), self.theme.text, cell.inflate(-6, -2), valign="middle");
                y += row_height;
        with_clip(screen, body, draw_inside);
