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
"""Complete CRUD/LS/IE example driven by ``sumgdialog``.

The application owns only the resource/data semantics.  Graphical forms come
from ``sumgdialog --resource`` and the shared ``sum.resource/1`` schema.
Nothing requires Administrator/root access; the default database lives in the
current user's data directory.
""";

import argparse;
import json;
import os;
from pathlib import Path;
import shutil;
import subprocess;
import sys;

HERE = Path(__file__).resolve().parent;
SCHEMA = HERE / "my_collection.resource.json";


def default_store():
    root = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"));
    return root / "sum" / "examples" / "my_collection.json";


def load_rows(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"));
    except FileNotFoundError:
        return [];
    if not isinstance(data, list): raise ValueError("collection database must contain a JSON array");
    return [dict(item) for item in data if isinstance(item, dict)];


def save_rows(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True);
    temp = path.with_name(path.name + ".tmp");
    temp.write_text(json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8");
    temp.replace(path);


def next_id(rows):
    values = [];
    for row in rows:
        try: values.append(int(row.get("id", 0)));
        except (TypeError, ValueError): pass;
    return str(max(values or [0]) + 1);


def gdialog(*args, capture=False):
    exe = shutil.which("sumgdialog");
    if not exe: raise RuntimeError("sumgdialog is not installed or not in PATH");
    result = subprocess.run([exe] + [str(item) for item in args], text=True, stdout=subprocess.PIPE if capture else None, check=False);
    if result.returncode != 0: return None;
    return (result.stdout or "").strip() if capture else "";


def ask_entry(title, prompt, default="", valid=()):
    args = ["--entry", prompt, "--title", title, "--default", default, "--theme", "Dark"];
    if valid: args += ["--valid-values", ",".join(valid)];
    return gdialog(*args, capture=True);


def form(operation, values=None):
    args = ["--resource", SCHEMA, "--operation", operation, "--theme", "Dark"];
    if values is not None: args += ["--values", json.dumps(values, ensure_ascii=False)];
    raw = gdialog(*args, capture=True);
    return None if raw is None else json.loads(raw);


def format_rows(rows):
    if not rows: return "(empty collection)";
    lines = [];
    for row in rows:
        lines.append("#{id}  {title}  [{type}]  rating={rating}  finished={finished}".format(**{key: row.get(key, "") for key in ("id", "title", "type", "rating", "finished")}));
        if row.get("notes"): lines.append("    {}".format(row["notes"]));
    return "\n".join(lines);


def create(rows):
    row = form("create");
    if row is None: return False;
    row["id"] = str(row.get("id") or next_id(rows));
    if any(str(item.get("id")) == row["id"] for item in rows):
        gdialog("--error", "ID already exists: {}".format(row["id"]), "--title", "My Collection", "--theme", "Dark");
        return False;
    rows.append(row);
    return True;


def find_by_id(rows, identifier):
    return next((item for item in rows if str(item.get("id")) == str(identifier)), None);


def read_one(rows):
    identifier = ask_entry("Read item", "ID:");
    if identifier is None: return False;
    row = find_by_id(rows, identifier);
    if row is None:
        gdialog("--warning", "Item not found: {}".format(identifier), "--title", "My Collection", "--theme", "Dark");
        return False;
    gdialog("--info", json.dumps(row, ensure_ascii=False, indent=2), "--title", "Item #{}".format(identifier), "--theme", "Dark");
    return False;


def update(rows):
    identifier = ask_entry("Update item", "ID:");
    if identifier is None: return False;
    row = find_by_id(rows, identifier);
    if row is None:
        gdialog("--warning", "Item not found: {}".format(identifier), "--title", "My Collection", "--theme", "Dark");
        return False;
    changed = form("update", row);
    if changed is None: return False;
    changed["id"] = identifier;
    row.clear(); row.update(changed);
    return True;


def delete(rows):
    identifier = ask_entry("Delete item", "ID:");
    if identifier is None: return False;
    row = find_by_id(rows, identifier);
    if row is None: return False;
    if gdialog("--yesno", "Delete #{}: {}?".format(identifier, row.get("title", "")), "--title", "Confirm delete", "--theme", "Dark") is None: return False;
    rows.remove(row);
    return True;


def search(rows):
    criteria = form("search");
    if criteria is None: return False;
    wanted = {key: str(value).casefold() for key, value in criteria.items() if value not in (None, "", False)};
    matches = [];
    for row in rows:
        ok = True;
        for key, value in wanted.items():
            if value not in str(row.get(key, "")).casefold(): ok = False; break;
        if ok: matches.append(row);
    gdialog("--info", format_rows(matches), "--title", "Search results", "--theme", "Dark");
    return False;


def import_rows(rows):
    source = ask_entry("Import", "JSON file:");
    if not source: return False;
    incoming = load_rows(Path(source).expanduser());
    existing = {str(item.get("id")) for item in rows};
    added = 0;
    for item in incoming:
        identifier = str(item.get("id") or next_id(rows));
        if identifier in existing: identifier = next_id(rows);
        item["id"] = identifier; existing.add(identifier); rows.append(item); added += 1;
    gdialog("--info", "Imported {} item(s).".format(added), "--title", "Import", "--theme", "Dark");
    return bool(added);


def export_rows(rows):
    target = ask_entry("Export", "JSON file:", str(Path.home() / "my_collection.export.json"));
    if not target: return False;
    save_rows(Path(target).expanduser(), rows);
    gdialog("--info", "Exported {} item(s).".format(len(rows)), "--title", "Export", "--theme", "Dark");
    return False;


def interactive(store):
    rows = load_rows(store);
    actions = ("create", "read", "update", "delete", "list", "search", "import", "export", "quit");
    while True:
        action = ask_entry("My Collection", "Action: create/read/update/delete/list/search/import/export/quit", "list", actions);
        if action is None or action == "quit": break;
        dirty = False;
        if action == "create": dirty = create(rows);
        elif action == "read": read_one(rows);
        elif action == "update": dirty = update(rows);
        elif action == "delete": dirty = delete(rows);
        elif action == "list": gdialog("--info", format_rows(rows), "--title", "My Collection", "--theme", "Dark");
        elif action == "search": search(rows);
        elif action == "import": dirty = import_rows(rows);
        elif action == "export": export_rows(rows);
        if dirty: save_rows(store, rows);
    return 0;


def main(argv=None):
    parser = argparse.ArgumentParser(description="Complete sumgdialog ResourceSchema CRUD example");
    parser.add_argument("--store", type=Path, default=default_store(), help="JSON database (default: user data directory)");
    args = parser.parse_args(argv);
    try: return interactive(args.store.expanduser());
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print("resource_catalog: {}".format(exc), file=sys.stderr);
        return 2;


if __name__ == "__main__":
    raise SystemExit(main());
