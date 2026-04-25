"""
╔══════════════════════════════════════════════════════════════════╗
║              RAHUL — Advanced Personal AI Assistant              ║
║              Linux Edition  v3.0  |  By Claude & You             ║
║                                                                  ║
║  • Typing-first (microphone optional)                            ║
║  • Gemini 2.5 Flash Native Audio                                 ║
║  • 20+ Actions: browser, files, code, web search, animation…    ║
║  • Persistent memory, screen vision, in-UI animations           ║
╚══════════════════════════════════════════════════════════════════╝
"""

import asyncio
import re
import threading
import json
import sys
import traceback
from pathlib import Path
from datetime import datetime

from google import genai
from google.genai import types
from ui import RahulUI
from memory.memory_manager import load_memory, update_memory, format_memory_for_prompt
from actions.open_app       import open_app
from actions.web_search     import web_search as web_search_action
from actions.weather        import weather_action
from actions.browser_control import browser_control
from actions.file_controller import file_controller
from actions.code_helper    import code_helper
from actions.screen_process import screen_process
from actions.reminder       import reminder_action
from actions.send_message   import send_message
from actions.system_control import system_control
from actions.youtube        import youtube_action
from actions.news_reader    import news_reader
from actions.calculator     import calculator
from actions.translate      import translate_action
from actions.image_gen      import image_gen
from actions.pdf_reader     import pdf_reader
from actions.email_action   import email_action
from actions.clipboard_mgr  import clipboard_mgr
from actions.process_mgr    import process_mgr
from actions.network_info   import network_info
from actions.animation_engine import animation_engine


def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


BASE_DIR       = get_base_dir()
API_CONFIG     = BASE_DIR / "config" / "api_keys.json"
PROMPT_PATH    = BASE_DIR / "core"   / "prompt.txt"
LIVE_MODEL     = "gemini-2.0-flash-live-001"
FALLBACK_MODEL = "gemini-2.0-flash"
CTRL_RE        = re.compile(r"<ctrl\d+>", re.IGNORECASE)


def _get_api_key() -> str:
    with open(API_CONFIG, "r", encoding="utf-8") as f:
        return json.load(f)["gemini_api_key"]


def _load_prompt() -> str:
    try:
        return PROMPT_PATH.read_text(encoding="utf-8")
    except Exception:
        return (
            "You are RAHUL, an advanced personal AI assistant running on Linux. "
            "You are helpful, proactive, and always use tools to complete tasks. "
            "When showing something to the user, use the animation_engine tool to "
            "display it beautifully on screen. Never simulate results — always call tools."
        )


def _clean(text: str) -> str:
    text = CTRL_RE.sub("", text)
    text = re.sub(r"[\x00-\x08\x0b-\x1f]", "", text)
    return text.strip()


# ── ALL TOOL DECLARATIONS ──────────────────────────────────────────────────────
TOOLS = [
    {
        "name": "open_app",
        "description": "Open any application on Linux. Use for: launching apps, programs, tools.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "app_name": {"type": "STRING", "description": "Application name e.g. 'firefox', 'vlc', 'gedit'"},
                "args": {"type": "STRING", "description": "Optional command-line arguments"},
            },
            "required": ["app_name"],
        },
    },
    {
        "name": "web_search",
        "description": "Search the web for any information. Returns rich results.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {"type": "STRING"},
                "mode": {"type": "STRING", "description": "search | news | images | compare"},
                "show_on_screen": {"type": "BOOLEAN", "description": "Display results as animation on UI"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "weather_report",
        "description": "Get weather for any city. Shows animated weather card on UI.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "city": {"type": "STRING"},
                "show_animation": {"type": "BOOLEAN", "description": "Show animated weather on screen"},
            },
            "required": ["city"],
        },
    },
    {
        "name": "browser_control",
        "description": "Control Firefox/Chromium browser. Navigate, search, click, fill forms.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "go_to|search|click|type|scroll|screenshot|back|forward|new_tab|close_tab"},
                "url": {"type": "STRING"},
                "query": {"type": "STRING"},
                "text": {"type": "STRING"},
                "selector": {"type": "STRING"},
                "browser": {"type": "STRING", "description": "firefox|chromium (default: firefox)"},
            },
            "required": ["action"],
        },
    },
    {
        "name": "file_controller",
        "description": "Manage files and folders: list, create, delete, move, copy, rename, read, write, find.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "list|create_file|create_folder|delete|move|copy|rename|read|write|find|disk_usage|largest"},
                "path": {"type": "STRING"},
                "destination": {"type": "STRING"},
                "new_name": {"type": "STRING"},
                "content": {"type": "STRING"},
                "name": {"type": "STRING"},
            },
            "required": ["action"],
        },
    },
    {
        "name": "code_helper",
        "description": "Write, edit, explain, run, or debug code files. Opens in terminal.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "write|edit|explain|run|debug|auto"},
                "description": {"type": "STRING"},
                "language": {"type": "STRING", "description": "python|bash|js|cpp|rust etc"},
                "file_path": {"type": "STRING"},
                "code": {"type": "STRING"},
                "output_path": {"type": "STRING"},
            },
            "required": ["action"],
        },
    },
    {
        "name": "screen_process",
        "description": (
            "Capture and analyze screen or webcam. "
            "MUST call when user says 'what do you see', 'look at screen', 'analyze this'. "
            "After calling, stay SILENT — vision module responds directly."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "angle": {"type": "STRING", "description": "screen|camera (default: screen)"},
                "text": {"type": "STRING", "description": "Question about what you see"},
            },
            "required": ["text"],
        },
    },
    {
        "name": "reminder",
        "description": "Set a timed reminder using Linux cron/at.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "date": {"type": "STRING", "description": "YYYY-MM-DD"},
                "time": {"type": "STRING", "description": "HH:MM (24h)"},
                "message": {"type": "STRING"},
            },
            "required": ["time", "message"],
        },
    },
    {
        "name": "send_message",
        "description": "Send message via Telegram or WhatsApp Web.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "receiver": {"type": "STRING"},
                "message_text": {"type": "STRING"},
                "platform": {"type": "STRING", "description": "telegram|whatsapp"},
            },
            "required": ["receiver", "message_text", "platform"],
        },
    },
    {
        "name": "system_control",
        "description": "Control Linux system: volume, brightness, wifi, bluetooth, screenshot, lock, shutdown, processes.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "volume|brightness|wifi|bluetooth|screenshot|lock|shutdown|restart|sleep|clipboard"},
                "value": {"type": "STRING", "description": "Level/value for volume (0-100), brightness (0-100)"},
                "state": {"type": "STRING", "description": "on|off|toggle"},
            },
            "required": ["action"],
        },
    },
    {
        "name": "youtube",
        "description": "Search and play YouTube videos in browser, or get video info/transcript.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "play|search|transcript|trending"},
                "query": {"type": "STRING"},
                "url": {"type": "STRING"},
                "region": {"type": "STRING", "description": "IN|US|GB etc"},
            },
            "required": [],
        },
    },
    {
        "name": "news_reader",
        "description": "Get latest news on any topic. Shows animated headlines on UI screen.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "topic": {"type": "STRING", "description": "Topic or keyword. Use 'general' for top news."},
                "count": {"type": "INTEGER", "description": "Number of articles (default: 5)"},
                "show_animation": {"type": "BOOLEAN", "description": "Show news ticker on UI"},
            },
            "required": ["topic"],
        },
    },
    {
        "name": "calculator",
        "description": "Perform mathematical calculations, unit conversions, currency conversion, equation solving.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "expression": {"type": "STRING", "description": "Math expression or conversion query"},
                "show_steps": {"type": "BOOLEAN", "description": "Show step-by-step solution on screen"},
            },
            "required": ["expression"],
        },
    },
    {
        "name": "translate",
        "description": "Translate text between any languages. Shows result on UI.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "text": {"type": "STRING"},
                "target_lang": {"type": "STRING", "description": "Target language e.g. Hindi, French, Japanese"},
                "source_lang": {"type": "STRING", "description": "Source language (auto-detect if omitted)"},
            },
            "required": ["text", "target_lang"],
        },
    },
    {
        "name": "image_gen",
        "description": "Generate AI images using free APIs (Pollinations.ai). Displays on UI screen.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "prompt": {"type": "STRING", "description": "Describe the image you want"},
                "style": {"type": "STRING", "description": "realistic|anime|art|3d|sketch"},
                "size": {"type": "STRING", "description": "512x512|1024x1024|1024x576"},
            },
            "required": ["prompt"],
        },
    },
    {
        "name": "pdf_reader",
        "description": "Read, summarize, search text in PDF files. Shows summary on UI.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "read|summarize|search|extract_text"},
                "file_path": {"type": "STRING"},
                "query": {"type": "STRING", "description": "Search query for search action"},
                "pages": {"type": "STRING", "description": "Page range e.g. '1-5' or 'all'"},
            },
            "required": ["action", "file_path"],
        },
    },
    {
        "name": "email_action",
        "description": "Send email via Gmail (opens browser with pre-filled compose).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "to": {"type": "STRING"},
                "subject": {"type": "STRING"},
                "body": {"type": "STRING"},
            },
            "required": ["to", "subject", "body"],
        },
    },
    {
        "name": "clipboard_mgr",
        "description": "Read from or write to Linux clipboard (xclip/xsel).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "read|write|clear"},
                "text": {"type": "STRING", "description": "Text to write (for write action)"},
            },
            "required": ["action"],
        },
    },
    {
        "name": "process_mgr",
        "description": "List, kill, or get info about running Linux processes.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "list|kill|info|top_cpu|top_mem"},
                "name": {"type": "STRING", "description": "Process name or PID for kill/info"},
            },
            "required": ["action"],
        },
    },
    {
        "name": "network_info",
        "description": "Get network info: IP address, speed test, ping, open ports, wifi networks.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "ip|speedtest|ping|ports|wifi_list"},
                "host": {"type": "STRING", "description": "Host for ping action"},
            },
            "required": ["action"],
        },
    },
    {
        "name": "animation_engine",
        "description": (
            "Show rich animated content on the RAHUL UI screen. "
            "Use this to visually present information: show charts, "
            "explain concepts with animation, display lists/cards beautifully, "
            "show news/weather/search results, create step-by-step tutorials. "
            "ALWAYS use this when saying 'Sir, dekho' or 'let me show you'. "
            "This makes RAHUL truly visual and impressive."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "type": {
                    "type": "STRING",
                    "description": (
                        "card       — show a single info card\n"
                        "list       — show animated bullet list\n"
                        "chart      — bar/line/pie chart\n"
                        "steps      — step-by-step guide with progress\n"
                        "news_ticker— scrolling news headlines\n"
                        "comparison — side-by-side comparison table\n"
                        "weather    — animated weather display\n"
                        "countdown  — animated countdown timer\n"
                        "mindmap    — topic mindmap visualization\n"
                        "typewriter — dramatic typing of text\n"
                        "image      — display an image with caption"
                    ),
                },
                "title": {"type": "STRING", "description": "Main heading"},
                "content": {
                    "type": "STRING",
                    "description": "JSON string with content. For list: [{text,icon}]. For chart: {labels:[],values:[],chart_type:'bar'}. For steps: [{step,description}]. For card: {body,icon,color}. For comparison: {headers:[],rows:[[]]}"
                },
                "color": {"type": "STRING", "description": "Accent color hex e.g. #00d4ff"},
                "duration": {"type": "INTEGER", "description": "Display duration in seconds (default: 8)"},
                "image_path": {"type": "STRING", "description": "Image file path for image type"},
            },
            "required": ["type", "title"],
        },
    },
    {
        "name": "save_memory",
        "description": (
            "Silently save important facts about the user to long-term memory. "
            "Call for: name, age, city, job, hobbies, projects, preferences. "
            "Do NOT announce saving. Always save in English."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "category": {"type": "STRING", "description": "identity|preferences|projects|relationships|wishes|notes"},
                "key": {"type": "STRING"},
                "value": {"type": "STRING"},
            },
            "required": ["category", "key", "value"],
        },
    },
    {
        "name": "shutdown_rahul",
        "description": "Shut down RAHUL completely when user says goodbye/close/exit in any language.",
        "parameters": {"type": "OBJECT", "properties": {}},
    },
]


class RahulCore:
    """
    Core AI engine using Gemini REST API (generateContent) with function calling.
    Works 100% on free tier — no Live API needed.
    """

    MODEL = "gemini-2.0-flash"   # Free tier, always available

    def __init__(self, ui: RahulUI):
        self.ui            = ui
        self._history      = []   # multi-turn conversation history
        self._lock         = threading.Lock()
        self._ready        = False
        self.ui.on_text_command = self._on_text_command

    # ── Build system prompt ────────────────────────────────────────────────────
    def _system_prompt(self) -> str:
        memory  = load_memory()
        mem_str = format_memory_for_prompt(memory)
        prompt  = _load_prompt()
        now     = datetime.now().strftime("%A, %d %B %Y — %I:%M %p")
        parts   = [f"[CURRENT DATE & TIME]\n{now}\n",
                   mem_str if mem_str else "", prompt]
        return "\n".join(filter(None, parts))

    # ── Convert our TOOLS list → Gemini SDK format ─────────────────────────────
    @staticmethod
    def _sdk_tools():
        from google.genai import types as gt
        declarations = []
        for t in TOOLS:
            props_raw = t.get("parameters", {}).get("properties", {})
            required  = t.get("parameters", {}).get("required", [])
            props_sdk = {}
            for pname, pval in props_raw.items():
                typ = pval.get("type", "STRING").upper()
                type_map = {
                    "STRING": gt.Type.STRING, "BOOLEAN": gt.Type.BOOLEAN,
                    "INTEGER": gt.Type.INTEGER, "NUMBER": gt.Type.NUMBER,
                    "OBJECT": gt.Type.OBJECT,  "ARRAY": gt.Type.ARRAY,
                }
                props_sdk[pname] = gt.Schema(
                    type=type_map.get(typ, gt.Type.STRING),
                    description=pval.get("description", ""),
                )
            schema = gt.Schema(
                type=gt.Type.OBJECT,
                properties=props_sdk,
                required=required if required else [],
            ) if props_sdk else gt.Schema(type=gt.Type.OBJECT, properties={})

            declarations.append(gt.FunctionDeclaration(
                name=t["name"],
                description=t["description"],
                parameters=schema,
            ))
        return [gt.Tool(function_declarations=declarations)]

    # ── Execute one tool call ──────────────────────────────────────────────────
    def _run_tool(self, name: str, args: dict) -> str:
        print(f"[RAHUL] ⚡ Tool: {name}  args={args}")
        self.ui.set_state("THINKING")
        self.ui.notify_tool(name)
        result = "Done."
        try:
            if name == "save_memory":
                cat = args.get("category", "notes")
                key = args.get("key", "")
                val = args.get("value", "")
                if key and val:
                    update_memory({cat: {key: {"value": val}}})
                return "Memory saved."

            elif name == "shutdown_rahul":
                self.ui.write_log("SYS: Shutting down RAHUL…")
                def _bye():
                    import time, os; time.sleep(1.2); os._exit(0)
                threading.Thread(target=_bye, daemon=True).start()
                return "Goodbye."

            dispatch = {
                "open_app":        lambda: open_app(args, self.ui),
                "web_search":      lambda: web_search_action(args, self.ui),
                "weather_report":  lambda: weather_action(args, self.ui),
                "browser_control": lambda: browser_control(args, self.ui),
                "file_controller": lambda: file_controller(args, self.ui),
                "code_helper":     lambda: code_helper(args, self.ui),
                "reminder":        lambda: reminder_action(args, self.ui),
                "send_message":    lambda: send_message(args, self.ui),
                "system_control":  lambda: system_control(args, self.ui),
                "youtube":         lambda: youtube_action(args, self.ui),
                "news_reader":     lambda: news_reader(args, self.ui),
                "calculator":      lambda: calculator(args, self.ui),
                "translate":       lambda: translate_action(args, self.ui),
                "image_gen":       lambda: image_gen(args, self.ui),
                "pdf_reader":      lambda: pdf_reader(args, self.ui),
                "email_action":    lambda: email_action(args, self.ui),
                "clipboard_mgr":   lambda: clipboard_mgr(args, self.ui),
                "process_mgr":     lambda: process_mgr(args, self.ui),
                "network_info":    lambda: network_info(args, self.ui),
                "animation_engine":lambda: animation_engine(args, self.ui),
            }

            if name == "screen_process":
                threading.Thread(
                    target=screen_process,
                    kwargs={"parameters": args, "player": self.ui},
                    daemon=True,
                ).start()
                return "Vision module activated."

            if name in dispatch:
                result = dispatch[name]()
            else:
                result = f"Unknown tool: {name}"

        except Exception as e:
            result = f"Tool '{name}' error: {e}"
            traceback.print_exc()
            self.ui.write_log(f"ERR: {name} — {str(e)[:100]}")

        print(f"[RAHUL] ✓ {name} → {str(result)[:80]}")
        return str(result)

    # ── Main chat turn (runs in background thread) ─────────────────────────────
    def _chat_turn(self, user_text: str):
        from google import genai as gai
        from google.genai import types as gt

        api_key = _get_api_key()
        client  = gai.Client(api_key=api_key)

        self.ui.set_state("THINKING")

        with self._lock:
            # Add user message to history
            self._history.append(
                gt.Content(role="user", parts=[gt.Part.from_text(text=user_text)])
            )

        sys_prompt = self._system_prompt()
        tools      = self._sdk_tools()

        # Agentic loop — keep calling until no more tool calls
        while True:
            try:
                with self._lock:
                    history_snapshot = list(self._history)

                response = client.models.generate_content(
                    model=self.MODEL,
                    contents=history_snapshot,
                    config=gt.GenerateContentConfig(
                        system_instruction=sys_prompt,
                        tools=tools,
                        temperature=0.7,
                        max_output_tokens=2048,
                    ),
                )
            except Exception as e:
                self.ui.write_log(f"ERR: Gemini API — {str(e)[:120]}")
                self.ui.set_state("LISTENING")
                return

            candidate = response.candidates[0] if response.candidates else None
            if not candidate:
                self.ui.write_log("ERR: No response from Gemini.")
                self.ui.set_state("LISTENING")
                return

            # Collect text + function calls from this response
            text_parts   = []
            func_calls   = []
            for part in candidate.content.parts:
                if hasattr(part, "text") and part.text:
                    text_parts.append(_clean(part.text))
                if hasattr(part, "function_call") and part.function_call:
                    func_calls.append(part.function_call)

            # Add model response to history
            with self._lock:
                self._history.append(candidate.content)

            # Show any text
            if text_parts:
                full_text = " ".join(text_parts).strip()
                if full_text:
                    self.ui.write_log(f"RAHUL: {full_text}")

            # If no tool calls — we're done
            if not func_calls:
                break

            # Execute all tool calls and add results to history
            tool_response_parts = []
            for fc in func_calls:
                t_name = fc.name
                t_args = dict(fc.args) if fc.args else {}
                t_result = self._run_tool(t_name, t_args)
                tool_response_parts.append(
                    gt.Part.from_function_response(
                        name=t_name,
                        response={"result": t_result},
                    )
                )

            with self._lock:
                self._history.append(
                    gt.Content(role="user", parts=tool_response_parts)
                )

            # Keep history trimmed to last 40 turns
            with self._lock:
                if len(self._history) > 40:
                    self._history = self._history[-40:]

        self.ui.set_state("LISTENING")

    # ── Called when user types a message ──────────────────────────────────────
    def _on_text_command(self, text: str):
        threading.Thread(
            target=self._chat_turn, args=(text,), daemon=True
        ).start()

    # ── Startup ───────────────────────────────────────────────────────────────
    def start(self):
        """Test connection and announce ready."""
        self._ready = False
        self.ui.set_state("THINKING")
        self.ui.write_log("SYS: Connecting to Gemini 2.0 Flash…")

        def _init():
            try:
                from google import genai as gai
                from google.genai import types as gt
                client = gai.Client(api_key=_get_api_key())
                # Quick ping
                r = client.models.generate_content(
                    model=self.MODEL,
                    contents="Say exactly: RAHUL online",
                    config=gt.GenerateContentConfig(max_output_tokens=10),
                )
                self._ready = True
                self.ui.set_state("LISTENING")
                self.ui.write_log("SYS: ✓ RAHUL v3.0 online — Type anything below!")
                self.ui.write_log("SYS: Model: gemini-2.0-flash  |  Free tier ✓")
            except Exception as e:
                self.ui.write_log(f"ERR: Cannot connect — {str(e)[:100]}")
                self.ui.write_log("SYS: Check your API key in config/api_keys.json")
                self.ui.set_state("INITIALISING")

        threading.Thread(target=_init, daemon=True).start()


def main():
    ui = RahulUI()

    def runner():
        ui.wait_for_api_key()
        core = RahulCore(ui)
        core.start()

    threading.Thread(target=runner, daemon=True).start()
    ui.root.mainloop()


if __name__ == "__main__":
    main()
