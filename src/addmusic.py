import re
import urllib.parse
import urllib.request
import webbrowser
import youtube_dl
from moviepy.editor import *
from moviepy.audio.fx.audio_fadeout import audio_fadeout

"""
Download mp3 from youtube
Add mp3 to final video (without audio)
"""


def download(code, newfilename):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }
    ydl_opts['outtmpl'] = newfilename
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(["https://www.youtube.com/watch?v=" + code])


def scrape(query):
    query_string = urllib.parse.urlencode({"search_query": query})
    html_content = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)
    text = html_content.read().decode()
    # print(text)
    search_results = re.findall(r'videoId\":\"(.{11})', text)
    return search_results[0]


def watch(code):
    webbrowser.open_new_tab("https://www.youtube.com/watch?v=" + code)


def add_music(oldvideoname, newvideoname, youtube_code, audiofadeouttime=5):
    videoclip = VideoFileClip(oldvideoname)

    tmpaudiofile = youtube_code + ".mp3"
    if os.path.exists(tmpaudiofile) is False:
        print("downloading mp3 file from youtube")
        download(youtube_code, tmpaudiofile)
    else:
        print("mp3 file already exists, no need to download")

    new_audioclip = AudioFileClip(tmpaudiofile)
    new_audioclip = CompositeAudioClip([new_audioclip])
    videoclip.audio = new_audioclip
    videoclip = videoclip.afx(audio_fadeout, audiofadeouttime)
    videoclip.write_videofile(newvideoname)


if __name__ == '__main__':
    add_music("video_final_without_audio.mp4", "video_final.mp4", "Mn9RcmkPBm4")  # knock knock

    if False:
        query = input("Search song title and/or artist:")
        ytube_code = scrape(query)
        print(ytube_code)
        input("Press any key to watch in browser")
        watch(ytube_code)
        if input("Do you want to use it? (Y/n)") == "n":
            pass
        else:
            newfilename = ytube_code + ".mp3"
            download(ytube_code, newfilename)
