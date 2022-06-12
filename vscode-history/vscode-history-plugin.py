#!/usr/bin/env python3
#
# VSCode history plugin for xbar
#
# <xbar.title>VSCode History</xbar.title>
# <xbar.version>v1.0</xbar.version>
# <xbar.author>fuzmish</xbar.author>
# <xbar.author.github>fuzmish</xbar.author.github>
# <xbar.desc>VSCode History</xbar.desc>
# <xbar.dependencies>python3</xbar.dependencies>
# <xbar.image>https://raw.githubusercontent.com/fuzmish/xbar-plugins/main/vscode-history/docs/screenshot.png</xbar.image>
# <xbar.abouturl>https://github.com/fuzmish/xbar-plugins/tree/main/vscode-history</xbar.abouturl>
#
import collections
import json
from os import path
import re
import subprocess
import sqlite3
import sys
import urllib.parse

# If you want the plugin to use the insiders version of VSCode, set this to True.
USE_INSIDERS = False

# The maximum length of the label string to be displayed in the xbar menu.
MAX_LABEL_TEXT_LENGTH = 120

# The absolute path to the home directory.
# Normally, you do not need to set this manually.
USER_HOME_DIR = path.expanduser("~")

# The shell to be used when executing menu actions.
# This plugin probably does not use shell-specific features.
DEFAULT_SHELL = "/bin/zsh"

if USE_INSIDERS:
    # The directory where vscode persistent data is stored.
    VSCODE_GLOBAL_STORAGE_DIR = path.join(
        USER_HOME_DIR, "Library/Application Support/Code - Insiders/User/globalStorage"
    )

    # The path to the vscode CLI command.
    # If PATH is already configured, you can simply specify "code".
    VSCODE_CLI_BIN = "/Applications/Visual Studio Code - Insiders.app/Contents/Resources/app/bin/code"

    # The path to the JSON file that this plugin will use to persist pinned items.
    PLUGIN_PERSISTENT_DATA_JSON = path.join(
        path.dirname(__file__), "." + path.basename(__file__) + ".insider.json"
    )

    # The icon image data to be displayed in the xbar menu bar.
    # The default value was generated as follows:
    # $ brew install librsvg
    # $ curl -o icon.svg https://upload.wikimedia.org/wikipedia/commons/4/4b/Visual_Studio_Code_Insiders_1.36_icon.svg
    # $ rsvg-convert -d 144 -p 144 -w 16 -h 16 icon.svg | base64 | tr -d '\n' | pbcopy
    VSCODE_LOGO_SVG = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAB+ElEQVQ4jY2SX0hTURzHP+fuThzzTwkOp2klk2UjAl9KfFkQET0V1IOtFwvmQ6w3aYmzEY4ISqJmOSkIEiHsqYyIpB6siCBZpVgRJUGKGdXSuG7cu9NDepvuYv5eDuf3+34/55zf+dlYa/REi4pLi0vcp0PhrKPwdebVWw1ArMmciNaAPo4ut3rq6ycRQsl+T12cfTAS+z+gL+IDmQRUVFnj2fQXAIBhfFEWZYql+VqkCeQYoFrWbbYqhXh7A3cua9zoCix7Um/HQbLyyXJHdmElQ6HSFQdRQNm6fm51X8fvL+TqqVYUBnN0KVC9HD07mw8YfroHIzsKgKOghdCBb6T1XqQECSCfk1qoIhh9b/UKhSuD8wyMNJLJDAFgtzmp3SgRKkx97WPK3kTb+d+WPWCpeT6fzrNkJ+lM/2JeUFEOW+pmGI+u+lMKiaAdt34Pb/UoL98MMa91m1WnI0LzpWFCgZJVbuB6iGAvQkBtZTM3E+3MaWFToSp+djd+5sLJ7dYAIY4DOsgjBGP7uf8hTaDtHD/mjpkqQSl11UmioQ0rASJnlXn4ROcu3K5H5n7so9ezs2HCnET+TWC+GaD1zGMmp3cg0K3KUjemrUc4N07EXvDu0zaQGoZuHmT8/BWfGbhr2RfrCB9e79znr9h8u6erqOVQ+VL6D386oGnQSlf0AAAAAElFTkSuQmCC"
else:
    VSCODE_GLOBAL_STORAGE_DIR = path.join(
        USER_HOME_DIR, "Library/Application Support/Code/User/globalStorage"
    )
    VSCODE_CLI_BIN = (
        "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
    )
    PLUGIN_PERSISTENT_DATA_JSON = path.join(
        path.dirname(__file__), "." + path.basename(__file__) + ".json"
    )
    # curl -o icon.svg https://upload.wikimedia.org/wikipedia/commons/9/9a/Visual_Studio_Code_1.35_icon.svg
    # rsvg-convert -d 144 -p 144 -w 16 -h 16 icon.svg | base64 | tr -d '\n' | pbcopy
    VSCODE_LOGO_SVG = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAACPElEQVQ4jY1SXUiTYRR+3u9ni1rJsrRoNqeyizaURGjDBCEJIutCKOimRVJUskLowgjBi8KCoBC8iYgR/YFSWxebs+giBkmlNpAIpFZZwowYTvbT93e6kG/7PhP0wMP7ct73OZznOYfHOsMzMLY17z2c2Hnmeput2v1+aSqWBQC2HnL9tXhNqsjPaERb3D4fAKCwMB/OvY0H1yxQMxD3/pS4KQJEgODe5y8/amqaW761C6uRd/ePt85JSBKRCCKACKShDPDV3ObgkzbcHi7Y+uIXAHA6eXtf7NgPiRJQwUEjQCPYQMMgEAjQwYSbk5OKaG0GAEuxELZF7gSU9hOBLPFDhmZUO4+jmcFD0YbRrGb0jtk7zlYsHTj3RhEtjcu6FBmpzyI22gDGIDA2W0nF/elbXQsA0DBiLsBlXt1dVF70+IR8/iU0AsCLcHkAxkH4NvNMWZzz6GQAZg80XbOjV6JPCUI2A10vtjmAPa0MEwmLyVkygyEYtQqCnFBUakH6O1DbJKPCLpY0aspXazLaURzpTwFA3eMVEngmvVZUagEAvsrxCOGrlZY/81dKY2N8XXFv56zl4vPjAJie18E2XRptzKn8BwtHJ6Whrqd6ZbEnEpB3OEPG7rlc5p7T09xtmoLhpJWLJJwOHVScTbHyfhBctfWmP/ri/EcGAOX+qXHxy4QfRLJurlGBJstpbjWiMeQH598hOeaFqmWhaqUp/f39K5KO3PCvxS9HZ+8uoTs0XTX48eGGI5ddevofxGALn06FJn0AAAAASUVORK5CYII="

# The path to the .vscdb file where the vscode history is stored.
# This file can be read as a SQLite3 database.
VSCODE_STATE_VSCDB = path.join(VSCODE_GLOBAL_STORAGE_DIR, "state.vscdb")

# The path to the JSON file that contains information about the currently opened VSCode windows.
VSCODE_STORAGE_JSON = path.join(VSCODE_GLOBAL_STORAGE_DIR, "storage.json")

# The icons are used to indicate the type of history entry.
ENTRY_ICON_UNKNOWN = "🦄"
ENTRY_ICON_LOCAL = "💻"
ENTRY_ICON_CONTAINER = "🐋"
ENTRY_ICON_DEV_CONTAINER = "📦"
ENTRY_ICON_SSH = "🔌"
ENTRY_ICON_ACTIVE_WINDOW = "🟢"
ENTRY_ICON_INACTIVE_WINDOW = "⚪"

# The icons used in the xbar menu.
MENU_ICON_PIN = "📌"
MENU_ICON_METADATA = "ℹ️"
MENU_ICON_WORKSPACE = "🏢"
MENU_ICON_FOLDER = "📂"
MENU_ICON_FILE = "📄"
MENU_ICON_EDIT_PINNED_JSON = "⚙️"
MENU_ICON_RECENT = "🔖"
MENU_ICON_ADVANCED = "🔧"
MENU_ICON_OPENED = "🔥"
MENU_ICON_OPEN_NEW_WINDOW = "➕"


def path_unexpand_user(target: str) -> str:
    if target.startswith(USER_HOME_DIR):
        target = "~" + target[len(USER_HOME_DIR) :]
    return target


def flatten_dict(d: dict, prefix="", separator=".") -> dict:
    items = []
    for k, v in d.items():
        new_key = prefix + separator + k if prefix else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten_dict(v, new_key, separator).items())
        else:
            items.append((new_key, v))
    return dict(items)


def create_entry_from_uri(uri: str, entry_type: str):
    ret = {
        "uri": uri,
        "type": entry_type,
        "icon": ENTRY_ICON_UNKNOWN,
        "label": uri,
        "metadata": {},
    }

    # local file/folder uri;; file://
    if uri.startswith("file://"):
        ret["icon"] = ENTRY_ICON_LOCAL
        target = urllib.parse.unquote(uri[7:])
        ret["label"] = path_unexpand_user(target)
        ret["metadata"]["path"] = target

    # remove development;; vscode-remote://
    if uri.startswith("vscode-remote://"):
        match = re.match(r"^vscode-remote://([^%]+)%2B([^/]+)(.*)$", uri)
        if match:
            mode, config, folder = match.groups()
            ret["metadata"]["mode"] = mode
            ret["metadata"]["config"] = config
            ret["metadata"]["folder"] = folder
            try:
                # trying to decode as hex string
                config = bytes.fromhex(config).decode()
                ret["metadata"]["config"] = config
                # trying to decode as json
                config = json.loads(config)
                for k, v in flatten_dict(config, "config").items():
                    ret["metadata"][k] = v
                del ret["metadata"]["config"]
            except:
                pass

            if mode == "dev-container":
                ret["icon"] = ENTRY_ICON_DEV_CONTAINER
                if isinstance(config, dict):
                    hostPath = path_unexpand_user(config["hostPath"])
                    if "settings" in config:
                        if "host" in config["settings"]:
                            host = config["settings"]["host"]
                            if not host.startswith("unix://"):
                                hostPath += f" @ {host}"
                                if host.startswith("ssh://"):
                                    ret["icon"] += ENTRY_ICON_SSH
                else:
                    hostPath = path_unexpand_user(config)
                ret["label"] = f"[DevContainer {hostPath}] {folder}"

            if mode == "attached-container":
                ret["icon"] = ENTRY_ICON_CONTAINER
                if isinstance(config, dict):
                    container = config["containerName"][1:]
                    if "settings" in config:
                        if "host" in config["settings"]:
                            host = config["settings"]["host"]
                            if not host.startswith("unix://"):
                                container += f" @ {host}"
                                if host.startswith("ssh://"):
                                    ret["icon"] += ENTRY_ICON_SSH
                else:
                    container = config
                ret["label"] = f"[Container {container}] {folder}"

            if mode == "ssh-remote":
                hostName = config
                ret["icon"] = ENTRY_ICON_SSH
                ret["label"] = f"[SSH {hostName}] {folder}"

    return ret


def dump_vscdb(vscdb_path=VSCODE_STATE_VSCDB):
    ret = {}
    with sqlite3.connect(f"file:{vscdb_path}?mode=ro", uri=True) as db:
        rows = db.cursor().execute("select key,value from ItemTable")
        for key, value in rows:
            try:
                ret[key] = json.loads(value)
            except:
                ret[key] = value
    return ret


def load_vsc_history(vscdb_path=VSCODE_STATE_VSCDB):
    with sqlite3.connect(f"file:{vscdb_path}?mode=ro", uri=True) as db:
        cur = db.cursor()
        rows = cur.execute(
            'select value from ItemTable where key = "history.recentlyOpenedPathsList"'
        )
        data = json.loads(list(rows)[0][0])
        uris = set()
        ret = []
        for entry in data["entries"]:
            if "folderUri" in entry:
                uri = entry["folderUri"]
                entry_type = "folder"
            elif "fileUri" in entry:
                uri = entry["fileUri"]
                entry_type = "file"
            elif "workspace" in entry:
                if "configPath" not in entry["workspace"]:
                    continue
                uri = entry["workspace"]["configPath"]
                entry_type = "workspace"
            else:
                continue
            if uri in uris:
                continue
            uris.add(uri)
            ret.append(create_entry_from_uri(uri, entry_type))
        return ret


def load_vsc_windows(json_path=VSCODE_STORAGE_JSON):
    uris = set()
    windows = []
    with open(json_path, "r") as fp:
        data = json.load(fp)
        state = data["windowsState"]
        # last active window
        if "lastActiveWindow" in state:
            if "folder" in state["lastActiveWindow"]:
                uri = state["lastActiveWindow"]["folder"]
                uris.add(uri)
                windows.append((create_entry_from_uri(uri, "folder"), True))
        # opened windows
        if "openedWindows" in state:
            for window in state["openedWindows"]:
                if "folder" in window:
                    uri = window["folder"]
                    if uri in uris:
                        continue
                    uris.add(uri)
                    windows.append((create_entry_from_uri(uri, "folder"), False))
    return windows


def load_pinned_entries(json_path=PLUGIN_PERSISTENT_DATA_JSON):
    ret = []
    try:
        with open(json_path, "r") as fp:
            data = json.load(fp)
            if "pinned" in data:
                assert isinstance(data["pinned"], list)
                ret = data["pinned"]
    except:
        pass
    return ret


def save_pinned_entries(entries, json_path=PLUGIN_PERSISTENT_DATA_JSON):
    with open(json_path, "w") as fp:
        json.dump({"pinned": entries}, fp, indent=2, ensure_ascii=False)


def insert_pinned_entry(uri, entry_type, json_path=PLUGIN_PERSISTENT_DATA_JSON):
    # check duplicate
    entries = load_pinned_entries(json_path)
    for entry in entries:
        if entry["uri"] == uri:
            return
    # insert and save
    save_pinned_entries(entries + [create_entry_from_uri(uri, entry_type)], json_path)


def remove_pinned_entry(uri, json_path=PLUGIN_PERSISTENT_DATA_JSON):
    # remove entry
    entries = load_pinned_entries(json_path)
    ret = list(filter(lambda x: x["uri"] != uri, entries))
    # save
    save_pinned_entries(ret, json_path)


def emit_xbar_separator():
    print("---")


def emit_xbar_menu_item(label, options):
    ret = label
    if "icon" in options:
        ret = f"{options['icon']} {label}"
    if "depth" in options:
        ret = ("--" * options["depth"]) + ret
    if "image" in options:
        ret += f" | image=\"{options['image']}\""
    if "refresh" in options and options["refresh"]:
        ret += " | refresh=true"
    if "length" in options:
        ret += f" | length={options['length']}"
    if "command" in options:
        ret += (
            f" | shell=\"{DEFAULT_SHELL}\" param1=-lic param2=\"{options['command']}\""
        )
    print(ret)


def emit_xbar_menu_item_for_entry(
    entry, pinned=False, additional_icon=None, start_depth=1
):
    # create label
    uri = entry["uri"]
    icon = entry["icon"]
    if additional_icon is not None:
        icon = f"{additional_icon}{icon}"
    emit_xbar_menu_item(
        entry["label"],
        {
            "depth": start_depth,
            "icon": icon,
            "length": MAX_LABEL_TEXT_LENGTH,
            "command": f"'{VSCODE_CLI_BIN}' --folder-uri '{uri}'",
        },
    )

    # submenu -> pin/unpin this item
    if pinned:
        emit_xbar_menu_item(
            "Unpin",
            {
                "depth": start_depth + 1,
                "icon": MENU_ICON_PIN,
                "refresh": True,
                "command": f"'{sys.executable}' '{__file__}' unpin '{uri}'",
            },
        )
    else:
        emit_xbar_menu_item(
            "Pin",
            {
                "depth": start_depth + 1,
                "icon": MENU_ICON_PIN,
                "refresh": True,
                "command": f"'{sys.executable}' '{__file__}' pin '{uri}' '{entry['type']}'",
            },
        )

    # submenu -> metadata
    emit_xbar_menu_item(
        "Metadata",
        {
            "depth": start_depth + 1,
            "icon": MENU_ICON_METADATA,
        },
    )
    metadata = dict(entry["metadata"])
    metadata["uri"] = uri
    for key, value in metadata.items():
        emit_xbar_menu_item(
            f"{key}: {value}",
            {
                "depth": start_depth + 2,
                "command": f"printf '%s' '{value}' | pbcopy",
            },
        )


def emit_xbar_menu_categorized(pinned=False):
    if pinned:
        emit_xbar_menu_item("Pinned", {"icon": MENU_ICON_PIN})
        entries = load_pinned_entries()
    else:
        emit_xbar_menu_item("Recent", {"icon": MENU_ICON_RECENT})
        entries = load_vsc_history()

    workspaces = list(filter(lambda e: e["type"] == "workspace", entries))
    if len(workspaces) > 0:
        emit_xbar_menu_item("Workspaces", {"icon": MENU_ICON_WORKSPACE})
        for entry in workspaces:
            emit_xbar_menu_item_for_entry(entry, pinned)

    folders = list(filter(lambda e: e["type"] == "folder", entries))
    if len(folders) > 0:
        emit_xbar_menu_item("Folders", {"icon": MENU_ICON_FOLDER})
        for entry in folders:
            emit_xbar_menu_item_for_entry(entry, pinned)

    files = list(filter(lambda e: e["type"] == "file", entries))
    if len(files) > 0:
        emit_xbar_menu_item("Files", {"icon": MENU_ICON_FILE})
        for entry in files:
            emit_xbar_menu_item_for_entry(entry, pinned)


def generate_xbar_menu():
    # menubar icon
    emit_xbar_menu_item("", {"image": VSCODE_LOGO_SVG})
    emit_xbar_separator()

    # pinend items
    emit_xbar_menu_categorized(True)
    emit_xbar_menu_item(
        "Edit",
        {
            "icon": MENU_ICON_EDIT_PINNED_JSON,
            "refresh": True,
            "command": f"'{VSCODE_CLI_BIN}' -n --wait '{PLUGIN_PERSISTENT_DATA_JSON}'",
        },
    )
    emit_xbar_separator()

    # show recent opened items
    emit_xbar_menu_categorized()
    emit_xbar_menu_item("Advanced", {"icon": MENU_ICON_ADVANCED})
    emit_xbar_menu_item(
        "Export entries",
        {
            "depth": 1,
            "command": f"'{sys.executable}' '{__file__}' export-recent",
        },
    )
    emit_xbar_menu_item(
        "Dump state.vscdb",
        {
            "depth": 1,
            "command": f"'{sys.executable}' '{__file__}' dump-vscdb",
        },
    )
    emit_xbar_menu_item(
        "Open VSCode global storage directory",
        {
            "depth": 1,
            "command": f"open '{VSCODE_GLOBAL_STORAGE_DIR}'",
        },
    )
    emit_xbar_separator()

    # show opened windows
    emit_xbar_menu_item("Opened", {"icon": MENU_ICON_OPENED})
    windows = load_vsc_windows()
    for entry, active in windows:
        icon = ENTRY_ICON_ACTIVE_WINDOW if active else ENTRY_ICON_INACTIVE_WINDOW
        emit_xbar_menu_item_for_entry(entry, additional_icon=icon)
    emit_xbar_menu_item(
        "New",
        {
            "icon": MENU_ICON_OPEN_NEW_WINDOW,
            "command": f"'{VSCODE_CLI_BIN}' -n",
        },
    )


def main():
    args = sys.argv[1:]

    # generate xbar menu
    if len(args) < 1:
        generate_xbar_menu()
        return

    # commands
    command = args[0]
    if command == "pin":
        assert len(args) == 3
        uri, entry_type = args[1:]
        insert_pinned_entry(uri, entry_type)
        return

    if command == "unpin":
        assert len(args) == 2
        uri = args[1]
        remove_pinned_entry(uri)
        return

    if command == "dump-vscdb":
        data = json.dumps(dump_vscdb(), indent=2)
        subprocess.run(["code", "-n", "-"], input=data.encode())
        return

    if command == "export-recent":
        data = json.dumps({"recent": load_vsc_history()}, indent=2, ensure_ascii=False)
        subprocess.run(["code", "-n", "-"], input=data.encode())
        return

    print(f"Unknown command: {command}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
