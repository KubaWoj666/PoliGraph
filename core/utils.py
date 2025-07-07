import tempfile
import yt_dlp
import whisper

import tempfile
import os
import yt_dlp
import whisper
import json

from sentence_transformers import SentenceTransformer
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound


from transformers import pipeline
from datetime import timedelta

def format_seconds(seconds_str):
    seconds = float(seconds_str)
    return str(timedelta(seconds=int(seconds)))

def split_transcript(transcript, max_duration=90):
    # odfiltrowanie nieprawidłowych wpisów
    transcript = transcript[0].get("tracks")[0].get("transcript")
    transcript = [entry for entry in transcript if "start" in entry and "text" in entry]

    if not transcript:
        raise ValueError("Transkrypt nie zawiera żadnych poprawnych wpisów z kluczem 'start'.")

    blocks = []
    current_block = []
    current_start = float(transcript[0]["start"])
    current_end = current_start + max_duration

    for entry in transcript:
        start = float(entry["start"])
        if start < current_end:
            current_block.append(entry)
        else:
            blocks.append(current_block)
            current_block = [entry]
            current_start = start
            current_end = current_start + max_duration

    if current_block:
        blocks.append(current_block)

    # formatowanie bloków do czytelnego tekstu
    formatted_blocks = []
    for block in blocks:
        start_time_str = format_seconds(block[0]["start"])
        text = " ".join(entry["text"] for entry in block)
        formatted_blocks.append({
            "start": start_time_str,
            "text": text.strip()
        })

    return formatted_blocks



def transcribe_from_youtube(url):
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "audio.%(ext)s")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        final_audio_path = os.path.join(tmpdir, "audio.wav")

        model = whisper.load_model("large")
        result = model.transcribe(final_audio_path)

    return result




model = SentenceTransformer("all-MiniLM-L6-v2")

def process_transcript(result, youtube_url):
    segments = result["segments"]
    texts = [seg["text"] for seg in segments]
    embeddings = model.encode(texts)

    upload_transcript_segments(segments, embeddings, youtube_url)


def transcription_from_yt(video_id):
    print(1)
    result = []
    print(2)
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['pl'])
    print(3)
    for entry in transcript:
        result.append({
            "start": entry['start'],
            "text": entry['text']
        })
    print(4)
    return result

import requests
import base64

API_TOKEN = "6863af7f3cf63c8e7e6b9f0f"
auth = base64.b64encode(f"{API_TOKEN}:".encode()).decode()

def fetch_transcripts(ids):
    API_TOKEN = "6863af7f3cf63c8e7e6b9f0f"  # bez "Bearer", tylko sam token
    auth = base64.b64encode(f"{API_TOKEN}:".encode()).decode()

    headers = {
        "Authorization": f"Basic {API_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://www.youtube-transcript.io/api/transcripts",
        headers=headers,
        json={"ids": ["G1STw9_At-E"]}  # samo video_id
    )

    response.raise_for_status()
    return response.json()

# from youtube_transcript_api import YouTubeTranscriptApi
# from youtube_transcript_api.formatters import TextFormatter
# from youtube_transcript_api._errors import NoTranscriptFound

# def transcription_from_yt(video_id):
#     try:
#         transcripts = YouTubeTranscriptApi.list_transcripts(video_id)

#         # Najpierw sprawdź, czy są generowane po polsku
#         try:
#             transcript = transcripts.find_generated_transcript(['pl']).fetch()
#         except:
#             print("⚠️ Nie znaleziono auto-generowanego transkryptu PL, próbuję inne...")
#             transcript = transcripts.find_transcript(['pl', 'en']).fetch()

#         return [{"start": entry["start"], "text": entry["text"]} for entry in transcript]

#     except NoTranscriptFound:
#         print(f"❌ Brak transkryptu dla filmu: {video_id}")
#         return []
#     except Exception as e:
#         print(f"❌ Błąd transkrypcji: {e}")
#         return []

# def split_transcript(transcript, block_duration=75, step=15):
#     blocks = []
#     times = [entry["start"] for entry in transcript]
#     max_time = max(times)

#     current_start = 0.0

#     while current_start < max_time:
#         current_end = current_start + block_duration

#         # Wybierz wpisy, które mieszczą się w przedziale czasowym
#         block_entries = [
#             entry for entry in transcript
#             if current_start <= float(entry["start"]) < current_end
#         ]

#         if block_entries:
#             block_text = " ".join([entry["text"] for entry in block_entries])
#             blocks.append({
#                 "start": round(current_start, 2),
#                 "end": round(min(current_end, max_time), 2),
#                 "text": block_text
#             })

#         current_start += step

#     return blocks

generator = pipeline("text2text-generation", model="google/flan-t5-base")



def extract_video_id(url):
    import re
    match = re.search(r"v=([^&]+)", url)
    return match.group(1) if match else None



# def save_blocks_to_jsonl(blocks, output_path="transcript_blocks.jsonl"):
#     with open(output_path, "w", encoding="utf-8") as f:
#         for block in blocks:
#             f.write(json.dumps(block, ensure_ascii=False) + "\n")

#def generate_tags(text):
#     max_chunk_chars = 800  # orientacyjnie: 512 tokenów ≈ 750–800 znaków

#     # Jeśli tekst za długi – przytnij
#     if len(text) > max_chunk_chars:
#         text = text[:max_chunk_chars]

#     prompt = f"Przypisz 10 krótkie tagi tematyczne do tego tekstu: {text}"
#     response = generator(prompt, max_length=50, do_sample=False)
#     return response[0]['generated_text']