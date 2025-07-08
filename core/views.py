from django.shortcuts import render, redirect
from django.http import HttpResponse
from .utils import  extract_video_id, split_transcript #save_blocks_to_jsonl
from qdrant_client import QdrantClient

from django.views.decorators.csrf import csrf_exempt


from .models import Video, Tag, TranscriptSegment


from django.shortcuts import render, redirect
from .utils import extract_video_id,  split_transcript, fetch_transcripts
from .embending import embed_and_store_transcript_fragment
from .models import Video, TranscriptSegment
from .summarize_and_tag import summarize_and_tag

import json

text = "szokujące, no ale on gra na najniższych instynktach. Gra będzie się teraz toczyć o każdy głos, każdy jeden. A więc do kogo trafi głos Joanny Syyszyn? na pewno nie trafi do Nawrockiego. No jako matka terminu kaczyzm to przecież jest niemożliwe, żebym Kaczystikolwiek sposób wspierała. No ale to decydujące będzie, co będą chcieli, czego będą chcieli moi wyborcy. Dlatego, że oni nie chcieli ani Nawrockiego, ani Trzaskowskiego. Oni chcieli, no nie chcieli też trzeciej nogi i wybrali senyszyn. Pani chciała być matką wszystkich Polaków. Na razie wychodzi na to, że Polacy wolą ojca. Natomiast żeby pani została tą matką w dłuższym dystansie, no to naprawdę trzeba wykazać się dużym zaangażowaniem. Czy pani ma do tego energię? Znaczy ja widzę, że pani ma dużo energii, natomiast czy pani chce się tak na maksa zaangażować w polityce, w politykę, czy też będzie pani takim"

def index_view(request):
    if request.method == "POST":
        video_url = request.POST.get("video")
        video_id = extract_video_id(video_url)
        # summarize = summarize_and_tag(text)
        # print(summarize.get("summary"))


        # sprawdź czy już jest takie wideo
        # video, created = Video.objects.get_or_create(url=video_url)

        transcript = fetch_transcripts(video_id)
        # print(transcript[0].get("tracks")[0])

        # if created:
        # transcript = transcription_from_yt(video_id)
        blocks = split_transcript(transcript)
        # print(blocks[0])

        for i, block in enumerate(blocks):
            if i == 1:
                break
            print(i)
            embed_and_store_transcript_fragment(fragment=block, video_id=video_id, video_ulr=video_url, block_index=i)
            print("done")

        # for block in blocks:
        #     embed_and_store_transcript_fragment(block, video_url)
            # TranscriptSegment.objects.create(
            #     video=video,
            #     start_time=block.get("start"),
            #     end_time=block.get("end"),
            #     text=block.get("text")
            # )

        # uruchom tagowanie asynchronicznie
        # print(test_celery_task())
        # tag_video_segments.delay(video.id)

        # return HttpResponse(json.dumps(transcript[0].get("tracks")[0].get("transcript")), content_type='application/json')
        return redirect("index")

    return render(request, "core/index.html")



# def index_view(request):
#     # tags = Tag.objects.all()
#     if request.method == "POST":
#         video_url = request.POST.get("video")
#         video_id = extract_video_id(video_url)
#         transcript = transcription_from_yt(video_id)
#         bloks = split_transcript(transcript)
#         # response = deepseek_batch_response(bloks)
#         # print(response)
#         print(test_celery_task())
#         # video = Video.objects.create(url=video_url)
#         # video.save
#         # text = bloks[0:3]
#         # for i , blok in enumerate(bloks, s):
#         #     print()
#         #     blok.get('text')

#         #     if i == 5:
#         #         break
#         # response = deepseek_batch_response(text)
#         # print(response)
#         # save_blocks_to_jsonl(bloks)
#         # print(bloks)

#         # tags = meta_response(text)
#         # print(tags)
        
#         # tags = deepseek_response(text)
#         # print(tags)

#         # tags = generate_response(text)
#         # print(tags)

    

#         for i in bloks:
#             # print(1)
#             start = i.get("start")
#             end = i.get("end")
#             text = i.get("text")

#             # tags = deepseek_response(text)
#             # tag_objs = []
#             # print(2)

#             # for t in tags:
#             #     tag_obj, _ = Tag.objects.get_or_create(name=t)
#             #     tag_objs.append(tag_obj)
#             #     print(3)
#             # print(4)
#             # transcript_segment = TranscriptSegment.objects.create(
#             #     start_time=start,
#             #     end_time=end,
#             #     text=text,
#             #     video=video
#             # )
#             # transcript_segment.tags.set(tag_objs)
#             # transcript_segment.save()



#         return redirect("index")


#     context = {}

#     return render(request, "core/index.html", context)
