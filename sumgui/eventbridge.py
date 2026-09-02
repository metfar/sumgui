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

from sumui import UIEvent;


def _mods(mod):
    result = [];
    checks = (
        (getattr(pygame, "KMOD_SHIFT", 0), "shift"),
        (getattr(pygame, "KMOD_CTRL", 0), "ctrl"),
        (getattr(pygame, "KMOD_ALT", 0), "alt"),
        (getattr(pygame, "KMOD_META", 0), "meta"),
    );
    for mask, name in checks:
        if mask and int(mod or 0) & mask:
            result.append(name);
    return tuple(result);


def event_to_common(event, size=None):
    """Translate one pygame event to the backend-neutral sumUI event model.

    The original pygame event remains the compatibility event consumed by
    legacy SumGUI widgets.  This translation is for new code and language
    runtimes that should not depend on pygame constants.
    """
    event_type = getattr(event, "type", None);
    width, height = tuple(size or (1, 1));
    if event_type == getattr(pygame, "MOUSEBUTTONDOWN", object()):
        return UIEvent("pointer_down", source="touch" if getattr(event, "touch", False) else "mouse", x=event.pos[0], y=event.pos[1], button=getattr(event, "button", 1));
    if event_type == getattr(pygame, "MOUSEBUTTONUP", object()):
        return UIEvent("pointer_up", source="touch" if getattr(event, "touch", False) else "mouse", x=event.pos[0], y=event.pos[1], button=getattr(event, "button", 1));
    if event_type == getattr(pygame, "MOUSEMOTION", object()):
        return UIEvent("pointer_move", source="touch" if getattr(event, "touch", False) else "mouse", x=event.pos[0], y=event.pos[1]);
    if event_type == getattr(pygame, "FINGERDOWN", object()):
        return UIEvent("pointer_down", source="touch", x=float(event.x) * width, y=float(event.y) * height, button=1, pointer_id=getattr(event, "finger_id", None));
    if event_type == getattr(pygame, "FINGERUP", object()):
        return UIEvent("pointer_up", source="touch", x=float(event.x) * width, y=float(event.y) * height, button=1, pointer_id=getattr(event, "finger_id", None));
    if event_type == getattr(pygame, "FINGERMOTION", object()):
        return UIEvent("pointer_move", source="touch", x=float(event.x) * width, y=float(event.y) * height, pointer_id=getattr(event, "finger_id", None));
    if event_type == getattr(pygame, "MOUSEWHEEL", object()):
        return UIEvent("wheel", source="mouse", delta_x=getattr(event, "x", 0.0), delta_y=getattr(event, "y", 0.0));
    if event_type == getattr(pygame, "KEYDOWN", object()):
        return UIEvent("key_down", source="keyboard", key=str(getattr(event, "key", "")), modifiers=_mods(getattr(event, "mod", 0)));
    if event_type == getattr(pygame, "KEYUP", object()):
        return UIEvent("key_up", source="keyboard", key=str(getattr(event, "key", "")), modifiers=_mods(getattr(event, "mod", 0)));
    if event_type == getattr(pygame, "TEXTINPUT", object()):
        return UIEvent("text_input", source="keyboard", text=getattr(event, "text", ""));
    if event_type == getattr(pygame, "VIDEORESIZE", object()):
        return UIEvent("resize", source="window", x=getattr(event, "w", width), y=getattr(event, "h", height));
    if event_type == getattr(pygame, "QUIT", object()):
        return UIEvent("quit", source="window");
    if event_type in (getattr(pygame, "WINDOWFOCUSLOST", object()),):
        return UIEvent("focus_out", source="window");
    if event_type in (getattr(pygame, "WINDOWFOCUSGAINED", object()),):
        return UIEvent("focus_in", source="window");
    return None;


def touch_to_mouse_event(event, size):
    """Return a pygame mouse compatibility event for a FINGER event.

    SumGUI 0.2 consumes native FINGER events itself and suppresses pygame's
    synthesized ``touch=True`` mouse duplicate.  This keeps one logical
    press/release pair, which is important on Android.
    """
    width, height = tuple(size or (1, 1));
    event_type = getattr(event, "type", None);
    mapping = {
        getattr(pygame, "FINGERDOWN", -101): getattr(pygame, "MOUSEBUTTONDOWN", -201),
        getattr(pygame, "FINGERUP", -102): getattr(pygame, "MOUSEBUTTONUP", -202),
        getattr(pygame, "FINGERMOTION", -103): getattr(pygame, "MOUSEMOTION", -203),
    };
    if event_type not in mapping:
        return event;
    pos = (int(round(float(event.x) * width)), int(round(float(event.y) * height)));
    data = {"pos": pos, "touch": True, "finger_id": getattr(event, "finger_id", None)};
    if event_type in (getattr(pygame, "FINGERDOWN", -101), getattr(pygame, "FINGERUP", -102)):
        data["button"] = 1;
    else:
        data["rel"] = (int(round(float(getattr(event, "dx", 0.0)) * width)), int(round(float(getattr(event, "dy", 0.0)) * height)));
        data["buttons"] = (1, 0, 0);
    return pygame.event.Event(mapping[event_type], data);


def is_focus_loss(event):
    event_type = getattr(event, "type", None);
    if event_type == getattr(pygame, "WINDOWFOCUSLOST", object()):
        return True;
    if event_type == getattr(pygame, "ACTIVEEVENT", object()) and getattr(event, "gain", 1) == 0:
        return True;
    return False;
