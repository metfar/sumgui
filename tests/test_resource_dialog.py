#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301

import importlib.machinery;
import importlib.util;
import json;
from pathlib import Path;
import sys;
import types;


def _load_resourceio():
    package = types.ModuleType("sumgui");
    package.__path__ = [str(Path(__file__).resolve().parents[1] / "sumgui")];
    package.__spec__ = importlib.machinery.ModuleSpec("sumgui", loader=None, is_package=True);
    sys.modules["sumgui"] = package;
    path = Path(__file__).resolve().parents[1] / "sumgui" / "resourceio.py";
    spec = importlib.util.spec_from_file_location("sumgui.resourceio", path);
    module = importlib.util.module_from_spec(spec);
    sys.modules["sumgui.resourceio"] = module;
    spec.loader.exec_module(module);
    return module;


def test_sumgdialog_resource_bridge_builds_graphical_form_spec(tmp_path):
    load_resource_dialog = _load_resourceio().load_resource_dialog;
    schema = tmp_path / "catalog.resource.json";
    schema.write_text(json.dumps({
        "schema": "sum.resource/1", "name": "catalog", "title": "Catalog", "key": "id",
        "capabilities": ["create", "read", "update", "delete", "list", "search", "import", "export"],
        "fields": [
            {"name": "id", "label": "ID"},
            {"name": "title", "label": "Title", "required": True},
            {"name": "kind", "label": "Kind", "kind": "combo", "options": ["Book", "Game"]},
        ],
    }), encoding="utf-8");
    spec = load_resource_dialog(schema, operation="update", values='{"id":"7","title":"Dune","kind":"Book"}', theme="Dark");
    assert spec.kind == "form";
    assert spec.title == "Update Catalog";
    assert spec.theme == "Dark";
    assert spec.fields[0].default == "7";
    assert spec.fields[1].default == "Dune";
    assert spec.fields[2].options == ("Book", "Game");
