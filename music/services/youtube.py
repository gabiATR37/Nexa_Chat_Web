from googleapiclient.discovery import build
from django.conf import settings


def search_youtube(query):

    youtube = build(
        "youtube",
        "v3",
        developerKey=settings.YOUTUBE_API_KEY
    )

    request = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        videoCategoryId="10",
        maxResults=1000,
        videoEmbeddable="true",
        videoSyndicated="true"
    )

    response = request.execute()

    songs = []

    for item in response["items"]:

        video_id = item.get("id", {}).get("videoId")

        if not video_id:
            continue

        songs.append({
            "id": video_id,
            "title": item["snippet"]["title"],
            "artist": item["snippet"]["channelTitle"],
            "image": item["snippet"]["thumbnails"]["high"]["url"],
        })

    return songs