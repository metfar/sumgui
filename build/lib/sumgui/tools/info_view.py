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
"""Tabbed Pygame frontend for the passive ``suminfo`` report.""";

import pygame;

from sumcore.info import collect_report, render_report;
from ..dialogs import _dialog_events;
from ..display import fit_window_size, set_default_icon;
from ..theme import make_theme;
from ..widgets import Button, Panel, TextArea, draw_clipped_text;


class InfoGUI:
    def __init__(self, report, groups=None, detailed=False, theme="Dark"):
        self.report = report;
        self.groups = [name for name in (groups or report.get("groups", {})) if name in report.get("groups", {})];
        self.index = 0;
        self.detailed = bool(detailed);
        self.detail_cache = {name: report.get("groups", {}).get(name) for name in self.groups} if self.detailed else {};
        pygame.init();
        set_default_icon();
        width, height = fit_window_size(1100, 720);
        self.screen = pygame.display.set_mode((max(640, width), max(420, height)));
        pygame.display.set_caption("suminfo");
        self.clock = pygame.time.Clock();
        self.theme = make_theme(theme);
        self.font = pygame.font.SysFont("monospace", max(14, min(20, height // 36)));
        self.small = pygame.font.SysFont("monospace", max(12, min(17, height // 42)), bold=True);
        self.panel = Panel(self.screen.get_rect(), theme=self.theme);
        self.tab_buttons = [];
        self.detail_button = None;
        self.viewer = None;
        self._build();
        self._refresh();

    def _build(self):
        width, height = self.screen.get_size();
        margin = 12;
        tab_y = 12;
        tab_h = max(34, self.small.get_height() + 14);
        detail_w = 110;
        available = width - margin * 2 - detail_w - 8;
        tab_w = max(58, available // max(1, len(self.groups)));
        self.tab_buttons = [];
        for index, group in enumerate(self.groups):
            rect = pygame.Rect(margin + index * tab_w, tab_y, tab_w - 4, tab_h);
            button = Button(rect, group.title(), self.small, on_click=lambda unused=None, i=index: self.select(i), theme=self.theme, tab_index=index);
            self.tab_buttons.append(self.panel.add(button));
        self.detail_button = self.panel.add(Button(pygame.Rect(width - margin - detail_w, tab_y, detail_w, tab_h), "Summary" if self.detailed else "Details", self.small, on_click=lambda *_args: self.toggle_details(), theme=self.theme, tab_index=len(self.groups)));
        viewer_rect = pygame.Rect(margin, tab_y + tab_h + 12, width - margin * 2, height - (tab_y + tab_h + 24));
        self.viewer = self.panel.add(TextArea(viewer_rect, self.font, text="", multiline=True, editable=False, show_scrollbar=True, theme=self.theme, tab_index=len(self.groups) + 1));
        self.panel.set_focus_widget(self.viewer);

    def _refresh(self):
        if not self.groups:
            text = "No information groups available.";
        else:
            group = self.groups[self.index];
            payload = self.report["groups"][group];
            if self.detailed:
                if group not in self.detail_cache:
                    self.detail_cache[group] = collect_report(groups=(group,), detailed=True)["groups"][group];
                payload = self.detail_cache[group];
            subset = dict(self.report);
            subset["groups"] = {group: payload};
            text = render_report(subset, detailed=self.detailed);
        self.viewer.set_text(text);
        if hasattr(self.viewer, "scroll_row"): self.viewer.scroll_row = 0;
        if hasattr(self.viewer, "scroll_col"): self.viewer.scroll_col = 0;
        self.detail_button.text = "Summary" if self.detailed else "Details";
        return True;

    def select(self, index):
        if not self.groups: return False;
        self.index = max(0, min(len(self.groups) - 1, int(index)));
        return self._refresh();

    def move(self, delta):
        if not self.groups: return False;
        self.index = (self.index + int(delta)) % len(self.groups);
        return self._refresh();

    def toggle_details(self):
        self.detailed = not self.detailed;
        return self._refresh();

    def run(self):
        try:
            while True:
                dt = self.clock.tick(60);
                for event in _dialog_events(self.screen):
                    if event.type == pygame.QUIT: return 0;
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE: return 0;
                        if event.key in (pygame.K_LEFT, pygame.K_PAGEUP) and (event.key == pygame.K_LEFT or event.mod & pygame.KMOD_CTRL): self.move(-1); continue;
                        if event.key in (pygame.K_RIGHT, pygame.K_PAGEDOWN) and (event.key == pygame.K_RIGHT or event.mod & pygame.KMOD_CTRL): self.move(1); continue;
                        if event.key == pygame.K_F5: self.toggle_details(); continue;
                    self.panel.handle_event(event);
                self.panel.update(dt);
                self.screen.fill(self.theme.bg);
                for index, button in enumerate(self.tab_buttons):
                    original = button.pressed;
                    button.pressed = index == self.index;
                    button.draw(self.screen);
                    button.pressed = original;
                self.detail_button.draw(self.screen);
                self.viewer.draw(self.screen);
                footer = "Left/Right: tabs   F5: details/summary   Esc: close";
                draw_clipped_text(self.screen, self.small, footer, self.theme.muted, pygame.Rect(18, self.screen.get_height() - self.small.get_height() - 6, self.screen.get_width() - 36, self.small.get_height()));
                pygame.display.flip();
        finally:
            pygame.quit();


def run(report, groups=None, detailed=False):
    return InfoGUI(report, groups=groups, detailed=detailed).run();
