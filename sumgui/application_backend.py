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

"""Graphical renderer for an existing SumTUI application tree.

This is the convergence backend: the application is created exactly once and
keeps its existing widgets, commands, focus model, dialogs, keyboard handling,
mouse handling and syntax highlighter.  SumGUI only changes the presentation
surface and translates Pygame input to the application's normal Sum events.

Native pixel widgets can progressively replace individual renderers later
without creating a second application implementation.
""";


def _load_runtime():
    try:
        import pygame;
        from rich.cells import get_character_cell_size;
        from rich.console import Console, ConsoleDimensions;
        from sumtui.events import Key, KeyEvent, MouseEvent, ResizeEvent;
    except (ImportError, ModuleNotFoundError) as exc:
        raise RuntimeError("The graphical Sum application backend requires pygame, rich and sumTUI") from exc;
    return pygame, get_character_cell_size, Console, ConsoleDimensions, Key, KeyEvent, MouseEvent, ResizeEvent;


def _triplet(color, fallback):
    if color is None:
        return tuple(fallback);
    try:
        value = color.get_truecolor();
        return (int(value.red), int(value.green), int(value.blue));
    except Exception:
        return tuple(fallback);


def style_colors(style, default_fg, default_bg):
    """Return renderer-friendly foreground/background RGB values.""";
    foreground = _triplet(getattr(style, "color", None), default_fg);
    background = _triplet(getattr(style, "bgcolor", None), default_bg);
    if bool(getattr(style, "reverse", False)):
        foreground, background = background, foreground;
    return foreground, background;


def _key_map(pygame, Key):
    names = {
        "K_ESCAPE": Key.ESCAPE, "K_RETURN": Key.ENTER, "K_KP_ENTER": Key.ENTER,
        "K_BACKSPACE": Key.BACKSPACE, "K_DELETE": Key.DELETE, "K_INSERT": Key.INSERT,
        "K_TAB": Key.TAB, "K_SPACE": Key.SPACE, "K_UP": Key.UP, "K_DOWN": Key.DOWN,
        "K_LEFT": Key.LEFT, "K_RIGHT": Key.RIGHT, "K_HOME": Key.HOME, "K_END": Key.END,
        "K_PAGEUP": Key.PAGE_UP, "K_PAGEDOWN": Key.PAGE_DOWN,
    };
    for index in range(1, 13):
        names["K_F{}".format(index)] = getattr(Key, "F{}".format(index));
    return {getattr(pygame, source): target for source, target in names.items() if hasattr(pygame, source)};


def pygame_key_to_sum(event, pygame, Key, KeyEvent):
    """Translate a Pygame KEYDOWN to the application's normal key event.

    Printable text without Ctrl/Alt is intentionally left to TEXTINPUT so
    international keyboards and composed Unicode input keep working.
    """;
    modifiers = int(getattr(event, "mod", pygame.key.get_mods()) or 0);
    ctrl = bool(modifiers & getattr(pygame, "KMOD_CTRL", 0));
    alt = bool(modifiers & getattr(pygame, "KMOD_ALT", 0));
    shift = bool(modifiers & getattr(pygame, "KMOD_SHIFT", 0));
    mapping = _key_map(pygame, Key);
    key = mapping.get(getattr(event, "key", None));
    if key is not None:
        # Printable characters are inserted exclusively through TEXTINPUT.
        # SPACE must still be represented as a logical key so buttons and
        # checkboxes can react to it, but attaching text here would cause
        # editors to insert one space for KEYDOWN and another for TEXTINPUT.
        return KeyEvent(key, text="", ctrl=ctrl, alt=alt, shift=shift);
    if not (ctrl or alt):
        return None;
    try:
        name = str(pygame.key.name(event.key) or "").lower();
    except Exception:
        name = "";
    if len(name) == 1:
        return KeyEvent(name, ctrl=ctrl, alt=alt, shift=shift);
    return None;


class GraphicalApplicationBackend:
    """Render a live Sum application tree to a Pygame window as styled cells.""";
    def __init__(self, application, title=None, font_name="monospace", font_size=18,
                 initial_columns=120, initial_rows=38, fps=60):
        runtime = _load_runtime();
        (self.pygame, self.get_character_cell_size, self.Console, self.ConsoleDimensions,
         self.Key, self.KeyEvent, self.MouseEvent, self.ResizeEvent) = runtime;
        self.application = application;
        self.title = str(title or getattr(application, "title", "Sum application"));
        self.font_name = str(font_name or "monospace");
        self.font_size = max(8, int(font_size));
        self.initial_columns = max(40, int(initial_columns));
        self.initial_rows = max(12, int(initial_rows));
        self.fps = max(10, int(fps));
        self.screen = None;
        self.clock = None;
        self.fonts = {};
        self.cell_width = 1;
        self.cell_height = 1;
        self.columns = self.initial_columns;
        self.rows = self.initial_rows;
        self.render_console = None;
        self._left_down = False;
        self._redraw_requested = True;

    def request_redraw(self):
        self._redraw_requested = True;
        return True;

    def save_png(self, filename):
        if self.screen is None:
            raise RuntimeError("graphical application window is not active");
        self._draw();
        self.pygame.image.save(self.screen, str(filename));
        return str(filename);

    def _make_fonts(self):
        pygame = self.pygame;
        self.fonts = {
            (False, False): pygame.font.SysFont(self.font_name, self.font_size, bold=False, italic=False),
            (True, False): pygame.font.SysFont(self.font_name, self.font_size, bold=True, italic=False),
            (False, True): pygame.font.SysFont(self.font_name, self.font_size, bold=False, italic=True),
            (True, True): pygame.font.SysFont(self.font_name, self.font_size, bold=True, italic=True),
        };
        normal = self.fonts[(False, False)];
        self.cell_width = max(1, int(normal.size("M")[0]));
        self.cell_height = max(1, int(normal.get_linesize()));
        return normal;

    def _update_grid(self, width, height, notify=True):
        self.columns = max(20, int(width) // self.cell_width);
        self.rows = max(8, int(height) // self.cell_height);
        self.render_console = self.Console(
            width=self.columns, height=self.rows, color_system="truecolor",
            force_terminal=True, legacy_windows=False, soft_wrap=False,
        );
        self.application.last_size = self.ConsoleDimensions(self.columns, self.rows);
        if notify:
            self.application.dispatch(self.ResizeEvent(self.columns, self.rows));
        return (self.columns, self.rows);

    def _render_lines(self):
        options = self.render_console.options.update(width=self.columns, height=self.rows);
        return self.render_console.render_lines(
            self.application._renderable(), options=options, pad=True, new_lines=False,
        );

    def _draw(self):
        pygame = self.pygame;
        theme = getattr(self.application, "theme", None);
        default_fg = tuple(getattr(theme, "text", (235, 245, 250)));
        default_bg = tuple(getattr(theme, "bg", (0, 0, 0)));
        self.screen.fill(default_bg);
        lines = self._render_lines();
        for row, segments in enumerate(lines[:self.rows]):
            column = 0;
            for segment in segments:
                if getattr(segment, "control", None):
                    continue;
                text = str(getattr(segment, "text", ""));
                style = getattr(segment, "style", None);
                foreground, background = style_colors(style, default_fg, default_bg);
                bold = bool(getattr(style, "bold", False));
                italic = bool(getattr(style, "italic", False));
                underline = bool(getattr(style, "underline", False));
                strike = bool(getattr(style, "strike", False));
                font = self.fonts[(bold, italic)];
                for char in text:
                    cells = max(0, int(self.get_character_cell_size(char)));
                    if cells <= 0:
                        continue;
                    if column >= self.columns:
                        break;
                    width = max(1, cells * self.cell_width);
                    rect = pygame.Rect(column * self.cell_width, row * self.cell_height, width, self.cell_height);
                    pygame.draw.rect(self.screen, background, rect);
                    if char != " ":
                        rendered = font.render(char, True, foreground);
                        self.screen.blit(rendered, (rect.x, rect.y));
                    if underline:
                        pygame.draw.line(self.screen, foreground, (rect.x, rect.bottom - 2), (rect.right - 1, rect.bottom - 2), 1);
                    if strike:
                        pygame.draw.line(self.screen, foreground, (rect.x, rect.centery), (rect.right - 1, rect.centery), 1);
                    column += cells;
                if column >= self.columns:
                    break;
        pygame.display.flip();
        return True;

    def _mouse_event(self, event):
        pygame = self.pygame;
        modifiers = pygame.key.get_mods();
        ctrl = bool(modifiers & getattr(pygame, "KMOD_CTRL", 0));
        alt = bool(modifiers & getattr(pygame, "KMOD_ALT", 0));
        shift = bool(modifiers & getattr(pygame, "KMOD_SHIFT", 0));
        pos = getattr(event, "pos", (0, 0));
        x = max(0, int(pos[0]) // self.cell_width);
        y = max(0, int(pos[1]) // self.cell_height);
        if event.type == pygame.MOUSEBUTTONDOWN:
            button_number = int(getattr(event, "button", 1));
            if button_number in (4, 5):
                return self.MouseEvent(x, y, button="wheel", action="scroll_up" if button_number == 4 else "scroll_down", ctrl=ctrl, alt=alt, shift=shift);
            button = {1: "left", 2: "middle", 3: "right"}.get(button_number, "none");
            if button == "left":
                self._left_down = True;
            return self.MouseEvent(x, y, button=button, action="press", ctrl=ctrl, alt=alt, shift=shift);
        if event.type == pygame.MOUSEBUTTONUP:
            button = {1: "left", 2: "middle", 3: "right"}.get(int(getattr(event, "button", 1)), "none");
            if button == "left":
                self._left_down = False;
            return self.MouseEvent(x, y, button=button, action="release", ctrl=ctrl, alt=alt, shift=shift);
        if event.type == pygame.MOUSEMOTION:
            buttons = getattr(event, "buttons", (0, 0, 0));
            left = bool(buttons and buttons[0]) or self._left_down;
            return self.MouseEvent(x, y, button="left" if left else "none", action="move", ctrl=ctrl, alt=alt, shift=shift);
        return None;

    def _dispatch_pygame(self, event):
        pygame = self.pygame;
        finger_types = (
            getattr(pygame, "FINGERDOWN", -101),
            getattr(pygame, "FINGERMOTION", -102),
            getattr(pygame, "FINGERUP", -103),
        );
        if event.type in finger_types:
            from .eventbridge import touch_to_mouse_event;
            compatibility_event = touch_to_mouse_event(event, self.screen.get_size());
            translated = self._mouse_event(compatibility_event);
            return bool(translated is not None and self.application.dispatch(translated));
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION) and bool(getattr(event, "touch", False)):
            # Pygame may synthesize a touch=True mouse event in addition to
            # the native FINGER event.  Native touch is the source of truth
            # so one physical gesture becomes one logical Sum pointer event.
            return False;
        if event.type == pygame.QUIT:
            self.application.stop();
            return True;
        resize_types = (
            getattr(pygame, "VIDEORESIZE", -1),
            getattr(pygame, "WINDOWRESIZED", -2),
            getattr(pygame, "WINDOWSIZECHANGED", -3),
        );
        if event.type in resize_types:
            width = max(self.cell_width * 20, int(getattr(event, "w", getattr(event, "x", self.screen.get_width()))));
            height = max(self.cell_height * 8, int(getattr(event, "h", getattr(event, "y", self.screen.get_height()))));
            if event.type == getattr(pygame, "VIDEORESIZE", -1):
                self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE);
            self._update_grid(width, height, notify=True);
            return True;
        if event.type == getattr(pygame, "WINDOWFOCUSLOST", -1):
            self._left_down = False;
            return False;
        if event.type == pygame.KEYDOWN:
            translated = pygame_key_to_sum(event, pygame, self.Key, self.KeyEvent);
            return bool(translated is not None and self.application.dispatch(translated));
        if event.type == pygame.TEXTINPUT:
            dirty = False;
            for char in str(getattr(event, "text", "")):
                dirty = self.application.dispatch(self.KeyEvent(char.lower(), text=char)) or dirty;
            return dirty;
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            translated = self._mouse_event(event);
            return bool(translated is not None and self.application.dispatch(translated));
        if event.type == getattr(pygame, "MOUSEWHEEL", -1):
            pos = pygame.mouse.get_pos();
            x = max(0, int(pos[0]) // self.cell_width);
            y = max(0, int(pos[1]) // self.cell_height);
            amount = int(getattr(event, "y", 0));
            dirty = False;
            action = "scroll_up" if amount > 0 else "scroll_down";
            for _unused in range(abs(amount)):
                dirty = self.application.dispatch(self.MouseEvent(x, y, button="wheel", action=action)) or dirty;
            return dirty;
        return False;

    def run(self):
        pygame = self.pygame;
        if getattr(self.application, "root", None) is None:
            raise RuntimeError("Application has no root widget");
        pygame.init();
        try:
            self._make_fonts();
            width = self.initial_columns * self.cell_width;
            height = self.initial_rows * self.cell_height;
            try:
                from .display import fit_window_size, set_default_icon;
                width, height = fit_window_size(width, height);
                set_default_icon();
            except Exception:
                pass;
            self.screen = pygame.display.set_mode((int(width), int(height)), pygame.RESIZABLE);
            pygame.display.set_caption(self.title);
            pygame.key.set_repeat(250, 31);
            pygame.key.start_text_input();
            self.clock = pygame.time.Clock();
            self._update_grid(*self.screen.get_size(), notify=True);
            self.application.running = True;
            self.application._run_thread_ident = __import__("threading").get_ident();
            self.application._active_gui_backend = self;
            dirty = True;
            while self.application.running:
                self.clock.tick(self.fps);
                dirty = self.application._process_external_requests() or dirty;
                for event in pygame.event.get():
                    dirty = self._dispatch_pygame(event) or dirty;
                for callback in list(self.application._idle_callbacks):
                    try:
                        dirty = bool(callback()) or dirty;
                    except Exception:
                        self.application.remove_idle(callback);
                        raise;
                dirty = self._redraw_requested or dirty;
                if dirty:
                    self._draw();
                    dirty = False;
                    self._redraw_requested = False;
            return 0;
        finally:
            self.application._active_gui_backend = None;
            self.application._run_thread_ident = None;
            try:
                pygame.key.stop_text_input();
            except Exception:
                pass;
            pygame.quit();


def run_application(application, **kwargs):
    return GraphicalApplicationBackend(application, **kwargs).run();


__all__ = [
    "GraphicalApplicationBackend", "pygame_key_to_sum", "run_application", "style_colors",
];
