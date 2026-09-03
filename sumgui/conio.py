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

"""Pygame text-grid backend for the common ``sumui.conio`` API.""";

from collections import deque;
import pygame;

from sumui import conio;
from .display import set_default_icon;

_PALETTE=((0,0,0),(0,0,170),(0,170,0),(0,170,170),(170,0,0),(170,0,170),(170,85,0),(170,170,170),(85,85,85),(85,85,255),(85,255,85),(85,255,255),(255,85,85),(255,85,255),(255,255,85),(255,255,255));

class ConioWindowBackend:
    def __init__(self,cols=80,rows=25,font_name="monospace",font_size=18,title="Σ Sum conio"):
        if not pygame.get_init(): pygame.init();
        if not pygame.font.get_init(): pygame.font.init();
        set_default_icon();
        self.cols=max(1,int(cols)); self.rows=max(1,int(rows)); self.font=pygame.font.SysFont(font_name,max(8,int(font_size))); self.cell_w=max(1,self.font.size("M")[0]); self.cell_h=max(1,self.font.get_linesize());
        self.screen=pygame.display.set_mode((self.cols*self.cell_w,self.rows*self.cell_h),pygame.RESIZABLE); pygame.display.set_caption(str(title));
        self.x=1; self.y=1; self.fg=conio.LIGHTGRAY; self.bg=conio.BLACK; self.intensity="normal"; self.window_rect=(1,1,self.cols,self.rows); self.keys=deque();
        self.cells=[[(' ',self.fg,self.bg) for _ in range(self.cols)] for _ in range(self.rows)]; self.render();
    def _bounds(self): x1,y1,x2,y2=self.window_rect; return x1,y1,min(self.cols,x2),min(self.rows,y2);
    def _absolute(self,x=None,y=None):
        x1,y1,_,_=self._bounds(); return x1+(self.x if x is None else int(x))-2,y1+(self.y if y is None else int(y))-2;
    def render(self):
        self.screen.fill(_PALETTE[self.bg&15]);
        for row,line in enumerate(self.cells):
            for col,(ch,fg,bg) in enumerate(line):
                rect=pygame.Rect(col*self.cell_w,row*self.cell_h,self.cell_w,self.cell_h); pygame.draw.rect(self.screen,_PALETTE[bg&15],rect);
                if ch!=' ': self.screen.blit(self.font.render(ch,True,_PALETTE[fg&15]),rect.topleft);
        ax,ay=self._absolute();
        if 0<=ax<self.cols and 0<=ay<self.rows: pygame.draw.line(self.screen,_PALETTE[self.fg&15],(ax*self.cell_w,(ay+1)*self.cell_h-2),((ax+1)*self.cell_w-1,(ay+1)*self.cell_h-2),1);
        pygame.display.flip();
    def _scroll(self):
        x1,y1,x2,y2=self._bounds();
        for row in range(y1-1,y2-1): self.cells[row][x1-1:x2]=list(self.cells[row+1][x1-1:x2]);
        self.cells[y2-1][x1-1:x2]=[(' ',self.fg,self.bg) for _ in range(x2-x1+1)]; self.y=max(1,self.y-1);
    def _put(self,ch):
        if ch=='\n': self.x=1; self.y+=1;
        elif ch=='\r': self.x=1;
        else:
            ax,ay=self._absolute();
            if 0<=ax<self.cols and 0<=ay<self.rows: self.cells[ay][ax]=(ch,self.fg,self.bg);
            self.x+=1;
            x1,y1,x2,y2=self._bounds(); width=x2-x1+1; height=y2-y1+1;
            if self.x>width: self.x=1; self.y+=1;
        x1,y1,x2,y2=self._bounds(); height=y2-y1+1;
        if self.y>height: self._scroll();
    def write(self,text):
        for ch in str(text): self._put(ch);
        self.render();
    def clrscr(self):
        x1,y1,x2,y2=self._bounds();
        for row in range(y1-1,y2):
            for col in range(x1-1,x2): self.cells[row][col]=(' ',self.fg,self.bg);
        self.x=1; self.y=1; self.render();
    def gotoxy(self,x,y): self.x=max(1,int(x)); self.y=max(1,int(y)); self.render();
    def _pump(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT: self.keys.append('\x1b');
            elif event.type==pygame.KEYDOWN:
                text=getattr(event,'unicode','');
                if text: self.keys.append(text);
                elif event.key==pygame.K_ESCAPE: self.keys.append('\x1b');
    def getch(self,echo=False):
        while not self.keys:
            self._pump(); pygame.time.wait(10);
        ch=self.keys.popleft();
        if echo: self.write(ch);
        return ch;
    def kbhit(self): self._pump(); return bool(self.keys);
    def textcolor(self,color): self.fg=int(color)&15;
    def textbackground(self,color): self.bg=int(color)&15;
    def clreol(self):
        ax,ay=self._absolute(); _,_,x2,_=self._bounds();
        if 0<=ay<self.rows:
            for col in range(max(0,ax),x2): self.cells[ay][col]=(' ',self.fg,self.bg);
        self.render();
    def delline(self):
        x1,y1,x2,y2=self._bounds(); row=y1+self.y-2;
        if y1-1<=row<y2:
            for r in range(row,y2-1): self.cells[r][x1-1:x2]=list(self.cells[r+1][x1-1:x2]);
            self.cells[y2-1][x1-1:x2]=[(' ',self.fg,self.bg) for _ in range(x2-x1+1)]; self.render();
    def insline(self):
        x1,y1,x2,y2=self._bounds(); row=y1+self.y-2;
        if y1-1<=row<y2:
            for r in range(y2-1,row,-1): self.cells[r][x1-1:x2]=list(self.cells[r-1][x1-1:x2]);
            self.cells[row][x1-1:x2]=[(' ',self.fg,self.bg) for _ in range(x2-x1+1)]; self.render();
    def highvideo(self): self.intensity='high';
    def lowvideo(self): self.intensity='low';
    def normvideo(self): self.intensity='normal'; self.fg=conio.LIGHTGRAY; self.bg=conio.BLACK;
    def textmode(self,mode): pass;
    def window(self,x1,y1,x2,y2): self.window_rect=(int(x1),int(y1),int(x2),int(y2)); self.x=1; self.y=1; self.render();


def install(**kwargs):
    backend=ConioWindowBackend(**kwargs); conio.use_backend(backend); return backend;
