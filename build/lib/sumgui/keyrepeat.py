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

DOS_FAST_DELAY_MS = 250;
DOS_FAST_INTERVAL_MS = 31;
DEFAULT_DELAY_MS = DOS_FAST_DELAY_MS;
DEFAULT_INTERVAL_MS = DOS_FAST_INTERVAL_MS;

_REPEATABLE_KEY_EVENTS = {
    pygame.K_BACKSPACE,
    pygame.K_DELETE,
    pygame.K_RETURN,
    pygame.K_KP_ENTER,
    pygame.K_TAB,
    pygame.K_LEFT,
    pygame.K_RIGHT,
    pygame.K_UP,
    pygame.K_DOWN,
    pygame.K_HOME,
    pygame.K_END,
    pygame.K_PAGEUP,
    pygame.K_PAGEDOWN,
    pygame.K_SPACE,
};

_MODIFIER_KEYS = {
    pygame.K_LSHIFT,
    pygame.K_RSHIFT,
    pygame.K_LCTRL,
    pygame.K_RCTRL,
    pygame.K_LALT,
    pygame.K_RALT,
    pygame.K_CAPSLOCK,
    pygame.K_NUMLOCKCLEAR,
};


class KeyRepeatState:
    def __init__(self, delay_ms=DEFAULT_DELAY_MS, interval_ms=DEFAULT_INTERVAL_MS, enabled=True):
        self.delay_ms = int(delay_ms);
        self.interval_ms = int(interval_ms);
        self.enabled = bool(enabled);
        self.pressed = {};
        self.last_keydown_key = None;

    def configure(self, delay_ms=DEFAULT_DELAY_MS, interval_ms=DEFAULT_INTERVAL_MS, enabled=True):
        self.delay_ms = max(0, int(delay_ms));
        self.interval_ms = max(1, int(interval_ms));
        self.enabled = bool(enabled);
        self.pressed = {};
        self.last_keydown_key = None;

    def is_repeatable_keydown(self, event):
        if event.key in _MODIFIER_KEYS:
            return False;
        unicode_value = getattr(event, "unicode", "");
        if unicode_value:
            return True;
        return event.key in _REPEATABLE_KEY_EVENTS;

    def keydown(self, event, now):
        self.last_keydown_key = event.key;
        if not self.enabled or not self.is_repeatable_keydown(event):
            return;
        previous = self.pressed.get(event.key, {});
        self.pressed[event.key] = {
            "mod": getattr(event, "mod", pygame.key.get_mods()),
            "next_ms": now + self.delay_ms,
            "text": previous.get("text", ""),
            "key_name": pygame.key.name(event.key),
        };

    def keyup(self, event):
        if event.key in self.pressed:
            del self.pressed[event.key];
        if self.last_keydown_key == event.key:
            self.last_keydown_key = None;

    def textinput(self, event):
        if self.last_keydown_key in self.pressed:
            self.pressed[self.last_keydown_key]["text"] = getattr(event, "text", "");

    def make_repeat_events(self, now):
        output = [];
        if not self.enabled:
            return output;
        for key, info in list(self.pressed.items()):
            if now < info["next_ms"]:
                continue;
            info["next_ms"] = now + self.interval_ms;
            text = info.get("text", "");
            mod = info.get("mod", pygame.key.get_mods());
            key_event = pygame.event.Event(
                pygame.KEYDOWN,
                key=key,
                mod=mod,
                unicode="",
                repeated=True,
            );
            output.append(key_event);
            if text:
                output.append(pygame.event.Event(pygame.TEXTINPUT, text=text, repeated=True));
        return output;

    def process_events(self, events):
        now = pygame.time.get_ticks();
        output = [];
        for event in events:
            output.append(event);
            if event.type == pygame.KEYDOWN:
                self.keydown(event, now);
            elif event.type == pygame.KEYUP:
                self.keyup(event);
            elif event.type == pygame.TEXTINPUT:
                self.textinput(event);
        output.extend(self.make_repeat_events(now));
        return output;


_GLOBAL_REPEAT = KeyRepeatState();


def enable_key_repeat(delay_ms=DEFAULT_DELAY_MS, interval_ms=DEFAULT_INTERVAL_MS):
    delay_ms = max(0, int(delay_ms));
    interval_ms = max(1, int(interval_ms));
    pygame.key.set_repeat(0, 0);
    _GLOBAL_REPEAT.configure(delay_ms, interval_ms, True);
    return delay_ms, interval_ms;


def disable_key_repeat():
    pygame.key.set_repeat(0, 0);
    _GLOBAL_REPEAT.configure(DEFAULT_DELAY_MS, DEFAULT_INTERVAL_MS, False);


def process_key_repeat(events):
    return _GLOBAL_REPEAT.process_events(events);


def get_events():
    return process_key_repeat(pygame.event.get());


class KeyRepeatConfig:
    def __init__(self, delay_ms=DEFAULT_DELAY_MS, interval_ms=DEFAULT_INTERVAL_MS, enabled=True):
        self.delay_ms = int(delay_ms);
        self.interval_ms = int(interval_ms);
        self.enabled = bool(enabled);

    def apply(self):
        if self.enabled:
            return enable_key_repeat(self.delay_ms, self.interval_ms);
        disable_key_repeat();
        return 0, 0;

    @classmethod
    def dos_fast(cls):
        return cls(DOS_FAST_DELAY_MS, DOS_FAST_INTERVAL_MS, True);

    @classmethod
    def slow(cls):
        return cls(500, 80, True);
