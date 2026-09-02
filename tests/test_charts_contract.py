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

import importlib.util;
from pathlib import Path;
import sys;
import types;
import unittest;

from sumui import ChartSpec;


def load_charts_module():
    pygame = types.ModuleType("pygame");
    sys.modules["pygame"] = pygame;
    package = types.ModuleType("sumgui");
    package.__path__ = [str(Path(__file__).resolve().parents[1] / "sumgui")];
    sys.modules["sumgui"] = package;
    widgets = types.ModuleType("sumgui.widgets");
    class Widget:
        def __init__(self, rect, focusable=False, tab_index=0):
            self.rect = rect;
            self.focusable = focusable;
            self.tab_index = tab_index;
            self.has_focus = False;
    widgets.Widget = Widget;
    widgets.draw_clipped_text = lambda *args, **kwargs: None;
    widgets.with_clip = lambda screen, rect, callback: callback();
    sys.modules["sumgui.widgets"] = widgets;
    theme = types.ModuleType("sumgui.theme");
    theme.DEFAULT_THEME = object();
    sys.modules["sumgui.theme"] = theme;
    path = Path(__file__).resolve().parents[1] / "sumgui" / "charts.py";
    spec = importlib.util.spec_from_file_location("sumgui.charts", path);
    module = importlib.util.module_from_spec(spec);
    sys.modules["sumgui.charts"] = module;
    spec.loader.exec_module(module);
    return module;


class SharedChartContractTests(unittest.TestCase):
    def test_chartview_accepts_sumui_spec(self):
        module = load_charts_module();
        spec = ChartSpec.bar(["A", "B"], [1, 2], title="Shared");
        view = module.ChartView(None, spec, None);
        self.assertIs(view.spec, spec);
        self.assertEqual(view.title, "Shared");
        self.assertEqual(view.spec.kind, "bar");

    def test_set_spec_switches_chart_kind(self):
        module = load_charts_module();
        view = module.ChartView(None, ChartSpec.bar(["A"], [1]), None);
        view.set_spec(ChartSpec.line([(0, 0), (1, 1)], title="Line"));
        self.assertEqual(view.spec.kind, "line");
        self.assertEqual(view.title, "Line");


if __name__ == "__main__":
    unittest.main();


def test_chartview_accepts_radar_and_horizontal_bar_specs():
    module = load_charts_module();
    radar = ChartSpec.radar(["A", "B", "C"], [1, 2, 3], title="Radar");
    view = module.ChartView(None, radar, None);
    assert view.spec.kind == "radar";
    hbar = ChartSpec.bar(["A", "B"], [1, 2], orientation="horizontal");
    view.set_spec(hbar);
    assert view.spec.option("orientation") == "horizontal";
