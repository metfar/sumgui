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
#

import math;
import pygame;
from sumui import ChartSpec, coerce_chart_spec;
from .widgets import Widget, draw_clipped_text, with_clip;
from .theme import DEFAULT_THEME;


def _nice_number(value):
    if abs(value - int(value)) < 0.000001:
        return str(int(value));
    return ("{:.2f}".format(value)).rstrip("0").rstrip(".");


class ChartBase(Widget):
    def __init__(self, rect, font, title="", x_label="", y_label="", theme=None, focusable=False, tab_index=0, fonts=None):
        super().__init__(rect, focusable=focusable, tab_index=tab_index);
        self.font = font;
        fonts = dict(fonts or {});
        self.title_font = fonts.get("title", font);
        self.axis_font = fonts.get("axis", font);
        self.tick_font = fonts.get("tick", font);
        self.legend_font = fonts.get("legend", font);
        self.title = title;
        self.x_label = x_label;
        self.y_label = y_label;
        self.theme = theme or DEFAULT_THEME;
        self.tooltip = None;

    def data_rect(self):
        left = 42 if self.y_label else 30;
        top = 30 if self.title else 12;
        right = 14;
        bottom = 38 if self.x_label else 26;
        rect = pygame.Rect(self.rect.x + left, self.rect.y + top, self.rect.width - left - right, self.rect.height - top - bottom);
        if rect.width < 1:
            rect.width = 1;
        if rect.height < 1:
            rect.height = 1;
        return rect;

    def draw_frame(self, screen):
        pygame.draw.rect(screen, self.theme.panel, self.rect, border_radius=8);
        pygame.draw.rect(screen, self.theme.cursor if self.has_focus else self.theme.line, self.rect, 3 if self.has_focus else 2, border_radius=8);
        if self.title:
            draw_clipped_text(screen, self.title_font, self.title, self.theme.text, pygame.Rect(self.rect.x + 8, self.rect.y + 6, self.rect.width - 16, self.title_font.get_height()));

    def draw_axes(self, screen, chart, min_x, max_x, min_y, max_y, x_ticks=3, y_ticks=3):
        pygame.draw.line(screen, self.theme.line, (chart.x, chart.bottom), (chart.right, chart.bottom), 1);
        pygame.draw.line(screen, self.theme.line, (chart.x, chart.y), (chart.x, chart.bottom), 1);
        if y_ticks > 1:
            for index in range(y_ticks):
                fraction = index / (y_ticks - 1);
                y = chart.bottom - int(fraction * chart.height);
                value = min_y + fraction * (max_y - min_y);
                pygame.draw.line(screen, self.theme.line, (chart.x - 3, y), (chart.right, y), 1);
                draw_clipped_text(screen, self.tick_font, _nice_number(value), self.theme.muted, pygame.Rect(self.rect.x + 4, y - self.tick_font.get_height() // 2, chart.x - self.rect.x - 8, self.tick_font.get_height()), align="right");
        if x_ticks > 1:
            for index in range(x_ticks):
                fraction = index / (x_ticks - 1);
                x = chart.x + int(fraction * chart.width);
                value = min_x + fraction * (max_x - min_x);
                pygame.draw.line(screen, self.theme.line, (x, chart.bottom), (x, chart.bottom + 3), 1);
                draw_clipped_text(screen, self.tick_font, _nice_number(value), self.theme.muted, pygame.Rect(x - 20, chart.bottom + 4, 40, self.tick_font.get_height()), align="center");
        if self.x_label:
            draw_clipped_text(screen, self.axis_font, self.x_label, self.theme.text, pygame.Rect(chart.x, self.rect.bottom - self.axis_font.get_height() - 4, chart.width, self.axis_font.get_height()), align="center");
        if self.y_label:
            draw_clipped_text(screen, self.axis_font, self.y_label, self.theme.text, pygame.Rect(self.rect.x + 6, self.rect.y + 26, chart.x - self.rect.x - 10, self.axis_font.get_height()), align="center");

    def draw_tooltip(self, screen):
        if self.tooltip is None:
            return;
        text, pos = self.tooltip;
        w = min(self.rect.width - 12, self.font.size(text)[0] + 12);
        h = self.font.get_height() + 8;
        x = max(self.rect.x + 4, min(self.rect.right - w - 4, pos[0] + 10));
        y = max(self.rect.y + 4, min(self.rect.bottom - h - 4, pos[1] - h - 10));
        tip_rect = pygame.Rect(x, y, w, h);
        pygame.draw.rect(screen, self.theme.bg, tip_rect);
        pygame.draw.rect(screen, self.theme.cursor, tip_rect, 2);
        draw_clipped_text(screen, self.font, text, self.theme.text, tip_rect.inflate(-8, -4), valign="middle");

    def map_point(self, chart, x, y, min_x, max_x, min_y, max_y):
        if max_x == min_x:
            max_x += 1;
        if max_y == min_y:
            max_y += 1;
        sx = chart.x + int((x - min_x) * max(1, chart.width - 1) / (max_x - min_x));
        sy = chart.bottom - 1 - int((y - min_y) * max(1, chart.height - 1) / (max_y - min_y));
        return sx, sy;

    def unmap_point(self, chart, sx, sy, min_x, max_x, min_y, max_y):
        sx = max(chart.x, min(chart.right - 1, sx));
        sy = max(chart.y, min(chart.bottom - 1, sy));
        if max_x == min_x:
            max_x += 1;
        if max_y == min_y:
            max_y += 1;
        x = min_x + ((sx - chart.x) / max(1, chart.width - 1)) * (max_x - min_x);
        y = min_y + ((chart.bottom - 1 - sy) / max(1, chart.height - 1)) * (max_y - min_y);
        return x, y;


class ChartView(ChartBase):
    """Render one backend-neutral sumui.ChartSpec through Pygame.""";

    def __init__(self, rect, spec, font, theme=None, focusable=False, tab_index=0, fonts=None):
        self.spec = coerce_chart_spec(spec);
        super().__init__(
            rect, font, self.spec.title, self.spec.x_axis.label, self.spec.y_axis.label,
            theme=theme, focusable=focusable, tab_index=tab_index, fonts=fonts,
        );

    def set_spec(self, spec):
        self.spec = coerce_chart_spec(spec);
        self.title = self.spec.title;
        self.x_label = self.spec.x_axis.label;
        self.y_label = self.spec.y_axis.label;
        return self;

    def _series_color(self, index):
        explicit = self.spec.option("series_colors", None);
        if explicit:
            colors = list(explicit);
            if colors:
                value=colors[int(index) % len(colors)]; return pygame.Color(value) if isinstance(value,str) else value;
        if self.theme.palette:
            panel = tuple(self.theme.panel[:3]);
            visible = [color for color in self.theme.palette if sum(abs(int(color[channel]) - int(panel[channel])) for channel in range(3)) >= 180];
            colors = visible or list(self.theme.palette);
            return colors[int(index) % len(colors)];
        return self.theme.button;

    def _bounds(self):
        points = [];
        for series in self.spec.series:
            points.extend(series.points);
        if not points:
            return 0.0, 1.0, 0.0, 1.0;
        xs = [point[0] for point in points];
        ys = [point[1] for point in points];
        min_x = self.spec.x_axis.minimum if self.spec.x_axis.minimum is not None else min(xs);
        max_x = self.spec.x_axis.maximum if self.spec.x_axis.maximum is not None else max(xs);
        min_y = self.spec.y_axis.minimum if self.spec.y_axis.minimum is not None else min(ys);
        max_y = self.spec.y_axis.maximum if self.spec.y_axis.maximum is not None else max(ys);
        if max_x == min_x:
            max_x += 1;
        if max_y == min_y:
            max_y += 1;
        return min_x, max_x, min_y, max_y;

    def _draw_bar(self, screen):
        if not self.spec.series:
            return;
        if str(self.spec.option("orientation", "vertical")).lower() in ("horizontal", "h", "hbar"):
            return self._draw_horizontal_bar(screen);
        chart = self.data_rect();
        categories = list(self.spec.categories);
        series_count = max(1, len(self.spec.series));
        value_count = max([len(series.values) for series in self.spec.series] or [0]);
        if value_count <= 0:
            return;
        if self.spec.stacked:
            positives=[0.0]*value_count; negatives=[0.0]*value_count;
            for series in self.spec.series:
                for index,value in enumerate(series.values):
                    if value >= 0: positives[index] += value;
                    else: negatives[index] += value;
            min_value = self.spec.y_axis.minimum if self.spec.y_axis.minimum is not None else min([0.0]+negatives);
            max_value = self.spec.y_axis.maximum if self.spec.y_axis.maximum is not None else max([0.0]+positives);
        else:
            all_values=[value for series in self.spec.series for value in series.values];
            min_value = self.spec.y_axis.minimum if self.spec.y_axis.minimum is not None else min([0.0] + all_values);
            max_value = self.spec.y_axis.maximum if self.spec.y_axis.maximum is not None else max([0.0] + all_values);
        if max_value <= min_value: max_value=min_value+1.0;
        self.draw_axes(screen, chart, 0, max(1, value_count - 1), min_value, max_value, x_ticks=0, y_ticks=3);
        group_width=max(1,chart.width//value_count);
        zero_y=chart.bottom-int((0.0-min_value)*chart.height/(max_value-min_value)); zero_y=max(chart.y,min(chart.bottom,zero_y));
        pos=[0.0]*value_count; neg=[0.0]*value_count;
        for series_index,series in enumerate(self.spec.series):
            color=self._series_color(series_index);
            bar_width=max(1,group_width-6) if self.spec.stacked else max(1,(group_width-4)//series_count);
            for index,value in enumerate(series.values):
                if self.spec.stacked:
                    base=pos[index] if value>=0 else neg[index]; top_value=base+value;
                    if value>=0: pos[index]=top_value;
                    else: neg[index]=top_value;
                    y1=chart.bottom-int((base-min_value)*chart.height/(max_value-min_value)); y2=chart.bottom-int((top_value-min_value)*chart.height/(max_value-min_value));
                    x=chart.x+index*group_width+3;
                else:
                    y1=zero_y; y2=chart.bottom-int((value-min_value)*chart.height/(max_value-min_value)); x=chart.x+index*group_width+2+series_index*bar_width;
                rect=pygame.Rect(x,min(y1,y2),max(1,bar_width-1),max(1,abs(y2-y1))); pygame.draw.rect(screen,color,rect);
                if self.spec.kind == "bar3d":
                    depth=max(2,min(7,bar_width//5));
                    pygame.draw.polygon(screen,color,[(rect.right,rect.top),(rect.right+depth,rect.top-depth),(rect.right+depth,rect.bottom-depth),(rect.right,rect.bottom)]);
                    pygame.draw.polygon(screen,color,[(rect.left,rect.top),(rect.left+depth,rect.top-depth),(rect.right+depth,rect.top-depth),(rect.right,rect.top)]);
        for index in range(value_count):
            label=categories[index] if index<len(categories) else str(index+1); x=chart.x+index*group_width;
            draw_clipped_text(screen,self.tick_font,label,self.theme.muted,pygame.Rect(x,chart.bottom+4,group_width,self.tick_font.get_height()),align="center");

    def _draw_horizontal_bar(self, screen):
        chart = self.data_rect();
        categories = list(self.spec.categories);
        series_count = max(1, len(self.spec.series));
        value_count = max([len(series.values) for series in self.spec.series] or [0]);
        if value_count <= 0:
            return;
        all_values = [value for series in self.spec.series for value in series.values];
        min_value = self.spec.x_axis.minimum if self.spec.x_axis.minimum is not None else min([0.0] + all_values);
        max_value = self.spec.x_axis.maximum if self.spec.x_axis.maximum is not None else max([0.0] + all_values);
        if max_value <= min_value:
            max_value = min_value + 1.0;
        pygame.draw.line(screen, self.theme.line, (chart.x, chart.y), (chart.x, chart.bottom), 1);
        group_height = max(1, chart.height // value_count);
        bar_height = max(1, (group_height - 4) // series_count);
        zero_x = chart.x + int((0.0 - min_value) * chart.width / (max_value - min_value));
        zero_x = max(chart.x, min(chart.right, zero_x));
        for series_index, series in enumerate(self.spec.series):
            color = self._series_color(series_index);
            for index, value in enumerate(series.values):
                y = chart.y + index * group_height + 2 + series_index * bar_height;
                value_x = chart.x + int((value - min_value) * chart.width / (max_value - min_value));
                left = min(zero_x, value_x);
                right = max(zero_x, value_x);
                rect = pygame.Rect(left, y, max(1, right - left), max(1, bar_height - 1));
                pygame.draw.rect(screen, color, rect);
        for index in range(value_count):
            label = categories[index] if index < len(categories) else str(index + 1);
            y = chart.y + index * group_height;
            draw_clipped_text(screen, self.tick_font, label, self.theme.muted, pygame.Rect(self.rect.x + 4, y, max(1, chart.x - self.rect.x - 8), group_height), align="right", valign="middle");
        for index in range(3):
            fraction = index / 2.0;
            x = chart.x + int(fraction * chart.width);
            value = min_value + fraction * (max_value - min_value);
            pygame.draw.line(screen, self.theme.line, (x, chart.bottom), (x, chart.bottom + 3), 1);
            draw_clipped_text(screen, self.tick_font, _nice_number(value), self.theme.muted, pygame.Rect(x - 24, chart.bottom + 4, 48, self.tick_font.get_height()), align="center");

    def _draw_radar(self, screen):
        if not self.spec.series:
            return;
        values = list(self.spec.series[0].values);
        if len(values) < 3:
            return;
        categories = list(self.spec.categories);
        body = pygame.Rect(self.rect.x + 32, self.rect.y + 34, max(1, self.rect.width - 64), max(1, self.rect.height - 68));
        center = body.center;
        radius = max(1, min(body.width, body.height) // 2 - 12);
        maximum = self.spec.y_axis.maximum if self.spec.y_axis.maximum is not None else max([1.0] + [abs(value) for value in values]);
        minimum = self.spec.y_axis.minimum if self.spec.y_axis.minimum is not None else 0.0;
        if maximum <= minimum:
            maximum = minimum + 1.0;
        count = len(values);
        axes = [];
        for index in range(count):
            angle = -math.pi / 2.0 + math.tau * index / count;
            axes.append((center[0] + int(math.cos(angle) * radius), center[1] + int(math.sin(angle) * radius), angle));
        for level in (0.25, 0.5, 0.75, 1.0):
            points = [(center[0] + int(math.cos(angle) * radius * level), center[1] + int(math.sin(angle) * radius * level)) for unused_x, unused_y, angle in axes];
            pygame.draw.polygon(screen, self.theme.line, points, 1);
        for index, (x, y, angle) in enumerate(axes):
            pygame.draw.line(screen, self.theme.line, center, (x, y), 1);
            label = categories[index] if index < len(categories) else str(index + 1);
            lx = center[0] + int(math.cos(angle) * (radius + 18));
            ly = center[1] + int(math.sin(angle) * (radius + 18));
            draw_clipped_text(screen, self.tick_font, label, self.theme.text, pygame.Rect(lx - 38, ly - self.tick_font.get_height() // 2, 76, self.tick_font.get_height()), align="center");
        mapped = [];
        for index, value in enumerate(values):
            fraction = max(0.0, min(1.0, (float(value) - minimum) / (maximum - minimum)));
            angle = axes[index][2];
            mapped.append((center[0] + int(math.cos(angle) * radius * fraction), center[1] + int(math.sin(angle) * radius * fraction)));
        color = self._series_color(0);
        pygame.draw.polygon(screen, color, mapped, 3);
        for point in mapped:
            pygame.draw.circle(screen, color, point, 4);

    def _draw_line_or_scatter(self, screen):
        chart = self.data_rect();
        min_x, max_x, min_y, max_y = self._bounds();
        category_axis = self.spec.kind == "line" and bool(self.spec.categories);
        self.draw_axes(screen, chart, min_x, max_x, min_y, max_y, x_ticks=0 if category_axis else 3, y_ticks=3);
        if category_axis:
            count = len(self.spec.categories);
            for index, label in enumerate(self.spec.categories):
                fraction = index / max(1, count - 1);
                x = chart.x + int(fraction * chart.width);
                draw_clipped_text(screen, self.tick_font, str(label), self.theme.muted, pygame.Rect(x - 40, chart.bottom + 4, 80, self.tick_font.get_height()), align="center");
        for series_index, series in enumerate(self.spec.series):
            color = self.theme.palette[series_index % len(self.theme.palette)] if self.theme.palette else self.theme.cursor;
            mapped = [self.map_point(chart, x, y, min_x, max_x, min_y, max_y) for x, y in series.points];
            if self.spec.kind == "line" and len(mapped) >= 2:
                pygame.draw.lines(screen, color, False, mapped, 2);
            for point in mapped:
                pygame.draw.circle(screen, color, point, 4);

    def _draw_pie(self, screen):
        if not self.spec.series:
            return;
        values = [max(0.0, value) for value in self.spec.series[0].values];
        total = sum(values);
        if total <= 0:
            return;
        body = pygame.Rect(self.rect.x + 8, self.rect.y + 30, self.rect.width - 16, self.rect.height - 38);
        center = body.center;
        radius = max(1, min(body.width, body.height) // 3);
        start = 0.0;
        for index, value in enumerate(values):
            angle = (value / total) * math.tau;
            points = [center];
            steps = max(3, int(angle * 16));
            for step in range(steps + 1):
                current = start + angle * step / steps;
                points.append((center[0] + int(math.cos(current) * radius), center[1] + int(math.sin(current) * radius)));
            color = self._series_color(index);
            pygame.draw.polygon(screen, color, points);
            start += angle;
        pygame.draw.circle(screen, self.theme.line, center, radius, 2);

    def _draw_legend(self, screen):
        if not self.spec.legend:
            return;
        labels = [];
        if self.spec.kind == "pie" and self.spec.categories:
            labels = [(str(label), index) for index, label in enumerate(self.spec.categories)];
        else:
            labels = [(series.name, index) for index, series in enumerate(self.spec.series) if series.name];
        if not labels:
            return;
        x = self.rect.right - 8;
        y = self.rect.y + 6;
        for label, index in reversed(labels[:6]):
            text_width = self.legend_font.size(label)[0] if self.legend_font is not None else len(label) * 8;
            width = min(self.rect.width // 2, text_width + 20);
            x -= width;
            color = self._series_color(index);
            pygame.draw.rect(screen, color, pygame.Rect(x, y + 3, 10, 10));
            draw_clipped_text(screen, self.legend_font, label, self.theme.text, pygame.Rect(x + 14, y, max(1, width - 14), self.legend_font.get_height()));
            x -= 8;

    def draw(self, screen):
        self.draw_frame(screen);
        def draw_inside():
            if self.spec.kind in ("bar", "bar3d"):
                self._draw_bar(screen);
            elif self.spec.kind in ("line", "scatter"):
                self._draw_line_or_scatter(screen);
            elif self.spec.kind == "pie":
                self._draw_pie(screen);
            elif self.spec.kind == "radar":
                self._draw_radar(screen);
        with_clip(screen, self.rect.inflate(-4, -4), draw_inside);
        self._draw_legend(screen);


class BarChart(ChartBase):
    def __init__(self, rect, data, font, title="", theme=None, x_label="", y_label=""):
        super().__init__(rect, font, title, x_label, y_label, theme);
        self.data = data;

    def draw(self, screen):
        self.draw_frame(screen);
        if not self.data:
            return;
        values = [item[1] for item in self.data];
        max_value = max(values + [1]);
        chart = self.data_rect();
        def draw_inside():
            self.draw_axes(screen, chart, 0, max(1, len(self.data) - 1), 0, max_value, x_ticks=0, y_ticks=3);
            bar_w = max(1, chart.width // len(self.data));
            for index, item in enumerate(self.data):
                label, value = item;
                h = int((value / max_value) * max(1, chart.height));
                x = chart.x + index * bar_w;
                y = chart.bottom - h;
                rect = pygame.Rect(x + 3, y, max(1, bar_w - 6), h);
                pygame.draw.rect(screen, self.theme.button, rect);
                draw_clipped_text(screen, self.tick_font, str(label), self.theme.muted, pygame.Rect(x + 3, chart.bottom + 4, max(1, bar_w - 6), self.tick_font.get_height()), align="center");
            if self.x_label:
                draw_clipped_text(screen, self.axis_font, self.x_label, self.theme.text, pygame.Rect(chart.x, self.rect.bottom - self.axis_font.get_height() - 4, chart.width, self.axis_font.get_height()), align="center");
        with_clip(screen, self.rect.inflate(-4, -4), draw_inside);


class LineChart(ChartBase):
    def __init__(self, rect, points, font, title="", theme=None, x_label="", y_label="", editable=False, on_change=None, tab_index=0):
        super().__init__(rect, font, title, x_label, y_label, theme, focusable=editable, tab_index=tab_index);
        self.points = list(points);
        self.editable = bool(editable);
        self.on_change = on_change;
        self.selected_index = None;
        self.dragging = False;
        self.drag_radius = 10;
        self._cached = None;

    def bounds(self):
        xs = [p[0] for p in self.points] or [0, 1];
        ys = [p[1] for p in self.points] or [0, 1];
        min_x = min(xs);
        max_x = max(xs);
        min_y = min(ys);
        max_y = max(ys);
        if max_x == min_x:
            max_x += 1;
        if max_y == min_y:
            max_y += 1;
        return min_x, max_x, min_y, max_y;

    def mapped_points(self):
        chart = self.data_rect();
        min_x, max_x, min_y, max_y = self.bounds();
        mapped = [];
        for x, y in self.points:
            mapped.append(self.map_point(chart, x, y, min_x, max_x, min_y, max_y));
        self._cached = (chart, min_x, max_x, min_y, max_y, mapped);
        return mapped;

    def nearest_point_index(self, pos):
        mapped = self.mapped_points();
        best_index = None;
        best_dist = None;
        for index, point in enumerate(mapped):
            dx = point[0] - pos[0];
            dy = point[1] - pos[1];
            dist = dx * dx + dy * dy;
            if best_dist is None or dist < best_dist:
                best_dist = dist;
                best_index = index;
        if best_dist is not None and best_dist <= self.drag_radius * self.drag_radius:
            return best_index;
        return None;

    def set_selected_from_pos(self, pos):
        index = self.nearest_point_index(pos);
        self.selected_index = index;
        if index is not None:
            x, y = self.points[index];
            self.tooltip = ("(" + _nice_number(x) + ", " + _nice_number(y) + ")", pos);
        else:
            self.tooltip = None;
        return index;

    def update_point_from_pos(self, pos):
        if self.selected_index is None:
            return;
        chart, min_x, max_x, min_y, max_y, unused = self._cached or (self.data_rect(), *self.bounds(), []);
        x, y = self.unmap_point(chart, pos[0], pos[1], min_x, max_x, min_y, max_y);
        old_x, old_y = self.points[self.selected_index];
        self.points[self.selected_index] = (old_x, y);
        self.tooltip = ("(" + _nice_number(old_x) + ", " + _nice_number(y) + ")", pos);
        if self.on_change is not None:
            self.on_change(self, self.selected_index, self.points[self.selected_index]);

    def handle_event(self, event):
        if not self.editable:
            return False;
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            index = self.set_selected_from_pos(event.pos);
            if index is not None:
                self.dragging = True;
                self.update_point_from_pos(event.pos);
                return True;
            return True;
        if event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.update_point_from_pos(event.pos);
                return True;
            if self.rect.collidepoint(event.pos):
                self.set_selected_from_pos(event.pos);
        if event.type == pygame.MOUSEBUTTONUP and self.dragging:
            self.dragging = False;
            return True;
        if event.type == pygame.KEYDOWN and self.has_focus and self.selected_index is not None:
            x, y = self.points[self.selected_index];
            ys = [p[1] for p in self.points] or [0, 1];
            step = max(0.1, (max(ys) - min(ys)) / 50.0);
            if event.key == pygame.K_UP:
                self.points[self.selected_index] = (x, y + step);
                return True;
            if event.key == pygame.K_DOWN:
                self.points[self.selected_index] = (x, y - step);
                return True;
        return False;

    def draw(self, screen):
        self.draw_frame(screen);
        if len(self.points) < 1:
            return;
        chart = self.data_rect();
        min_x, max_x, min_y, max_y = self.bounds();
        mapped = [];
        for x, y in self.points:
            mapped.append(self.map_point(chart, x, y, min_x, max_x, min_y, max_y));
        self._cached = (chart, min_x, max_x, min_y, max_y, mapped);
        def draw_inside():
            self.draw_axes(screen, chart, min_x, max_x, min_y, max_y, x_ticks=3, y_ticks=3);
            if len(mapped) >= 2:
                pygame.draw.lines(screen, self.theme.cursor, False, mapped, 3);
            for index, point in enumerate(mapped):
                color = self.theme.button if index == self.selected_index else self.theme.text;
                pygame.draw.circle(screen, color, point, 5 if index == self.selected_index else 4);
                pygame.draw.circle(screen, self.theme.line, point, 5 if index == self.selected_index else 4, 1);
            self.draw_tooltip(screen);
        with_clip(screen, self.rect.inflate(-4, -4), draw_inside);


class PieChart(ChartBase):
    def __init__(self, rect, data, font, title="", theme=None):
        super().__init__(rect, font, title, "", "", theme);
        self.data = data;

    def draw(self, screen):
        self.draw_frame(screen);
        total = sum(value for label, value in self.data);
        if total <= 0:
            return;
        body = pygame.Rect(self.rect.x + 8, self.rect.y + 30, self.rect.width - 16, self.rect.height - 38);
        center = body.center;
        radius = max(1, min(body.width, body.height) // 3);
        def draw_inside():
            start = 0.0;
            for index, item in enumerate(self.data):
                label, value = item;
                angle = (value / total) * math.tau;
                points = [center];
                steps = max(3, int(angle * 16));
                for step in range(steps + 1):
                    a = start + angle * step / steps;
                    points.append((center[0] + int(math.cos(a) * radius), center[1] + int(math.sin(a) * radius)));
                pygame.draw.polygon(screen, self.theme.palette[index % len(self.theme.palette)], points);
                start += angle;
            pygame.draw.circle(screen, self.theme.line, center, radius, 2);
        with_clip(screen, self.rect.inflate(-4, -4), draw_inside);


class ScatterChart(ChartBase):
    def __init__(self, rect, points, font, title="", theme=None, x_label="", y_label=""):
        super().__init__(rect, font, title, x_label, y_label, theme);
        self.points = points;
        self.hover_index = None;

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION and self.rect.collidepoint(event.pos):
            chart = self.data_rect();
            xs = [p[0] for p in self.points] or [0, 1];
            ys = [p[1] for p in self.points] or [0, 1];
            min_x, max_x, min_y, max_y = min(xs), max(xs), min(ys), max(ys);
            best_index = None;
            best_dist = None;
            for index, point in enumerate(self.points):
                sx, sy = self.map_point(chart, point[0], point[1], min_x, max_x, min_y, max_y);
                dist = (sx - event.pos[0]) ** 2 + (sy - event.pos[1]) ** 2;
                if best_dist is None or dist < best_dist:
                    best_dist = dist;
                    best_index = index;
            if best_dist is not None and best_dist < 100:
                self.hover_index = best_index;
                x, y = self.points[best_index];
                self.tooltip = ("(" + _nice_number(x) + ", " + _nice_number(y) + ")", event.pos);
            else:
                self.hover_index = None;
                self.tooltip = None;
        return False;

    def draw(self, screen):
        self.draw_frame(screen);
        if not self.points:
            return;
        chart = self.data_rect();
        xs = [p[0] for p in self.points];
        ys = [p[1] for p in self.points];
        min_x = min(xs);
        max_x = max(xs);
        min_y = min(ys);
        max_y = max(ys);
        if max_x == min_x:
            max_x += 1;
        if max_y == min_y:
            max_y += 1;
        def draw_inside():
            self.draw_axes(screen, chart, min_x, max_x, min_y, max_y, x_ticks=3, y_ticks=3);
            for index, point in enumerate(self.points):
                x, y = point;
                sx, sy = self.map_point(chart, x, y, min_x, max_x, min_y, max_y);
                radius = 5 if index == self.hover_index else 4;
                pygame.draw.circle(screen, self.theme.cursor, (sx, sy), radius);
            self.draw_tooltip(screen);
        with_clip(screen, self.rect.inflate(-4, -4), draw_inside);
