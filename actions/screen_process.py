"""screen_process.py — Capture screen/webcam and analyze with Gemini Vision"""
import os, time, base64, tempfile, threading


def screen_process(parameters: dict, player=None) -> str:
    angle = parameters.get("angle", "screen")
    text  = parameters.get("text", "What do you see on the screen?")

    img_path = None

    try:
        if angle == "camera":
            img_path = _capture_camera()
        else:
            img_path = _capture_screen()

        if not img_path or not os.path.exists(img_path):
            if player:
                player.write_log("ERR: Could not capture image.")
            return "Screen capture failed."

        if player:
            player.show_image(img_path)
            player.write_log("SYS: Screen captured — analyzing…")

        # Analyze with Gemini Vision
        result = _analyze_with_gemini(img_path, text, player)
        return result

    except Exception as e:
        return f"Screen process error: {e}"


def _capture_screen() -> str:
    ts   = time.strftime("%Y%m%d_%H%M%S")
    path = f"/tmp/screen_{ts}.png"
    tools = [
        f"scrot {path}",
        f"import -window root {path}",
        f"gnome-screenshot -f {path}",
        f"maim {path}",
    ]
    for tool in tools:
        cmd = tool.split()[0]
        if os.system(f"which {cmd} > /dev/null 2>&1") == 0:
            os.system(tool)
            if os.path.exists(path):
                return path
    return ""


def _capture_camera() -> str:
    ts   = time.strftime("%Y%m%d_%H%M%S")
    path = f"/tmp/camera_{ts}.jpg"
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                cv2.imwrite(path, frame)
                return path
    except ImportError:
        pass
    # Fallback: fswebcam
    os.system(f"fswebcam -r 1280x720 --no-banner {path}")
    return path if os.path.exists(path) else ""


def _analyze_with_gemini(img_path: str, prompt: str, player) -> str:
    try:
        import json
        from pathlib import Path
        config_file = Path(__file__).resolve().parent.parent / "config" / "api_keys.json"
        api_key = json.loads(config_file.read_text())["gemini_api_key"]

        from google import genai
        from google.genai import types

        with open(img_path, "rb") as f:
            img_bytes = f.read()

        client   = genai.Client(api_key=api_key,
                                 http_options={"api_version": "v1beta"})
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                types.Part.from_text(text=prompt),
            ],
        )
        result = response.text.strip()

        if player:
            player.write_log(f"RAHUL: {result[:200]}")

        return result

    except Exception as e:
        return f"Vision analysis error: {e}"
