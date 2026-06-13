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
from .theme import C64_COLORS, DEFAULT_THEME, DOS_COLORS, MSX_COLORS, SPECTRUM_COLORS;
from .clipboard import get_clipboard_text, set_clipboard_text;


def with_clip(screen, rect, draw_func):
    previous_clip = screen.get_clip();
    screen.set_clip(pygame.Rect(rect));
    try:
        draw_func();
    finally:
        screen.set_clip(previous_clip);


def draw_clipped_text(screen, font, text, color, rect, align="left", valign="top"):
    rect = pygame.Rect(rect);
    if rect.width <= 0 or rect.height <= 0:
        return;
    render_text = str(text);
    rendered = font.render(render_text, True, color);
    if rendered.get_width() > rect.width:
        ellipsis = "…";
        while render_text and font.size(render_text + ellipsis)[0] > rect.width:
            render_text = render_text[:-1];
        rendered = font.render(render_text + ellipsis if render_text else ellipsis, True, color);
    x = rect.x;
    y = rect.y;
    if align == "center":
        x = rect.centerx - rendered.get_width() // 2;
    elif align == "right":
        x = rect.right - rendered.get_width();
    if valign == "middle":
        y = rect.centery - rendered.get_height() // 2;
    elif valign == "bottom":
        y = rect.bottom - rendered.get_height();
    previous_clip = screen.get_clip();
    screen.set_clip(rect);
    screen.blit(rendered, (x, y));
    screen.set_clip(previous_clip);


class Widget:
    def __init__(self, rect, focusable=False, tab_index=0, accepts_tab=False):
        self.rect = pygame.Rect(rect);
        self.visible = True;
        self.enabled = True;
        self.focusable = bool(focusable);
        self.tab_index = int(tab_index);
        self.accepts_tab = bool(accepts_tab);
        self.has_focus = False;
        self.parent = None;

    def set_focus(self, focused=True):
        self.has_focus = bool(focused);

    def get_rect(self):
        return self.rect;

    def handle_event(self, event):
        return False;

    def update(self, dt):
        return None;

    def draw(self, screen):
        return None;


class Label(Widget):
    def __init__(self, rect, text, font, theme=None):
        super().__init__(rect, focusable=False);
        self.text = text;
        self.font = font;
        self.theme = theme or DEFAULT_THEME;

    def draw(self, screen):
        lines = str(self.text).split("\n");
        y = self.rect.y;
        line_h = self.font.get_height();
        for line in lines:
            if y + line_h > self.rect.bottom:
                break;
            draw_clipped_text(screen, self.font, line, self.theme.text, pygame.Rect(self.rect.x, y, self.rect.width, line_h));
            y += line_h;


class Button(Widget):
    def __init__(self, rect, text, font, on_click=None, theme=None, image=None, tab_index=0):
        super().__init__(rect, focusable=True, tab_index=tab_index);
        self.text = text;
        self.font = font;
        self.on_click = on_click;
        self.theme = theme or DEFAULT_THEME;
        self.image = image;
        self.pressed = False;

    def click(self):
        if self.on_click is not None:
            self.on_click(self);

    def handle_event(self, event):
        if not self.enabled:
            return False;
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.pressed = True;
            return True;
        if event.type == pygame.MOUSEBUTTONUP:
            was_pressed = self.pressed;
            self.pressed = False;
            if was_pressed and self.rect.collidepoint(event.pos):
                self.click();
                return True;
        if event.type == pygame.KEYDOWN and self.has_focus:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.click();
                return True;
        return False;

    def draw(self, screen):
        color = self.theme.button_alt if self.pressed else self.theme.button;
        pygame.draw.rect(screen, color, self.rect, border_radius=8);
        border = self.theme.cursor if self.has_focus else self.theme.line;
        pygame.draw.rect(screen, border, self.rect, 3 if self.has_focus else 2, border_radius=8);
        content_rect = self.rect.inflate(-8, -4);
        if self.image is not None:
            size = min(content_rect.height, content_rect.width, 28);
            image_rect = pygame.Rect(content_rect.x + 4, content_rect.centery - size // 2, size, size);
            scaled = pygame.transform.scale(self.image, (size, size));
            screen.blit(scaled, image_rect);
            text_rect = pygame.Rect(image_rect.right + 4, content_rect.y, max(1, content_rect.right - image_rect.right - 8), content_rect.height);
            draw_clipped_text(screen, self.font, self.text, self.theme.button_text, text_rect, align="center", valign="middle");
        else:
            draw_clipped_text(screen, self.font, self.text, self.theme.button_text, content_rect, align="center", valign="middle");


class Panel(Widget):
    def __init__(self, rect, theme=None):
        super().__init__(rect, focusable=False);
        self.theme = theme or DEFAULT_THEME;
        self.children = [];
        self.focused_widget = None;
        self.mouse_capture_widget = None;

    def add(self, widget):
        widget.parent = self;
        self.children.append(widget);
        if self.focused_widget is None and getattr(widget, "focusable", False) and widget.enabled and widget.visible:
            self.set_focus_widget(widget);
        return widget;

    def focusable_children(self):
        items = [w for w in self.children if getattr(w, "focusable", False) and w.enabled and w.visible];
        indexed = list(enumerate(items));
        indexed.sort(key=lambda pair: (pair[1].tab_index, pair[0]));
        return [item for unused, item in indexed];

    def set_focus_widget(self, widget):
        if widget is not None and (not getattr(widget, "focusable", False) or not widget.enabled or not widget.visible):
            widget = None;
        if self.focused_widget is widget:
            return;
        if self.focused_widget is not None:
            self.focused_widget.set_focus(False);
        self.focused_widget = widget;
        if self.focused_widget is not None:
            self.focused_widget.set_focus(True);

    def focus_next(self, backwards=False):
        items = self.focusable_children();
        if not items:
            self.set_focus_widget(None);
            return None;
        if self.focused_widget not in items:
            index = len(items) - 1 if backwards else 0;
        else:
            current = items.index(self.focused_widget);
            index = (current - 1) % len(items) if backwards else (current + 1) % len(items);
        self.set_focus_widget(items[index]);
        return self.focused_widget;

    def widget_at_pos(self, pos):
        for widget in reversed(self.children):
            if widget.visible and widget.enabled and widget.get_rect().collidepoint(pos):
                return widget;
        return None;

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            shift = bool(getattr(event, "mod", pygame.key.get_mods()) & pygame.KMOD_SHIFT);
            if self.focused_widget is not None and getattr(self.focused_widget, "accepts_tab", False):
                if self.focused_widget.handle_event(event):
                    return True;
            self.focus_next(backwards=shift);
            return True;
        if event.type == pygame.MOUSEBUTTONDOWN:
            widget = self.widget_at_pos(event.pos);
            if widget is not None:
                if getattr(widget, "focusable", False):
                    self.set_focus_widget(widget);
                handled = widget.handle_event(event);
                if handled:
                    self.mouse_capture_widget = widget;
                    return True;
            else:
                self.set_focus_widget(None);
            return self.rect.collidepoint(event.pos);
        if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
            if self.mouse_capture_widget is not None:
                handled = self.mouse_capture_widget.handle_event(event);
                if event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_capture_widget = None;
                return handled;
        if event.type in (pygame.KEYDOWN, pygame.TEXTINPUT, pygame.MOUSEWHEEL):
            if self.focused_widget is not None and self.focused_widget.handle_event(event):
                return True;
        for widget in reversed(self.children):
            if widget is self.focused_widget:
                continue;
            if widget.handle_event(event):
                return True;
        return False;

    def update(self, dt):
        for widget in self.children:
            widget.update(dt);

    def draw(self, screen):
        pygame.draw.rect(screen, self.theme.panel, self.rect, border_radius=8);
        pygame.draw.rect(screen, self.theme.line, self.rect, 2, border_radius=8);
        previous_clip = screen.get_clip();
        screen.set_clip(self.rect.inflate(-4, -4));
        for widget in self.children:
            if widget.visible:
                widget.draw(screen);
        screen.set_clip(previous_clip);


class StatusBar(Widget):
    def __init__(self, rect, font, text="READY", theme=None, zones=None):
        super().__init__(rect, focusable=False);
        self.font = font;
        self.text = text;
        self.theme = theme or DEFAULT_THEME;
        self.zones = zones;

    def set_zone(self, index, text):
        if self.zones is None:
            self.text = text;
            return;
        if 0 <= index < len(self.zones):
            zone = self.zones[index];
            if isinstance(zone, dict):
                zone["text"] = text;
            else:
                label, width = zone;
                self.zones[index] = (text, width);

    def draw(self, screen):
        pygame.draw.rect(screen, self.theme.button_alt, self.rect);
        pygame.draw.rect(screen, self.theme.line, self.rect, 1);
        if not self.zones:
            draw_clipped_text(screen, self.font, self.text, self.theme.text, self.rect.inflate(-16, -4), valign="middle");
            return;
        x = self.rect.x;
        remaining_width = self.rect.width;
        flexible = 0;
        fixed_width = 0;
        for zone in self.zones:
            width = zone.get("width", None) if isinstance(zone, dict) else zone[1];
            if width in (None, -1):
                flexible += 1;
            else:
                fixed_width += int(width);
        flex_width = max(1, (self.rect.width - fixed_width) // max(1, flexible));
        for zone in self.zones:
            if isinstance(zone, dict):
                text = zone.get("text", "");
                width = zone.get("width", None);
                align = zone.get("align", "left");
            else:
                text, width = zone;
                align = "left";
            if width in (None, -1):
                width = flex_width;
            width = min(int(width), remaining_width);
            zone_rect = pygame.Rect(x, self.rect.y, width, self.rect.height);
            pygame.draw.rect(screen, self.theme.line, zone_rect, 1);
            draw_clipped_text(screen, self.font, text, self.theme.text, zone_rect.inflate(-10, -4), align=align, valign="middle");
            x += width;
            remaining_width -= width;
            if remaining_width <= 0:
                break;


class ToolBar(Widget):
    def __init__(self, rect, font, items, theme=None):
        super().__init__(rect, focusable=False);
        self.font = font;
        self.theme = theme or DEFAULT_THEME;
        self.buttons = [];
        self.set_items(items);

    def parse_item(self, item):
        if isinstance(item, dict):
            return item.get("text", ""), item.get("callback", None), item.get("image", None);
        if len(item) == 2:
            text, callback = item;
            return text, callback, None;
        text, callback, image = item[:3];
        return text, callback, image;

    def set_items(self, items):
        self.buttons = [];
        if not items:
            return;
        gap = 4;
        button_w = max(42, (self.rect.width - gap * (len(items) + 1)) // len(items));
        for index, item in enumerate(items):
            text, callback, image = self.parse_item(item);
            x = self.rect.x + gap + index * (button_w + gap);
            rect = pygame.Rect(x, self.rect.y + gap, button_w, self.rect.height - gap * 2);
            button = Button(rect, text, self.font, callback, self.theme, image=image, tab_index=index);
            self.buttons.append(button);

    def handle_event(self, event):
        for button in self.buttons:
            if button.handle_event(event):
                return True;
        return False;

    def draw(self, screen):
        pygame.draw.rect(screen, self.theme.panel, self.rect);
        previous_clip = screen.get_clip();
        screen.set_clip(self.rect);
        for button in self.buttons:
            button.draw(screen);
        screen.set_clip(previous_clip);


class PaletteWidget(Widget):
    def __init__(self, rect, colors, cell_size, on_select=None, theme=None, tab_index=0):
        super().__init__(rect, focusable=True, tab_index=tab_index);
        self.colors = colors;
        self.cell_size = cell_size;
        self.on_select = on_select;
        self.theme = theme or DEFAULT_THEME;
        self.selected = 0;

    def select(self, index):
        if 0 <= index < len(self.colors):
            self.selected = index;
            if self.on_select is not None:
                self.on_select(index);

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            mx, my = event.pos;
            cols = max(1, self.rect.width // self.cell_size);
            col = (mx - self.rect.x) // self.cell_size;
            row = (my - self.rect.y) // self.cell_size;
            index = int(row * cols + col);
            if 0 <= index < len(self.colors):
                self.select(index);
                return True;
        if event.type == pygame.KEYDOWN and self.has_focus:
            cols = max(1, self.rect.width // self.cell_size);
            if event.key == pygame.K_LEFT:
                self.select(max(0, self.selected - 1));
                return True;
            if event.key == pygame.K_RIGHT:
                self.select(min(len(self.colors) - 1, self.selected + 1));
                return True;
            if event.key == pygame.K_UP:
                self.select(max(0, self.selected - cols));
                return True;
            if event.key == pygame.K_DOWN:
                self.select(min(len(self.colors) - 1, self.selected + cols));
                return True;
        return False;

    def draw(self, screen):
        cols = max(1, self.rect.width // self.cell_size);
        for index, color in enumerate(self.colors):
            col = index % cols;
            row = index // cols;
            rect = pygame.Rect(self.rect.x + col * self.cell_size, self.rect.y + row * self.cell_size, self.cell_size - 2, self.cell_size - 2);
            pygame.draw.rect(screen, color, rect);
            border = self.theme.cursor if (index == self.selected or self.has_focus and index == self.selected) else self.theme.line;
            pygame.draw.rect(screen, border, rect, 3 if index == self.selected else 2);


class GridCell:
    def __init__(self, color=-1, text="", image=None, data=None):
        self.color = color;
        self.text = text;
        self.image = image;
        self.data = data;


class GridWidget(Widget):
    def __init__(self, rect, rows=8, cols=8, palette=None, font=None, on_change=None, theme=None, tab_index=0):
        super().__init__(rect, focusable=True, tab_index=tab_index);
        self.rows = rows;
        self.cols = cols;
        self.palette = palette or DEFAULT_THEME.palette;
        self.font = font;
        self.theme = theme or DEFAULT_THEME;
        self.on_change = on_change;
        self.cursor_row = 0;
        self.cursor_col = 0;
        self.cells = [[GridCell() for _ in range(cols)] for _ in range(rows)];
        self.paint_value = 15;
        self.drag_value = None;

    def cell_at_pos(self, pos):
        if not self.rect.collidepoint(pos):
            return None;
        cell_w = self.rect.width / self.cols;
        cell_h = self.rect.height / self.rows;
        col = int((pos[0] - self.rect.x) / cell_w);
        row = int((pos[1] - self.rect.y) / cell_h);
        return max(0, min(self.rows - 1, row)), max(0, min(self.cols - 1, col));

    def set_cell(self, row, col, color=None, text=None, image=None, data=None):
        cell = self.cells[row][col];
        if color is not None:
            cell.color = color;
        if text is not None:
            cell.text = text;
        if image is not None:
            cell.image = image;
        if data is not None:
            cell.data = data;
        if self.on_change is not None:
            self.on_change(row, col, cell);

    def toggle_cell(self, row, col):
        cell = self.cells[row][col];
        cell.color = self.paint_value if cell.color == -1 else -1;
        if self.on_change is not None:
            self.on_change(row, col, cell);

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and self.has_focus:
            if event.key == pygame.K_LEFT:
                self.cursor_col = max(0, self.cursor_col - 1);
                return True;
            if event.key == pygame.K_RIGHT:
                self.cursor_col = min(self.cols - 1, self.cursor_col + 1);
                return True;
            if event.key == pygame.K_UP:
                self.cursor_row = max(0, self.cursor_row - 1);
                return True;
            if event.key == pygame.K_DOWN:
                self.cursor_row = min(self.rows - 1, self.cursor_row + 1);
                return True;
            if event.key == pygame.K_SPACE:
                self.toggle_cell(self.cursor_row, self.cursor_col);
                return True;
        if event.type == pygame.MOUSEBUTTONDOWN:
            found = self.cell_at_pos(event.pos);
            if found is None:
                return False;
            row, col = found;
            self.cursor_row = row;
            self.cursor_col = col;
            current = self.cells[row][col].color;
            self.drag_value = self.paint_value if current == -1 else -1;
            self.set_cell(row, col, color=self.drag_value);
            return True;
        if event.type == pygame.MOUSEMOTION and getattr(event, "buttons", (0, 0, 0))[0]:
            found = self.cell_at_pos(event.pos);
            if found is None or self.drag_value is None:
                return False;
            row, col = found;
            self.cursor_row = row;
            self.cursor_col = col;
            self.set_cell(row, col, color=self.drag_value);
            return True;
        if event.type == pygame.MOUSEBUTTONUP:
            self.drag_value = None;
        return False;

    def draw(self, screen):
        pygame.draw.rect(screen, self.theme.panel, self.rect);
        cell_w = self.rect.width / self.cols;
        cell_h = self.rect.height / self.rows;
        for row in range(self.rows):
            for col in range(self.cols):
                rect = pygame.Rect(int(self.rect.x + col * cell_w), int(self.rect.y + row * cell_h), int(cell_w) + 1, int(cell_h) + 1);
                cell = self.cells[row][col];
                if isinstance(cell.color, int) and 0 <= cell.color < len(self.palette):
                    pygame.draw.rect(screen, self.palette[cell.color], rect.inflate(-2, -2));
                if cell.image is not None:
                    scaled = pygame.transform.scale(cell.image, (max(1, rect.width - 4), max(1, rect.height - 4)));
                    screen.blit(scaled, (rect.x + 2, rect.y + 2));
                if cell.text and self.font is not None:
                    draw_clipped_text(screen, self.font, cell.text, self.theme.text, rect.inflate(-4, -4), align="center", valign="middle");
                pygame.draw.rect(screen, self.theme.line, rect, 1);
        cursor_rect = pygame.Rect(int(self.rect.x + self.cursor_col * cell_w), int(self.rect.y + self.cursor_row * cell_h), int(cell_w) + 1, int(cell_h) + 1);
        pygame.draw.rect(screen, self.theme.cursor, cursor_rect, 3);
        if self.has_focus:
            pygame.draw.rect(screen, self.theme.cursor, self.rect, 3);


class TextArea(Widget):
    def __init__(self, rect, font, text="", multiline=True, show_scrollbar=True, editable=True, max_lines=-1, max_cols=-1, theme=None, show_v_scrollbar=None, show_h_scrollbar=False, accepts_tab=False, tab_index=0):
        super().__init__(rect, focusable=True, tab_index=tab_index, accepts_tab=accepts_tab);
        self.font = font;
        self.lines = text.split("\n") if text else [""];
        self.multiline = multiline;
        if show_v_scrollbar is None:
            show_v_scrollbar = show_scrollbar;
        self.show_v_scrollbar = bool(show_v_scrollbar);
        self.show_h_scrollbar = bool(show_h_scrollbar);
        self.show_scrollbar = self.show_v_scrollbar;
        self.editable = editable;
        self.max_lines = max_lines;
        self.max_cols = max_cols;
        self.theme = theme or DEFAULT_THEME;
        self.cursor_row = len(self.lines) - 1;
        self.cursor_col = len(self.lines[self.cursor_row]);
        self.scroll_row = 0;
        self.scroll_col = 0;
        self.active = False;
        self.cursor_ms = 0;
        self.cursor_visible = True;
        self.padding = 8;
        self.scrollbar_size = 14;
        self.drag_scroll = None;
        self.drag_selecting = False;
        self.selection_anchor = None;

    def set_focus(self, focused=True):
        super().set_focus(focused);
        self.active = bool(focused);
        if focused:
            pygame.key.start_text_input();
            pygame.key.set_text_input_rect(self.rect);
        else:
            pygame.key.stop_text_input();

    def text(self):
        return "\n".join(self.lines);

    def set_text(self, text):
        self.lines = text.split("\n") if text else [""];
        self.cursor_row = min(self.cursor_row, len(self.lines) - 1);
        self.cursor_col = min(self.cursor_col, len(self.lines[self.cursor_row]));
        self.clear_selection();
        self.ensure_visible();

    def cursor_position(self):
        return (self.cursor_row, self.cursor_col);

    def compare_positions(self, a, b):
        if a[0] < b[0]:
            return -1;
        if a[0] > b[0]:
            return 1;
        if a[1] < b[1]:
            return -1;
        if a[1] > b[1]:
            return 1;
        return 0;

    def clear_selection(self):
        self.selection_anchor = None;

    def begin_selection_if_needed(self):
        if self.selection_anchor is None:
            self.selection_anchor = self.cursor_position();

    def has_selection(self):
        return self.selection_anchor is not None and self.selection_anchor != self.cursor_position();

    def selection_range(self):
        if not self.has_selection():
            pos = self.cursor_position();
            return pos, pos;
        anchor = self.selection_anchor;
        cursor = self.cursor_position();
        if self.compare_positions(anchor, cursor) <= 0:
            return anchor, cursor;
        return cursor, anchor;

    def set_cursor(self, row, col, selecting=False):
        if selecting:
            self.begin_selection_if_needed();
        else:
            self.clear_selection();
        row = max(0, min(len(self.lines) - 1, int(row)));
        col = max(0, min(len(self.lines[row]), int(col)));
        self.cursor_row = row;
        self.cursor_col = col;
        self.ensure_visible();

    def selected_text(self):
        if not self.has_selection():
            return "";
        start, end = self.selection_range();
        start_row, start_col = start;
        end_row, end_col = end;
        if start_row == end_row:
            return self.lines[start_row][start_col:end_col];
        selected = [self.lines[start_row][start_col:]];
        for row in range(start_row + 1, end_row):
            selected.append(self.lines[row]);
        selected.append(self.lines[end_row][:end_col]);
        return "\n".join(selected);

    def delete_selection(self):
        if not self.has_selection() or not self.editable:
            return False;
        start, end = self.selection_range();
        start_row, start_col = start;
        end_row, end_col = end;
        if start_row == end_row:
            line = self.lines[start_row];
            self.lines[start_row] = line[:start_col] + line[end_col:];
        else:
            prefix = self.lines[start_row][:start_col];
            suffix = self.lines[end_row][end_col:];
            self.lines[start_row:end_row + 1] = [prefix + suffix];
        self.cursor_row = start_row;
        self.cursor_col = start_col;
        self.clear_selection();
        self.ensure_visible();
        return True;

    def copy_text(self):
        if self.has_selection():
            set_clipboard_text(self.selected_text());
        else:
            set_clipboard_text(self.text());

    def cut_text(self):
        if not self.editable:
            self.copy_text();
            return;
        if self.has_selection():
            set_clipboard_text(self.selected_text());
            self.delete_selection();
            return;
        self.copy_text();
        self.lines = [""];
        self.cursor_row = 0;
        self.cursor_col = 0;
        self.scroll_row = 0;
        self.scroll_col = 0;
        self.clear_selection();
        self.ensure_visible();

    def paste_text(self):
        if not self.editable:
            return;
        text = get_clipboard_text();
        if text:
            self.insert_text(text);

    def select_all(self):
        self.selection_anchor = (0, 0);
        self.cursor_row = len(self.lines) - 1;
        self.cursor_col = len(self.lines[self.cursor_row]);
        self.ensure_visible();

    def max_line_length(self):
        return max([len(line) for line in self.lines] + [0]);

    def content_rect(self):
        rect = self.rect.inflate(-self.padding * 2, -self.padding * 2);
        if self.show_v_scrollbar:
            rect.width = max(1, rect.width - self.scrollbar_size);
        if self.show_h_scrollbar:
            rect.height = max(1, rect.height - self.scrollbar_size);
        return rect;

    def visible_rows(self):
        rect = self.content_rect();
        return max(1, rect.height // max(1, self.font.get_height()));

    def visible_cols(self):
        rect = self.content_rect();
        char_w = max(1, self.font.size("M")[0]);
        return max(1, rect.width // char_w);

    def max_scroll_row(self):
        return max(0, len(self.lines) - self.visible_rows());

    def max_scroll_col(self):
        return max(0, self.max_line_length() - self.visible_cols());

    def clamp_scroll(self):
        self.scroll_row = max(0, min(self.max_scroll_row(), self.scroll_row));
        self.scroll_col = max(0, min(self.max_scroll_col(), self.scroll_col));

    def ensure_visible(self):
        rows = self.visible_rows();
        cols = self.visible_cols();
        if self.cursor_row < self.scroll_row:
            self.scroll_row = self.cursor_row;
        if self.cursor_row >= self.scroll_row + rows:
            self.scroll_row = self.cursor_row - rows + 1;
        if self.cursor_col < self.scroll_col:
            self.scroll_col = self.cursor_col;
        if self.cursor_col >= self.scroll_col + cols:
            self.scroll_col = self.cursor_col - cols + 1;
        self.clamp_scroll();

    def insert_text(self, text):
        if not self.editable:
            return;
        if self.has_selection():
            self.delete_selection();
        for char in text:
            if char == "\n":
                self.newline();
                continue;
            line = self.lines[self.cursor_row];
            if self.max_cols != -1 and len(line) >= self.max_cols:
                continue;
            self.lines[self.cursor_row] = line[:self.cursor_col] + char + line[self.cursor_col:];
            self.cursor_col += 1;
        self.clear_selection();
        self.ensure_visible();

    def newline(self):
        if not self.editable:
            return;
        if self.has_selection():
            self.delete_selection();
        if not self.multiline:
            return;
        if self.max_lines != -1 and len(self.lines) >= self.max_lines:
            return;
        line = self.lines[self.cursor_row];
        self.lines[self.cursor_row] = line[:self.cursor_col];
        self.lines.insert(self.cursor_row + 1, line[self.cursor_col:]);
        self.cursor_row += 1;
        self.cursor_col = 0;
        self.clear_selection();
        self.ensure_visible();

    def backspace(self):
        if not self.editable:
            return;
        if self.delete_selection():
            return;
        if self.cursor_col > 0:
            line = self.lines[self.cursor_row];
            self.lines[self.cursor_row] = line[:self.cursor_col - 1] + line[self.cursor_col:];
            self.cursor_col -= 1;
        elif self.cursor_row > 0:
            old_len = len(self.lines[self.cursor_row - 1]);
            self.lines[self.cursor_row - 1] += self.lines[self.cursor_row];
            self.lines.pop(self.cursor_row);
            self.cursor_row -= 1;
            self.cursor_col = old_len;
        self.ensure_visible();

    def delete(self):
        if not self.editable:
            return;
        if self.delete_selection():
            return;
        line = self.lines[self.cursor_row];
        if self.cursor_col < len(line):
            self.lines[self.cursor_row] = line[:self.cursor_col] + line[self.cursor_col + 1:];
        elif self.cursor_row + 1 < len(self.lines):
            self.lines[self.cursor_row] += self.lines[self.cursor_row + 1];
            self.lines.pop(self.cursor_row + 1);
        self.ensure_visible();

    def move_cursor(self, dx, dy, selecting=False):
        row = self.cursor_row;
        col = self.cursor_col;
        if dy != 0:
            row = max(0, min(len(self.lines) - 1, row + dy));
            col = min(col, len(self.lines[row]));
        if dx < 0:
            if col > 0:
                col -= 1;
            elif row > 0:
                row -= 1;
                col = len(self.lines[row]);
        elif dx > 0:
            if col < len(self.lines[row]):
                col += 1;
            elif row + 1 < len(self.lines):
                row += 1;
                col = 0;
        self.set_cursor(row, col, selecting=selecting);

    def move_home(self, selecting=False):
        self.set_cursor(self.cursor_row, 0, selecting=selecting);

    def move_end(self, selecting=False):
        self.set_cursor(self.cursor_row, len(self.lines[self.cursor_row]), selecting=selecting);

    def move_page(self, direction, selecting=False):
        row = self.cursor_row + direction * self.visible_rows();
        row = max(0, min(len(self.lines) - 1, row));
        col = min(self.cursor_col, len(self.lines[row]));
        self.set_cursor(row, col, selecting=selecting);

    def position_from_mouse(self, pos):
        rect = self.content_rect();
        line_h = self.font.get_height();
        char_w = max(1, self.font.size("M")[0]);
        row = self.scroll_row + max(0, min(self.visible_rows() - 1, (pos[1] - rect.y) // line_h));
        row = max(0, min(len(self.lines) - 1, int(row)));
        col = self.scroll_col + max(0, (pos[0] - rect.x) // char_w);
        col = max(0, min(len(self.lines[row]), int(col)));
        return row, col;

    def vertical_scrollbar_rect(self):
        return pygame.Rect(self.rect.right - self.padding - self.scrollbar_size + 3, self.rect.y + self.padding, self.scrollbar_size - 6, max(1, self.rect.height - self.padding * 2 - (self.scrollbar_size if self.show_h_scrollbar else 0)));

    def horizontal_scrollbar_rect(self):
        return pygame.Rect(self.rect.x + self.padding, self.rect.bottom - self.padding - self.scrollbar_size + 3, max(1, self.rect.width - self.padding * 2 - (self.scrollbar_size if self.show_v_scrollbar else 0)), self.scrollbar_size - 6);

    def scrollbar_hit(self, pos):
        if self.show_v_scrollbar and self.vertical_scrollbar_rect().collidepoint(pos):
            return "vertical";
        if self.show_h_scrollbar and self.horizontal_scrollbar_rect().collidepoint(pos):
            return "horizontal";
        return None;

    def apply_scroll_drag(self, pos):
        if self.drag_scroll == "vertical":
            bar = self.vertical_scrollbar_rect();
            max_scroll = self.max_scroll_row();
            if max_scroll <= 0:
                self.scroll_row = 0;
                return;
            fraction = (pos[1] - bar.y) / max(1, bar.height);
            self.scroll_row = max(0, min(max_scroll, int(round(fraction * max_scroll))));
        elif self.drag_scroll == "horizontal":
            bar = self.horizontal_scrollbar_rect();
            max_scroll = self.max_scroll_col();
            if max_scroll <= 0:
                self.scroll_col = 0;
                return;
            fraction = (pos[0] - bar.x) / max(1, bar.width);
            self.scroll_col = max(0, min(max_scroll, int(round(fraction * max_scroll))));

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                hit = self.scrollbar_hit(event.pos);
                if hit is not None:
                    self.drag_scroll = hit;
                    self.apply_scroll_drag(event.pos);
                    return True;
                if self.content_rect().collidepoint(event.pos):
                    row, col = self.position_from_mouse(event.pos);
                    self.set_cursor(row, col, selecting=False);
                    self.selection_anchor = (row, col);
                    self.drag_selecting = True;
                    return True;
                return True;
        if event.type == pygame.MOUSEMOTION:
            if self.drag_scroll is not None:
                self.apply_scroll_drag(event.pos);
                return True;
            if self.drag_selecting:
                row, col = self.position_from_mouse(event.pos);
                self.set_cursor(row, col, selecting=True);
                return True;
        if event.type == pygame.MOUSEBUTTONUP:
            if self.drag_scroll is not None:
                self.drag_scroll = None;
                return True;
            if self.drag_selecting:
                self.drag_selecting = False;
                if not self.has_selection():
                    self.clear_selection();
                return True;
        if event.type == pygame.MOUSEWHEEL and self.active:
            if self.show_v_scrollbar or event.y != 0:
                self.scroll_row = max(0, min(self.max_scroll_row(), self.scroll_row - event.y));
            if self.show_h_scrollbar or event.x != 0:
                self.scroll_col = max(0, min(self.max_scroll_col(), self.scroll_col + event.x));
            return True;
        if not self.active:
            return False;
        if event.type == pygame.TEXTINPUT:
            self.insert_text(event.text);
            return True;
        if event.type == pygame.KEYDOWN:
            mods = getattr(event, "mod", pygame.key.get_mods());
            ctrl = bool(mods & pygame.KMOD_CTRL);
            shift = bool(mods & pygame.KMOD_SHIFT);
            if ctrl and event.key in (pygame.K_c, pygame.K_INSERT):
                self.copy_text();
                return True;
            if (ctrl and event.key == pygame.K_x) or (shift and event.key == pygame.K_DELETE):
                self.cut_text();
                return True;
            if (ctrl and event.key == pygame.K_v) or (shift and event.key == pygame.K_INSERT):
                self.paste_text();
                return True;
            if ctrl and event.key == pygame.K_a:
                self.select_all();
                return True;
            if event.key == pygame.K_TAB:
                if self.accepts_tab:
                    self.insert_text("\t");
                    return True;
                return False;
            if event.key == pygame.K_BACKSPACE:
                self.backspace();
                return True;
            if event.key == pygame.K_DELETE:
                self.delete();
                return True;
            if event.key == pygame.K_RETURN:
                self.newline();
                return True;
            if event.key == pygame.K_LEFT:
                self.move_cursor(-1, 0, selecting=shift);
                return True;
            if event.key == pygame.K_RIGHT:
                self.move_cursor(1, 0, selecting=shift);
                return True;
            if event.key == pygame.K_UP:
                self.move_cursor(0, -1, selecting=shift);
                return True;
            if event.key == pygame.K_DOWN:
                self.move_cursor(0, 1, selecting=shift);
                return True;
            if event.key == pygame.K_HOME:
                self.move_home(selecting=shift);
                return True;
            if event.key == pygame.K_END:
                self.move_end(selecting=shift);
                return True;
            if event.key == pygame.K_PAGEUP:
                self.move_page(-1, selecting=shift);
                return True;
            if event.key == pygame.K_PAGEDOWN:
                self.move_page(1, selecting=shift);
                return True;
        return False;

    def update(self, dt):
        self.cursor_ms += dt;
        if self.cursor_ms >= 500:
            self.cursor_visible = not self.cursor_visible;
            self.cursor_ms = 0;

    def draw_vertical_scrollbar(self, screen):
        if not self.show_v_scrollbar or len(self.lines) <= self.visible_rows():
            return;
        bar = self.vertical_scrollbar_rect();
        pygame.draw.rect(screen, self.theme.line, bar);
        fraction = self.visible_rows() / max(1, len(self.lines));
        knob_h = max(12, int(bar.height * fraction));
        max_scroll = max(1, self.max_scroll_row());
        knob_y = bar.y + int((bar.height - knob_h) * (self.scroll_row / max_scroll));
        pygame.draw.rect(screen, self.theme.button, pygame.Rect(bar.x, knob_y, bar.width, knob_h));

    def draw_horizontal_scrollbar(self, screen):
        if not self.show_h_scrollbar or self.max_line_length() <= self.visible_cols():
            return;
        bar = self.horizontal_scrollbar_rect();
        pygame.draw.rect(screen, self.theme.line, bar);
        fraction = self.visible_cols() / max(1, self.max_line_length());
        knob_w = max(12, int(bar.width * fraction));
        max_scroll = max(1, self.max_scroll_col());
        knob_x = bar.x + int((bar.width - knob_w) * (self.scroll_col / max_scroll));
        pygame.draw.rect(screen, self.theme.button, pygame.Rect(knob_x, bar.y, knob_w, bar.height));

    def draw_scrollbar(self, screen):
        self.draw_vertical_scrollbar(screen);
        self.draw_horizontal_scrollbar(screen);

    def selection_columns_for_row(self, row):
        if not self.has_selection():
            return None;
        start, end = self.selection_range();
        start_row, start_col = start;
        end_row, end_col = end;
        if row < start_row or row > end_row:
            return None;
        line_len = len(self.lines[row]);
        left = start_col if row == start_row else 0;
        right = end_col if row == end_row else line_len;
        if left == right and start_row != end_row:
            right = max(right, 1);
        return max(0, left), max(0, right);

    def draw_selection_for_row(self, screen, text_rect, row, y, char_w, line_h):
        selected = self.selection_columns_for_row(row);
        if selected is None:
            return;
        left, right = selected;
        visible_left = max(left, self.scroll_col);
        visible_right = min(right, self.scroll_col + self.visible_cols());
        if visible_right <= visible_left:
            return;
        x = text_rect.x + (visible_left - self.scroll_col) * char_w;
        width = max(char_w, (visible_right - visible_left) * char_w);
        pygame.draw.rect(screen, self.theme.button_alt, pygame.Rect(x, y, width, line_h));

    def draw(self, screen):
        pygame.draw.rect(screen, self.theme.panel, self.rect, border_radius=8);
        pygame.draw.rect(screen, self.theme.cursor if self.active else self.theme.line, self.rect, 3 if self.active else 2, border_radius=8);
        line_h = self.font.get_height();
        char_w = max(1, self.font.size("M")[0]);
        text_rect = self.content_rect();
        def draw_inside():
            rows = self.visible_rows();
            cols = self.visible_cols();
            for index in range(rows):
                row = self.scroll_row + index;
                if row >= len(self.lines):
                    break;
                line = self.lines[row];
                visible = line[self.scroll_col:self.scroll_col + cols];
                y = text_rect.y + index * line_h;
                self.draw_selection_for_row(screen, text_rect, row, y, char_w, line_h);
                draw_clipped_text(screen, self.font, visible, self.theme.text, pygame.Rect(text_rect.x, y, text_rect.width, line_h));
            if self.active and self.cursor_visible:
                if self.scroll_row <= self.cursor_row < self.scroll_row + rows:
                    cx = text_rect.x + max(0, self.cursor_col - self.scroll_col) * char_w;
                    cy = text_rect.y + (self.cursor_row - self.scroll_row) * line_h;
                    if text_rect.collidepoint(cx, cy):
                        pygame.draw.rect(screen, self.theme.cursor, pygame.Rect(cx, cy + 2, 3, line_h - 4));
        with_clip(screen, text_rect, draw_inside);
        self.draw_scrollbar(screen);


class ColorPicker(Widget):
    def __init__(self, rect, font, mode="palette16", colors=None, on_change=None, theme=None, tab_index=0):
        super().__init__(rect, focusable=True, tab_index=tab_index);
        self.font = font;
        self.mode = mode;
        self.theme = theme or DEFAULT_THEME;
        self.on_change = on_change;
        self.colors = list(colors or SPECTRUM_COLORS);
        self.selected = 0;
        self.rgb = self.colors[0] if self.colors else (0, 0, 0);
        self.cmyk = self.rgb_to_cmyk(*self.rgb);

    def rgb_to_cmyk(self, r, g, b):
        if (r, g, b) == (0, 0, 0):
            return (0, 0, 0, 100);
        c = 1 - r / 255.0;
        m = 1 - g / 255.0;
        y = 1 - b / 255.0;
        k = min(c, m, y);
        return tuple(int(round(v)) for v in ((c - k) / (1 - k) * 100, (m - k) / (1 - k) * 100, (y - k) / (1 - k) * 100, k * 100));

    def cmyk_to_rgb(self, c, m, y, k):
        c = max(0, min(100, c)) / 100.0;
        m = max(0, min(100, m)) / 100.0;
        y = max(0, min(100, y)) / 100.0;
        k = max(0, min(100, k)) / 100.0;
        return (int(255 * (1 - c) * (1 - k)), int(255 * (1 - m) * (1 - k)), int(255 * (1 - y) * (1 - k)));

    def value(self):
        return self.rgb;

    def notify(self):
        if self.on_change is not None:
            self.on_change(self, self.rgb);

    def set_rgb(self, r, g, b):
        self.rgb = (max(0, min(255, int(r))), max(0, min(255, int(g))), max(0, min(255, int(b))));
        self.cmyk = self.rgb_to_cmyk(*self.rgb);
        self.notify();

    def set_cmyk(self, c, m, y, k):
        self.cmyk = (max(0, min(100, int(c))), max(0, min(100, int(m))), max(0, min(100, int(y))), max(0, min(100, int(k))));
        self.rgb = self.cmyk_to_rgb(*self.cmyk);
        self.notify();

    def select_palette(self, index):
        if 0 <= index < len(self.colors):
            self.selected = index;
            self.set_rgb(*self.colors[index]);

    def palette_cell_at(self, pos):
        if not self.rect.collidepoint(pos):
            return None;
        swatch_area = pygame.Rect(self.rect.x + 8, self.rect.y + 8, self.rect.width - 16, max(1, self.rect.height - 60));
        cols = 8 if len(self.colors) > 8 else max(1, len(self.colors));
        cell = max(12, min(swatch_area.width // cols, swatch_area.height // max(1, (len(self.colors) + cols - 1) // cols)));
        col = (pos[0] - swatch_area.x) // cell;
        row = (pos[1] - swatch_area.y) // cell;
        index = int(row * cols + col);
        if 0 <= index < len(self.colors):
            return index;
        return None;

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            index = self.palette_cell_at(event.pos);
            if index is not None:
                self.select_palette(index);
                return True;
            return True;
        if event.type == pygame.KEYDOWN and self.has_focus:
            if event.key == pygame.K_LEFT:
                self.select_palette(max(0, self.selected - 1));
                return True;
            if event.key == pygame.K_RIGHT:
                self.select_palette(min(len(self.colors) - 1, self.selected + 1));
                return True;
            if event.key == pygame.K_UP:
                self.select_palette(max(0, self.selected - 8));
                return True;
            if event.key == pygame.K_DOWN:
                self.select_palette(min(len(self.colors) - 1, self.selected + 8));
                return True;
        return False;

    def draw(self, screen):
        pygame.draw.rect(screen, self.theme.panel, self.rect, border_radius=8);
        pygame.draw.rect(screen, self.theme.cursor if self.has_focus else self.theme.line, self.rect, 3 if self.has_focus else 2, border_radius=8);
        swatch_area = pygame.Rect(self.rect.x + 8, self.rect.y + 8, self.rect.width - 16, max(1, self.rect.height - 60));
        cols = 8 if len(self.colors) > 8 else max(1, len(self.colors));
        cell = max(12, min(swatch_area.width // cols, swatch_area.height // max(1, (len(self.colors) + cols - 1) // cols)));
        for index, color in enumerate(self.colors):
            col = index % cols;
            row = index // cols;
            rect = pygame.Rect(swatch_area.x + col * cell, swatch_area.y + row * cell, cell - 2, cell - 2);
            pygame.draw.rect(screen, color, rect);
            pygame.draw.rect(screen, self.theme.cursor if index == self.selected else self.theme.line, rect, 3 if index == self.selected else 1);
        preview = pygame.Rect(self.rect.x + 8, self.rect.bottom - 44, 42, 32);
        pygame.draw.rect(screen, self.rgb, preview);
        pygame.draw.rect(screen, self.theme.line, preview, 1);
        draw_clipped_text(screen, self.font, "RGB {} {} {}".format(*self.rgb), self.theme.text, pygame.Rect(preview.right + 8, self.rect.bottom - 47, self.rect.width - preview.width - 24, 18));
        draw_clipped_text(screen, self.font, "CMYK {} {} {} {}".format(*self.cmyk), self.theme.muted, pygame.Rect(preview.right + 8, self.rect.bottom - 26, self.rect.width - preview.width - 24, 18));


class Slider(Widget):
    def __init__(self, rect, minimum=0.0, maximum=1.0, value=0.0, orientation="horizontal", step=None, on_change=None, font=None, label="", theme=None, tab_index=0):
        super().__init__(rect, focusable=True, tab_index=tab_index);
        self.minimum = float(minimum);
        self.maximum = float(maximum);
        self.value = float(value);
        self.orientation = orientation;
        self.step = step;
        self.on_change = on_change;
        self.font = font;
        self.label = label;
        self.theme = theme or DEFAULT_THEME;
        self.dragging = False;
        self.value = self.clamp_value(self.value);

    def clamp_value(self, value):
        low = min(self.minimum, self.maximum);
        high = max(self.minimum, self.maximum);
        value = max(low, min(high, float(value)));
        if self.step not in (None, 0):
            value = round((value - self.minimum) / self.step) * self.step + self.minimum;
            value = max(low, min(high, value));
        return value;

    def fraction(self):
        if self.maximum == self.minimum:
            return 0.0;
        return (self.value - self.minimum) / (self.maximum - self.minimum);

    def set_value(self, value, notify=True):
        old_value = self.value;
        self.value = self.clamp_value(value);
        if notify and self.on_change is not None and self.value != old_value:
            self.on_change(self, self.value);

    def value_from_pos(self, pos):
        if self.orientation == "vertical":
            usable = max(1, self.rect.height - 24);
            fraction = 1.0 - ((pos[1] - self.rect.y - 12) / usable);
        else:
            usable = max(1, self.rect.width - 24);
            fraction = (pos[0] - self.rect.x - 12) / usable;
        fraction = max(0.0, min(1.0, fraction));
        return self.minimum + fraction * (self.maximum - self.minimum);

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.dragging = True;
            self.set_value(self.value_from_pos(event.pos));
            return True;
        if event.type == pygame.MOUSEMOTION and self.dragging:
            self.set_value(self.value_from_pos(event.pos));
            return True;
        if event.type == pygame.MOUSEBUTTONUP and self.dragging:
            self.dragging = False;
            return True;
        if event.type == pygame.KEYDOWN and self.has_focus:
            delta = self.step if self.step not in (None, 0) else (self.maximum - self.minimum) / 20.0;
            if self.orientation == "vertical":
                if event.key == pygame.K_UP:
                    self.set_value(self.value + delta);
                    return True;
                if event.key == pygame.K_DOWN:
                    self.set_value(self.value - delta);
                    return True;
            else:
                if event.key == pygame.K_RIGHT:
                    self.set_value(self.value + delta);
                    return True;
                if event.key == pygame.K_LEFT:
                    self.set_value(self.value - delta);
                    return True;
            if event.key == pygame.K_HOME:
                self.set_value(self.minimum);
                return True;
            if event.key == pygame.K_END:
                self.set_value(self.maximum);
                return True;
        return False;

    def draw(self, screen):
        pygame.draw.rect(screen, self.theme.panel, self.rect, border_radius=8);
        pygame.draw.rect(screen, self.theme.cursor if self.has_focus else self.theme.line, self.rect, 3 if self.has_focus else 2, border_radius=8);
        def draw_inside():
            if self.label and self.font is not None:
                label_rect = pygame.Rect(self.rect.x + 8, self.rect.y + 4, self.rect.width - 16, self.font.get_height());
                draw_clipped_text(screen, self.font, self.label, self.theme.text, label_rect);
            value_text = "{:.2f}".format(self.value).rstrip("0").rstrip(".");
            if self.font is not None:
                value_rect = pygame.Rect(self.rect.x + 8, self.rect.bottom - self.font.get_height() - 4, self.rect.width - 16, self.font.get_height());
                draw_clipped_text(screen, self.font, value_text, self.theme.muted, value_rect, align="right");
            if self.orientation == "vertical":
                track = pygame.Rect(self.rect.centerx - 4, self.rect.y + 24, 8, self.rect.height - 48);
                pygame.draw.rect(screen, self.theme.line, track);
                knob_y = track.bottom - int(self.fraction() * max(1, track.height));
                knob = pygame.Rect(self.rect.x + 8, knob_y - 10, self.rect.width - 16, 20);
            else:
                track = pygame.Rect(self.rect.x + 18, self.rect.centery - 4, self.rect.width - 36, 8);
                pygame.draw.rect(screen, self.theme.line, track);
                fill = pygame.Rect(track.x, track.y, int(track.width * self.fraction()), track.height);
                pygame.draw.rect(screen, self.theme.button, fill);
                knob_x = track.x + int(self.fraction() * max(1, track.width));
                knob = pygame.Rect(knob_x - 10, self.rect.centery - 18, 20, 36);
            pygame.draw.rect(screen, self.theme.button, knob, border_radius=6);
            pygame.draw.rect(screen, self.theme.text, knob, 2, border_radius=6);
        with_clip(screen, self.rect.inflate(-4, -4), draw_inside);


class CanvasArea(Widget):
    def __init__(self, rect, theme=None, background=None, on_draw=None, on_event=None, tab_index=0, interactive=True, auto_redraw=True):
        super().__init__(rect, focusable=bool(interactive), tab_index=tab_index);
        self._widget_rect = pygame.Rect(rect);
        try:
            del self.rect;
        except AttributeError:
            pass;
        self.theme = theme or DEFAULT_THEME;
        self.background = background;
        self.on_draw = on_draw;
        self.on_event = on_event;
        self.interactive = bool(interactive);
        self.auto_redraw = bool(auto_redraw);
        self.needs_redraw = True;
        self.mouse_down = False;
        self.last_pos = None;
        self.offset_x = 0;
        self.offset_y = 0;
        self.zoom = 1.0;
        self.stroke_color = self.theme.text;
        self.fill_color = self.theme.button;
        self.line_width = 2;
        self.font = pygame.font.SysFont("monospace", 18, bold=True);
        self.commands = [];
        self.state_stack = [];

    def get_rect(self):
        return self._widget_rect;

    def local_pos(self, pos):
        return (pos[0] - self._widget_rect.x, pos[1] - self._widget_rect.y);

    def content_rect(self):
        return self._widget_rect.inflate(-8, -8);

    def canvas_pos(self, pos):
        local = self.local_pos(pos);
        return ((local[0] - 4 - self.offset_x) / self.zoom, (local[1] - 4 - self.offset_y) / self.zoom);

    def request_redraw(self):
        self.needs_redraw = True;

    def redraw(self):
        self.request_redraw();

    def clear(self):
        self.commands = [];
        self.request_redraw();

    def save_state(self):
        self.state_stack.append((self.stroke_color, self.fill_color, self.line_width, self.font, self.offset_x, self.offset_y, self.zoom));

    def restore_state(self):
        if not self.state_stack:
            return;
        self.stroke_color, self.fill_color, self.line_width, self.font, self.offset_x, self.offset_y, self.zoom = self.state_stack.pop();
        self.request_redraw();

    def translate(self, dx, dy):
        self.offset_x += dx;
        self.offset_y += dy;
        self.request_redraw();

    def set_scale(self, zoom):
        self.zoom = max(0.01, float(zoom));
        self.request_redraw();

    def add_command(self, name, *args, **kwargs):
        self.commands.append((name, args, kwargs));
        self.request_redraw();

    def line(self, x1, y1, x2, y2, color=None, width=None):
        self.add_command("line", x1, y1, x2, y2, color=color, width=width);

    def rect(self, x, y, w, h, color=None, width=None):
        self.add_command("rect", x, y, w, h, color=color, width=width);

    def stroke_rect(self, x, y, w, h, color=None, width=None):
        self.rect(x, y, w, h, color=color, width=width);

    def fill_rect(self, x, y, w, h, color=None):
        self.add_command("fill_rect", x, y, w, h, color=color);

    def circle(self, x, y, r, color=None, width=None):
        self.add_command("circle", x, y, r, color=color, width=width);

    def fill_circle(self, x, y, r, color=None):
        self.add_command("fill_circle", x, y, r, color=color);

    def ellipse(self, x, y, w, h, color=None, width=None):
        self.add_command("ellipse", x, y, w, h, color=color, width=width);

    def fill_ellipse(self, x, y, w, h, color=None):
        self.add_command("fill_ellipse", x, y, w, h, color=color);

    def polygon(self, points, color=None, width=None):
        self.add_command("polygon", list(points), color=color, width=width);

    def fill_polygon(self, points, color=None):
        self.add_command("fill_polygon", list(points), color=color);

    def text(self, x, y, text, color=None, font=None):
        self.add_command("text", x, y, str(text), color=color, font=font);

    def image(self, x, y, surface, w=None, h=None):
        self.add_command("image", x, y, surface, w, h);

    def _point(self, area, x, y):
        return (area.x + int(self.offset_x + x * self.zoom), area.y + int(self.offset_y + y * self.zoom));

    def _rect(self, area, x, y, w, h):
        px, py = self._point(area, x, y);
        return pygame.Rect(px, py, max(1, int(w * self.zoom)), max(1, int(h * self.zoom)));

    def _points(self, area, points):
        return [self._point(area, x, y) for x, y in points];

    def draw_command(self, screen, area, command):
        name, args, kwargs = command;
        color = kwargs.get("color", None);
        width = kwargs.get("width", None);
        if color is None:
            color = self.stroke_color;
        if width is None:
            width = self.line_width;
        width = max(1, int(width));
        if name == "line":
            x1, y1, x2, y2 = args;
            pygame.draw.line(screen, color, self._point(area, x1, y1), self._point(area, x2, y2), width);
        elif name == "rect":
            x, y, w, h = args;
            pygame.draw.rect(screen, color, self._rect(area, x, y, w, h), width);
        elif name == "fill_rect":
            x, y, w, h = args;
            pygame.draw.rect(screen, kwargs.get("color", self.fill_color), self._rect(area, x, y, w, h));
        elif name == "circle":
            x, y, r = args;
            pygame.draw.circle(screen, color, self._point(area, x, y), max(1, int(r * self.zoom)), width);
        elif name == "fill_circle":
            x, y, r = args;
            pygame.draw.circle(screen, kwargs.get("color", self.fill_color), self._point(area, x, y), max(1, int(r * self.zoom)));
        elif name == "ellipse":
            x, y, w, h = args;
            pygame.draw.ellipse(screen, color, self._rect(area, x, y, w, h), width);
        elif name == "fill_ellipse":
            x, y, w, h = args;
            pygame.draw.ellipse(screen, kwargs.get("color", self.fill_color), self._rect(area, x, y, w, h));
        elif name == "polygon":
            points = args[0];
            if len(points) >= 2:
                pygame.draw.polygon(screen, color, self._points(area, points), width);
        elif name == "fill_polygon":
            points = args[0];
            if len(points) >= 3:
                pygame.draw.polygon(screen, kwargs.get("color", self.fill_color), self._points(area, points));
        elif name == "text":
            x, y, value = args;
            font = kwargs.get("font", None) or self.font;
            rendered = font.render(value, True, kwargs.get("color", self.stroke_color));
            screen.blit(rendered, self._point(area, x, y));
        elif name == "image":
            x, y, surface, w, h = args;
            if surface is not None:
                target = surface;
                if w is not None and h is not None:
                    target = pygame.transform.scale(surface, (max(1, int(w * self.zoom)), max(1, int(h * self.zoom))));
                screen.blit(target, self._point(area, x, y));

    def handle_event(self, event):
        if not self.interactive:
            return False;
        if event.type == pygame.MOUSEBUTTONDOWN and self._widget_rect.collidepoint(event.pos):
            self.mouse_down = True;
            self.last_pos = event.pos;
            if self.on_event is not None:
                return bool(self.on_event(self, event));
            return True;
        if event.type == pygame.MOUSEMOTION and self.mouse_down:
            self.last_pos = event.pos;
            if self.on_event is not None:
                return bool(self.on_event(self, event));
            return True;
        if event.type == pygame.MOUSEBUTTONUP and self.mouse_down:
            self.mouse_down = False;
            if self.on_event is not None:
                return bool(self.on_event(self, event));
            return True;
        if event.type == pygame.KEYDOWN and self.has_focus:
            if self.on_event is not None:
                return bool(self.on_event(self, event));
        return False;

    def draw(self, screen):
        bg = self.background if self.background is not None else self.theme.panel;
        pygame.draw.rect(screen, bg, self._widget_rect, border_radius=8);
        pygame.draw.rect(screen, self.theme.cursor if self.has_focus else self.theme.line, self._widget_rect, 3 if self.has_focus else 2, border_radius=8);
        area = self.content_rect();
        def draw_inside():
            for command in self.commands:
                self.draw_command(screen, area, command);
            if self.on_draw is not None:
                self.on_draw(self, screen, area);
        with_clip(screen, area, draw_inside);
        self.needs_redraw = False;
