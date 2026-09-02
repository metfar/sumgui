#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301

import importlib.util;
from pathlib import Path;
import sys;
import types;


def _package_stub():
    import importlib.machinery;
    package = types.ModuleType("sumgui");
    package.__path__ = [str(Path(__file__).resolve().parents[1] / "sumgui")];
    package.__spec__ = importlib.machinery.ModuleSpec("sumgui", loader=None, is_package=True);
    package.GUI_BACKEND = types.SimpleNamespace(name="gui", family="graphical", charts=True, graphics=True);
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
    import importlib.machinery;
    pygame.__spec__ = importlib.machinery.ModuleSpec("pygame", loader=None);
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


def test_display_fit_keeps_768p_examples_on_screen():
    pygame = types.ModuleType("pygame");
    pygame.error = RuntimeError;
    class Display:
        @staticmethod
        def get_init():
            return True;
        @staticmethod
        def get_desktop_sizes():
            return [(1366, 768)];
        @staticmethod
        def Info():
            return types.SimpleNamespace(current_w=1366, current_h=768);
    pygame.display = Display;
    sys.modules["pygame"] = pygame;
    _package_stub();
    path = Path(__file__).resolve().parents[1] / "sumgui" / "display.py";
    spec = importlib.util.spec_from_file_location("sumgui.display", path);
    module = importlib.util.module_from_spec(spec);
    sys.modules["sumgui.display"] = module;
    spec.loader.exec_module(module);
    width, height = module.fit_window_size(1074, 2102);
    assert width <= 1366 - 32;
    assert height <= 768 - 64;
    assert (width, height) == module.fit_window_size(1074, 2102, desktop=(1366, 768));
    assert module.fit_window_size(640, 480, desktop=(1366, 768)) == (640, 480);


def test_demo_full_uses_its_complete_portrait_logical_canvas():
    import ast;
    source_path = Path(__file__).resolve().parents[1] / "examples" / "demo_full.py";
    source = source_path.read_text(encoding="utf-8");
    tree = ast.parse(source);
    constants = {};
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and isinstance(node.value, ast.Constant):
            constants[node.targets[0].id] = node.value.value;
    assert constants.get("BASE_WIDTH") == 720;
    assert constants.get("BASE_HEIGHT") == 1280;
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "Scale"];
    assert calls;
    keywords = {item.arg: item.value for item in calls[0].keywords};
    assert isinstance(keywords.get("base_width"), ast.Name) and keywords["base_width"].id == "BASE_WIDTH";
    assert isinstance(keywords.get("base_height"), ast.Name) and keywords["base_height"].id == "BASE_HEIGHT";


def test_udg_painter_reborn_is_part_of_the_source_distribution_tree():
    root = Path(__file__).resolve().parents[1] / "udg_painter_reborn";
    expected = (
        "__init__.py", "__main__.py", "udg_painter_sumgui.py", "graphic.udg",
        "casa.udg", "macaco.udg", "casa.png", "graphic.xpm", "LICENSE", "README.md",
    );
    assert root.is_dir();
    for name in expected:
        assert (root / name).is_file(), name;

def test_sumgdialog_entry_uses_common_focus_ring_for_tab_navigation():
    import ast;
    root = Path(__file__).resolve().parents[1];
    source = (root / "sumgui" / "dialogs.py").read_text(encoding="utf-8");
    tree = ast.parse(source);
    function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "input_box");
    calls = [node for node in ast.walk(function) if isinstance(node, ast.Call)];
    names = [];
    for call in calls:
        if isinstance(call.func, ast.Name):
            names.append(call.func.id);
    assert "Panel" in names;
    assert "TextInput" in names;
    assert names.count("Button") >= 2;
    assert any(
        isinstance(call.func, ast.Attribute)
        and isinstance(call.func.value, ast.Name)
        and call.func.value.id == "focus"
        and call.func.attr == "handle_event"
        for call in calls
    );
    tab_indexes = [];
    for call in calls:
        if isinstance(call.func, ast.Name) and call.func.id in ("TextInput", "Button"):
            for keyword in call.keywords:
                if keyword.arg == "tab_index" and isinstance(keyword.value, ast.Constant):
                    tab_indexes.append(keyword.value.value);
    assert tab_indexes[:3] == [0, 1, 2];


def test_sumgdialog_demo_buttons_participate_in_tab_navigation():
    import ast;
    root = Path(__file__).resolve().parents[1];
    source = (root / "sumgui" / "tools" / "gdialog.py").read_text(encoding="utf-8");
    tree = ast.parse(source);
    function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_demo_menu");
    calls = [node for node in ast.walk(function) if isinstance(node, ast.Call)];
    assert any(isinstance(call.func, ast.Name) and call.func.id == "Panel" for call in calls);
    assert any(isinstance(call.func, ast.Name) and call.func.id == "Button" for call in calls);
    assert any(
        isinstance(call.func, ast.Attribute)
        and isinstance(call.func.value, ast.Name)
        and call.func.value.id == "panel"
        and call.func.attr == "handle_event"
        for call in calls
    );



def test_application_backend_translates_native_touch_once():
    import importlib.util;
    from pathlib import Path;
    import sys;
    import types;

    pygame = types.ModuleType("pygame");
    import importlib.machinery;
    pygame.__spec__ = importlib.machinery.ModuleSpec("pygame", loader=None);
    pygame.FINGERDOWN = 1;
    pygame.FINGERMOTION = 2;
    pygame.FINGERUP = 3;
    pygame.MOUSEBUTTONDOWN = 4;
    pygame.MOUSEBUTTONUP = 5;
    pygame.MOUSEMOTION = 6;
    pygame.MOUSEWHEEL = 7;
    pygame.KEYDOWN = 8;
    pygame.TEXTINPUT = 9;
    pygame.QUIT = 10;
    pygame.VIDEORESIZE = 11;
    pygame.WINDOWRESIZED = 12;
    pygame.WINDOWSIZECHANGED = 13;
    pygame.WINDOWFOCUSLOST = 14;
    pygame.KMOD_CTRL = 1;
    pygame.KMOD_ALT = 2;
    pygame.KMOD_SHIFT = 4;
    pygame.key = types.SimpleNamespace(get_mods=lambda: 0);
    pygame.mouse = types.SimpleNamespace(get_pos=lambda: (0, 0));
    class EventFactory:
        @staticmethod
        def Event(kind, data):
            return types.SimpleNamespace(type=kind, **data);
    pygame.event = EventFactory;
    sys.modules["pygame"] = pygame;
    _package_stub();
    root = Path(__file__).resolve().parents[1] / "sumgui";
    for module_name in ("eventbridge", "application_backend"):
        path = root / (module_name + ".py");
        spec = importlib.util.spec_from_file_location("sumgui." + module_name, path);
        module = importlib.util.module_from_spec(spec);
        sys.modules["sumgui." + module_name] = module;
        spec.loader.exec_module(module);
    backend_module = sys.modules["sumgui.application_backend"];
    backend = backend_module.GraphicalApplicationBackend.__new__(backend_module.GraphicalApplicationBackend);
    received = [];
    backend.pygame = pygame;
    backend.screen = types.SimpleNamespace(get_size=lambda: (800, 600), get_width=lambda: 800, get_height=lambda: 600);
    backend.cell_width = 10;
    backend.cell_height = 20;
    backend._left_down = False;
    backend.MouseEvent = lambda x, y, **kwargs: types.SimpleNamespace(x=x, y=y, **kwargs);
    backend.KeyEvent = lambda *args, **kwargs: types.SimpleNamespace(args=args, **kwargs);
    backend.application = types.SimpleNamespace(dispatch=lambda event: received.append(event) or True, stop=lambda: None);
    touch = types.SimpleNamespace(type=pygame.FINGERDOWN, x=0.5, y=0.25, finger_id=7);
    assert backend._dispatch_pygame(touch) is True;
    assert len(received) == 1;
    assert (received[0].x, received[0].y, received[0].button, received[0].action) == (40, 7, "left", "press");
    duplicate = types.SimpleNamespace(type=pygame.MOUSEBUTTONDOWN, pos=(400, 150), button=1, touch=True);
    assert backend._dispatch_pygame(duplicate) is False;
    assert len(received) == 1;


def test_native_editorview_has_semantic_syntax_and_line_numbers_contract():
    import ast;
    from pathlib import Path;
    source = (Path(__file__).resolve().parents[1] / "sumgui" / "widgets.py").read_text(encoding="utf-8");
    tree = ast.parse(source);
    classes = {node.name: node for node in tree.body if isinstance(node, ast.ClassDef)};
    assert "TextArea" in classes;
    assert "EditorView" in classes;
    textarea_init = next(node for node in classes["TextArea"].body if isinstance(node, ast.FunctionDef) and node.name == "__init__");
    textarea_args = [item.arg for item in textarea_init.args.args];
    assert "syntax_highlighter" in textarea_args;
    assert "line_numbers" in textarea_args;
    methods = {node.name for node in classes["TextArea"].body if isinstance(node, ast.FunctionDef)};
    assert {"_syntax_roles", "display_cells_for_row", "_invalidate_syntax"} <= methods;
    editor_init = next(node for node in classes["EditorView"].body if isinstance(node, ast.FunctionDef) and node.name == "__init__");
    defaults = editor_init.args.defaults;
    arg_names = [item.arg for item in editor_init.args.args];
    line_index = arg_names.index("line_numbers");
    first_default = len(arg_names) - len(defaults);
    default_node = defaults[line_index - first_default];
    assert isinstance(default_node, ast.Constant) and default_node.value is True;


def test_gui_themes_include_tui_baseline_schemes_without_pygame():
    import importlib.util;
    from pathlib import Path;
    import sys;
    _package_stub();
    path = Path(__file__).resolve().parents[1] / "sumgui" / "theme.py";
    spec = importlib.util.spec_from_file_location("sumgui.theme", path);
    module = importlib.util.module_from_spec(spec);
    sys.modules["sumgui.theme"] = module;
    spec.loader.exec_module(module);
    for name in ("ZX", "DOS", "RAR", "DBASE", "FOXPRO", "XBASE", "C64", "MSX", "Dark", "Light"):
        assert name in module.THEMES;
        theme = module.make_theme(name);
        assert isinstance(theme.role_color("syntax_keyword"), tuple);
        assert len(theme.role_color("syntax_keyword")) == 3;
    assert module.DEFAULT_THEME.name == "ZX";
