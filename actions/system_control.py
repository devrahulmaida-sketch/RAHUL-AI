"""system_control.py — Linux system control via pactl, xrandr, nmcli, etc."""
import subprocess, os, time


def _run(cmd: str) -> str:
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return (r.stdout + r.stderr).strip()
    except Exception as e:
        return str(e)


def system_control(parameters: dict, player=None) -> str:
    action = parameters.get("action", "")
    value  = str(parameters.get("value", ""))
    state  = parameters.get("state", "toggle")

    if action == "volume":
        if value:
            vol = max(0, min(150, int(value)))
            _run(f"pactl set-sink-volume @DEFAULT_SINK@ {vol}%")
            return f"Volume set to {vol}%"
        else:
            out = _run("pactl get-sink-volume @DEFAULT_SINK@")
            return f"Volume info: {out}"

    elif action == "mute_volume":
        _run("pactl set-sink-mute @DEFAULT_SINK@ toggle")
        return "Volume mute toggled."

    elif action == "brightness":
        if value:
            br = max(1, min(100, int(value)))
            # Try multiple methods
            result = _run(f"brightnessctl set {br}%")
            if "error" in result.lower() or not result:
                result = _run(f"xrandr --output $(xrandr | grep ' connected' | head -1 | cut -d' ' -f1) --brightness {br/100:.2f}")
            return f"Brightness set to {br}%"
        return "brightness: provide a value (0-100)"

    elif action == "screenshot":
        ts   = time.strftime("%Y%m%d_%H%M%S")
        path = f"/tmp/screenshot_{ts}.png"
        # Try multiple screenshot tools
        for cmd in [f"scrot {path}", f"import -window root {path}",
                    f"gnome-screenshot -f {path}", f"maim {path}"]:
            if os.system(f"which {cmd.split()[0]} > /dev/null 2>&1") == 0:
                _run(cmd)
                break
        if os.path.exists(path):
            if player: player.show_image(path)
            return f"Screenshot saved: {path}"
        return "Screenshot failed — install scrot: sudo apt install scrot"

    elif action == "wifi":
        if state == "off":
            _run("nmcli radio wifi off")
            return "WiFi turned off."
        elif state == "on":
            _run("nmcli radio wifi on")
            return "WiFi turned on."
        else:
            _run("nmcli radio wifi toggle")
            out = _run("nmcli radio wifi")
            return f"WiFi toggled. Status: {out}"

    elif action == "bluetooth":
        if state == "off":
            _run("rfkill block bluetooth")
            return "Bluetooth turned off."
        elif state == "on":
            _run("rfkill unblock bluetooth")
            return "Bluetooth turned on."
        else:
            out = _run("rfkill list bluetooth")
            return f"Bluetooth: {out}"

    elif action == "lock":
        cmds = ["gnome-screensaver-command -l", "loginctl lock-session",
                "xdg-screensaver lock", "i3lock"]
        for cmd in cmds:
            if os.system(f"which {cmd.split()[0]} > /dev/null 2>&1") == 0:
                _run(cmd + " &")
                return "Screen locked."
        return "Lock failed — no lock utility found."

    elif action == "shutdown":
        _run("shutdown -h now")
        return "Shutting down..."

    elif action == "restart":
        _run("reboot")
        return "Restarting..."

    elif action == "sleep":
        _run("systemctl suspend")
        return "System suspended."

    elif action == "clipboard":
        for tool in ["xclip -o", "xsel --clipboard --output"]:
            out = _run(tool)
            if out:
                return f"Clipboard: {out[:500]}"
        return "Could not read clipboard (install xclip: sudo apt install xclip)"

    elif action == "battery":
        out = _run("upower -i /org/freedesktop/UPower/devices/battery_BAT0 2>/dev/null || cat /sys/class/power_supply/BAT0/capacity 2>/dev/null")
        return f"Battery: {out[:200]}"

    elif action == "uptime":
        return _run("uptime -p")

    elif action == "disk":
        return _run("df -h --output=source,size,used,avail,pcent,target | head -8")

    elif action == "memory":
        return _run("free -h")

    else:
        return f"Unknown system action: {action}"
