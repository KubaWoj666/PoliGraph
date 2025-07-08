from celery import shared_task
from .models import Video, TranscriptSegment, Tag
from openai import OpenAI
from more_itertools import chunked  # pip install more-itertools
from environs import Env

env = Env()
env.read_env()


client = OpenAI(
  base_url=env.str("OPENAI_API_BASE"),
  api_key=env.str("OPENAI_API_KEY"),
)

@shared_task
def test_celery_task():
    print("✅ Celery is working!")
    return "Done"





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




