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
import math;

import pygame;

from sumui import BASIC16_PALETTE, VGA256_PALETTE, ChartSpec, ColorSpec, FontSpec, GraphicsCommand, GraphicsMode, GraphicsProgram, ImageSpec, TableSpec, indexed_basic_color, modern_mode;

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
        self.font_spec = FontSpec(
            family=str(self.mode.option("font_name", "") or ""),
            size=int(self.mode.option("font_size", 0) or 0),
        );
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
        if isinstance(value, int):
            palette_profile = str(self.mode.option("palette_profile", "") or "").strip().lower();
            if self.mode.profile in ("basic", "qbasic", "gwbasic") or palette_profile == "basic":
                colors = int(self.mode.option("colors", 16) or 16);
                try:
                    return indexed_basic_color(value, colors);
                except ValueError:
                    pass;
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

    def arc(self, x, y, start_angle, end_angle, radius, color=None, line_width=1):
        radius=max(0,int(round(radius)));
        rect=pygame.Rect(int(round(x))-radius,int(round(y))-radius,radius*2,radius*2);
        pygame.draw.arc(self.surface,self._profile_color(self.foreground if color is None else color),rect,math.radians(float(start_angle)),math.radians(float(end_angle)),max(1,int(line_width)));
        return self;

    def ellipse(self, x, y, start_angle, end_angle, rx, ry, color=None, line_width=1, fill=False):
        rx=max(0,int(round(rx))); ry=max(0,int(round(ry)));
        rect=pygame.Rect(int(round(x))-rx,int(round(y))-ry,rx*2,ry*2);
        active=self._profile_color(self.foreground if color is None else color);
        if fill or (float(start_angle)%360==0 and float(end_angle)%360==0):
            pygame.draw.ellipse(self.surface,active,rect,0 if fill else max(1,int(line_width)));
        elif abs(float(end_angle)-float(start_angle)) >= 360:
            pygame.draw.ellipse(self.surface,active,rect,0 if fill else max(1,int(line_width)));
        else:
            pygame.draw.arc(self.surface,active,rect,math.radians(float(start_angle)),math.radians(float(end_angle)),max(1,int(line_width)));
        return self;

    def set_font(self, family=None, size=None, bold=None, italic=None, underline=None):
        current = self.font_spec;
        self.font_spec = FontSpec(
            family=current.family if family is None else str(family),
            size=current.size if size is None else int(size),
            bold=current.bold if bold is None else bool(bold),
            italic=current.italic if italic is None else bool(italic),
            underline=current.underline if underline is None else bool(underline),
        );
        return self;

    def _pygame_font(self, spec=None, default_size=16, theme=None):
        theme = theme or None;
        requested = FontSpec.from_dict(spec) if spec is not None else FontSpec();
        merged = requested.merged(
            self.font_spec,
            default_family=getattr(theme, "font_name", "monospace") if theme is not None else "monospace",
            default_size=default_size,
        );
        font = pygame.font.SysFont(merged.family or "monospace", max(1, int(merged.size or default_size)), bold=merged.bold, italic=merged.italic);
        font.set_underline(merged.underline);
        return font;

    def text(self, x, y, value, color=None, font=None, size=None, font_name=None, direction=0):
        if font is None:
            requested = FontSpec(family=str(font_name or ""), size=int(size or 0));
            font = self._pygame_font(requested, default_size=16);
        rendered = font.render(str(value), True, self._profile_color(self.foreground if color is None else color));
        if int(direction or 0):
            rendered = pygame.transform.rotate(rendered, 90);
        self.surface.blit(rendered, (int(round(x)), int(round(y))));
        return self;

    def blit(self, image, x=0, y=0):
        target = image.surface if isinstance(image, GraphicsSurface) else image;
        self.surface.blit(target, (int(round(x)), int(round(y))));
        return self;

    def _surface_from_image(self, image):
        if isinstance(image, GraphicsSurface):
            return image.surface;
        if isinstance(image, ImageSpec):
            mode = "RGBA" if image.pixel_format in ("rgba", "rgba32", "argb32") else "RGB";
            return pygame.image.fromstring(image.pixels, image.size, mode);
        return image;

    def capture(self, x=0, y=0, width=None, height=None):
        x = int(round(x)); y = int(round(y));
        width = self.width - x if width is None else int(round(width));
        height = self.height - y if height is None else int(round(height));
        rect = pygame.Rect(x, y, max(0, width), max(0, height)).clip(self.surface.get_rect());
        if rect.width <= 0 or rect.height <= 0:
            raise ValueError("capture region is outside the graphics surface");
        region = self.surface.subsurface(rect).copy();
        pixels = pygame.image.tostring(region, "RGBA");
        return ImageSpec(rect.width, rect.height, pixels, "rgba32", (("source_x", rect.x), ("source_y", rect.y)));

    def put(self, x, y, image):
        target = self._surface_from_image(image);
        if target is None:
            raise ValueError("PUT requires an image");
        self.surface.blit(target, (int(round(x)), int(round(y))));
        return self;

    def paint(self, x, y, color=None, border=None):
        x = int(round(x)); y = int(round(y));
        if not (0 <= x < self.width and 0 <= y < self.height):
            return self;
        fill_color = tuple(self._profile_color(self.foreground if color is None else color))[:4];
        target_color = tuple(self.surface.get_at((x, y)));
        border_color = None if border is None else tuple(self._profile_color(border))[:4];
        if border_color is None and target_color[:len(fill_color)] == fill_color[:len(target_color)]:
            return self;
        pending = [(x, y)];
        visited = set();
        while pending:
            px, py = pending.pop();
            if (px, py) in visited or px < 0 or py < 0 or px >= self.width or py >= self.height:
                continue;
            visited.add((px, py));
            current = tuple(self.surface.get_at((px, py)));
            if border_color is not None:
                if current[:3] == border_color[:3] or current[:3] == fill_color[:3]:
                    continue;
            elif current != target_color:
                continue;
            self.surface.set_at((px, py), fill_color);
            pending.append((px + 1, py));
            pending.append((px - 1, py));
            pending.append((px, py + 1));
            pending.append((px, py - 1));
        return self;

    def set_color(self, foreground=None, background=None, border=None):
        if foreground is not None:
            self.set_ink(foreground);
        if background is not None:
            self.set_paper(background);
        if border is not None:
            self.set_border(border);
        return self;

    def save_image(self, filename, image=None):
        target = self.surface if image is None else self._surface_from_image(image);
        pygame.image.save(target, str(filename));
        return str(filename);

    @staticmethod
    def load_image(filename):
        loaded = pygame.image.load(str(filename));
        if pygame.display.get_init() and pygame.display.get_surface() is not None:
            loaded = loaded.convert_alpha();
        pixels = pygame.image.tostring(loaded, "RGBA");
        return ImageSpec(loaded.get_width(), loaded.get_height(), pixels, "rgba32", (("filename", str(filename)),));

    def draw_chart(self, x, y, width, height, spec, theme=None):
        from .charts import ChartView;
        from .theme import DEFAULT_THEME;
        if not pygame.font.get_init():
            pygame.font.init();
        chart_spec = spec if isinstance(spec, ChartSpec) else ChartSpec.from_dict(spec);
        active_theme = theme or DEFAULT_THEME;
        renderer = str(chart_spec.option("renderer", "native") or "native").strip().lower();
        if renderer in ("matplotlib", "mpl", "seaborn", "sns"):
            from .chart_backends import render_chart_rgba;
            backend = "seaborn" if renderer in ("seaborn", "sns") else "matplotlib";
            rendered_width, rendered_height, rgba = render_chart_rgba(chart_spec, int(width), int(height), active_theme, renderer=backend);
            image = pygame.image.fromstring(rgba, (rendered_width, rendered_height), "RGBA");
            self.surface.blit(image, (int(x), int(y)));
            return self;
        automatic_size = max(9, min(18, int(height) // 14 if int(height) > 0 else 12));
        base_spec = chart_spec.font.merged(self.font_spec, default_family=active_theme.font_name, default_size=automatic_size);
        base_font = self._pygame_font(base_spec, default_size=automatic_size, theme=active_theme);
        fonts = {
            "title": self._pygame_font(chart_spec.title_font.merged(base_spec, default_size=max(1, base_spec.size + 2)), default_size=max(1, base_spec.size + 2), theme=active_theme),
            "axis": self._pygame_font(chart_spec.axis_font.merged(base_spec), default_size=base_spec.size, theme=active_theme),
            "tick": self._pygame_font(chart_spec.tick_font.merged(base_spec, default_size=max(1, base_spec.size - 1)), default_size=max(1, base_spec.size - 1), theme=active_theme),
            "legend": self._pygame_font(chart_spec.legend_font.merged(base_spec, default_size=max(1, base_spec.size - 1)), default_size=max(1, base_spec.size - 1), theme=active_theme),
        };
        ChartView(
            pygame.Rect(int(x), int(y), max(1, int(width)), max(1, int(height))),
            chart_spec, base_font, theme=active_theme, fonts=fonts,
        ).draw(self.surface);
        return self;

    def draw_table(self, x, y, width, height, spec, theme=None):
        from .tables import TableView;
        from .theme import DEFAULT_THEME;
        if not pygame.font.get_init():
            pygame.font.init();
        table_spec = spec if isinstance(spec, TableSpec) else TableSpec.from_dict(spec);
        active_theme = theme or DEFAULT_THEME;
        automatic_size = max(9, min(18, int(height) // max(8, len(table_spec.rows) + 3)));
        base_spec = table_spec.font.merged(self.font_spec, default_family=active_theme.font_name, default_size=automatic_size);
        base_font = self._pygame_font(base_spec, default_size=automatic_size, theme=active_theme);
        fonts = {
            "title": self._pygame_font(table_spec.title_font.merged(base_spec, default_size=max(1, base_spec.size + 2)), default_size=max(1, base_spec.size + 2), theme=active_theme),
            "header": self._pygame_font(table_spec.header_font.merged(base_spec, default_size=base_spec.size), default_size=base_spec.size, theme=active_theme),
        };
        TableView(
            pygame.Rect(int(x), int(y), max(1, int(width)), max(1, int(height))),
            table_spec, base_font, theme=active_theme, fonts=fonts,
        ).draw(self.surface);
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
        if op == "arc":
            return self.arc(args[0], args[1], args[2], args[3], args[4], options.get("color"), options.get("width", 1));
        if op == "ellipse":
            return self.ellipse(args[0], args[1], args[2], args[3], args[4], args[5], options.get("color"), options.get("width", 1), options.get("fill", False));
        if op in ("text", "draw_text"):
            return self.text(args[0], args[1], args[2], options.get("color"), size=options.get("size", 16), font_name=options.get("font_name", "monospace"), direction=options.get("direction", 0));
        if op == "setfont":
            return self.set_font(options.get("family", args[0] if args else None), options.get("size", args[1] if len(args)>1 else None), options.get("bold"), options.get("italic"), options.get("underline"));
        if op == "setfillstyle":
            return self;
        if op in ("paint", "fill"):
            return self.paint(args[0], args[1], options.get("color", args[2] if len(args) > 2 else None), options.get("border", args[3] if len(args) > 3 else None));
        if op == "color":
            return self.set_color(args[0] if len(args) > 0 else None, args[1] if len(args) > 1 else None, args[2] if len(args) > 2 else None);
        if op in ("put", "blit_image"):
            return self.put(args[0], args[1], args[2]);
        if op == "chart":
            return self.draw_chart(args[0], args[1], args[2], args[3], args[4], theme=options.get("theme"));
        if op == "table":
            return self.draw_table(args[0], args[1], args[2], args[3], args[4], theme=options.get("theme"));
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
    """Interactive renderer for Sum graphics, including page buffering.

    Drawing commands update the physical display immediately in AUTO mode when
    the active page is also visible.  MANUAL mode accumulates changes until an
    explicit ``update`` command.  Active and visible pages remain independent,
    matching classic BASIC page-flipping semantics.
    """;
    def __init__(self, title="Sum graphics", window_size=None, fit_display=True, smooth=False):
        self.title=str(title); self.window_size=tuple(window_size) if window_size is not None else None; self.fit_display=bool(fit_display); self.smooth=bool(smooth);
        self.surface=None; self.pages=[]; self.screen=None; self.mode=None; self.closed=False; self.clock=None;
        self.active_page=0; self.visible_page=0; self.auto_update=True;

    def _desired_size(self, mode):
        if self.window_size is not None: return int(self.window_size[0]),int(self.window_size[1]);
        if mode.profile=="spectrum": return mode.logical_width*3,mode.logical_height*3;
        return mode.logical_width,mode.logical_height;

    def _select_active(self):
        if self.pages: self.surface=self.pages[self.active_page];
        return self.surface;

    def _open(self, mode):
        if not pygame.get_init(): pygame.init();
        elif not pygame.display.get_init(): pygame.display.init();
        try:
            from .display import set_default_icon; set_default_icon();
        except (ImportError,AttributeError): pass;
        self.mode=mode if isinstance(mode,GraphicsMode) else GraphicsMode.from_dict(mode);
        page_count=max(1,int(self.mode.option("pages",1) or 1));
        self.active_page=max(0,min(page_count-1,int(self.mode.option("active_page",0) or 0)));
        self.visible_page=max(0,min(page_count-1,int(self.mode.option("visible_page",0) or 0)));
        self.auto_update=str(self.mode.option("refresh","auto") or "auto").lower()!="manual";
        self.pages=[GraphicsSurface(self.mode) for _ in range(page_count)]; self._select_active();
        requested=self._desired_size(self.mode); size=fit_window_size(*requested) if self.fit_display and not self.mode.fullscreen else requested;
        flags=pygame.FULLSCREEN if self.mode.fullscreen else (pygame.RESIZABLE if self.mode.resizable else 0);
        self.screen=pygame.display.set_mode((0,0),flags) if self.mode.fullscreen else pygame.display.set_mode(size,flags);
        pygame.display.set_caption(self.title); self.clock=pygame.time.Clock(); self.closed=False; self.present(); return self;

    def _ensure_open(self):
        if self.surface is None or self.screen is None or self.closed: self._open(self.mode or modern_mode(640,480));
        return self;

    def set_active_page(self,index):
        index=int(index);
        if index<0 or index>=len(self.pages): raise ValueError("active graphics page is out of range");
        self.active_page=index; self._select_active(); return index;

    def set_visible_page(self,index):
        index=int(index);
        if index<0 or index>=len(self.pages): raise ValueError("visible graphics page is out of range");
        self.visible_page=index; self.present(); return index;

    def copy_page(self,source,destination):
        source=int(source); destination=int(destination);
        if source<0 or source>=len(self.pages) or destination<0 or destination>=len(self.pages): raise ValueError("graphics page is out of range");
        self.pages[destination].surface.blit(self.pages[source].surface,(0,0));
        if self.auto_update and destination==self.visible_page: self.present();
        return destination;

    def handle(self,item):
        if isinstance(item,GraphicsMode): self._open(item); return item;
        command=item if isinstance(item,GraphicsCommand) else GraphicsCommand.from_dict(item); op=command.operation; args=tuple(command.arguments); options=dict(command.options);
        if op in ("close","text_mode"): self.close(); return command;
        self._ensure_open();
        if op=="capture": return self.surface.capture(*(args or (0,0,self.surface.width,self.surface.height)));
        if op=="save_image": return self.surface.save_image(args[0],image=args[1] if len(args)>1 else None);
        if op=="load_image": return self.surface.load_image(args[0]);
        if op=="getpixel": return self.surface.point(args[0],args[1]);
        if op in ("active_page","set_active_page"): self.set_active_page(args[0]); return command;
        if op in ("visible_page","set_visible_page"): self.set_visible_page(args[0]); return command;
        if op in ("copy_page","copy_screen"): self.copy_page(args[0],args[1]); return command;
        if op in ("update","refresh","redraw"): self.present(); return command;
        if op=="refresh_mode": self.auto_update=str(args[0]).lower()!="manual"; return command;
        self.surface.execute(command); self.poll();
        if not self.closed and self.auto_update and self.active_page==self.visible_page: self.present();
        return command;

    __call__=handle;

    def present(self):
        if not self.pages or self.screen is None or self.closed: return None;
        pump = getattr(pygame.event, "pump", None);
        if pump is not None:
            pump();
        visible=self.pages[self.visible_page]; rect=visible.present(self.screen,smooth=self.smooth); pygame.display.flip(); return rect;

    def poll(self):
        if self.screen is None or self.closed: return False;
        resized=False;
        resize_types=(getattr(pygame,"VIDEORESIZE",-1),getattr(pygame,"WINDOWRESIZED",-2),getattr(pygame,"WINDOWSIZECHANGED",-3));
        for event in pygame.event.get():
            if event.type==pygame.QUIT: self.closed=True; break;
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE: self.closed=True; break;
            if event.type in resize_types:
                size=getattr(event,"size",(getattr(event,"w",1),getattr(event,"h",1))); width=max(1,int(getattr(event,"w",size[0]))); height=max(1,int(getattr(event,"h",size[1]))); flags=pygame.RESIZABLE if self.mode is None or self.mode.resizable else 0; self.screen=pygame.display.set_mode((width,height),flags); resized=True;
        if self.closed: self.close(); return False;
        if resized:
            self.present();
        return True;

    def service(self, seconds=0.0, frame_rate=60):
        if self.screen is None or self.closed:
            return False;
        duration=max(0.0,float(seconds));
        deadline=time.monotonic()+duration;
        while True:
            if not self.poll():
                return True;
            self.present();
            if duration <= 0.0 or time.monotonic() >= deadline:
                break;
            if self.clock is not None:
                self.clock.tick(max(1,int(frame_rate)));
            else:
                time.sleep(min(1.0/max(1,int(frame_rate)),max(0.0,deadline-time.monotonic())));
        return True;

    def pause(self, seconds=0.0, frame_rate=60):
        """Wait until timeout or any keyboard, mouse or touch press.

        ``seconds == 0`` waits indefinitely. The display remains responsive,
        resize events are honored and the visible page is continuously
        presented. Returns True when input/close interrupted the wait and
        False when a finite timeout elapsed.
        """;
        if self.screen is None or self.closed:
            return True;
        duration=max(0.0,float(seconds));
        deadline=None if duration==0.0 else time.monotonic()+duration;
        resize_types=(getattr(pygame,"VIDEORESIZE",-1),getattr(pygame,"WINDOWRESIZED",-2),getattr(pygame,"WINDOWSIZECHANGED",-3));
        input_types=(getattr(pygame,"KEYDOWN",-10),getattr(pygame,"MOUSEBUTTONDOWN",-11),getattr(pygame,"FINGERDOWN",-12));
        while not self.closed:
            resized=False;
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    self.closed=True;
                    self.close();
                    return True;
                if event.type in input_types:
                    self.present();
                    return True;
                if event.type in resize_types:
                    size=getattr(event,"size",(getattr(event,"w",1),getattr(event,"h",1)));
                    width=max(1,int(getattr(event,"w",size[0])));
                    height=max(1,int(getattr(event,"h",size[1])));
                    flags=pygame.RESIZABLE if self.mode is None or self.mode.resizable else 0;
                    self.screen=pygame.display.set_mode((width,height),flags);
                    resized=True;
            if resized or not self.closed:
                self.present();
            if deadline is not None and time.monotonic()>=deadline:
                return False;
            if self.clock is not None:
                self.clock.tick(max(1,int(frame_rate)));
            else:
                time.sleep(1.0/max(1,int(frame_rate)));
        return True;

    def wait_for_close(self,frame_rate=60):
        if self.screen is None or self.closed: return 0;
        while not self.closed:
            self.poll();
            if self.closed: break;
            self.present();
            if self.clock is not None: self.clock.tick(max(1,int(frame_rate)));
            else: time.sleep(1.0/max(1,int(frame_rate)));
        return 0;

    def close(self):
        self.closed=True; self.screen=None;
        try:
            if pygame.display.get_init(): pygame.display.quit();
        except pygame.error: pass;
        return None;

    def finish(self,wait=False):
        if self.screen is None: return 0;
        if wait and not self.closed: return self.wait_for_close();
        self.close(); return 0;
