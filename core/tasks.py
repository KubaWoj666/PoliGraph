from celery import shared_task
from .models import Video, TranscriptSegment, Tag
from openai import OpenAI
from more_itertools import chunked  # pip install more-itertools

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)

@shared_task
def test_celery_task():
    print("✅ Celery is working!")
    return "Done"



# @shared_task
# def tag_video_segments(video_id):
#     video = Video.objects.get(id=video_id)
#     segments = TranscriptSegment.objects.filter(video=video)
#     texts = [{"text": s.text} for s in segments]
#     tag_lists = deepseek_batch_response(texts)

#     for segment, tags in zip(segments, tag_lists):
#         tag_objs = []
#         for tag in tags:
#             tag_obj, _ = Tag.objects.get_or_create(name=tag.strip())
#             print("tag_obj", tag_obj)
#             tag_objs.append(tag_obj)
#         segment.tags.set(tag_objs)

@shared_task
def tag_video_segments(video_id):
    video = Video.objects.get(id=video_id)
    segments = TranscriptSegment.objects.filter(video=video).order_by('start_time')

    for segment in segments:
        tags = deepseek_response(segment.text)  # jedno zapytanie do modelu
        tag_objs = []
        for tag in tags:
            clean_tag = tag.strip()
            if clean_tag:
                tag_obj, _ = Tag.objects.get_or_create(name=clean_tag)
                tag_objs.append(tag_obj)
        segment.tags.set(tag_objs)
    
    print("Done ✅✅")

    video.save()



# @shared_task
# def tag_video_segments(video_id):
#     video = Video.objects.get(id=video_id)
#     segments = list(TranscriptSegment.objects.filter(video=video).order_by("start_time"))

#     chunk_size = 30
#     for chunk in chunked(segments, chunk_size):
#         prompt = (
#             "For each of the following text fragments, assign 5 short thematic tags in Polish. "
#             "Each set of tags should be on a separate line, separated by commas. "
#             "Respond only with the tags — no numbering, no extra formatting, no additional comments.\n\n"
#         )

#         for i, seg in enumerate(chunk):
#             prompt += f"{i+1}. {seg.text.strip()}\n"

#         try:
#             response = client.chat.completions.create(
#                 model="deepseek/deepseek-chat-v3-0324:free",
#                 messages=[{"role": "user", "content": prompt}]
#             )

#             lines = response.choices[0].message.content.strip().splitlines()
#             if len(lines) != len(chunk):
#                 raise ValueError("Mismatch: number of tag lines doesn't match number of segments")

#             for segment, tag_line in zip(chunk, lines):
#                 tags = [t.strip() for t in tag_line.split(",") if t.strip()]
#                 tag_objs = [Tag.objects.get_or_create(name=tag)[0] for tag in tags]
#                 segment.tags.set(tag_objs)

#         except Exception as e:
#             print("❌ Błąd w chunku:", e)

#     video.save()



import json


# @shared_task
# def tag_video_segments(video_id):
#     video = Video.objects.get(id=video_id)
#     segments = list(TranscriptSegment.objects.filter(video=video).order_by("start_time"))

#     for seg in segments:
#         try:
#             response = client.chat.completions.create(
#                 model="openai/gpt-4o-mini",  # lub np. gpt-3.5
#                 messages=[
#                     {
#                         "role": "user",
#                         "content": f"Przypisz dokładnie 5 krótkich tematycznych tagów w języku polskim do tego tekstu:\n\n{seg.text}\n\nZwróć tylko tablicę tagów w JSON-ie: [\"tag1\", \"tag2\", ...]"
#                     }
#                 ],
#                 temperature=0.5,
#             )

#             raw_text = response.choices[0].message.content.strip()
#             tags = json.loads(raw_text)

#             tag_objs = [Tag.objects.get_or_create(name=tag.strip())[0] for tag in tags]
#             seg.tags.set(tag_objs)

#         except Exception as e:
#             print(f"❌ Błąd dla segmentu ID {seg.id}:\n", e)

#     video.save()
#     print("✅ Gotowe – tagi przypisane!")
