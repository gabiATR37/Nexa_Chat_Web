from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .services.youtube import search_youtube


@login_required
def music_home(request):

    query = request.GET.get("q", "").strip()

    songs = []

    if query:
        songs = search_youtube(query)

        for song in songs:
            song["platform"] = "youtube"

    return render(
        request,
        "music/index.html",
        {
            "query": query,
            "songs": songs,
            "artists": [],
            "albums": [],
            "playlists": [],
            "trends": [],
        },
    )