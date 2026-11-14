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
"""Pure ResourceSchema loading bridge used by graphical dialog frontends.""";

import json;
from pathlib import Path;

from sumui import ResourceSchema;


def load_resource_dialog(resource, operation="create", values=None, theme="ZX", title=None):
    schema = ResourceSchema.from_json(Path(resource).expanduser().read_text(encoding="utf-8"));
    initial = {};
    if values:
        if isinstance(values, dict): initial = dict(values);
        else:
            raw = str(values).strip();
            candidate = Path(raw).expanduser();
            if not raw.startswith("{") and candidate.is_file(): raw = candidate.read_text(encoding="utf-8");
            initial = json.loads(raw);
            if not isinstance(initial, dict): raise ValueError("values must contain a JSON object");
    return schema.dialog_spec(operation, values=initial, theme=theme, title=title);
