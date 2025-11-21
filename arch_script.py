import json
import os
import platform
import subprocess
import sys

def get_config_path(ide_choice):
    system = platform.system()
    home = os.path.expanduser("~")
    
    if system == "Darwin":
        base_path = os.path.join(home, "Library", "Application Support")
        if ide_choice == "vscode":
            return os.path.join(base_path, "Code", "User")
        elif ide_choice == "windsurf":
            return os.path.join(base_path, "Windsurf", "User")
        elif ide_choice == "cursor":
            return os.path.join(base_path, "Cursor", "User")
            
    elif system == "Linux":
        # Standard XDG config path for Arch/Linux
        base_path = os.path.join(home, ".config")
        
        if ide_choice == "vscode":
            # Arch users might use official binary (Code) or Open Source (Code - OSS)
            standard_path = os.path.join(base_path, "Code", "User")
            oss_path = os.path.join(base_path, "Code - OSS", "User")
            
            if os.path.exists(standard_path):
                return standard_path
            elif os.path.exists(oss_path):
                print(f"Detected 'Code - OSS' directory. Using: {oss_path}")
                return oss_path
            else:
                # Default to standard if neither exists yet, let it create folders
                return standard_path
                
        elif ide_choice == "windsurf":
            return os.path.join(base_path, "Windsurf", "User")
        elif ide_choice == "cursor":
            return os.path.join(base_path, "Cursor", "User")
            
    return None

def update_settings_json(config_path, vim_settings):
    if not os.path.exists(config_path):
        try:
            os.makedirs(config_path)
        except OSError as e:
            print(f"Error creating directory {config_path}: {e}")
            return

    settings_file = os.path.join(config_path, "settings.json")
    settings = {}
    
    if os.path.exists(settings_file):
        with open(settings_file, "r", encoding="utf-8") as f:
            try:
                settings = json.load(f)
            except json.JSONDecodeError:
                settings = {}
    
    for key, value in vim_settings.items():
        # Smart merge for nested dictionaries like vim.handleKeys
        if key == "vim.handleKeys" and key in settings and isinstance(settings[key], dict) and isinstance(value, dict):
            settings[key].update(value)
        else:
            settings[key] = value
        
    with open(settings_file, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)
    print(f"Updated settings.json at {settings_file}")

def update_keybindings_json(config_path, keybindings):
    keybindings_file = os.path.join(config_path, "keybindings.json")
    existing_keybindings = []
    
    if os.path.exists(keybindings_file):
        with open(keybindings_file, "r", encoding="utf-8") as f:
            try:
                existing_keybindings = json.load(f)
            except json.JSONDecodeError:
                existing_keybindings = []
    
    # Helper to check if binding exists to avoid duplicates
    # We compare command and key combination
    for new_binding in keybindings:
        exists = False
        for existing in existing_keybindings:
            if (existing.get("key") == new_binding.get("key") and 
                existing.get("command") == new_binding.get("command")):
                exists = True
                break
        
        if not exists:
            existing_keybindings.append(new_binding)
            
    with open(keybindings_file, "w", encoding="utf-8") as f:
        json.dump(existing_keybindings, f, indent=4)
    print(f"Updated keybindings.json at {keybindings_file}")

def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")

def main():
    print(f"Detected OS: {platform.system()}")
    ide_choice = input("Which IDE are you making changes to? (vscode/windsurf/cursor): ").lower()
    
    if ide_choice not in ["vscode", "windsurf", "cursor"]:
        print("Invalid choice. Please choose 'vscode', 'windsurf', or 'cursor'.")
        return

    config_path = get_config_path(ide_choice)
    if not config_path:
        print(f"Could not determine config path for {platform.system()}.")
        return

    # Determine modifier key based on OS
    # macOS uses 'cmd', Linux/Windows uses 'ctrl'
    is_mac = platform.system() == "Darwin"
    mod_key = "cmd" if is_mac else "ctrl"

    vim_settings = {
        "vim.useSystemClipboard": True,
        "vim.leader": "<Space>",
        "vim.hlsearch": True,
        "vim.handleKeys": {
            "<C-w>": False,
            "<C-p>": False
        },
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

    # On Linux, VS Code often ignores system key remappings (like Caps->Esc) 
    # unless we force it to use 'keyCode' dispatch.
    if platform.system() == "Linux":
        vim_settings["keyboard.dispatch"] = "keyCode"

    # Dynamically set keybindings based on the modifier key (cmd vs ctrl)
    keybindings = [
        {
          "key": f"{mod_key}+shift+a",
          "command": "workbench.action.terminal.focusNext",
          "when": "terminalFocus"
        },
        {
          "key": f"{mod_key}+shift+b",
          "command": "workbench.action.terminal.focusPrevious",
          "when": "terminalFocus"
        },
        {
          "key": f"{mod_key}+shift+j",
          "command": "workbench.action.togglePanel"
        },
        {
          "key": f"{mod_key}+shift+n",
          "command": "workbench.action.terminal.new",
          "when": "terminalFocus"
        },
        {
          "key": f"{mod_key}+shift+w",
          "command": "workbench.action.terminal.kill",
          "when": "terminalFocus"
        },
        {
          "command": "workbench.action.toggleSidebarVisibility",
          "key": f"{mod_key}+e"
        },
        {
          "command": "workbench.files.action.focusFilesExplorer",
          "key": f"{mod_key}+e",
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

    # macOS Specific: Disable PressAndHold for repeated keys in Vim
    if is_mac:
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
            print(f"Successfully updated ApplePressAndHold settings for {app_name}.")
        else:
            print(f"Could not find bundle ID for {app_name}.")
    
    # Linux Specific Message
    elif platform.system() == "Linux":
        print("\nLinux configuration complete.")
        print("Note: Key re-mapping changed from 'cmd' to 'ctrl' automatically.")
        print("Note: 'keyboard.dispatch' set to 'keyCode' to fix CapsLock -> Esc issues.")

if __name__ == "__main__":
    main()
