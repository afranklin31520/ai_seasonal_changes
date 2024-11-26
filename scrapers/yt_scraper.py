import youtube_transcript_api as yt
import os
import json
import googleapiclient.discovery
import googleapiclient.errors
import datetime
from database_inserter import insert_into_db
def get_youtube_video_text(video_id:str) -> str:
    text = yt.YouTubeTranscriptApi().get_transcript(video_id=video_id)
    myStr = ""
    for caption in text:
       myStr+=caption['text']+" "
    return myStr

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
def batch_insert():
    with open(r"C:\Users\afran\Downloads\ai_research\credentials\client_secret.json") as file:
        #YOUR API KEY HERE
        API_KEY = None
        pass
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"

    # Get credentials and create an API client
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=API_KEY)

    get_vid_ids = youtube.search().list(
        part="snippet",
        maxResults=50,
        q="ai summer",
        type="video",
        videoCaption="closedCaption"
    )
    response = get_vid_ids.execute()
    video_info = {}
    video_info["video_ids"] = {}
    for video in response["items"]:
        try:
            title = video["snippet"]["title"]
            author = video["snippet"]["channelTitle"]
            pub_date = video["snippet"]["publishedAt"]
            pub_date = pub_date.split("T")[0].split("-")
            pub_date = datetime.date(year=int(pub_date[0]),month=int(pub_date[1]),day=int(pub_date[2]))
            vid_id = video["id"]["videoId"]
            tags_request = youtube.videos().list(
                part="snippet,topicDetails,paidProductPlacementDetails",
                id=vid_id
            ).execute()
            tags : dict = tags_request["items"][0].get("snippet")
            tags = "".join(tags.get("tags")) if tags.get("tags") else ""
            url = "https://www.youtube.com/watch?v=" + vid_id
            summary = video["snippet"]["description"].replace('"',"'")
            full_text = get_youtube_video_text(vid_id).replace('"',"'")
            geo_aff , ins_aff , funding = "","", ""
            values = [title,author,pub_date,url,summary,full_text,tags,funding,geo_aff,ins_aff]
            insert_into_db(values)
            print("video record added to db")
        except Exception as e:
            pass


    