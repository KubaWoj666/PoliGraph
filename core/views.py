from django.contrib import messages
from django.shortcuts import render, redirect
from .utils import  extract_video_id, split_transcript
from django.shortcuts import render, redirect
from .utils import extract_video_id,  split_transcript, fetch_transcripts
from .embending import embed_and_store_transcript_fragment, embed_user_query



def index_view(request):
    if request.method == "POST":
        video_url = request.POST.get("video")
        video_id = extract_video_id(video_url)

        transcript = fetch_transcripts(video_id)        
        
        blocks = split_transcript(transcript)

        if not blocks:
            messages.error(request, "Brak transkryptu do przetworzenia.")
            return redirect("index")
        

        for i, block in enumerate(blocks):
            if i == 2:
                break
            print(i)
            embed_and_store_transcript_fragment(fragment=block, video_id=video_id, video_ulr=video_url, block_index=i)
            print("done")

        messages.success(request, "Trasscrypt pomyślie zapisany do bazy danych")
        return redirect("index")

    return render(request, "core/index.html")


def search_view(request):
    if request.method == "POST":
        query = request.POST.get("query")
        print(query)
        embed_user_query(query)
        return redirect("index")
    return render(request, "core/index.html")