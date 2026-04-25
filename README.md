# 🤖 RAHUL — Advanced Personal AI Assistant
### Linux Edition v3.0 | Powered by Gemini 2.5 Flash

> **"Sir, ye dekho — khas aapke liye laya hun!"**
> An AI that sees your screen, remembers you, talks to you, and works FOR you.

---

## ✨ What makes RAHUL special?

RAHUL is not just a chatbot. It's a **visual, proactive AI assistant** that:

- 🎨 **Shows things ON its own screen** — news tickers, charts, weather cards, step guides, comparisons — all animated right inside the UI
- 🧠 **Remembers you** — your name, city, preferences, projects — permanently
- 👁️ **Sees your screen** — take a screenshot and RAHUL analyzes what's on it
- ⌨️ **Works without a microphone** — fully typing-based (voice optional)
- 🐧 **Built for Linux** — uses native tools: notify-send, pactl, nmcli, xdg-open
- 🆓 **100% Free** — Gemini API (free tier), no paid subscriptions

---

## 🚀 Quick Start (Linux)

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/RAHUL-AI.git
cd RAHUL-AI

# 2. Run setup (installs everything)
python3 setup.py

# 3. Start RAHUL
python3 main.py
```

On first launch, RAHUL will ask for your **FREE Gemini API key**.
Get it here → [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

---

## 📋 Requirements

| Requirement | Details |
|---|---|
| **OS** | Linux (Ubuntu 20.04+ / Debian / Fedora / Arch) |
| **Python** | 3.10 or newer |
| **API Key** | Free Gemini API key |
| **Microphone** | ❌ NOT required — typing works fully |

---

## 🛠️ Manual Install (if setup.py fails)

```bash
# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers
python3 -m playwright install firefox chromium

# Install Linux tools (Ubuntu/Debian)
sudo apt-get install -y scrot xclip libnotify-bin at network-manager

# Run
python3 main.py
```

---

## 💬 What can RAHUL do?

### 🎭 Visual Animations (shown ON the UI screen)
| Animation Type | When used |
|---|---|
| `card` | Quick info display |
| `list` | Search results, options |
| `chart` | Data, stats, comparisons |
| `steps` | Tutorials, guides, roadmaps |
| `news_ticker` | Scrolling news headlines |
| `comparison` | Side-by-side tables |
| `weather` | Animated weather display |
| `typewriter` | Dramatic text reveal |
| `countdown` | Timer display |
| `image` | Generated/captured images |

### 🔧 All Capabilities
| Category | Actions |
|---|---|
| 🌐 **Web** | Search, news, weather, browser control |
| 📁 **Files** | List, create, edit, delete, move, find files |
| 💻 **Code** | Write, run, debug Python/Bash/JS/C++ code |
| 🖥️ **System** | Volume, brightness, WiFi, screenshot, processes |
| 🎨 **AI Images** | Generate any image (free, no key needed) |
| 📺 **YouTube** | Search, play, get transcripts |
| 📰 **News** | Latest news on any topic with ticker |
| 🔢 **Calculator** | Math, unit conversion, equations |
| 🌍 **Translate** | Any language ↔ any language |
| 📄 **PDF** | Read, summarize, search PDF files |
| 📧 **Email** | Compose & send via Gmail |
| 💬 **Messages** | Telegram bot, WhatsApp Web |
| ⏰ **Reminders** | Set timed reminders |
| 📊 **System Stats** | CPU, RAM, network live monitoring |
| 🧠 **Memory** | Remembers you permanently |
| 👁️ **Screen Vision** | Analyze screenshots with AI |
| 📋 **Clipboard** | Read/write clipboard |
| 🌐 **Network** | IP, ping, speed test, WiFi list |

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|---|---|
| `F4` | Toggle microphone mute |
| `F5` | Cycle UI themes (Cyan → Gold → Purple) |
| `F11` | Toggle fullscreen |
| `F2` | View conversation history |
| `Escape` | Exit fullscreen |
| `Enter` | Send typed command |

---

## 🎨 UI Themes

RAHUL has 3 built-in themes — press **F5** to switch:

- 🔵 **CYAN** — Classic iron man blue (default)
- 🟡 **GOLD** — Iron Man gold
- 🟣 **PURPLE** — Galaxy purple

---

## 🧠 Memory Configuration

RAHUL remembers things automatically. Memory is stored in `memory/memory.json`.

You can tell RAHUL things like:
- *"Mera naam Rahul hai, main Bhopal mein rehta hun"*
- *"Mujhe Python bahut pasand hai"*
- *"Mera project ek AI startup hai"*

RAHUL will remember these forever and reference them naturally.

---

## 📡 Optional: Telegram Bot Setup

To use the `send_message` action with Telegram:

1. Talk to [@BotFather](https://t.me/BotFather) on Telegram
2. Create a new bot → get the token
3. Add to `config/api_keys.json`:

```json
{
    "gemini_api_key": "your_gemini_key",
    "telegram_bot_token": "your_bot_token",
    "telegram_chat_id": "your_chat_id"
}
```

---

## 🗂️ Project Structure

```
RAHUL/
├── main.py              ← Entry point + AI engine
├── ui.py                ← Advanced UI with animation engine
├── setup.py             ← One-click installer
├── requirements.txt     ← Python dependencies
│
├── actions/             ← 22+ tool implementations
│   ├── animation_engine.py
│   ├── open_app.py
│   ├── web_search.py
│   ├── weather.py
│   ├── browser_control.py
│   ├── file_controller.py
│   ├── code_helper.py
│   ├── screen_process.py
│   ├── system_control.py
│   ├── youtube.py
│   ├── news_reader.py
│   ├── calculator.py
│   ├── translate.py
│   ├── image_gen.py
│   ├── pdf_reader.py
│   ├── email_action.py
│   ├── send_message.py
│   ├── reminder.py
│   ├── clipboard_mgr.py
│   ├── process_mgr.py
│   └── network_info.py
│
├── memory/
│   ├── memory_manager.py
│   └── memory.json      ← Auto-created
│
├── core/
│   └── prompt.txt       ← RAHUL's personality & instructions
│
└── config/
    └── api_keys.json    ← Auto-created on first run
```

---

## 🗣️ Example Commands (Type anything naturally!)

```
"Aaj ka weather Bhopal ka dikha"
"YouTube pe lo-fi music chala do"
"Mera screen dekho aur batao kya hai"
"Python mein hello world likho aur chala do"
"Latest AI news dikha"
"Calculator: 15% of 8500 kya hoga"
"Translate 'I love coding' to Hindi"
"Screenshot lo"
"AI image generate karo: futuristic city at night"
"Disk space kitna bacha hai?"
"Firefox mein Google kholo"
```

---

## ⚠️ Known Limitations

- Voice input/output requires `sounddevice` + working audio setup
- Browser automation (Playwright) needs Firefox/Chromium installed
- Some system tools need `sudo apt install` once

---

## 📜 License

Personal and non-commercial use only.

---

> ⭐ **Star this repo if RAHUL impresses you!**
