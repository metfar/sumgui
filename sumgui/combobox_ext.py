#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301
#
#  Copyright 2018- William Martinez Bas <metfar@gmail.com>
#  GPL-2.0-or-later
"""Native SUM GUI combo with a multiline modal popup and scrollbar.

Proposed standalone component for sumGUI. Requires sumUI's selection_models.
It is not imported automatically from sumgui until the package integration.
""";
import pygame;
from sumgui.widgets import Widget, draw_clipped_text;
from sumui.selection_models import ComboModel;


class ComboBox(Widget):
    def __init__(self, rect, app, entries=(), value=None, mode="selection", validator=None,
                 on_change=None, rows=7, tab_index=0, texts=None):
        super().__init__(rect, focusable=True, tab_index=tab_index);
        self.app = app;
        self.theme = app.theme;
        self.font = app.font;
        self.model = ComboModel(entries, value=value, mode=mode, validator=validator);
        self.on_change = on_change;
        self.rows = max(1, int(rows));
        self.invalid_message = "";
        self.texts = dict(texts or {});

    @property
    def value(self):
        return self.model.value;

    def set_entries(self, entries):
        self.model.set_entries(entries);
        return self;

    def set_value(self, value, notify=True):
        self.model.choose(value);
        self.invalid_message = "";
        if notify and self.on_change is not None:
            self.on_change(value);
        return self;

    def open_popup(self):
        self.app.show_modal(_ComboPopup(self));

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            self.open_popup();
            return True;
        if event.type == pygame.KEYDOWN and self.has_focus and event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_DOWN):
            self.open_popup();
            return True;
        return False;

    def draw(self, screen):
        pygame.draw.rect(screen, self.theme.panel, self.rect, border_radius=5);
        pygame.draw.rect(screen, self.theme.cursor if self.has_focus else self.theme.line, self.rect, 2, border_radius=5);
        entry = next((item for item in self.model.entries if item.selectable and item.value == self.value), None);
        label = entry.label if entry else str(self.value if self.value is not None else "");
        draw_clipped_text(screen, self.font, label, self.theme.text, self.rect.inflate(-14, -6), valign="middle");
        indicator = "(!)" if self.invalid_message else "▼";
        color = getattr(self.theme, "error", (230, 40, 40)) if self.invalid_message else self.theme.text;
        right = pygame.Rect(self.rect.right - 55, self.rect.y + 4, 50, self.rect.height - 8);
        draw_clipped_text(screen, self.font, indicator, color, right, align="center", valign="middle");


class _ComboPopup(Widget):
    def __init__(self, combo):
        super().__init__(pygame.Rect(0, 0, combo.app.width, combo.app.height), focusable=True);
        self.combo = combo;
        self.app = combo.app;
        self.theme = combo.theme;
        self.font = combo.font;
        self.row_height = max(32, self.font.get_height() + 11);
        self.rows = combo.rows;
        self.query = "";
        self.error = "";
        self.entries = [];
        self.index = 0;
        self.scroll = 0;
        self.dragging = False;
        self.drag_start_y = 0;
        self.drag_start_scroll = 0;
        self.popup = pygame.Rect(combo.rect.x, combo.rect.bottom + 3, combo.rect.width,
                                 self.row_height * (self.rows + 1) + 6);
        if self.popup.bottom >= self.app.height:
            self.popup.y = max(5, combo.rect.top - self.popup.height - 3);
        self.update_entries();

    def update_entries(self):
        self.entries = self.combo.model.candidates(self.query, fuzzy=False);
        self.index = 0;
        for index, entry in enumerate(self.entries):
            if entry.selectable and entry.value == self.combo.value:
                self.index = index;
                break;
        if self.entries and not self.entries[self.index].selectable:
            self.move(1);
        self.ensure_visible();

    def max_scroll(self):
        return max(0, len(self.entries) - self.rows);

    def ensure_visible(self):
        self.scroll = max(0, min(self.scroll, self.max_scroll()));
        if self.index < self.scroll:
            self.scroll = self.index;
        elif self.index >= self.scroll + self.rows:
            self.scroll = self.index - self.rows + 1;

    def move(self, step):
        target = self.index + step;
        while 0 <= target < len(self.entries):
            if self.entries[target].selectable:
                self.index = target;
                self.ensure_visible();
                return True;
            target += 1 if step > 0 else -1;
        return False;

    def close(self):
        self.app.close_modal();

    def choose(self, value):
        try:
            self.combo.model.choose(value);
        except (ValueError, TypeError) as exc:
            self.error = str(exc);
            self.combo.invalid_message = self.error;
            return False;
        self.combo.invalid_message = "";
        self.close();
        if self.combo.on_change is not None:
            self.combo.on_change(value);
        return True;

    def accept(self):
        if self.entries and self.entries[self.index].selectable:
            return self.choose(self.entries[self.index].value);
        if self.combo.model.mode in ("editable", "extensible") and self.query:
            return self.choose(self.query);
        return False;

    def _track(self):
        rect = pygame.Rect(self.popup.right - 18, self.popup.y + self.row_height + 2,
                           16, self.rows * self.row_height);
        count = max(1, len(self.entries));
        height = max(22, int(rect.height * min(1.0, self.rows / count)));
        travel = max(1, rect.height - height);
        y = rect.y + round(travel * self.scroll / max(1, self.max_scroll()));
        return rect, pygame.Rect(rect.x + 2, y, rect.width - 4, height);

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close();
                return True;
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.accept();
                return True;
            if event.key == pygame.K_BACKSPACE and self.query:
                self.query = self.query[:-1];
                self.update_entries();
                return True;
            if event.key in (pygame.K_DOWN, pygame.K_UP, pygame.K_PAGEUP, pygame.K_PAGEDOWN):
                step = {pygame.K_DOWN: 1, pygame.K_UP: -1, pygame.K_PAGEUP: -self.rows,
                        pygame.K_PAGEDOWN: self.rows}[event.key];
                self.move(step);
                return True;
            if event.key == pygame.K_HOME:
                self.index = 0;
                self.move(1) if self.entries and not self.entries[0].selectable else None;
                self.ensure_visible();
                return True;
            if event.key == pygame.K_END:
                self.index = max(0, len(self.entries) - 1);
                self.move(-1) if self.entries and not self.entries[self.index].selectable else None;
                self.ensure_visible();
                return True;
        if event.type == pygame.TEXTINPUT:
            self.query += event.text;
            self.update_entries();
            return True;
        if event.type == pygame.MOUSEWHEEL:
            self.scroll = max(0, min(self.max_scroll(), self.scroll - event.y));
            return True;
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.dragging:
            self.dragging = False;
            return True;
        if event.type == pygame.MOUSEMOTION and self.dragging:
            track, thumb = self._track();
            travel = max(1, track.height - thumb.height);
            offset = round((event.pos[1] - self.drag_start_y) * self.max_scroll() / travel);
            self.scroll = max(0, min(self.max_scroll(), self.drag_start_scroll + offset));
            return True;
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.popup.collidepoint(event.pos):
                self.close();
                return True;
            track, thumb = self._track();
            if track.collidepoint(event.pos):
                if thumb.collidepoint(event.pos):
                    self.dragging = True;
                    self.drag_start_y = event.pos[1];
                    self.drag_start_scroll = self.scroll;
                else:
                    self.scroll = max(0, min(self.max_scroll(), self.scroll + (self.rows if event.pos[1] > thumb.bottom else -self.rows)));
                return True;
            row = (event.pos[1] - self.popup.y - self.row_height - 2) // self.row_height;
            index = self.scroll + int(row);
            if 0 <= index < len(self.entries) and self.entries[index].selectable:
                self.index = index;
                self.accept();
            return True;
        return True;

    def draw(self, screen):
        pygame.draw.rect(screen, self.theme.panel, self.popup, border_radius=5);
        pygame.draw.rect(screen, self.theme.line, self.popup, 2, border_radius=5);
        search = self.query or self.combo.texts.get("placeholder", "Type to search...");
        text_rect = pygame.Rect(self.popup.x + 10, self.popup.y + 3,
                                self.popup.width - 20, self.row_height - 4);
        draw_clipped_text(screen, self.font, search, self.theme.text if self.query else self.theme.muted,
                          text_rect, valign="middle");
        track, thumb = self._track();
        old_clip = screen.get_clip();
        area = pygame.Rect(self.popup.x + 3, self.popup.y + self.row_height + 2,
                           self.popup.width - 23, self.rows * self.row_height);
        screen.set_clip(area);
        for row in range(self.rows):
            index = self.scroll + row;
            if index >= len(self.entries):
                break;
            item = self.entries[index];
            item_rect = pygame.Rect(area.x, area.y + row * self.row_height,
                                    area.width, self.row_height);
            if index == self.index and item.selectable:
                pygame.draw.rect(screen, self.theme.button, item_rect);
            color = self.theme.muted if not item.selectable else (self.theme.button_text if index == self.index else self.theme.text);
            draw_clipped_text(screen, self.font, item.label, color, item_rect.inflate(-12, -4), valign="middle");
        screen.set_clip(old_clip);
        pygame.draw.rect(screen, self.theme.bg, track);
        pygame.draw.rect(screen, self.theme.cursor, thumb);
        if self.error:
            draw_clipped_text(screen, self.font, "(!) " + self.error, getattr(self.theme, "error", (230, 40, 40)),
                              text_rect, valign="middle");
