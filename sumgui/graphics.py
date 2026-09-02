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

from sumui import ColorSpec, GraphicsCommand, GraphicsMode, GraphicsProgram, modern_mode;


def _rgb(value, default=(255, 255, 255)):
    if value is None:
        return tuple(default);
    if isinstance(value, int):
        # Language frontends may use packed 0xRRGGBB values.
        return ((value >> 16) & 255, (value >> 8) & 255, value & 255);
    color = ColorSpec.from_value(value);
    return color.rgba;


class GraphicsSurface:
    """Logical pixel surface shared by Sum language frontends.

    ``GraphicsMode`` owns the program-visible coordinate system.  The Pygame
    window may be any physical size; ``present`` applies the selected scaling
    policy without changing program coordinates.
    """
    def __init__(self, mode=None, background=(0, 0, 0, 255)):
        self.mode = mode if isinstance(mode, GraphicsMode) else (GraphicsMode.from_dict(mode) if mode is not None else modern_mode(640, 480));
        flags = pygame.SRCALPHA if self.mode.pixel_format in ("rgba", "rgba32", "argb32") else 0;
        self.surface = pygame.Surface(self.mode.size, flags);
        self.background = _rgb(background, (0, 0, 0, 255));
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

    def clear(self, color=None):
        self.surface.fill(_rgb(self.background if color is None else color, (0, 0, 0, 255)));
        return self;

    def plot(self, x, y, color=(255, 255, 255)):
        x = int(round(x)); y = int(round(y));
        if 0 <= x < self.width and 0 <= y < self.height:
            self.surface.set_at((x, y), _rgb(color));
        return self;

    def point(self, x, y):
        x = int(round(x)); y = int(round(y));
        if 0 <= x < self.width and 0 <= y < self.height:
            return tuple(self.surface.get_at((x, y)));
        return None;

    def line(self, x1, y1, x2, y2, color=(255, 255, 255), width=1):
        pygame.draw.line(self.surface, _rgb(color), (int(round(x1)), int(round(y1))), (int(round(x2)), int(round(y2))), max(1, int(width)));
        return self;

    def rectangle(self, x, y, width, height, color=(255, 255, 255), line_width=1, fill=False):
        rect = pygame.Rect(int(round(x)), int(round(y)), int(round(width)), int(round(height)));
        pygame.draw.rect(self.surface, _rgb(color), rect, 0 if fill else max(1, int(line_width)));
        return self;

    def circle(self, x, y, radius, color=(255, 255, 255), line_width=1, fill=False):
        pygame.draw.circle(self.surface, _rgb(color), (int(round(x)), int(round(y))), max(0, int(round(radius))), 0 if fill else max(1, int(line_width)));
        return self;

    def text(self, x, y, value, color=(255, 255, 255), font=None, size=16, font_name="monospace"):
        if font is None:
            font = pygame.font.SysFont(font_name, max(1, int(size)));
        rendered = font.render(str(value), True, _rgb(color));
        self.surface.blit(rendered, (int(round(x)), int(round(y))));
        return self;

    def blit(self, image, x=0, y=0):
        target = image.surface if isinstance(image, GraphicsSurface) else image;
        self.surface.blit(target, (int(round(x)), int(round(y))));
        return self;

    def execute(self, command):
        command = command if isinstance(command, GraphicsCommand) else GraphicsCommand.from_dict(command);
        args = tuple(command.arguments);
        options = dict(command.options);
        op = command.operation;
        if op in ("clear", "cls"):
            return self.clear(options.get("color", args[0] if args else None));
        if op in ("plot", "pset", "pixel"):
            return self.plot(args[0], args[1], options.get("color", args[2] if len(args) > 2 else (255, 255, 255)));
        if op == "line":
            return self.line(args[0], args[1], args[2], args[3], options.get("color", args[4] if len(args) > 4 else (255, 255, 255)), options.get("width", 1));
        if op in ("rect", "rectangle", "box"):
            return self.rectangle(args[0], args[1], args[2], args[3], options.get("color", (255, 255, 255)), options.get("width", 1), options.get("fill", False));
        if op == "circle":
            return self.circle(args[0], args[1], args[2], options.get("color", (255, 255, 255)), options.get("width", 1), options.get("fill", False));
        if op in ("text", "draw_text"):
            return self.text(args[0], args[1], args[2], options.get("color", (255, 255, 255)), size=options.get("size", 16), font_name=options.get("font_name", "monospace"));
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
        target.blit(scaled, rect.topleft);
        return rect;
