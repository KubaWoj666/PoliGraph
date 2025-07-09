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
from django.contrib import messages

from transformers import pipeline
from datetime import timedelta

import requests
from environs import Env

env = Env()
env.read_env()


def format_seconds(seconds_str):
    seconds = float(seconds_str)
    return str(timedelta(seconds=int(seconds)))

def split_transcript(transcript, max_duration=90):
    # odfiltrowanie nieprawidłowych wpisów
    
    try:
        transcript = transcript[0].get("tracks")[0].get("transcript")
        transcript = [entry for entry in transcript if "start" in entry and "text" in entry]
    except (IndexError, AttributeError, TypeError):
        print("DUP")
        return []

    if not transcript:
        print("PAPAPA")
        return []
    # if not transcript:
    #     raise ValueError("Transkrypt nie zawiera żadnych poprawnych wpisów z kluczem 'start'.")

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



def fetch_transcripts(ids):

    headers = {
        "Authorization": f"Basic {env.str("API_TOKEN")}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        env.str("API_URL"),
        headers=headers,
        json={"ids": [ids]}  
    )

    response.raise_for_status()
    return response.json()


def extract_video_id(url):
    import re
    match = re.search(r"v=([^&]+)", url)
    return match.group(1) if match else None


# def transcription_from_yt(video_id):
#     print(1)
#     result = []
#     print(2)
#     transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['pl'])
#     print(3)
#     for entry in transcript:
#         result.append({
#             "start": entry['start'],
#             "text": entry['text']
#         })
#     print(4)
#     return result



