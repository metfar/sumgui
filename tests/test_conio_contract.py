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

from sumui import conio, stdio;


class FakeRect:
    def __init__(self, x, y, width, height):
        self.x=int(x); self.y=int(y); self.width=int(width); self.height=int(height);
    @property
    def topleft(self): return (self.x,self.y);


class FakeSurface:
    def __init__(self,size):
        self._size=tuple(size); self.fill_color=None; self.blits=[];
    def fill(self,color): self.fill_color=tuple(color);
    def blit(self,image,position): self.blits.append((image,tuple(position)));
    def get_size(self): return self._size;


class FakeFont:
    def size(self,text): return (max(1,len(str(text)))*8,16);
    def get_linesize(self): return 18;
    def render(self,text,unused_antialias,color): return (str(text),tuple(color));


class FakeClock:
    def __init__(self): self.ticks=0;
    def tick(self,unused_rate): self.ticks+=1; return 0;


def _load_conio(monkeypatch, events=None):
    queue=list(events or []); state={"surface":None,"flips":0,"pumps":0};
    pygame=types.ModuleType("pygame");
    pygame.RESIZABLE=1; pygame.QUIT=2; pygame.KEYDOWN=3; pygame.K_ESCAPE=27; pygame.VIDEORESIZE=4; pygame.WINDOWRESIZED=5; pygame.WINDOWSIZECHANGED=6;
    pygame.get_init=lambda: True; pygame.init=lambda: None;
    pygame.font=types.SimpleNamespace(get_init=lambda:True,init=lambda:None,SysFont=lambda unused_name,unused_size:FakeFont());
    pygame.Rect=FakeRect;
    pygame.draw=types.SimpleNamespace(rect=lambda *args,**kwargs:None,line=lambda *args,**kwargs:None);
    def set_mode(size,unused_flags=0): state["surface"]=FakeSurface(size); return state["surface"];
    pygame.display=types.SimpleNamespace(set_mode=set_mode,set_caption=lambda unused_title:None,flip=lambda:state.__setitem__("flips",state["flips"]+1));
    pygame.event=types.SimpleNamespace(get=lambda: [queue.pop(0)] if queue else [],pump=lambda:state.__setitem__("pumps",state["pumps"]+1));
    pygame.time=types.SimpleNamespace(Clock=FakeClock);
    monkeypatch.setitem(sys.modules,"pygame",pygame);
    package=types.ModuleType("sumgui_conio_test"); package.__path__=[str(Path(__file__).resolve().parents[1]/"sumgui")]; monkeypatch.setitem(sys.modules,"sumgui_conio_test",package);
    display=types.ModuleType("sumgui_conio_test.display"); display.set_default_icon=lambda:None; monkeypatch.setitem(sys.modules,"sumgui_conio_test.display",display);
    path=Path(__file__).resolve().parents[1]/"sumgui"/"conio.py";
    spec=importlib.util.spec_from_file_location("sumgui_conio_test.conio",path); module=importlib.util.module_from_spec(spec); monkeypatch.setitem(sys.modules,"sumgui_conio_test.conio",module); spec.loader.exec_module(module);
    return module,pygame,state;


def test_conio_graphical_backend_keeps_cells_visible_and_stdio_uses_same_backend(monkeypatch):
    module,unused_pygame,state=_load_conio(monkeypatch);
    previous=conio.backend();
    backend=module.ConioWindowBackend(cols=20,rows=6,font_size=16,title="test");
    try:
        conio.use_backend(backend);
        conio.textbackground(conio.BLUE); conio.textcolor(conio.WHITE); conio.clrscr(); conio.gotoxy(2,2); conio.cputs("HELLO");
        assert ''.join(cell[0] for cell in backend.cells[1][1:6]) == "HELLO";
        assert backend.screen.fill_color == module._PALETTE[conio.BLUE];
        stdio.use_conio(); stdio.printf("!");
        assert backend.cells[1][6][0] == "!";
        assert state["flips"] >= 4;
        assert state["pumps"] >= 4;
    finally:
        conio.use_backend(previous);
        stdio.set_streams(stdout=sys.stdout,stderr=sys.stderr);


def test_conio_pump_redraws_after_resize_and_buffers_key(monkeypatch):
    resize=types.SimpleNamespace(type=4,size=(500,300),w=500,h=300);
    key=types.SimpleNamespace(type=3,unicode="x",key=ord("x"));
    module,unused_pygame,state=_load_conio(monkeypatch,[resize,key]);
    backend=module.ConioWindowBackend(cols=20,rows=6,font_size=16,title="test");
    flips=state["flips"];
    assert backend._pump() is True;
    assert backend.screen.get_size() == (500,300);
    assert state["flips"] > flips;
    assert backend._pump() is True;
    assert backend.keys.popleft() == "x";
