#!/usr/bin/env python3
import os
import sys
import argparse
from pathlib import Path
from openai import OpenAI
from gtts import gTTS  # Fallback to Google Translate TTS

# Load env manually if needed (or rely on system env)
def load_env(file_path):
    if not os.path.exists(file_path): return
    with open(file_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                parts = line.strip().split('=', 1)
                if len(parts) == 2:
                    if parts[0] not in os.environ:
                        os.environ[parts[0]] = parts[1]

# Try to load .env from workspace root
load_env(os.path.join(os.path.dirname(__file__), '../../../.env'))

def generate_speech_openai(text, output_file="speech.mp3", model="tts-1", voice="alloy"):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found")

    client = OpenAI(api_key=api_key)
    response = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text
    )
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    response.stream_to_file(output_path)
    return str(output_path.absolute())

def generate_speech_gtts(text, output_file="speech.mp3", lang='zh-tw'):
    try:
        # Fallback to gTTS if OpenAI is not available
        print("Falling back to gTTS (Google Translate TTS)...")
        tts = gTTS(text=text, lang=lang)
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tts.save(str(output_path))
        return str(output_path.absolute())
    except Exception as e:
        print(f"Error generating speech with gTTS: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert text to speech using OpenAI API or gTTS")
    parser.add_argument("text", help="Text to convert")
    parser.add_argument("--output", "-o", default="speech.mp3", help="Output file path")
    parser.add_argument("--model", "-m", default="tts-1", help="TTS model (tts-1 or tts-1-hd)")
    parser.add_argument("--voice", "-v", default="alloy", help="Voice (alloy, echo, fable, onyx, nova, shimmer)")
    parser.add_argument("--lang", "-l", default="zh-tw", help="Language code for gTTS fallback")

    args = parser.parse_args()

    # Try OpenAI first
    try:
        generate_speech_openai(args.text, args.output, args.model, args.voice)
        print(f"Audio saved to: {os.path.abspath(args.output)}")
    except Exception as e:
        print(f"OpenAI TTS failed ({e}), trying fallback...")
        generate_speech_gtts(args.text, args.output, args.lang)
        print(f"Audio saved to: {os.path.abspath(args.output)}")
