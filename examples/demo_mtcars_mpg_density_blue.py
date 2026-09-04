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
import pygame;
from sumdata import dataset;
from sumplot import after_stat, aes, geom_histogram, ggplot, to_chart_spec;
from sumgui import ChartView, make_theme, set_default_icon;

WIDTH=960; HEIGHT=640; BLUE="#51A8C9";

def build_plot():
    mtcars=dataset("mtcars"); return ggplot(mtcars,aes("mpg",after_stat("density")))+geom_histogram(binwidth=1,fill=BLUE);

def main():
    pygame.init(); set_default_icon(); screen=pygame.display.set_mode((WIDTH,HEIGHT)); pygame.display.set_caption("sumGUI - mtcars MPG density"); font=pygame.font.SysFont("monospace",16); theme=make_theme("ZX"); chart=to_chart_spec(build_plot()); view=ChartView(pygame.Rect(24,24,WIDTH-48,HEIGHT-48),chart,font,theme=theme); clock=pygame.time.Clock(); saved=False; running=True;
    while running:
        for event in pygame.event.get():
            if event.type==pygame.QUIT or (event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE): running=False;
        screen.fill(theme.bg); view.draw(screen); pygame.display.flip();
        if not saved: pygame.image.save(screen,"mtcars_mpg_density_blue_sumgui.png"); saved=True;
        clock.tick(60);
    pygame.quit(); return 0;

if __name__=="__main__": raise SystemExit(main());
