import json
import os
import platform
import subprocess
import sys

def interactive_menu(prompt, options):
    print(prompt)
    try:
        import sys, tty, termios
        fd = sys.stdin.fileno()
        if not sys.stdin.isatty():
            raise ImportError("Not a TTY")
    except (ImportError, AttributeError):
        for i, opt in enumerate(options):
            print(f"{i + 1}. {opt}")
        while True:
            try:
                choice = int(input("Enter number: ")) - 1
                if 0 <= choice < len(options):
                    return options[choice]
            except ValueError:
                pass
            print("Invalid choice.")

    current_idx = 0
    while True:
        for i, option in enumerate(options):
            prefix = " > " if i == current_idx else "   "
            sys.stdout.write(f"\r\033[K{prefix}{option}\n")
        
        sys.stdout.write(f"\033[{len(options)}A")
        sys.stdout.flush()
        
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                ch += sys.stdin.read(2)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            
        if ch == '\x1b[A': # Up
            current_idx = (current_idx - 1) % len(options)
        elif ch == '\x1b[B': # Down
            current_idx = (current_idx + 1) % len(options)
        elif ch == '\r' or ch == '\n': # Enter
            sys.stdout.write(f"\033[{len(options)}B\n")
            return options[current_idx]
        elif ch == '\x03': # Ctrl+C
            sys.stdout.write(f"\033[{len(options)}B\n")
            sys.exit(0)

def get_config_path(env_choice, ide_choice):
    home = os.path.expanduser("~")
    
    if env_choice == "macOS":
        base_path = os.path.join(home, "Library", "Application Support")
        if ide_choice == "vscode":
            return os.path.join(base_path, "Code", "User")
        elif ide_choice == "windsurf":
            return os.path.join(base_path, "Windsurf", "User")
        elif ide_choice == "cursor":
            return os.path.join(base_path, "Cursor", "User")
        elif ide_choice == "antigravity":
            return os.path.join(base_path, "Antigravity", "User")
            
    elif env_choice == "Linux / Arch":
        base_path = os.path.join(home, ".config")
        
        if ide_choice == "vscode":
            standard_path = os.path.join(base_path, "Code", "User")
            oss_path = os.path.join(base_path, "Code - OSS", "User")
            
            if os.path.exists(standard_path):
                return standard_path
            elif os.path.exists(oss_path):
                print(f"Detected 'Code - OSS' directory. Using: {oss_path}")
                return oss_path
            else:
                return standard_path
                
        elif ide_choice == "windsurf":
            return os.path.join(base_path, "Windsurf", "User")
        elif ide_choice == "cursor":
            return os.path.join(base_path, "Cursor", "User")
        elif ide_choice == "antigravity":
            return os.path.join(base_path, "Antigravity", "User")
            
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
    env_options = ["macOS", "Linux / Arch"]
    env_choice = interactive_menu("Which environment are you configuring? Use arrow keys:", env_options)

    ide_options = ["vscode", "windsurf", "cursor", "antigravity"]
    ide_choice = interactive_menu("Which IDE are you making changes to? Use arrow keys:", ide_options)

    config_path = get_config_path(env_choice, ide_choice)
    if not config_path:
        print(f"Could not determine config path for {env_choice}.")
        return

    is_mac = env_choice == "macOS"
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

    if env_choice == "Linux / Arch":
        vim_settings["keyboard.dispatch"] = "keyCode"

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
          "command": "deleteFile",
          "key": "d",
          "when": "filesExplorerFocus && !inputFocus"
        }
    ]

    update_settings_json(config_path, vim_settings)
    update_keybindings_json(config_path, keybindings)

    if is_mac:
        if platform.system() == "Darwin":
            if ide_choice == "vscode":
                app_name = "Code"
            elif ide_choice == "windsurf":
                app_name = "Windsurf"
            elif ide_choice == "cursor":
                app_name = "Cursor"
            else:
                app_name = "Antigravity"
            
            bundle_id_command = f"osascript -e 'id of app \"{app_name}\"'"
            result = subprocess.run(bundle_id_command, shell=True, capture_output=True, text=True, check=False)
            bundle_id = result.stdout.strip()
            
            if bundle_id:
                defaults_command = f"defaults write {bundle_id} ApplePressAndHoldEnabled -bool false"
                run_command(defaults_command)
                print(f"Successfully updated ApplePressAndHold settings for {app_name}.")
            else:
                print(f"Could not find bundle ID for {app_name}.")
        else:
            print("Skipped ApplePressAndHold configuration (script is not running on macOS).")
            
    elif env_choice == "Linux / Arch":
        print("\nLinux configuration complete.")
        print("Note: Key re-mapping changed from 'cmd' to 'ctrl' automatically.")
        print("Note: 'keyboard.dispatch' set to 'keyCode' to fix CapsLock -> Esc issues.")

if __name__ == "__main__":
    main()
