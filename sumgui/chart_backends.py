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

"""Optional Matplotlib/Seaborn renderers for backend-neutral ChartSpec values.

The adapters intentionally render through the non-interactive Agg canvas.  A
Sum application therefore keeps ownership of its Pygame window, icon, event
loop and layout while reusing Matplotlib/Seaborn's mature chart drawing.
""";

import math;

from sumui import ChartSpec, coerce_chart_spec;


def _rgb(value):
    if isinstance(value, str):
        return value;
    values = tuple(value or (0, 0, 0));
    return tuple(max(0.0, min(1.0, float(channel) / 255.0)) for channel in values[:3]);


def _font_kwargs(spec, fallback_size=10):
    kwargs = {"fontsize": int(spec.size or fallback_size)};
    if spec.family:
        kwargs["fontfamily"] = spec.family;
    if spec.bold:
        kwargs["fontweight"] = "bold";
    if spec.italic:
        kwargs["fontstyle"] = "italic";
    return kwargs;


def _palette(spec, theme):
    explicit = spec.option("series_colors", None);
    if explicit:
        return [_rgb(color) for color in explicit];
    values = list(getattr(theme, "palette", ()) or ());
    if not values:
        values = [(40, 110, 200), (0, 150, 136), (145, 90, 190), (220, 105, 40), (80, 160, 90)];
    # A chart series should never accidentally become the panel background.
    background = tuple(getattr(theme, "panel", (255, 255, 255))[:3]);
    visible = [value for value in values if tuple(value[:3]) != background and tuple(value[:3]) != (0, 0, 0)];
    return [_rgb(value) for value in (visible or values)];


def available_chart_renderers():
    result = ["native"];
    try:
        import matplotlib;  # noqa:F401
        result.append("matplotlib");
    except ImportError:
        pass;
    try:
        import seaborn;  # noqa:F401
        if "matplotlib" not in result:
            result.append("matplotlib");
        result.append("seaborn");
    except ImportError:
        pass;
    return tuple(result);


def render_chart_rgba(spec, width, height, theme, renderer="matplotlib"):
    """Render one ChartSpec into an RGBA byte buffer.

    Returns ``(width, height, rgba_bytes)``.  No Pygame module is imported, so
    this function is testable in headless build environments.
    """;
    chart = coerce_chart_spec(spec);
    renderer = str(renderer or chart.option("renderer", "matplotlib")).strip().lower();
    if renderer not in ("matplotlib", "seaborn"):
        raise ValueError("external chart renderer must be matplotlib or seaborn");
    try:
        from matplotlib.backends.backend_agg import FigureCanvasAgg;
        from matplotlib.figure import Figure;
    except ImportError as exc:
        raise RuntimeError("Matplotlib chart rendering requires the optional matplotlib package") from exc;
    sns = None;
    if renderer == "seaborn":
        try:
            import seaborn as sns;
        except ImportError as exc:
            raise RuntimeError("Seaborn chart rendering requires the optional seaborn package") from exc;

    width = max(64, int(width));
    height = max(64, int(height));
    dpi = 100.0;
    figure = Figure(figsize=(width / dpi, height / dpi), dpi=dpi, constrained_layout=True);
    canvas = FigureCanvasAgg(figure);
    panel = _rgb(getattr(theme, "panel", (255, 255, 255)));
    text = _rgb(getattr(theme, "text", (20, 20, 20)));
    muted = _rgb(getattr(theme, "muted", (90, 90, 90)));
    grid = _rgb(getattr(theme, "line", (190, 190, 190)));
    colors = _palette(chart, theme);
    figure.patch.set_facecolor(panel);

    context = sns.axes_style("whitegrid") if sns is not None else None;
    if context is not None:
        context.__enter__();
    try:
        polar = chart.kind == "radar";
        axis = figure.add_subplot(111, polar=polar);
        axis.set_facecolor(panel);
        axis.tick_params(colors=muted, labelsize=int(chart.tick_font.size or chart.font.size or 9));
        for spine in getattr(axis, "spines", {}).values():
            spine.set_color(grid);
        if hasattr(axis, "grid"):
            axis.grid(True, color=grid, linewidth=0.7, alpha=0.65);

        categories = list(chart.categories);
        if chart.kind == "bar":
            horizontal = str(chart.option("orientation", "vertical")).lower() in ("horizontal", "h", "hbar");
            series_count = max(1, len(chart.series));
            count = max([len(series.values) for series in chart.series] or [0]);
            positions = list(range(count));
            if horizontal:
                total_height = 0.8;
                one_height = total_height / series_count;
                for series_index, series in enumerate(chart.series):
                    offset = (series_index - (series_count - 1) / 2.0) * one_height;
                    ys = [position + offset for position in positions[:len(series.values)]];
                    if sns is not None and series_count == 1:
                        sns.barplot(x=list(series.values), y=categories[:len(series.values)] or positions[:len(series.values)], color=colors[series_index % len(colors)], ax=axis, orient="h");
                    else:
                        axis.barh(ys, list(series.values), height=one_height * 0.9, color=colors[series_index % len(colors)], label=series.name or None);
                if categories and not (sns is not None and series_count == 1):
                    axis.set_yticks(positions[:len(categories)], categories[:count]);
            else:
                total_width = 0.8;
                one_width = total_width / series_count;
                for series_index, series in enumerate(chart.series):
                    offset = (series_index - (series_count - 1) / 2.0) * one_width;
                    xs = [position + offset for position in positions[:len(series.values)]];
                    if sns is not None and series_count == 1:
                        sns.barplot(x=categories[:len(series.values)] or positions[:len(series.values)], y=list(series.values), color=colors[series_index % len(colors)], ax=axis);
                    else:
                        axis.bar(xs, list(series.values), width=one_width * 0.9, color=colors[series_index % len(colors)], label=series.name or None);
                if categories and not (sns is not None and series_count == 1):
                    axis.set_xticks(positions[:len(categories)], categories[:count]);
        elif chart.kind in ("line", "scatter"):
            for series_index, series in enumerate(chart.series):
                xs = list(series.x_values) if series.x_values else list(range(len(series.values)));
                ys = list(series.values);
                label = series.name or None;
                color = colors[series_index % len(colors)];
                if chart.kind == "line":
                    if sns is not None:
                        sns.lineplot(x=xs, y=ys, marker="o", color=color, label=label, ax=axis);
                    else:
                        axis.plot(xs, ys, marker="o", color=color, label=label);
                else:
                    if sns is not None:
                        sns.scatterplot(x=xs, y=ys, color=color, label=label, ax=axis);
                    else:
                        axis.scatter(xs, ys, color=color, label=label);
            if categories and chart.kind == "line":
                axis.set_xticks(list(range(len(categories))), categories);
        elif chart.kind == "pie":
            if chart.series:
                values = list(chart.series[0].values);
                labels = categories[:len(values)] if categories else None;
                axis.pie(values, labels=labels, colors=[colors[index % len(colors)] for index in range(len(values))], textprops={"color": text, **_font_kwargs(chart.tick_font.merged(chart.font), 9)});
                axis.set_aspect("equal");
        elif chart.kind == "radar":
            if chart.series:
                values = list(chart.series[0].values);
                count = len(values);
                if count >= 3:
                    angles = [math.tau * index / count for index in range(count)];
                    closed_angles = angles + angles[:1];
                    closed_values = values + values[:1];
                    axis.plot(closed_angles, closed_values, color=colors[0], linewidth=2);
                    axis.fill(closed_angles, closed_values, color=colors[0], alpha=0.20);
                    if categories:
                        axis.set_xticks(angles, categories[:count]);

        if chart.title:
            axis.set_title(chart.title, color=text, **_font_kwargs(chart.title_font.merged(chart.font), 12));
        if chart.x_axis.label and chart.kind != "pie":
            axis.set_xlabel(chart.x_axis.label, color=text, **_font_kwargs(chart.axis_font.merged(chart.font), 10));
        if chart.y_axis.label and chart.kind != "pie":
            axis.set_ylabel(chart.y_axis.label, color=text, **_font_kwargs(chart.axis_font.merged(chart.font), 10));
        if chart.x_axis.minimum is not None or chart.x_axis.maximum is not None:
            axis.set_xlim(left=chart.x_axis.minimum, right=chart.x_axis.maximum);
        if chart.y_axis.minimum is not None or chart.y_axis.maximum is not None:
            axis.set_ylim(bottom=chart.y_axis.minimum, top=chart.y_axis.maximum);
        if chart.legend and chart.kind not in ("pie", "radar") and any(series.name for series in chart.series):
            handles, labels = axis.get_legend_handles_labels();
            if labels:
                legend = axis.legend(handles, labels, frameon=False, prop={"size": int(chart.legend_font.size or chart.font.size or 9)});
                if legend is not None:
                    for label in legend.get_texts():
                        label.set_color(text);
        axis.tick_params(axis="both", colors=muted);
        canvas.draw();
        rgba = bytes(canvas.buffer_rgba());
        return width, height, rgba;
    finally:
        if context is not None:
            context.__exit__(None, None, None);
