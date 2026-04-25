"""
RAHUL Advanced AI — Linux Setup Script
Run: python3 setup.py
"""
import subprocess, sys, os, shutil, platform


def run(cmd, check=True):
    print(f"  → {cmd}")
    result = subprocess.run(cmd, shell=True, check=check)
    return result.returncode == 0


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║        RAHUL Advanced AI — Linux Setup v3.0              ║
╚══════════════════════════════════════════════════════════╝
""")

    if platform.system() != "Linux":
        print("⚠️  This project is designed for Linux.")
        print("   Windows/macOS support is limited.")

    print("📦 Step 1: Installing Python packages…")
    run(f"{sys.executable} -m pip install --upgrade pip -q")
    run(f"{sys.executable} -m pip install -r requirements.txt")

    print("\n🌐 Step 2: Installing Playwright browsers…")
    run(f"{sys.executable} -m playwright install firefox chromium")
    run(f"{sys.executable} -m playwright install-deps", check=False)

    print("\n🔧 Step 3: Checking Linux system tools…")
    tools = {
        "scrot":          "sudo apt-get install -y scrot",
        "xclip":          "sudo apt-get install -y xclip",
        "notify-send":    "sudo apt-get install -y libnotify-bin",
        "at":             "sudo apt-get install -y at",
        "nmcli":          "sudo apt-get install -y network-manager",
        "brightnessctl":  "sudo apt-get install -y brightnessctl",
    }
    for tool, install_cmd in tools.items():
        if shutil.which(tool):
            print(f"  ✓ {tool} found")
        else:
            print(f"  ✗ {tool} missing — trying to install…")
            run(install_cmd, check=False)

    print("\n📁 Step 4: Creating config and memory directories…")
    os.makedirs("config",  exist_ok=True)
    os.makedirs("memory",  exist_ok=True)
    os.makedirs("assets",  exist_ok=True)

    print("\n🔑 Step 5: Checking API key configuration…")
    config_file = os.path.join("config", "api_keys.json")
    if os.path.exists(config_file):
        print("  ✓ api_keys.json found")
    else:
        print("  ℹ  api_keys.json not found — RAHUL will ask on first launch")

    print("""
╔══════════════════════════════════════════════════════════╗
║  ✅  Setup Complete!                                     ║
║                                                          ║
║  Run RAHUL:                                              ║
║    python3 main.py                                       ║
║                                                          ║
║  Get FREE Gemini API key:                                ║
║    https://aistudio.google.com/apikey                   ║
╚══════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    main()
