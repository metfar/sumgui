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

import time;

import pygame;

from sumui import ColorSpec, GraphicsCommand, GraphicsMode, GraphicsProgram, modern_mode;

from .display import fit_window_size;


SPECTRUM_PALETTE = (
    (0, 0, 0), (0, 0, 205), (205, 0, 0), (205, 0, 205),
    (0, 205, 0), (0, 205, 205), (205, 205, 0), (205, 205, 205),
    (0, 0, 0), (0, 0, 255), (255, 0, 0), (255, 0, 255),
    (0, 255, 0), (0, 255, 255), (255, 255, 0), (255, 255, 255),
);


def _rgb(value, default=(255, 255, 255)):
    if value is None:
        return tuple(default);
    if isinstance(value, int):
        # Language frontends may use packed 0xRRGGBB values.
        return ((value >> 16) & 255, (value >> 8) & 255, value & 255);
    color = ColorSpec.from_value(value);
    return color.rgba;


def _spectrum_color(value, bright=False):
    try:
        index = int(value);
    except (TypeError, ValueError):
        return _rgb(value);
    if 0 <= index <= 7:
        index += 8 if bright else 0;
    if 0 <= index < len(SPECTRUM_PALETTE):
        return SPECTRUM_PALETTE[index];
    return _rgb(index);


class GraphicsSurface:
    """Logical pixel surface shared by Sum language frontends.

    ``GraphicsMode`` owns the program-visible coordinate system.  The Pygame
    window may be any physical size; ``present`` applies the selected scaling
    policy without changing program coordinates.
    """;
    def __init__(self, mode=None, background=(0, 0, 0, 255)):
        self.mode = mode if isinstance(mode, GraphicsMode) else (GraphicsMode.from_dict(mode) if mode is not None else modern_mode(640, 480));
        flags = pygame.SRCALPHA if self.mode.pixel_format in ("rgba", "rgba32", "argb32") else 0;
        self.surface = pygame.Surface(self.mode.size, flags);
        self.background = self._profile_color(background, default=(0, 0, 0, 255));
        self.foreground = self._profile_color(7 if self.mode.profile == "spectrum" else (255, 255, 255), default=(255, 255, 255));
        self.border = self.background;
        self.bright = False;
        self.flash = False;
        self.inverse = False;
        self.over = False;
        self.clear();

    @property
    def width(self):
        return self.mode.logical_width;

    @property
    def height(self):
        return self.mode.logical_height;

    @property
    def size(self):
        return self.mode.size;

    def _profile_color(self, value, default=(255, 255, 255)):
        if self.mode.profile == "spectrum" and isinstance(value, int):
            return _spectrum_color(value, self.bright if hasattr(self, "bright") else False);
        return _rgb(value, default);

    def clear(self, color=None):
        self.surface.fill(self._profile_color(self.background if color is None else color, (0, 0, 0, 255)));
        return self;

    def plot(self, x, y, color=None):
        x = int(round(x)); y = int(round(y));
        if 0 <= x < self.width and 0 <= y < self.height:
            self.surface.set_at((x, y), self._profile_color(self.foreground if color is None else color));
        return self;

    def point(self, x, y):
        x = int(round(x)); y = int(round(y));
        if 0 <= x < self.width and 0 <= y < self.height:
            return tuple(self.surface.get_at((x, y)));
        return None;

    def line(self, x1, y1, x2, y2, color=None, width=1):
        pygame.draw.line(self.surface, self._profile_color(self.foreground if color is None else color), (int(round(x1)), int(round(y1))), (int(round(x2)), int(round(y2))), max(1, int(width)));
        return self;

    def rectangle(self, x, y, width, height, color=None, line_width=1, fill=False):
        rect = pygame.Rect(int(round(x)), int(round(y)), int(round(width)), int(round(height)));
        pygame.draw.rect(self.surface, self._profile_color(self.foreground if color is None else color), rect, 0 if fill else max(1, int(line_width)));
        return self;

    def circle(self, x, y, radius, color=None, line_width=1, fill=False):
        pygame.draw.circle(self.surface, self._profile_color(self.foreground if color is None else color), (int(round(x)), int(round(y))), max(0, int(round(radius))), 0 if fill else max(1, int(line_width)));
        return self;

    def text(self, x, y, value, color=None, font=None, size=16, font_name="monospace"):
        if font is None:
            font = pygame.font.SysFont(font_name, max(1, int(size)));
        rendered = font.render(str(value), True, self._profile_color(self.foreground if color is None else color));
        self.surface.blit(rendered, (int(round(x)), int(round(y))));
        return self;

    def blit(self, image, x=0, y=0):
        target = image.surface if isinstance(image, GraphicsSurface) else image;
        self.surface.blit(target, (int(round(x)), int(round(y))));
        return self;

    def set_ink(self, value):
        self.foreground = self._profile_color(value);
        return self;

    def set_paper(self, value):
        self.background = self._profile_color(value, (0, 0, 0));
        return self;

    def set_border(self, value):
        self.border = self._profile_color(value, (0, 0, 0));
        return self;

    def set_bright(self, value):
        enabled = bool(int(value));
        if enabled != self.bright:
            old = self.foreground;
            self.bright = enabled;
            if self.mode.profile == "spectrum":
                try:
                    index = SPECTRUM_PALETTE.index(tuple(old[:3]));
                    self.foreground = _spectrum_color(index % 8, self.bright);
                except ValueError:
                    pass;
        return self;

    def execute(self, command):
        command = command if isinstance(command, GraphicsCommand) else GraphicsCommand.from_dict(command);
        args = tuple(command.arguments);
        options = dict(command.options);
        op = command.operation;
        if op in ("clear", "cls"):
            return self.clear(options.get("color", args[0] if args else None));
        if op in ("plot", "pset", "pixel"):
            return self.plot(args[0], args[1], options.get("color", args[2] if len(args) > 2 else None));
        if op == "line":
            return self.line(args[0], args[1], args[2], args[3], options.get("color", args[4] if len(args) > 4 else None), options.get("width", 1));
        if op in ("rect", "rectangle", "box"):
            return self.rectangle(args[0], args[1], args[2], args[3], options.get("color"), options.get("width", 1), options.get("fill", False));
        if op == "circle":
            return self.circle(args[0], args[1], args[2], options.get("color"), options.get("width", 1), options.get("fill", False));
        if op in ("text", "draw_text"):
            return self.text(args[0], args[1], args[2], options.get("color"), size=options.get("size", 16), font_name=options.get("font_name", "monospace"));
        if op == "ink":
            return self.set_ink(args[0]);
        if op == "paper":
            return self.set_paper(args[0]);
        if op == "border":
            return self.set_border(args[0]);
        if op == "bright":
            return self.set_bright(args[0]);
        if op == "flash":
            self.flash = bool(int(args[0])); return self;
        if op == "inverse":
            self.inverse = bool(int(args[0])); return self;
        if op == "over":
            self.over = bool(int(args[0])); return self;
        raise ValueError("Unsupported graphics operation: {}".format(op));

    def execute_program(self, program):
        program = program if isinstance(program, GraphicsProgram) else GraphicsProgram.from_dict(program);
        if program.mode != self.mode:
            self.mode = program.mode;
            flags = pygame.SRCALPHA if self.mode.pixel_format in ("rgba", "rgba32", "argb32") else 0;
            self.surface = pygame.Surface(self.mode.size, flags);
        if program.background is not None:
            self.background = program.background.rgba;
        self.clear();
        for command in program.commands:
            self.execute(command);
        return self;

    def destination_rect(self, target_size):
        target_width, target_height = int(target_size[0]), int(target_size[1]);
        if self.mode.scaling in ("stretch", "native"):
            if self.mode.scaling == "native":
                width = min(self.width, target_width); height = min(self.height, target_height);
            else:
                width = target_width; height = target_height;
        else:
            scale = min(target_width / float(self.width), target_height / float(self.height));
            if self.mode.scaling == "integer":
                scale = max(1.0, float(int(scale))) if scale >= 1.0 else scale;
            width = max(1, int(round(self.width * scale)));
            height = max(1, int(round(self.height * scale)));
        return pygame.Rect((target_width - width) // 2, (target_height - height) // 2, width, height);

    def present(self, target, smooth=False):
        rect = self.destination_rect(target.get_size());
        if rect.size == self.surface.get_size():
            scaled = self.surface;
        else:
            scaler = pygame.transform.smoothscale if smooth and self.mode.scaling != "integer" else pygame.transform.scale;
            scaled = scaler(self.surface, rect.size);
        target.fill(self.border[:3] if len(self.border) >= 3 else self.border);
        target.blit(scaled, rect.topleft);
        return rect;


class GraphicsWindow:
    """Interactive Pygame renderer for the backend-neutral Sum graphics stream.

    The object is callable, so it can be installed directly as a language
    runtime graphics handler.  ``GraphicsMode`` changes/recreates the logical
    surface and ``GraphicsCommand`` instances are drawn immediately.
    """;
    def __init__(self, title="Sum graphics", window_size=None, fit_display=True, smooth=False):
        self.title = str(title);
        self.window_size = tuple(window_size) if window_size is not None else None;
        self.fit_display = bool(fit_display);
        self.smooth = bool(smooth);
        self.surface = None;
        self.screen = None;
        self.mode = None;
        self.closed = False;
        self.clock = None;

    def _desired_size(self, mode):
        if self.window_size is not None:
            return int(self.window_size[0]), int(self.window_size[1]);
        if mode.profile == "spectrum":
            return mode.logical_width * 3, mode.logical_height * 3;
        return mode.logical_width, mode.logical_height;

    def _open(self, mode):
        if not pygame.get_init():
            pygame.init();
        elif not pygame.display.get_init():
            pygame.display.init();
        try:
            from .display import set_default_icon;
            set_default_icon();
        except (ImportError, AttributeError):
            pass;
        self.mode = mode if isinstance(mode, GraphicsMode) else GraphicsMode.from_dict(mode);
        self.surface = GraphicsSurface(self.mode);
        requested = self._desired_size(self.mode);
        size = fit_window_size(*requested) if self.fit_display and not self.mode.fullscreen else requested;
        flags = pygame.FULLSCREEN if self.mode.fullscreen else (pygame.RESIZABLE if self.mode.resizable else 0);
        self.screen = pygame.display.set_mode((0, 0), flags) if self.mode.fullscreen else pygame.display.set_mode(size, flags);
        pygame.display.set_caption(self.title);
        self.clock = pygame.time.Clock();
        self.closed = False;
        self.present();
        return self;

    def _ensure_open(self):
        if self.surface is None or self.screen is None or self.closed:
            self._open(self.mode or modern_mode(640, 480));
        return self;

    def handle(self, item):
        if isinstance(item, GraphicsMode):
            self._open(item);
            return item;
        command = item if isinstance(item, GraphicsCommand) else GraphicsCommand.from_dict(item);
        if command.operation in ("close", "text_mode"):
            self.close();
            return command;
        self._ensure_open();
        self.surface.execute(command);
        self.poll();
        if not self.closed:
            self.present();
        return command;

    __call__ = handle;

    def present(self):
        if self.surface is None or self.screen is None or self.closed:
            return None;
        rect = self.surface.present(self.screen, smooth=self.smooth);
        pygame.display.flip();
        return rect;

    def poll(self):
        if self.screen is None or self.closed:
            return False;
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.closed = True;
                break;
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.closed = True;
                break;
            if event.type == getattr(pygame, "VIDEORESIZE", -1):
                size = getattr(event, "size", (getattr(event, "w", 1), getattr(event, "h", 1)));
                width = max(1, int(getattr(event, "w", size[0])));
                height = max(1, int(getattr(event, "h", size[1])));
                flags = pygame.RESIZABLE if self.mode is None or self.mode.resizable else 0;
                self.screen = pygame.display.set_mode((width, height), flags);
        if self.closed:
            self.close();
            return False;
        return True;

    def wait_for_close(self, frame_rate=60):
        if self.screen is None or self.closed:
            return 0;
        while not self.closed:
            self.poll();
            if self.closed:
                break;
            self.present();
            if self.clock is not None:
                self.clock.tick(max(1, int(frame_rate)));
            else:
                time.sleep(1.0 / max(1, int(frame_rate)));
        return 0;

    def close(self):
        self.closed = True;
        self.screen = None;
        try:
            if pygame.display.get_init():
                pygame.display.quit();
        except pygame.error:
            pass;
        return None;

    def finish(self, wait=False):
        if self.screen is None:
            return 0;
        if wait and not self.closed:
            return self.wait_for_close();
        self.close();
        return 0;
