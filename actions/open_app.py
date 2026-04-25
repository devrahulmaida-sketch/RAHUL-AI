"""open_app.py — Launch applications on Linux"""
import subprocess, shutil, os


APP_ALIASES = {
    "firefox": "firefox",
    "chrome": "google-chrome",
    "chromium": "chromium-browser",
    "vlc": "vlc",
    "gedit": "gedit",
    "notepad": "gedit",
    "terminal": "x-terminal-emulator",
    "file manager": "nautilus",
    "files": "nautilus",
    "calculator": "gnome-calculator",
    "settings": "gnome-control-center",
    "vscode": "code",
    "code": "code",
    "spotify": "spotify",
    "discord": "discord",
    "telegram": "telegram-desktop",
    "whatsapp": "firefox --new-tab https://web.whatsapp.com",
    "youtube": "firefox --new-tab https://youtube.com",
    "gmail": "firefox --new-tab https://mail.google.com",
    "maps": "firefox --new-tab https://maps.google.com",
}


def open_app(parameters: dict, player=None) -> str:
    name = parameters.get("app_name", "").lower().strip()
    args = parameters.get("args", "")

    cmd = APP_ALIASES.get(name, name)
    if args:
        cmd = f"{cmd} {args}"

    try:
        subprocess.Popen(cmd, shell=True,
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
        if player:
            player.write_log(f"SYS: Launched → {name}")
        return f"Opened: {name}"
    except Exception as e:
        return f"Failed to open {name}: {e}"
