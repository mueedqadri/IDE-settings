import json
import os
import platform
import subprocess

def get_config_path(ide_choice):
    if platform.system() == "Darwin":
        if ide_choice == "vscode":
            return os.path.expanduser("~/Library/Application Support/Code/User/")
        elif ide_choice == "windsurf":
            return os.path.expanduser("~/Library/Application Support/Windsurf/User/")
        elif ide_choice == "cursor":
            return os.path.expanduser("~/.cursor/")
    return None

def update_settings_json(config_path, vim_settings):
    settings_file = os.path.join(config_path, "settings.json")
    settings = {}
    if os.path.exists(settings_file):
        with open(settings_file, "r", encoding="utf-8") as f:
            try:
                settings = json.load(f)
            except json.JSONDecodeError:
                settings = {}
    
    for key, value in vim_settings.items():
        settings[key] = value
        
    with open(settings_file, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)

def update_keybindings_json(config_path, keybindings):
    keybindings_file = os.path.join(config_path, "keybindings.json")
    existing_keybindings = []
    if os.path.exists(keybindings_file):
        with open(keybindings_file, "r", encoding="utf-8") as f:
            try:
                existing_keybindings = json.load(f)
            except json.JSONDecodeError:
                existing_keybindings = []
    
    for new_binding in keybindings:
        if new_binding not in existing_keybindings:
            existing_keybindings.append(new_binding)
            
    with open(keybindings_file, "w", encoding="utf-8") as f:
        json.dump(existing_keybindings, f, indent=4)

def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")

def main():
    ide_choice = input("Which IDE are you making changes to? (vscode/windsurf/cursor): ").lower()
    
    if ide_choice not in ["vscode", "windsurf", "cursor"]:
        print("Invalid choice. Please choose 'vscode', 'windsurf', or 'cursor'.")
        return

    config_path = get_config_path(ide_choice)
    if not config_path:
        print("Unsupported OS or IDE.")
        return

    vim_settings = {
        "vim.leader": "<Space>",
        "vim.hlsearch": True,
        "vim.normalModeKeyBindingsNonRecursive": [
            { "before": ["<S-h>"], "commands": [":bprevious"] },
            { "before": ["<S-l>"], "commands": [":bnext"] },
            { "before": ["leader", "v"], "commands": [":vsplit"] },
            { "before": ["leader", "s"], "commands": [":split"] },
            { "before": ["leader", "h"], "commands": ["workbench.action.focusLeftGroup"] },
            { "before": ["leader", "j"], "commands": ["workbench.action.focusBelowGroup"] },
            { "before": ["leader", "k"], "commands": ["workbench.action.focusAboveGroup"] },
            { "before": ["leader", "l"], "commands": ["workbench.action.focusRightGroup"] },
            { "before": ["leader", "w"], "commands": [":w!"] },
            { "before": ["leader", "q"], "commands": [":q!"] },
            { "before": ["leader", "x"], "commands": [":x!"] },
            { "before": ["[", "d"], "commands": ["editor.action.marker.prev"] },
            { "before": ["]", "d"], "commands": ["editor.action.marker.next"] },
            { "before": ["<leader>", "c", "a"], "commands": ["editor.action.quickFix"] },
            { "before": ["leader", "f"], "commands": ["workbench.action.quickOpen"] },
            { "before": ["leader", "p"], "commands": ["editor.action.formatDocument"] },
            { "before": ["g", "h"], "commands": ["editor.action.showDefinitionPreviewHover"] }
        ],
        "vim.visualModeKeyBindings": [
            { "before": ["<"], "commands": ["editor.action.outdentLines"] },
            { "before": [">"], "commands": ["editor.action.indentLines"] },
            { "before": ["J"], "commands": ["editor.action.moveLinesDowAction"] },
            { "before": ["K"], "commands": ["editor.action.moveLinesUpAction"] },
            { "before": ["leader", "c"], "commands": ["editor.action.commentLine"] }
        ]
    }

    keybindings = [
        {
          "key": "cmd+shift+a",
          "command": "workbench.action.terminal.focusNext",
          "when": "terminalFocus"
        },
        {
          "key": "cmd+shift+b",
          "command": "workbench.action.terminal.focusPrevious",
          "when": "terminalFocus"
        },
        {
          "key": "cmd+shift+j",
          "command": "workbench.action.togglePanel"
        },
        {
          "key": "cmd+shift+n",
          "command": "workbench.action.terminal.new",
          "when": "terminalFocus"
        },
        {
          "key": "cmd+shift+w",
          "command": "workbench.action.terminal.kill",
          "when": "terminalFocus"
        },
        {
          "command": "workbench.action.toggleSidebarVisibility",
          "key": "cmd+e"
        },
        {
          "command": "workbench.files.action.focusFilesExplorer",
          "key": "cmd+e",
          "when": "editorTextFocus"
        },
        {
          "key": "n",
          "command": "explorer.newFile",
          "when": "filesExplorerFocus && !inputFocus"
        },
        {
          "command": "renameFile",
          "key": "r",
          "when": "filesExplorerFocus && !inputFocus"
        },
        {
          "key": "shift+n",
          "command": "explorer.newFolder",
          "when": "explorerViewletFocus"
        },
        {
          "key": "shift+n",
          "command": "workbench.action.newWindow",
          "when": "!explorerViewletFocus"
        },
        {
          "command": "deleteFile",
          "key": "d",
          "when": "filesExplorerFocus && !inputFocus"
        }
    ]

    update_settings_json(config_path, vim_settings)
    update_keybindings_json(config_path, keybindings)

    if platform.system() == "Darwin":
        if ide_choice == "vscode":
            app_name = "Code"
        elif ide_choice == "windsurf":
            app_name = "Windsurf"
        else:
            app_name = "Cursor"
        bundle_id_command = f"osascript -e 'id of app \"{app_name}\"'"
        result = subprocess.run(bundle_id_command, shell=True, capture_output=True, text=True, check=False)
        bundle_id = result.stdout.strip()
        if bundle_id:
            defaults_command = f"defaults write {bundle_id} ApplePressAndHoldEnabled -bool false"
            run_command(defaults_command)
            print(f"Successfully updated settings for {app_name}.")
        else:
            print(f"Could not find bundle ID for {app_name}.")

if __name__ == "__main__":
    main()
