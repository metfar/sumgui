#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301

import importlib.util;
from pathlib import Path;
import sys;
import types;


def _package_stub():
    package = types.ModuleType("sumgui");
    package.__path__ = [str(Path(__file__).resolve().parents[1] / "sumgui")];
    sys.modules["sumgui"] = package;
    return package;


def test_gui_backend_contract_without_loading_pygame():
    _package_stub();
    path = Path(__file__).resolve().parents[1] / "sumgui" / "contracts.py";
    spec = importlib.util.spec_from_file_location("sumgui.contracts", path);
    module = importlib.util.module_from_spec(spec);
    sys.modules["sumgui.contracts"] = module;
    spec.loader.exec_module(module);
    assert module.GUI_BACKEND.name == "gui";
    assert module.GUI_BACKEND.graphics is True;
    assert module.GUI_BACKEND.touch is True;


def test_event_bridge_normalizes_touch_coordinates():
    pygame = types.ModuleType("pygame");
    pygame.FINGERDOWN = 1;
    pygame.FINGERUP = 2;
    pygame.FINGERMOTION = 3;
    pygame.MOUSEBUTTONDOWN = 4;
    pygame.MOUSEBUTTONUP = 5;
    pygame.MOUSEMOTION = 6;
    pygame.MOUSEWHEEL = 7;
    pygame.KEYDOWN = 8;
    pygame.KEYUP = 9;
    pygame.TEXTINPUT = 10;
    pygame.VIDEORESIZE = 11;
    pygame.QUIT = 12;
    pygame.WINDOWFOCUSLOST = 13;
    pygame.WINDOWFOCUSGAINED = 14;
    pygame.ACTIVEEVENT = 15;
    pygame.KMOD_SHIFT = 1;
    pygame.KMOD_CTRL = 2;
    pygame.KMOD_ALT = 4;
    pygame.KMOD_META = 8;
    class EventFactory:
        @staticmethod
        def Event(kind, data):
            return types.SimpleNamespace(type=kind, **data);
    pygame.event = EventFactory;
    sys.modules["pygame"] = pygame;
    _package_stub();
    path = Path(__file__).resolve().parents[1] / "sumgui" / "eventbridge.py";
    spec = importlib.util.spec_from_file_location("sumgui.eventbridge", path);
    module = importlib.util.module_from_spec(spec);
    sys.modules["sumgui.eventbridge"] = module;
    spec.loader.exec_module(module);
    source = types.SimpleNamespace(type=pygame.FINGERDOWN, x=0.5, y=0.25, finger_id=7);
    common = module.event_to_common(source, (800, 600));
    assert common.type == "pointer_down";
    assert common.position == (400.0, 150.0);
    compatibility = module.touch_to_mouse_event(source, (800, 600));
    assert compatibility.type == pygame.MOUSEBUTTONDOWN;
    assert compatibility.pos == (400, 150);
