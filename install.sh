#!/bin/bash
# ╔══════════════════════════════════════════════════════════╗
# ║     RAHUL Advanced AI — One-Click Linux Installer        ║
# ║     Usage: bash install.sh                               ║
# ╚══════════════════════════════════════════════════════════╝

set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║        RAHUL Advanced AI — Linux Installer           ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
REQUIRED="3.10"
if python3 -c "import sys; exit(0 if sys.version_info >= (3,10) else 1)"; then
    echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"
else
    echo -e "${RED}✗ Python 3.10+ required. Found: $PYTHON_VERSION${NC}"
    echo "  Install: sudo apt install python3.11"
    exit 1
fi

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}Installing pip...${NC}"
    sudo apt-get install -y python3-pip
fi

# Install system dependencies
echo -e "\n${CYAN}Installing system tools...${NC}"
if command -v apt-get &> /dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y \
        python3-tk \
        scrot \
        xclip \
        libnotify-bin \
        at \
        network-manager \
        brightnessctl \
        curl \
        2>/dev/null || true
elif command -v dnf &> /dev/null; then
    sudo dnf install -y \
        python3-tkinter \
        scrot \
        xclip \
        libnotify \
        at \
        NetworkManager \
        2>/dev/null || true
elif command -v pacman &> /dev/null; then
    sudo pacman -S --noconfirm \
        python-tkinter \
        scrot \
        xclip \
        libnotify \
        at \
        networkmanager \
        2>/dev/null || true
fi

# Install Python packages
echo -e "\n${CYAN}Installing Python packages...${NC}"
pip3 install --upgrade pip -q
pip3 install -r requirements.txt

# Install Playwright
echo -e "\n${CYAN}Installing Playwright browsers...${NC}"
python3 -m playwright install firefox chromium
python3 -m playwright install-deps 2>/dev/null || true

# Create directories
mkdir -p config memory assets

echo -e "\n${GREEN}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║  ✅  Installation Complete!                          ║"
echo "║                                                      ║"
echo "║  Start RAHUL:                                        ║"
echo "║    python3 main.py                                   ║"
echo "║                                                      ║"
echo "║  FREE Gemini API Key:                                ║"
echo "║    https://aistudio.google.com/apikey               ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"
