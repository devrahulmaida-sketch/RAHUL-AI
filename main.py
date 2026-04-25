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
LIVE_MODEL     = "models/gemini-2.5-flash-preview-native-audio-dialog"
FALLBACK_MODEL = "gemini-2.5-flash"
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
    """Core AI engine — manages Gemini Live session + tool execution."""

    def __init__(self, ui: RahulUI):
        self.ui       = ui
        self.session  = None
        self._loop    = None
        self.audio_q  = None
        self.out_q    = None
        self._turn_ev = None
        self._is_speaking = False
        self._speak_lock  = threading.Lock()
        self.ui.on_text_command = self._on_text_command
        self._audio_enabled = False

        # Try to import sounddevice for optional audio
        try:
            import sounddevice as sd
            self._sd = sd
            self._audio_enabled = True
            self.ui.write_log("SYS: Audio input/output available.")
        except Exception:
            self._sd = None
            self.ui.write_log("SYS: No audio — typing-only mode active.")

    def _on_text_command(self, text: str):
        if not self._loop or not self.session:
            return
        asyncio.run_coroutine_threadsafe(
            self.session.send_client_content(
                turns={"parts": [{"text": text}]}, turn_complete=True
            ),
            self._loop,
        )

    def speak_error(self, tool_name: str, error):
        short = str(error)[:120]
        self.ui.write_log(f"ERR: {tool_name} — {short}")

    def _build_config(self) -> types.LiveConnectConfig:
        memory  = load_memory()
        mem_str = format_memory_for_prompt(memory)
        prompt  = _load_prompt()
        now     = datetime.now().strftime("%A, %d %B %Y — %I:%M %p")

        parts = [
            f"[CURRENT DATE & TIME]\n{now}\n",
            mem_str if mem_str else "",
            prompt,
        ]

        modalities = ["TEXT"]
        if self._audio_enabled:
            modalities = ["AUDIO"]

        cfg = types.LiveConnectConfig(
            response_modalities=modalities,
            system_instruction="\n".join(filter(None, parts)),
            tools=[{"function_declarations": TOOLS}],
            session_resumption=types.SessionResumptionConfig(),
        )
        if self._audio_enabled:
            cfg.output_audio_transcription = {}
            cfg.input_audio_transcription  = {}
            cfg.speech_config = types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
                )
            )
        return cfg

    # ── Tool router ────────────────────────────────────────────────────────────
    async def _execute_tool(self, fc) -> types.FunctionResponse:
        name = fc.name
        args = dict(fc.args or {})
        print(f"[RAHUL] ⚡ Tool: {name}  args={args}")
        self.ui.set_state("THINKING")
        self.ui.notify_tool(name)
        loop   = asyncio.get_event_loop()
        result = "Done."

        try:
            if name == "save_memory":
                cat, key, val = args.get("category","notes"), args.get("key",""), args.get("value","")
                if key and val:
                    update_memory({cat: {key: {"value": val}}})
                if not self.ui.muted:
                    self.ui.set_state("LISTENING")
                return types.FunctionResponse(id=fc.id, name=name, response={"result": "ok"})

            elif name == "shutdown_rahul":
                self.ui.write_log("SYS: Shutting down RAHUL…")
                def _exit():
                    import time, os
                    time.sleep(1.2)
                    os._exit(0)
                threading.Thread(target=_exit, daemon=True).start()
                result = "Goodbye."

            elif name == "open_app":
                result = await loop.run_in_executor(None, lambda: open_app(args, self.ui))

            elif name == "web_search":
                result = await loop.run_in_executor(None, lambda: web_search_action(args, self.ui))

            elif name == "weather_report":
                result = await loop.run_in_executor(None, lambda: weather_action(args, self.ui))

            elif name == "browser_control":
                result = await loop.run_in_executor(None, lambda: browser_control(args, self.ui))

            elif name == "file_controller":
                result = await loop.run_in_executor(None, lambda: file_controller(args, self.ui))

            elif name == "code_helper":
                result = await loop.run_in_executor(None, lambda: code_helper(args, self.ui))

            elif name == "screen_process":
                threading.Thread(
                    target=screen_process, kwargs={"parameters": args, "player": self.ui},
                    daemon=True
                ).start()
                result = "Vision module activated."

            elif name == "reminder":
                result = await loop.run_in_executor(None, lambda: reminder_action(args, self.ui))

            elif name == "send_message":
                result = await loop.run_in_executor(None, lambda: send_message(args, self.ui))

            elif name == "system_control":
                result = await loop.run_in_executor(None, lambda: system_control(args, self.ui))

            elif name == "youtube":
                result = await loop.run_in_executor(None, lambda: youtube_action(args, self.ui))

            elif name == "news_reader":
                result = await loop.run_in_executor(None, lambda: news_reader(args, self.ui))

            elif name == "calculator":
                result = await loop.run_in_executor(None, lambda: calculator(args, self.ui))

            elif name == "translate":
                result = await loop.run_in_executor(None, lambda: translate_action(args, self.ui))

            elif name == "image_gen":
                result = await loop.run_in_executor(None, lambda: image_gen(args, self.ui))

            elif name == "pdf_reader":
                result = await loop.run_in_executor(None, lambda: pdf_reader(args, self.ui))

            elif name == "email_action":
                result = await loop.run_in_executor(None, lambda: email_action(args, self.ui))

            elif name == "clipboard_mgr":
                result = await loop.run_in_executor(None, lambda: clipboard_mgr(args, self.ui))

            elif name == "process_mgr":
                result = await loop.run_in_executor(None, lambda: process_mgr(args, self.ui))

            elif name == "network_info":
                result = await loop.run_in_executor(None, lambda: network_info(args, self.ui))

            elif name == "animation_engine":
                result = await loop.run_in_executor(None, lambda: animation_engine(args, self.ui))

            else:
                result = f"Unknown tool: {name}"

        except Exception as e:
            result = f"Tool '{name}' failed: {e}"
            traceback.print_exc()
            self.speak_error(name, e)

        if not self.ui.muted:
            self.ui.set_state("LISTENING")
        print(f"[RAHUL] ✓ {name} → {str(result)[:80]}")
        return types.FunctionResponse(id=fc.id, name=name, response={"result": str(result)})

    # ── Audio tasks (optional) ─────────────────────────────────────────────────
    async def _send_realtime(self):
        while True:
            msg = await self.out_q.get()
            await self.session.send_realtime_input(media=msg)

    async def _listen_audio(self):
        SEND_SR, CHANNELS, CHUNK = 16000, 1, 1024
        loop = asyncio.get_event_loop()
        def cb(indata, frames, time_info, status):
            with self._speak_lock:
                speaking = self._is_speaking
            if not speaking and not self.ui.muted:
                loop.call_soon_threadsafe(
                    self.out_q.put_nowait, {"data": indata.tobytes(), "mime_type": "audio/pcm"}
                )
        with self._sd.InputStream(samplerate=SEND_SR, channels=CHANNELS,
                                   dtype="int16", blocksize=CHUNK, callback=cb):
            while True:
                await asyncio.sleep(0.1)

    async def _receive_audio(self):
        out_buf, in_buf = [], []
        while True:
            async for resp in self.session.receive():
                if resp.data:
                    self.audio_q.put_nowait(resp.data)

                if resp.server_content:
                    sc = resp.server_content
                    if sc.output_transcription and sc.output_transcription.text:
                        txt = _clean(sc.output_transcription.text)
                        if txt: out_buf.append(txt)
                    if sc.input_transcription and sc.input_transcription.text:
                        txt = _clean(sc.input_transcription.text)
                        if txt: in_buf.append(txt)
                    if sc.turn_complete:
                        if self._turn_ev: self._turn_ev.set()
                        if in_buf:
                            self.ui.write_log(f"You: {' '.join(in_buf).strip()}")
                            in_buf = []
                        if out_buf:
                            self.ui.write_log(f"RAHUL: {' '.join(out_buf).strip()}")
                            out_buf = []

                if resp.tool_call:
                    frs = []
                    for fc in resp.tool_call.function_calls:
                        fr = await self._execute_tool(fc)
                        frs.append(fr)
                    await self.session.send_tool_response(function_responses=frs)

    async def _receive_text(self):
        """Text-only mode receiver."""
        out_buf = []
        while True:
            async for resp in self.session.receive():
                if resp.server_content:
                    sc = resp.server_content
                    if sc.model_turn:
                        for part in sc.model_turn.parts:
                            if hasattr(part, "text") and part.text:
                                out_buf.append(_clean(part.text))
                    if sc.turn_complete:
                        if self._turn_ev: self._turn_ev.set()
                        if out_buf:
                            self.ui.write_log(f"RAHUL: {' '.join(out_buf).strip()}")
                            out_buf = []

                if resp.tool_call:
                    frs = []
                    for fc in resp.tool_call.function_calls:
                        fr = await self._execute_tool(fc)
                        frs.append(fr)
                    await self.session.send_tool_response(function_responses=frs)

    async def _play_audio(self):
        RECV_SR, CHANNELS, CHUNK = 24000, 1, 1024
        stream = self._sd.RawOutputStream(
            samplerate=RECV_SR, channels=CHANNELS, dtype="int16", blocksize=CHUNK
        )
        stream.start()
        try:
            while True:
                try:
                    chunk = await asyncio.wait_for(self.audio_q.get(), timeout=0.1)
                except asyncio.TimeoutError:
                    if (self._turn_ev and self._turn_ev.is_set()
                            and self.audio_q.empty()):
                        self.ui.stop_speaking()
                        self._turn_ev.clear()
                    continue
                self.ui.start_speaking()
                await asyncio.to_thread(stream.write, chunk)
        finally:
            stream.stop(); stream.close()

    # ── Main run loop ──────────────────────────────────────────────────────────
    async def run(self):
        client = genai.Client(api_key=_get_api_key(),
                               http_options={"api_version": "v1beta"})
        while True:
            try:
                print("[RAHUL] Connecting to Gemini…")
                self.ui.set_state("THINKING")
                config = self._build_config()

                async with client.aio.live.connect(model=LIVE_MODEL, config=config) as session:
                    self.session = session
                    self._loop   = asyncio.get_event_loop()
                    self.audio_q = asyncio.Queue()
                    self.out_q   = asyncio.Queue(maxsize=10)
                    self._turn_ev = asyncio.Event()

                    self.ui.set_state("LISTENING")
                    self.ui.write_log("SYS: RAHUL v3.0 online. Type your command below.")

                    async with asyncio.TaskGroup() as tg:
                        if self._audio_enabled:
                            tg.create_task(self._send_realtime())
                            tg.create_task(self._listen_audio())
                            tg.create_task(self._receive_audio())
                            tg.create_task(self._play_audio())
                        else:
                            tg.create_task(self._receive_text())

            except Exception as e:
                print(f"[RAHUL] Error: {e}")
                traceback.print_exc()

            self.ui.stop_speaking()
            self.ui.set_state("THINKING")
            print("[RAHUL] Reconnecting in 3s…")
            await asyncio.sleep(3)


def main():
    ui = RahulUI()

    def runner():
        ui.wait_for_api_key()
        core = RahulCore(ui)
        try:
            asyncio.run(core.run())
        except KeyboardInterrupt:
            print("\n[RAHUL] Shutdown.")

    threading.Thread(target=runner, daemon=True).start()
    ui.root.mainloop()


if __name__ == "__main__":
    main()
