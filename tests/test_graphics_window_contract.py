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

import importlib.util;
from pathlib import Path;
import sys;
import types;

from sumui import GraphicsCommand, basic_mode, spectrum_mode;


class FakeRect:
    def __init__(self, *args):
        if len(args) == 1:
            args = tuple(args[0]);
        self.x, self.y, self.width, self.height = [int(value) for value in args];

    @property
    def size(self):
        return (self.width, self.height);

    @property
    def topleft(self):
        return (self.x, self.y);


class FakeSurface:
    def __init__(self, size, flags=0):
        self._size = (int(size[0]), int(size[1]));
        self.flags = flags;
        self.pixels = {};
        self.fill_color = None;
        self.blits = [];

    def get_size(self):
        return self._size;

    def fill(self, color):
        self.fill_color = tuple(color);

    def set_at(self, position, color):
        self.pixels[tuple(position)] = tuple(color);

    def get_at(self, position):
        return self.pixels.get(tuple(position), self.fill_color or (0, 0, 0, 255));

    def blit(self, image, position):
        self.blits.append((image, tuple(position)));


class FakeClock:
    def tick(self, unused_rate):
        return 0;


class FakeFont:
    def __init__(self, size):
        self.size = int(size);

    def render(self, text, unused_antialias, unused_color):
        return FakeSurface((max(1, len(str(text))) * max(1, self.size // 2), max(1, self.size)));


def _pygame_stub():
    pygame = types.ModuleType("pygame");
    pygame.SRCALPHA = 1;
    pygame.FULLSCREEN = 2;
    pygame.RESIZABLE = 4;
    pygame.QUIT = 10;
    pygame.KEYDOWN = 11;
    pygame.K_ESCAPE = 27;
    pygame.VIDEORESIZE = 12;
    pygame.error = RuntimeError;
    pygame.Rect = FakeRect;
    pygame.Surface = FakeSurface;
    pygame.get_init = lambda: True;
    pygame.init = lambda: None;
    pygame.draw = types.SimpleNamespace(
        line=lambda *args, **kwargs: None,
        rect=lambda *args, **kwargs: None,
        circle=lambda *args, **kwargs: None,
    );
    pygame.transform = types.SimpleNamespace(
        scale=lambda unused_surface, size: FakeSurface(size),
        smoothscale=lambda unused_surface, size: FakeSurface(size),
    );
    pygame.font = types.SimpleNamespace(SysFont=lambda unused_name, size: FakeFont(size));
    pygame.event = types.SimpleNamespace(get=lambda: []);
    pygame.time = types.SimpleNamespace(Clock=FakeClock);
    display_state = {"surface": None, "caption": None, "quit": False};

    def set_mode(size, unused_flags=0):
        display_state["surface"] = FakeSurface(size);
        return display_state["surface"];

    pygame.display = types.SimpleNamespace(
        get_init=lambda: True,
        init=lambda: None,
        set_mode=set_mode,
        set_caption=lambda title: display_state.__setitem__("caption", title),
        flip=lambda: None,
        quit=lambda: display_state.__setitem__("quit", True),
    );
    pygame._display_state = display_state;
    return pygame;


def _load_graphics(monkeypatch):
    pygame = _pygame_stub();
    monkeypatch.setitem(sys.modules, "pygame", pygame);
    package = types.ModuleType("sumgui_contract_test");
    package.__path__ = [str(Path(__file__).resolve().parents[1] / "sumgui")];
    monkeypatch.setitem(sys.modules, "sumgui_contract_test", package);
    display = types.ModuleType("sumgui_contract_test.display");
    display.fit_window_size = lambda width, height: (int(width), int(height));
    monkeypatch.setitem(sys.modules, "sumgui_contract_test.display", display);
    path = Path(__file__).resolve().parents[1] / "sumgui" / "graphics.py";
    spec = importlib.util.spec_from_file_location("sumgui_contract_test.graphics", path);
    module = importlib.util.module_from_spec(spec);
    monkeypatch.setitem(sys.modules, "sumgui_contract_test.graphics", module);
    spec.loader.exec_module(module);
    return module, pygame;


def test_graphics_window_consumes_shared_basic_stream(monkeypatch):
    module, pygame = _load_graphics(monkeypatch);
    window = module.GraphicsWindow(title="BASIC graphics");
    mode = spectrum_mode();
    window.handle(mode);
    assert window.surface.size == (256, 192);
    assert window.screen.get_size() == (768, 576);
    assert pygame._display_state["caption"] == "BASIC graphics";
    window.handle(GraphicsCommand("ink", (6,)));
    window.handle(GraphicsCommand("plot", (10, 20)));
    assert window.surface.point(10, 20)[:3] == module.SPECTRUM_PALETTE[6];
    window.handle(GraphicsCommand("close"));
    assert window.closed is True;
    assert pygame._display_state["quit"] is True;


def test_basic_mode_uses_qbasic_gwbasic_16_color_palette(monkeypatch):
    module, unused_pygame = _load_graphics(monkeypatch);
    surface = module.GraphicsSurface(basic_mode(4, 4));
    surface.set_ink(14);
    surface.plot(1, 1);
    assert surface.point(1, 1)[:3] == module.BASIC16_PALETTE[14];


def test_graphics_window_supports_manual_refresh_and_active_visible_pages(monkeypatch):
    from sumui import GraphicsCommand, display_mode;
    module, unused_pygame = _load_graphics(monkeypatch);
    window = module.GraphicsWindow(title="Pages");
    window.handle(display_mode(320, 240, 256, refresh="manual", pages=3, active_page=1, visible_page=0));
    assert len(window.pages) == 3;
    assert window.active_page == 1;
    assert window.visible_page == 0;
    assert window.auto_update is False;
    window.handle(GraphicsCommand("active_page", (2,)));
    assert window.surface is window.pages[2];
    window.handle(GraphicsCommand("copy_page", (2, 1)));
    window.handle(GraphicsCommand("visible_page", (1,)));
    assert window.visible_page == 1;
    window.handle(GraphicsCommand("refresh_mode", ("auto",)));
    assert window.auto_update is True;


def test_r17_python_compatibility_examples_and_font_sizes_are_packaged():
    root = Path(__file__).resolve().parents[1];
    assert (root / "sumgui" / "bgi.py").exists();
    assert (root / "sumgui" / "conio.py").exists();
    assert (root / "examples" / "demo_bgi_compat.py").exists();
    assert (root / "examples" / "demo_conio_compat.py").exists();
    source = (root / "examples" / "demo_report_dashboard.py").read_text(encoding="utf-8");
    assert "FontSpec(size=10)" in source;
    assert "FontSpec(size=12, bold=True)" in source;
    assert "FontSpec(size=9)" in source;
