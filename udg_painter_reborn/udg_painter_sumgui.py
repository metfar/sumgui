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

# New version based on https://github.com/metfar/ZX-Spectrum-like-UDG-Painter/ implemented using sumGUI

import ast;
import json;
import math;
import os;
import sys;

import pygame;

try:
    from PIL import Image;
except ImportError:
    Image = None;

from sumgui import Button, Panel, Widget, get_events, enable_key_repeat, make_theme;
from sumgui.dialogs import message_box;
from sumgui.widgets import draw_clipped_text;

BASE_WIDTH = 720;
BASE_HEIGHT = 1280;
HEIGHT = 960;#1360
WIDTH = int(BASE_WIDTH * (HEIGHT / BASE_HEIGHT));
MIN_GRID_SIZE = 1;
MAX_GRID_SIZE = 64;
START_GRID_SIZE = 8;
SAVE_MODES = ["COLOR", "BINARY", "XPM", "ICO"];
SAVE_EXTENSIONS = {"COLOR": ".udg", "BINARY": ".bin", "XPM": ".xpm", "ICO": ".ico"};

SPECTRUM_COLORS = [
    (0, 0, 0),
    (0, 0, 205),
    (205, 0, 0),
    (205, 0, 205),
    (0, 205, 0),
    (0, 205, 205),
    (205, 205, 0),
    (205, 205, 205),
    (22, 22, 22),
    (0, 0, 255),
    (255, 0, 0),
    (255, 0, 255),
    (0, 255, 0),
    (0, 255, 255),
    (255, 255, 0),
    (255, 255, 255),
];

RETRO_EXTRA_COLORS = [
    (128, 64, 0),
    (255, 128, 0),
    (64, 64, 64),
    (96, 128, 160),
    (192, 192, 192),
    (96, 0, 160),
    (96, 112, 0),
    (0, 96, 96),
    (192, 160, 112),
    (192, 96, 80),
    (96, 176, 160),
    (160, 128, 208),
    (144, 176, 0),
    (224, 112, 128),
    (112, 160, 208),
    (240, 224, 128),
];

CUSTOM_COLORS = [
    (0, 96, 104),
    (96, 176, 160),
    (80, 104, 128),
    (255, 88, 72),
    (96, 0, 160),
    (96, 112, 0),
    (208, 144, 0),
    (0, 40, 64),
    (32, 80, 160),
    (0, 80, 128),
    (128, 0, 0),
    (0, 104, 104),
    (112, 0, 112),
    (128, 128, 128),
    (16, 16, 16),
    (255, 255, 255),
];

APP_COLORS = SPECTRUM_COLORS + RETRO_EXTRA_COLORS + CUSTOM_COLORS;
CUSTOM_COLOR_START = len(SPECTRUM_COLORS) + len(RETRO_EXTRA_COLORS);
PALETTE_COLUMNS = 8;

BG = (10, 30, 32);
GRID_BG = (28, 48, 54);
GRID_LINE = (55, 75, 85);
TEXT = (235, 245, 250);
BTN = (140, 220, 40);
BTN2 = (60, 100, 120);
BTN_TEXT = (10, 25, 30);
ERROR = (255, 100, 100);


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, int(value)));


def empty_grid(size):
    return [[-1 for _ in range(size)] for _ in range(size)];


def copy_grid(grid):
    return [list(row) for row in grid];


def grid_size(grid):
    rows = len(grid);
    cols = max([len(row) for row in grid if isinstance(row, list)] + [0]);
    return max(rows, cols, 1);


def normalize_grid(grid, size=None):
    size = clamp(size or grid_size(grid), MIN_GRID_SIZE, MAX_GRID_SIZE);
    clean = empty_grid(size);

    for row in range(min(size, len(grid))):
        if not isinstance(grid[row], list):
            continue;

        for col in range(min(size, len(grid[row]))):
            value = grid[row][col];
            if isinstance(value, int) and -1 <= value < len(APP_COLORS):
                clean[row][col] = value;

    return clean;


def nearest_spectrum_color(rgb):
    best_index = 0;
    best_distance = None;

    for index, color in enumerate(APP_COLORS):
        distance = ((int(rgb[0]) - color[0]) ** 2 + (int(rgb[1]) - color[1]) ** 2 + (int(rgb[2]) - color[2]) ** 2);
        if best_distance is None or distance < best_distance:
            best_distance = distance;
            best_index = index;

    return best_index;


def grid_to_binary_bytes(grid):
    size = grid_size(grid);
    bytes_per_row = (size + 7) // 8;
    output = bytearray();

    for row in range(size):
        padded = list(grid[row]) + [-1 for _ in range(bytes_per_row * 8 - size)];
        for start in range(0, len(padded), 8):
            value = 0;
            for cell in padded[start:start + 8]:
                bit = 1 if cell >= 0 else 0;
                value = (value << 1) | bit;
            output.append(value);

    return bytes(output);


def infer_binary_square_size(data):
    data_len = len(data);
    for size in range(MAX_GRID_SIZE, MIN_GRID_SIZE - 1, -1):
        if size * ((size + 7) // 8) == data_len:
            return size;
    return START_GRID_SIZE;


def binary_bytes_to_grid(data):
    size = infer_binary_square_size(data);
    bytes_per_row = (size + 7) // 8;
    grid = empty_grid(size);

    for row in range(size):
        start = row * bytes_per_row;
        row_bytes = data[start:start + bytes_per_row];
        col = 0;
        for value in row_bytes:
            for bit_index in range(7, -1, -1):
                if col < size:
                    bit = (value >> bit_index) & 1;
                    grid[row][col] = 15 if bit else -1;
                    col += 1;

    return grid;


def binary_rows_to_grid(rows, rows_count=None, cols_count=None):
    size = clamp(max(rows_count or len(rows), cols_count or len(rows), 1), MIN_GRID_SIZE, MAX_GRID_SIZE);
    grid = empty_grid(size);

    for row, value in enumerate(rows[:size]):
        for bit_index in range(size - 1, -1, -1):
            col = size - 1 - bit_index;
            bit = (int(value) >> bit_index) & 1;
            grid[row][col] = 15 if bit else -1;

    return grid;


def color_to_hex(color):
    return "#{:02X}{:02X}{:02X}".format(color[0], color[1], color[2]);


def xpm_symbols(count):
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+,-/:;<=>?@[]^_{|}~";
    if count + 1 > len(chars):
        raise ValueError("Palette too large for single-character XPM symbols.");
    return ["."] + list(chars[:count]);


def grid_to_xpm_text(grid):
    size = grid_size(grid);
    symbols = xpm_symbols(len(APP_COLORS));
    lines = [];
    lines.append("/* XPM */");
    lines.append("static char * udg_image[] = {");
    lines.append('"' + str(size) + ' ' + str(size) + ' ' + str(len(APP_COLORS) + 1) + ' 1",');
    lines.append('". c None",');

    for color_index, color in enumerate(APP_COLORS):
        lines.append('"' + symbols[color_index + 1] + ' c ' + color_to_hex(color) + '",');

    for row_index, row in enumerate(grid):
        text_row = "";
        for cell in row:
            text_row += symbols[cell + 1] if isinstance(cell, int) and 0 <= cell < len(APP_COLORS) else ".";
        comma = "," if row_index < size - 1 else "";
        lines.append('"' + text_row + '"' + comma);

    lines.append("};");
    lines.append("");
    return "\n".join(lines);


def parse_xpm_color(value):
    value = value.strip();
    if value.lower() == "none":
        return None;
    if value.startswith("#") and len(value) >= 7:
        try:
            return (int(value[1:3], 16), int(value[3:5], 16), int(value[5:7], 16));
        except ValueError:
            return None;
    names = {"black": (0, 0, 0), "blue": (0, 0, 255), "red": (255, 0, 0), "magenta": (255, 0, 255), "green": (0, 255, 0), "cyan": (0, 255, 255), "yellow": (255, 255, 0), "white": (255, 255, 255), "gray": (205, 205, 205), "grey": (205, 205, 205)};
    return names.get(value.lower());


def extract_xpm_strings(text):
    strings = [];
    for line in text.splitlines():
        line = line.strip();
        if '"' not in line:
            continue;
        start = line.find('"');
        end = line.rfind('"');
        if end > start:
            strings.append(line[start + 1:end]);
    return strings;


def xpm_text_to_grid(text):
    strings = extract_xpm_strings(text);
    if not strings:
        raise ValueError("No XPM string data found.");
    header = strings[0].split();
    if len(header) < 4:
        raise ValueError("Invalid XPM header.");
    width = int(header[0]);
    height = int(header[1]);
    colors = int(header[2]);
    cpp = int(header[3]);
    palette = {};

    for index in range(colors):
        item = strings[index + 1];
        key = item[:cpp];
        rest = item[cpp:].strip().split();
        color_value = None;
        for pos, token in enumerate(rest):
            if token == "c" and pos + 1 < len(rest):
                color_value = parse_xpm_color(rest[pos + 1]);
                break;
        palette[key] = -1 if color_value is None else nearest_spectrum_color(color_value);

    rows = strings[1 + colors:1 + colors + height];
    size = clamp(max(width, height), MIN_GRID_SIZE, MAX_GRID_SIZE);
    raw_grid = empty_grid(size);

    for row in range(height):
        row_text = rows[row];
        for col in range(width):
            key = row_text[col * cpp:(col + 1) * cpp];
            raw_grid[row][col] = palette.get(key, -1);

    return normalize_grid(raw_grid, size);


def grid_to_rgba_image(grid):
    if Image is None:
        raise RuntimeError("Pillow is required for ICO export.");
    size = grid_size(grid);
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0));
    pixels = image.load();
    for row in range(size):
        for col in range(size):
            color_index = grid[row][col];
            if isinstance(color_index, int) and 0 <= color_index < len(APP_COLORS):
                rgb = APP_COLORS[color_index];
                pixels[col, row] = (rgb[0], rgb[1], rgb[2], 255);
    return image;


def image_to_grid(image):
    rgba = image.convert("RGBA");
    source_w, source_h = rgba.size;
    size = clamp(max(source_w, source_h, 1), MIN_GRID_SIZE, MAX_GRID_SIZE);
    grid = empty_grid(size);
    pixels = rgba.load();

    for row in range(source_h):
        for col in range(source_w):
            r, g, b, a = pixels[col, row];
            if a >= 64:
                grid[row][col] = nearest_spectrum_color((r, g, b));

    return grid;


def load_ico_file(filename):
    if Image is None:
        raise RuntimeError("Pillow is required for ICO load.");
    with Image.open(filename) as image:
        if hasattr(image, "ico"):
            sizes = sorted(image.ico.sizes(), key=lambda item: (item[0] * item[1], item[0], item[1]));
            if sizes:
                image = image.ico.getimage(sizes[0]);
        return image_to_grid(image);


def save_graphic(filename, grid, save_mode):
    if not filename.strip():
        return "EMPTY FILENAME";
    extension = SAVE_EXTENSIONS.get(save_mode, ".udg");
    filename = filename.strip();
    if not filename.lower().endswith(extension):
        filename += extension;

    if save_mode == "COLOR":
        size = grid_size(grid);
        data = {"format": "UDG_COLOR_MATRIX", "rows": size, "cols": size, "palette": "SUMGUI_EXTENDED_48", "colors": APP_COLORS, "grid": grid};
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4);
    elif save_mode == "BINARY":
        with open(filename, "wb") as file:
            file.write(grid_to_binary_bytes(grid));
    elif save_mode == "XPM":
        with open(filename, "w", encoding="utf-8") as file:
            file.write(grid_to_xpm_text(grid));
    elif save_mode == "ICO":
        image = grid_to_rgba_image(grid);
        size = grid_size(grid);
        image.save(filename, format="ICO", sizes=[(size, size)]);
    else:
        return "UNKNOWN SAVE MODE";

    return "SAVED " + save_mode + ": " + filename;


def load_graphic(filename):
    lower_name = filename.lower();
    if lower_name.endswith(".bin"):
        with open(filename, "rb") as file:
            return binary_bytes_to_grid(file.read());
    if lower_name.endswith(".xpm"):
        with open(filename, "r", encoding="utf-8") as file:
            return xpm_text_to_grid(file.read());
    if lower_name.endswith(".ico"):
        return load_ico_file(filename);

    with open(filename, "r", encoding="utf-8") as file:
        text = file.read();
    try:
        data = json.loads(text);
    except json.JSONDecodeError:
        data = ast.literal_eval(text);

    if isinstance(data, dict) and data.get("format") == "UDG_COLOR_MATRIX":
        file_rows = int(data.get("rows", len(data.get("grid", []))));
        file_cols = int(data.get("cols", file_rows));
        size = clamp(max(file_rows, file_cols), MIN_GRID_SIZE, MAX_GRID_SIZE);
        return normalize_grid(data["grid"], size);
    if isinstance(data, dict) and data.get("format") == "ZX_SPECTRUM_BINARY_ROWS":
        file_rows = int(data.get("rows", len(data.get("bytes", []))));
        file_cols = int(data.get("cols", file_rows));
        return binary_rows_to_grid(data["bytes"], file_rows, file_cols);
    if isinstance(data, list):
        if all(isinstance(row, list) for row in data):
            return normalize_grid(data);
        return binary_rows_to_grid(data, len(data), len(data));
    raise ValueError("Unknown file format.");


def resize_canvas(grid, new_size):
    new_size = clamp(new_size, MIN_GRID_SIZE, MAX_GRID_SIZE);
    new_grid = empty_grid(new_size);
    old_size = grid_size(grid);
    for row in range(min(old_size, new_size)):
        for col in range(min(old_size, new_size)):
            new_grid[row][col] = grid[row][col];
    return new_grid;


def resize_nearest_from_reference(reference_grid, new_size):
    old_size = grid_size(reference_grid);
    new_size = clamp(new_size, MIN_GRID_SIZE, MAX_GRID_SIZE);
    result = empty_grid(new_size);
    if old_size <= 1 or new_size <= 1:
        result[0][0] = reference_grid[0][0];
        return result;
    for row in range(new_size):
        source_row = round(row * (old_size - 1) / (new_size - 1));
        for col in range(new_size):
            source_col = round(col * (old_size - 1) / (new_size - 1));
            result[row][col] = reference_grid[source_row][source_col];
    return result;


def shift_grid_wrap(grid, dx, dy):
    size = grid_size(grid);
    new_grid = empty_grid(size);
    for row in range(size):
        for col in range(size):
            new_row = (row + dy) % size;
            new_col = (col + dx) % size;
            new_grid[new_row][new_col] = grid[row][col];
    return new_grid;


def list_files(directory, extensions):
    items = [];
    try:
        for name in os.listdir(directory):
            path = os.path.join(directory, name);
            if os.path.isdir(path):
                items.append(("[" + name + "/]", path, True));
            elif any(name.lower().endswith(ext) for ext in extensions):
                items.append((name, path, False));
    except OSError:
        return [];
    items.sort(key=lambda item: (not item[2], item[0].lower()));
    return [("[..]", os.path.dirname(os.path.abspath(directory)), True)] + items;


def visible_input_window(font, text, cursor, max_width):
    start = 0;

    while start < cursor and font.size(text[start:cursor])[0] > max_width:
        start += 1;

    end = cursor;

    while end < len(text) and font.size(text[start:end + 1])[0] <= max_width:
        end += 1;

    return text[start:end], start;


def filename_dialog(screen, clock, theme, title, default_name):
    font_big = pygame.font.SysFont("monospace", max(16, screen.get_height() // 32), bold=True);
    font_small = pygame.font.SysFont("monospace", max(12, screen.get_height() // 48), bold=True);
    width, height = screen.get_size();
    rect = pygame.Rect(width // 12, height // 3, width * 10 // 12, height // 3);
    input_rect = pygame.Rect(rect.x + 20, rect.y + height // 10, rect.width - 40, height // 15);
    ok_rect = pygame.Rect(rect.x + 20, rect.bottom - height // 12, rect.width // 2 - 30, height // 17);
    cancel_rect = pygame.Rect(rect.centerx + 10, rect.bottom - height // 12, rect.width // 2 - 30, height // 17);
    text = default_name or "graphic";
    cursor = len(text);
    cursor_visible = True;
    cursor_ms = 0;
    pygame.key.start_text_input();
    pygame.key.set_text_input_rect(input_rect);

    while True:
        dt = clock.tick(60);
        cursor_ms += dt;

        if cursor_ms >= 500:
            cursor_visible = not cursor_visible;
            cursor_ms = 0;

        for event in get_events():
            if event.type == pygame.QUIT:
                pygame.key.stop_text_input();
                return None;
            if event.type == pygame.TEXTINPUT:
                for char in event.text:
                    if char.isalnum() or char in "_-./":
                        text = text[:cursor] + char + text[cursor:];
                        cursor += 1;
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.key.stop_text_input();
                    return None;
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    pygame.key.stop_text_input();
                    return text;
                if event.key == pygame.K_BACKSPACE and cursor > 0:
                    text = text[:cursor - 1] + text[cursor:];
                    cursor -= 1;
                if event.key == pygame.K_DELETE and cursor < len(text):
                    text = text[:cursor] + text[cursor + 1:];
                if event.key == pygame.K_LEFT:
                    cursor = max(0, cursor - 1);
                if event.key == pygame.K_RIGHT:
                    cursor = min(len(text), cursor + 1);
                if event.key == pygame.K_HOME:
                    cursor = 0;
                if event.key == pygame.K_END:
                    cursor = len(text);
            if event.type == pygame.MOUSEBUTTONDOWN:
                if ok_rect.collidepoint(event.pos):
                    pygame.key.stop_text_input();
                    return text;
                if cancel_rect.collidepoint(event.pos):
                    pygame.key.stop_text_input();
                    return None;

        pygame.draw.rect(screen, theme.panel, rect, border_radius=8);
        pygame.draw.rect(screen, theme.line, rect, 3, border_radius=8);
        draw_clipped_text(screen, font_big, title, theme.text, pygame.Rect(rect.x + 20, rect.y + 16, rect.width - 40, font_big.get_height() + 8));
        pygame.draw.rect(screen, theme.bg, input_rect, border_radius=4);
        pygame.draw.rect(screen, theme.line, input_rect, 2, border_radius=4);
        input_inner = pygame.Rect(input_rect.x + 10, input_rect.y + 8, input_rect.width - 20, input_rect.height - 16);
        visible_text, view_start = visible_input_window(font_big, text, cursor, input_inner.width - 8);
        before_cursor = text[view_start:cursor];
        previous_clip = screen.get_clip();
        screen.set_clip(input_inner);
        screen.blit(font_big.render(visible_text, True, theme.text), (input_inner.x, input_inner.y));
        cursor_x = input_inner.x + font_big.size(before_cursor)[0] + 2;

        if cursor_visible:
            pygame.draw.rect(screen, theme.cursor, pygame.Rect(cursor_x, input_inner.y, 4, input_inner.height));

        screen.set_clip(previous_clip);
        for button_rect, label in ((ok_rect, "OK"), (cancel_rect, "CANCEL")):
            pygame.draw.rect(screen, theme.button, button_rect, border_radius=6);
            pygame.draw.rect(screen, theme.line, button_rect, 2, border_radius=6);
            draw_clipped_text(screen, font_big, label, theme.button_text, button_rect, align="center", valign="middle");
        pygame.display.flip();


def file_dialog(screen, clock, theme, title, extensions):
    font_big = pygame.font.SysFont("monospace", max(16, screen.get_height() // 34), bold=True);
    font_small = pygame.font.SysFont("monospace", max(12, screen.get_height() // 52), bold=True);
    width, height = screen.get_size();
    directory = os.getcwd();
    selected = 0;
    scroll = 0;
    visible_rows = 10;
    row_h = max(24, height // 18);
    rect = pygame.Rect(width // 14, height // 8, width * 12 // 14, height * 3 // 4);
    cancel_rect = pygame.Rect(rect.centerx - width // 8, rect.bottom - height // 14, width // 4, height // 18);

    while True:
        items = list_files(directory, extensions);
        selected = clamp(selected, 0, max(0, len(items) - 1));
        scroll = clamp(scroll, 0, max(0, len(items) - visible_rows));
        if selected < scroll:
            scroll = selected;
        if selected >= scroll + visible_rows:
            scroll = selected - visible_rows + 1;

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None;
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None;
                if event.key == pygame.K_UP:
                    selected = max(0, selected - 1);
                if event.key == pygame.K_DOWN:
                    selected = min(len(items) - 1, selected + 1);
                if event.key == pygame.K_HOME:
                    selected = 0;
                if event.key == pygame.K_END:
                    selected = max(0, len(items) - 1);
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    if not items:
                        continue;
                    label, path, is_dir = items[selected];
                    if is_dir:
                        directory = os.path.abspath(path);
                        selected = 0;
                        scroll = 0;
                    else:
                        return path;
                if event.key in (pygame.K_LEFT, pygame.K_BACKSPACE):
                    directory = os.path.dirname(os.path.abspath(directory));
                    selected = 0;
                    scroll = 0;
            if event.type == pygame.MOUSEBUTTONDOWN:
                if cancel_rect.collidepoint(event.pos):
                    return None;
                list_top = rect.y + height // 8;
                for idx in range(scroll, min(len(items), scroll + visible_rows)):
                    item_rect = pygame.Rect(rect.x + 18, list_top + (idx - scroll) * row_h, rect.width - 36, row_h - 4);
                    if item_rect.collidepoint(event.pos):
                        selected = idx;
                        label, path, is_dir = items[idx];
                        if is_dir:
                            directory = os.path.abspath(path);
                            selected = 0;
                            scroll = 0;
                        else:
                            return path;

        pygame.draw.rect(screen, theme.panel, rect, border_radius=8);
        pygame.draw.rect(screen, theme.line, rect, 3, border_radius=8);
        draw_clipped_text(screen, font_big, title, theme.text, pygame.Rect(rect.x + 18, rect.y + 14, rect.width - 36, font_big.get_height() + 8));
        draw_clipped_text(screen, font_small, directory, theme.muted, pygame.Rect(rect.x + 18, rect.y + 58, rect.width - 36, font_small.get_height() + 6));
        list_top = rect.y + height // 8;
        for idx in range(scroll, min(len(items), scroll + visible_rows)):
            label, path, is_dir = items[idx];
            item_rect = pygame.Rect(rect.x + 18, list_top + (idx - scroll) * row_h, rect.width - 36, row_h - 4);
            color = theme.button if idx == selected else theme.bg;
            pygame.draw.rect(screen, color, item_rect, border_radius=4);
            pygame.draw.rect(screen, theme.line, item_rect, 1, border_radius=4);
            draw_clipped_text(screen, font_small, label, theme.button_text if idx == selected else theme.text, pygame.Rect(item_rect.x + 10, item_rect.y + 4, item_rect.width - 20, item_rect.height - 8));
        pygame.draw.rect(screen, theme.button, cancel_rect, border_radius=6);
        pygame.draw.rect(screen, theme.line, cancel_rect, 2, border_radius=6);
        draw_clipped_text(screen, font_big, "CANCEL", theme.button_text, cancel_rect, align="center", valign="middle");
        pygame.display.flip();
        clock.tick(60);



class TransparentPanel(Panel):
    def draw(self, screen):
        previous_clip = screen.get_clip();
        screen.set_clip(self.rect);
        for widget in self.children:
            if widget.visible:
                widget.draw(screen);
        screen.set_clip(previous_clip);


class OldStyleButton(Button):
    def __init__(self, rect, text, font, on_click=None, bg_color=None, fg_color=None, radius=20, theme=None, tab_index=0):
        super().__init__(rect, text, font, on_click=on_click, theme=theme, tab_index=tab_index);
        self.bg_color = bg_color or BTN;
        self.fg_color = fg_color or (10, 25, 30);
        self.radius = radius;

    def draw(self, screen):
        color = self.bg_color;
        if self.pressed:
            color = tuple(max(0, component - 25) for component in color);
        pygame.draw.rect(screen, color, self.rect, border_radius=self.radius);
        draw_clipped_text(screen, self.font, self.text, self.fg_color, self.rect.inflate(-8, -4), align="center", valign="middle");


class ExtendedPaletteWidget(Widget):
    def __init__(self, rect, colors, columns, cell_size, callback, theme, tab_index=20):
        super().__init__(rect, focusable=True, tab_index=tab_index);
        self.colors = colors;
        self.columns = max(1, int(columns));
        self.cell_size = max(8, int(cell_size));
        self.callback = callback;
        self.theme = theme;
        self.selected = 0;
        self.font = pygame.font.SysFont("monospace", max(8, self.cell_size // 3), bold=True);

    def color_rect(self, index):
        col = index % self.columns;
        row = index // self.columns;
        x = self.rect.x + col * self.cell_size;
        y = self.rect.y + row * self.cell_size;
        inset = max(2, self.cell_size // 12);
        return pygame.Rect(x + inset, y + inset, self.cell_size - inset * 2, self.cell_size - inset * 2);

    def index_at(self, pos):
        if not self.rect.collidepoint(pos):
            return None;
        col = (pos[0] - self.rect.x) // self.cell_size;
        row = (pos[1] - self.rect.y) // self.cell_size;
        index = int(row * self.columns + col);
        if 0 <= index < len(self.colors):
            return index;
        return None;

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            index = self.index_at(event.pos);
            if index is None:
                return False;
            self.selected = index;
            if self.callback:
                self.callback(index);
            return True;
        return False;

    def draw(self, screen):
        pygame.draw.rect(screen, self.theme.panel, self.rect, border_radius=max(4, self.cell_size // 8));
        pygame.draw.rect(screen, self.theme.line, self.rect, max(1, self.cell_size // 18), border_radius=max(4, self.cell_size // 8));
        for index, color in enumerate(self.colors):
            rect = self.color_rect(index);
            pygame.draw.rect(screen, color, rect, border_radius=max(2, self.cell_size // 10));
            pygame.draw.rect(screen, self.theme.line, rect, max(1, self.cell_size // 20), border_radius=max(2, self.cell_size // 10));
            if index == self.selected:
                pygame.draw.rect(screen, (255, 255, 255), rect.inflate(max(4, self.cell_size // 7), max(4, self.cell_size // 7)), max(2, self.cell_size // 12), border_radius=max(4, self.cell_size // 8));
            label = str(index);
            label_rect = pygame.Rect(rect.x, rect.y - self.font.get_height() + 2, rect.width, self.font.get_height());
            draw_clipped_text(screen, self.font, label, self.theme.text, label_rect, align="center", valign="middle");



def rgb_to_hex(color):
    return "#{:02X}{:02X}{:02X}".format(clamp(color[0], 0, 255), clamp(color[1], 0, 255), clamp(color[2], 0, 255));


def hex_to_rgb(text):
    value = text.strip();
    if value.startswith("#"):
        value = value[1:];
    if len(value) != 6:
        return None;
    try:
        return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16));
    except ValueError:
        return None;


def parse_color_value(text):
    value = text.strip();
    if value.startswith("#") or (len(value) == 6 and all(char in "0123456789abcdefABCDEF" for char in value)):
        return hex_to_rgb(value);
    if "," in value:
        parts = [part.strip() for part in value.split(",")];
    else:
        parts = [part.strip() for part in value.split()];
    if len(parts) == 3 and all(part.isdigit() for part in parts):
        return tuple(clamp(int(part), 0, 255) for part in parts);
    return None;


def draw_color_slider(screen, font, theme, label, rect, value, active=False):
    pygame.draw.rect(screen, theme.bg, rect, border_radius=6);
    pygame.draw.rect(screen, theme.cursor if active else theme.line, rect, 2, border_radius=6);
    text_rect = pygame.Rect(rect.x + 8, rect.y + 4, rect.width - 16, font.get_height() + 4);
    draw_clipped_text(screen, font, label + ": " + str(value), theme.text, text_rect);
    bar_rect = pygame.Rect(rect.x + 14, rect.centery + font.get_height() // 4, rect.width - 28, max(6, rect.height // 7));
    pygame.draw.rect(screen, theme.line, bar_rect, border_radius=3);
    fill_w = int(bar_rect.width * value / 255);
    if fill_w > 0:
        pygame.draw.rect(screen, theme.button, pygame.Rect(bar_rect.x, bar_rect.y, fill_w, bar_rect.height), border_radius=3);
    knob_x = bar_rect.x + int(bar_rect.width * value / 255);
    knob_rect = pygame.Rect(knob_x - 6, bar_rect.centery - 12, 12, 24);
    pygame.draw.rect(screen, theme.cursor, knob_rect, border_radius=5);
    draw_clipped_text(screen, font, "0", theme.muted, pygame.Rect(bar_rect.x, bar_rect.bottom + 2, 40, font.get_height()));
    draw_clipped_text(screen, font, "255", theme.muted, pygame.Rect(bar_rect.right - 45, bar_rect.bottom + 2, 45, font.get_height()), align="right");


def rgb_dialog(screen, clock, theme, title, color):
    font_big = pygame.font.SysFont("monospace", max(16, screen.get_height() // 34), bold=True);
    font_small = pygame.font.SysFont("monospace", max(12, screen.get_height() // 50), bold=True);
    width, height = screen.get_size();
    rect = pygame.Rect(width // 14, height // 5, width * 12 // 14, height * 3 // 5);
    input_rect = pygame.Rect(rect.x + 20, rect.y + height // 10, rect.width - 40, height // 16);
    preview_old_rect = pygame.Rect(rect.x + 20, input_rect.bottom + 18, rect.width // 2 - 32, height // 14);
    preview_new_rect = pygame.Rect(rect.centerx + 12, input_rect.bottom + 18, rect.width // 2 - 32, height // 14);
    slider_h = max(54, height // 17);
    slider_gap = max(10, height // 90);
    slider_top = preview_old_rect.bottom + height // 24;
    slider_rects = [pygame.Rect(rect.x + 20, slider_top + idx * (slider_h + slider_gap), rect.width - 40, slider_h) for idx in range(3)];
    ok_rect = pygame.Rect(rect.x + 20, rect.bottom - height // 13, rect.width // 2 - 30, height // 18);
    cancel_rect = pygame.Rect(rect.centerx + 10, rect.bottom - height // 13, rect.width // 2 - 30, height // 18);
    current = [clamp(color[0], 0, 255), clamp(color[1], 0, 255), clamp(color[2], 0, 255)];
    text = rgb_to_hex(current);
    cursor = len(text);
    cursor_visible = True;
    cursor_ms = 0;
    dragging_slider = None;
    pygame.key.start_text_input();
    pygame.key.set_text_input_rect(input_rect);

    def update_from_text():
        nonlocal current;
        parsed = parse_color_value(text);
        if parsed is not None:
            current = [parsed[0], parsed[1], parsed[2]];
            return True;
        return False;

    def update_slider(index, pos_x):
        nonlocal text, cursor;
        bar_rect = pygame.Rect(slider_rects[index].x + 14, slider_rects[index].centery + font_small.get_height() // 4, slider_rects[index].width - 28, max(6, slider_rects[index].height // 7));
        current[index] = clamp(round((pos_x - bar_rect.x) * 255 / max(1, bar_rect.width)), 0, 255);
        text = rgb_to_hex(current);
        cursor = len(text);

    while True:
        dt = clock.tick(60);
        cursor_ms += dt;
        if cursor_ms >= 500:
            cursor_visible = not cursor_visible;
            cursor_ms = 0;
        for event in get_events():
            if event.type == pygame.QUIT:
                pygame.key.stop_text_input();
                return None;
            if event.type == pygame.TEXTINPUT:
                for char in event.text:
                    if char in "0123456789abcdefABCDEF#, ":
                        text = text[:cursor] + char + text[cursor:];
                        cursor += 1;
                        update_from_text();
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.key.stop_text_input();
                    return None;
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if update_from_text():
                        pygame.key.stop_text_input();
                        return tuple(current);
                if event.key == pygame.K_BACKSPACE and cursor > 0:
                    text = text[:cursor - 1] + text[cursor:];
                    cursor -= 1;
                    update_from_text();
                if event.key == pygame.K_DELETE and cursor < len(text):
                    text = text[:cursor] + text[cursor + 1:];
                    update_from_text();
                if event.key == pygame.K_LEFT:
                    cursor = max(0, cursor - 1);
                if event.key == pygame.K_RIGHT:
                    cursor = min(len(text), cursor + 1);
                if event.key == pygame.K_HOME:
                    cursor = 0;
                if event.key == pygame.K_END:
                    cursor = len(text);
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if ok_rect.collidepoint(event.pos):
                    if update_from_text():
                        pygame.key.stop_text_input();
                        return tuple(current);
                elif cancel_rect.collidepoint(event.pos):
                    pygame.key.stop_text_input();
                    return None;
                elif input_rect.collidepoint(event.pos):
                    rel_x = max(0, event.pos[0] - input_rect.x - 10);
                    cursor = 0;
                    for pos in range(len(text) + 1):
                        if font_big.size(text[:pos])[0] <= rel_x:
                            cursor = pos;
                    pygame.key.set_text_input_rect(input_rect);
                else:
                    for idx, slider_rect in enumerate(slider_rects):
                        if slider_rect.collidepoint(event.pos):
                            dragging_slider = idx;
                            update_slider(idx, event.pos[0]);
                            break;
            if event.type == pygame.MOUSEBUTTONUP:
                dragging_slider = None;
            if event.type == pygame.MOUSEMOTION and dragging_slider is not None:
                update_slider(dragging_slider, event.pos[0]);

        pygame.draw.rect(screen, theme.panel, rect, border_radius=8);
        pygame.draw.rect(screen, theme.line, rect, 3, border_radius=8);
        draw_clipped_text(screen, font_big, title, theme.text, pygame.Rect(rect.x + 20, rect.y + 16, rect.width - 40, font_big.get_height() + 8));
        draw_clipped_text(screen, font_small, "HEX editable (#RRGGBB) o RGB editable (R,G,B)", theme.muted, pygame.Rect(rect.x + 20, rect.y + 58, rect.width - 40, font_small.get_height() + 8));
        pygame.draw.rect(screen, theme.bg, input_rect, border_radius=4);
        pygame.draw.rect(screen, theme.line, input_rect, 2, border_radius=4);
        input_inner = pygame.Rect(input_rect.x + 10, input_rect.y + 8, input_rect.width - 20, input_rect.height - 16);
        visible_text, view_start = visible_input_window(font_big, text, cursor, input_inner.width - 8);
        before_cursor = text[view_start:cursor];
        previous_clip = screen.get_clip();
        screen.set_clip(input_inner);
        screen.blit(font_big.render(visible_text, True, theme.text), (input_inner.x, input_inner.y));
        cursor_x = input_inner.x + font_big.size(before_cursor)[0] + 2;
        if cursor_visible:
            pygame.draw.rect(screen, theme.cursor, pygame.Rect(cursor_x, input_inner.y, 4, input_inner.height));
        screen.set_clip(previous_clip);
        pygame.draw.rect(screen, color, preview_old_rect, border_radius=6);
        pygame.draw.rect(screen, tuple(current), preview_new_rect, border_radius=6);
        pygame.draw.rect(screen, theme.line, preview_old_rect, 2, border_radius=6);
        pygame.draw.rect(screen, theme.line, preview_new_rect, 2, border_radius=6);
        draw_clipped_text(screen, font_small, "ANTES", theme.text, preview_old_rect.inflate(-8, -6), align="center", valign="middle");
        draw_clipped_text(screen, font_small, "NUEVO", theme.text, preview_new_rect.inflate(-8, -6), align="center", valign="middle");
        for idx, label in enumerate(("R", "G", "B")):
            draw_color_slider(screen, font_small, theme, label, slider_rects[idx], current[idx], active=(dragging_slider == idx));
        rgb_text = "RGB: " + str(tuple(current)) + "   HEX: " + rgb_to_hex(current);
        draw_clipped_text(screen, font_small, rgb_text, theme.text, pygame.Rect(rect.x + 20, ok_rect.y - font_small.get_height() - 10, rect.width - 40, font_small.get_height() + 6));
        for button_rect, label in ((ok_rect, "OK"), (cancel_rect, "CANCEL")):
            pygame.draw.rect(screen, theme.button, button_rect, border_radius=6);
            pygame.draw.rect(screen, theme.line, button_rect, 2, border_radius=6);
            draw_clipped_text(screen, font_big, label, theme.button_text, button_rect, align="center", valign="middle");
        pygame.display.flip();


class UDGCanvas(Widget):
    def __init__(self, rect, app):
        super().__init__(rect, focusable=True, tab_index=1);
        self.app = app;
        self.drag_value = None;
        self.last_cell = None;

    def geometry(self):
        size = self.app.size;
        cell = max(2, min(self.rect.width, self.rect.height) // size);
        grid_w = cell * size;
        grid_h = cell * size;
        grid_x = self.rect.x + (self.rect.width - grid_w) // 2;
        grid_y = self.rect.y + (self.rect.height - grid_h) // 2;
        return cell, grid_x, grid_y, grid_w, grid_h;

    def cell_at(self, pos):
        if not self.rect.collidepoint(pos):
            return None;
        cell, grid_x, grid_y, grid_w, grid_h = self.geometry();
        if not (grid_x <= pos[0] < grid_x + grid_w and grid_y <= pos[1] < grid_y + grid_h):
            return None;
        col = int((pos[0] - grid_x) // cell);
        row = int((pos[1] - grid_y) // cell);
        return row, col;

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            found = self.cell_at(event.pos);
            if found is None:
                return False;
            row, col = found;
            self.app.cursor_row = row;
            self.app.cursor_col = col;
            current = self.app.grid[row][col];
            self.drag_value = self.app.selected_color if current == -1 else -1;
            self.app.grid[row][col] = self.drag_value;
            self.app.clear_scale_reference();
            self.last_cell = found;
            return True;
        if event.type == pygame.MOUSEMOTION and self.drag_value is not None:
            found = self.cell_at(event.pos);
            if found is not None and found != self.last_cell:
                row, col = found;
                self.app.cursor_row = row;
                self.app.cursor_col = col;
                self.app.grid[row][col] = self.drag_value;
                self.app.clear_scale_reference();
                self.last_cell = found;
                return True;
        if event.type == pygame.MOUSEBUTTONUP:
            self.drag_value = None;
            self.last_cell = None;
        return False;

    def draw(self, screen):
        size = self.app.size;
        cell, grid_x, grid_y, grid_w, grid_h = self.geometry();
        scale = self.app.scale;
        bg_rect = pygame.Rect(grid_x, grid_y, grid_w, grid_h);
        pygame.draw.rect(screen, GRID_BG, bg_rect, border_radius=scale(24));
        for row in range(size):
            for col in range(size):
                x = grid_x + col * cell;
                y = grid_y + row * cell;
                color_index = self.app.grid[row][col];
                if color_index >= 0:
                    inset = max(1, scale(2));
                    pygame.draw.rect(screen, APP_COLORS[color_index], (x + inset, y + inset, max(1, cell - inset * 2), max(1, cell - inset * 2)));
                pygame.draw.rect(screen, GRID_LINE, (x, y, cell, cell), max(1, scale(2)));
        pygame.draw.rect(screen, GRID_LINE, bg_rect, max(1, scale(5)), border_radius=scale(24));
        cursor_x = grid_x + self.app.cursor_col * cell;
        cursor_y = grid_y + self.app.cursor_row * cell;
        pygame.draw.rect(screen, (255, 255, 255), (cursor_x, cursor_y, cell, cell), max(2, scale(4)));
        inner = max(1, scale(4));
        if cell > inner * 2:
            pygame.draw.rect(screen, (255, 255, 0), (cursor_x + inner, cursor_y + inner, cell - inner * 2, cell - inner * 2), max(1, scale(2)));


class UDGApp:
    def __init__(self):
        pygame.init();
        enable_key_repeat(250, 31);
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT));
        pygame.display.set_caption("Spectrum UDG Painter");
        self.clock = pygame.time.Clock();
        self.scale_factor = HEIGHT / BASE_HEIGHT;
        self.theme = make_theme("dark");
        self.theme.bg = BG;
        self.theme.panel = GRID_BG;
        self.theme.line = GRID_LINE;
        self.theme.text = TEXT;
        self.theme.button = BTN;
        self.theme.button_alt = BTN2;
        self.theme.button_text = (10, 25, 30);
        self.theme.cursor = TEXT;
        self.font_big = pygame.font.SysFont("monospace", max(12, self.scale(32)), bold=True);
        self.font_small = pygame.font.SysFont("monospace", max(8, self.scale(20)), bold=True);
        self.font_tiny = pygame.font.SysFont("monospace", max(9, self.scale(20)), bold=True);
        self.grid = empty_grid(START_GRID_SIZE);
        self.size = START_GRID_SIZE;
        self.selected_color = 14;
        self.save_mode = "COLOR";
        self.current_filename = "UNTITLED";
        self.status = "READY";
        self.cursor_row = 0;
        self.cursor_col = 0;
        self.scale_reference = None;
        self.panel = TransparentPanel(pygame.Rect(0, 0, WIDTH, HEIGHT), self.theme);
        self.create_widgets();

    def scale(self, value):
        return max(1, int(round(value * self.scale_factor)));

    def rect(self, x, y, w, h):
        return pygame.Rect(self.scale(x), self.scale(y), self.scale(w), self.scale(h));

    def create_widgets(self):
        self.panel.children = [];

        margin = self.scale(35);
        gap = self.scale(10);
        big_h = self.scale(70);
        small_h = self.scale(64);
        mode_h = self.scale(70);

        palette_rows = int(math.ceil(len(APP_COLORS) / PALETTE_COLUMNS));
        palette_cell = min(self.scale(44), max(self.scale(28), (WIDTH - margin * 2) // PALETTE_COLUMNS));
        palette_w = PALETTE_COLUMNS * palette_cell;
        palette_h = palette_rows * palette_cell;
        palette_y = HEIGHT - palette_h - self.scale(18);
        palette_rect = pygame.Rect((WIDTH - palette_w) // 2, palette_y, palette_w, palette_h);

        small_row_2_y = palette_y - small_h - self.scale(14);
        small_row_1_y = small_row_2_y - small_h - gap;
        mode_y = small_row_1_y - mode_h - gap;
        big_y = mode_y - big_h - gap;

        grid_y = self.scale(285);
        max_grid_by_width = WIDTH - margin * 2;
        max_grid_by_height = max(self.scale(220), big_y - grid_y - self.scale(28));
        grid_side = min(max_grid_by_width, self.scale(520), max_grid_by_height);
        grid_rect = pygame.Rect((WIDTH - grid_side) // 2, grid_y, grid_side, grid_side);
        self.canvas = UDGCanvas(grid_rect, self);
        self.panel.add(self.canvas);

        big_gap = self.scale(20);
        big_w = (WIDTH - margin * 2 - big_gap * 2) // 3;
        self.clear_button = OldStyleButton(pygame.Rect(margin, big_y, big_w, big_h), "CLEAR", self.font_big, lambda widget: self.clear(), BTN, (10, 25, 30), self.scale(20), self.theme, 2);
        self.save_button = OldStyleButton(pygame.Rect(margin + big_w + big_gap, big_y, big_w, big_h), "SAVE", self.font_big, lambda widget: self.save(), BTN, (10, 25, 30), self.scale(20), self.theme, 3);
        self.load_button = OldStyleButton(pygame.Rect(margin + (big_w + big_gap) * 2, big_y, big_w, big_h), "LOAD", self.font_big, lambda widget: self.load(), BTN, (10, 25, 30), self.scale(20), self.theme, 4);
        half_gap = self.scale(14);
        half_w = (WIDTH - margin * 2 - half_gap) // 2;
        self.mode_button = OldStyleButton(pygame.Rect(margin, mode_y, half_w, mode_h), "FORMAT:  " + self.save_mode, self.font_tiny, lambda widget: self.cycle_mode(), BTN2, TEXT, self.scale(20), self.theme, 5);
        self.edit_color_button = OldStyleButton(pygame.Rect(margin + half_w + half_gap, mode_y, half_w, mode_h), "EDIT COLOR", self.font_tiny, lambda widget: self.edit_selected_color(), BTN2, TEXT, self.scale(20), self.theme, 6);
        for widget in (self.clear_button, self.save_button, self.load_button, self.mode_button, self.edit_color_button):
            self.panel.add(widget);

        small_labels = [
            ("CAN-", lambda widget: self.canvas_resize(-1)),
            ("CAN+", lambda widget: self.canvas_resize(1)),
            ("SCL-", lambda widget: self.scale_resize(-1)),
            ("SCL+", lambda widget: self.scale_resize(1)),
            ("SHL", lambda widget: self.shift(-1, 0)),
            ("SHU", lambda widget: self.shift(0, -1)),
            ("SHD", lambda widget: self.shift(0, 1)),
            ("SHR", lambda widget: self.shift(1, 0)),
        ];
        small_gap = self.scale(14);
        small_w = (WIDTH - margin * 2 - small_gap * 3) // 4;
        index = 0;
        for row, y in enumerate((small_row_1_y, small_row_2_y)):
            for col in range(4):
                text, callback = small_labels[index];
                x = margin + col * (small_w + small_gap);
                button = OldStyleButton(pygame.Rect(x, y, small_w, small_h), text, self.font_tiny, callback, BTN2, TEXT, self.scale(14), self.theme, 7 + index);
                self.panel.add(button);
                index += 1;

        self.palette = ExtendedPaletteWidget(palette_rect, APP_COLORS, PALETTE_COLUMNS, palette_cell, self.select_color, self.theme, tab_index=20);
        self.palette.selected = self.selected_color;
        self.panel.add(self.palette);
        self.update_statusbar();

    def update_statusbar(self):
        if hasattr(self, "mode_button"):
            self.mode_button.text = "FORMAT:  " + self.save_mode;

    def clear_scale_reference(self):
        self.scale_reference = None;

    def set_grid(self, grid):
        self.grid = normalize_grid(grid);
        self.size = grid_size(self.grid);
        self.cursor_row = clamp(self.cursor_row, 0, self.size - 1);
        self.cursor_col = clamp(self.cursor_col, 0, self.size - 1);
        self.clear_scale_reference();
        self.create_widgets();

    def select_color(self, index):
        self.selected_color = index;
        self.status = "COLOR: " + str(index);
        if hasattr(self, "palette"):
            self.palette.selected = index;


    def edit_selected_color(self):
        old_color = APP_COLORS[self.selected_color];
        new_color = rgb_dialog(self.screen, self.clock, self.theme, "EDIT COLOR " + str(self.selected_color), old_color);
        if new_color is None:
            self.status = "COLOR EDIT CANCELLED";
            return;
        APP_COLORS[self.selected_color] = new_color;
        self.status = "COLOR " + str(self.selected_color) + " = " + rgb_to_hex(new_color) + " " + str(new_color);
        self.create_widgets();

    def clear(self):
        self.grid = empty_grid(self.size);
        self.status = "CLEARED";
        self.clear_scale_reference();

    def cycle_mode(self):
        self.save_mode = SAVE_MODES[(SAVE_MODES.index(self.save_mode) + 1) % len(SAVE_MODES)];
        self.status = "MODE: " + self.save_mode;
        self.update_statusbar();

    def save(self):
        default = os.path.splitext(os.path.basename(self.current_filename))[0] if self.current_filename and self.current_filename != "UNTITLED" else "graphic";
        filename = filename_dialog(self.screen, self.clock, self.theme, "SAVE " + self.save_mode, default);
        if filename is None:
            self.status = "SAVE CANCELLED";
            return;
        target = filename;
        extension = SAVE_EXTENSIONS.get(self.save_mode, ".udg");
        if not target.lower().endswith(extension):
            target += extension;
        if os.path.exists(target):
            ok = message_box(self.screen, self.clock, "OVERWRITE", target + " exists. Press OK to overwrite or ESC to cancel.", self.theme);
            if not ok:
                self.status = "SAVE CANCELLED";
                return;
        try:
            self.status = save_graphic(filename, self.grid, self.save_mode);
            self.current_filename = target;
        except Exception as exc:
            self.status = "SAVE ERROR: " + str(exc);

    def load(self):
        filename = file_dialog(self.screen, self.clock, self.theme, "LOAD GRAPHIC", [".udg", ".bin", ".xpm", ".ico"]);
        if filename is None:
            self.status = "LOAD CANCELLED";
            return;
        try:
            self.set_grid(load_graphic(filename));
            self.current_filename = filename;
            self.status = "LOADED " + os.path.basename(filename);
        except Exception as exc:
            self.status = "LOAD ERROR: " + str(exc);

    def canvas_resize(self, delta):
        self.size = clamp(self.size + delta, MIN_GRID_SIZE, MAX_GRID_SIZE);
        self.grid = resize_canvas(self.grid, self.size);
        self.cursor_row = clamp(self.cursor_row, 0, self.size - 1);
        self.cursor_col = clamp(self.cursor_col, 0, self.size - 1);
        self.status = "CANVAS " + str(self.size) + "x" + str(self.size);
        self.clear_scale_reference();
        self.create_widgets();

    def scale_resize(self, delta):
        target_size = clamp(self.size + delta, MIN_GRID_SIZE, MAX_GRID_SIZE);
        if target_size == self.size:
            return;
        if self.scale_reference is None:
            self.scale_reference = copy_grid(self.grid);
        self.grid = resize_nearest_from_reference(self.scale_reference, target_size);
        self.size = target_size;
        self.cursor_row = clamp(self.cursor_row, 0, self.size - 1);
        self.cursor_col = clamp(self.cursor_col, 0, self.size - 1);
        self.status = "SCALE " + str(self.size) + "x" + str(self.size);
        self.create_widgets();

    def shift(self, dx, dy):
        self.grid = shift_grid_wrap(self.grid, dx, dy);
        self.status = "SHIFT " + str(dx) + "," + str(dy);
        self.clear_scale_reference();

    def toggle_cursor_pixel(self):
        if self.grid[self.cursor_row][self.cursor_col] == -1:
            self.grid[self.cursor_row][self.cursor_col] = self.selected_color;
        else:
            self.grid[self.cursor_row][self.cursor_col] = -1;
        self.status = "PIXEL TOGGLED";
        self.clear_scale_reference();

    def handle_key(self, event):
        mods = pygame.key.get_mods() | getattr(event, "mod", 0);
        shift = bool(mods & pygame.KMOD_SHIFT);
        if event.key == pygame.K_ESCAPE:
            return False;
        if event.key == pygame.K_LEFT:
            if shift:
                self.shift(-1, 0);
            else:
                self.cursor_col = max(0, self.cursor_col - 1);
                self.status = "CURSOR: " + str(self.cursor_row) + "," + str(self.cursor_col);
            return True;
        if event.key == pygame.K_RIGHT:
            if shift:
                self.shift(1, 0);
            else:
                self.cursor_col = min(self.size - 1, self.cursor_col + 1);
                self.status = "CURSOR: " + str(self.cursor_row) + "," + str(self.cursor_col);
            return True;
        if event.key == pygame.K_UP:
            if shift:
                self.shift(0, -1);
            else:
                self.cursor_row = max(0, self.cursor_row - 1);
                self.status = "CURSOR: " + str(self.cursor_row) + "," + str(self.cursor_col);
            return True;
        if event.key == pygame.K_DOWN:
            if shift:
                self.shift(0, 1);
            else:
                self.cursor_row = min(self.size - 1, self.cursor_row + 1);
                self.status = "CURSOR: " + str(self.cursor_row) + "," + str(self.cursor_col);
            return True;
        if event.key == pygame.K_SPACE:
            self.toggle_cursor_pixel();
            return True;
        if event.key in (pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7):
            normal = event.key - pygame.K_0;
            self.select_color(normal + 8 if shift else normal);
            return True;
        if event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS, 43):
            if shift:
                self.scale_resize(1);
            else:
                self.canvas_resize(1);
            return True;
        if event.key in (pygame.K_MINUS, pygame.K_KP_MINUS, 45):
            if shift:
                self.scale_resize(-1);
            else:
                self.canvas_resize(-1);
            return True;
        if event.key == pygame.K_s:
            self.save();
            return True;
        if event.key == pygame.K_l:
            self.load();
            return True;
        if event.key == pygame.K_m:
            self.cycle_mode();
            return True;
        if event.key == pygame.K_e:
            self.edit_selected_color();
            return True;
        if event.key == pygame.K_c:
            self.clear();
            return True;
        return True;

    def draw(self):
        self.screen.fill(BG);
        x=40;
        y=70;
        fntbig=self.font_big.get_height()+self.scale(6)+1;
        fntsml=self.font_small.get_height()+self.scale(5)+1;
        draw_clipped_text(self.screen, self.font_big, "SPECTRUM UDG PAINTER", TEXT, pygame.Rect(self.scale(x), self.scale(y), WIDTH - self.scale(80), fntbig));y+=2*fntbig;
        draw_clipped_text(self.screen, self.font_small, "Arrows cursor. Shift+arrows shift image.", TEXT, pygame.Rect(self.scale(x), self.scale(y), WIDTH - self.scale(80), fntsml));y+=fntsml;
        draw_clipped_text(self.screen, self.font_small, "+/- canvas. Shift+/- scale.", TEXT, pygame.Rect(self.scale(x), self.scale(y), WIDTH - self.scale(80), fntsml));y+=fntsml;
        
        draw_clipped_text(self.screen, self.font_small, "COLOR: " + str(self.selected_color), TEXT, pygame.Rect(self.scale(x), self.scale(y), WIDTH - self.scale(80), fntsml));y+=fntsml;
        draw_clipped_text(self.screen, self.font_small, "FILE: " + os.path.basename(str(self.current_filename)), TEXT, pygame.Rect(self.scale(x), self.scale(y), WIDTH - self.scale(80), fntsml));y+=fntsml;
        self.panel.draw(self.screen);
        self.update_statusbar();

    def run(self):
        running = True;
        while running:
            dt = self.clock.tick(60);
            for event in get_events():
                if event.type == pygame.QUIT:
                    running = False;
                    break;
                if event.type == pygame.KEYDOWN:
                    running = self.handle_key(event);
                    continue;
                self.panel.handle_event(event);
            self.panel.update(dt);
            self.draw();
            pygame.display.flip();
        pygame.quit();


def main():
    app = UDGApp();
    app.run();


if __name__ == "__main__":
    main();


