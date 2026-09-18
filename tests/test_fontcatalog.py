#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from importlib.util import module_from_spec, spec_from_file_location;
from pathlib import Path;
from types import SimpleNamespace;


def _module():
    path=Path(__file__).resolve().parents[1]/"sumgui"/"fontcatalog.py"; spec=spec_from_file_location("sumgui_fontcatalog_test",path); module=module_from_spec(spec); import sys; sys.modules[spec.name]=module; spec.loader.exec_module(module); return module;


def test_font_names_are_unique_and_alphabetical_casefolded():
    module=_module(); values=module.sort_font_names(["zeta","Arial","alpha","ARIAL"],current="Mono"); assert values==("alpha","Arial","Mono","monospace","zeta");


def test_font_filter_matches_substrings_case_insensitively():
    module=_module(); values=("DejaVu Sans Mono","Liberation Mono","Noto Sans","Orator"); assert module.filter_font_names(values,"mono")==("DejaVu Sans Mono","Liberation Mono"); assert module.filter_font_names(values,"orat")==("Orator",);


def test_monospace_catalog_filters_proportional_fonts():
    module=_module();
    class FakeFont:
        def __init__(self,name): self.name=name;
        def size(self,text): return ((8 if self.name!="prop" or text=="i" else 11)*len(text),16);
    class FontAPI:
        @staticmethod
        def get_fonts(): return ["prop","mono","orator"];
        @staticmethod
        def SysFont(name,size): return FakeFont(name);
    values=module.system_font_names(FontAPI(),current="mono",monospace_only=True); assert "mono" in values; assert "orator" in values; assert "prop" not in values; assert values==tuple(sorted(values,key=lambda item:(item.casefold(),item)));


def test_font_selection_carries_independent_case_weights():
    module=_module(); value=module.FontSelection("Source Code Pro",False,False,True,0.78,1,2);
    assert value.family=="Source Code Pro"; assert value.small_caps_scale==0.78; assert value.uppercase_embolden==1; assert value.lowercase_embolden==2;
