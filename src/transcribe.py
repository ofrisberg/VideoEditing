import speech_recognition as sr
from pydub import AudioSegment
import moviepy.editor as mp
from pydub.utils import make_chunks
import math

AudioSegment.converter = "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe"
AudioSegment.ffmpeg = "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe"
AudioSegment.ffprobe = "C:\\Program Files\\ffmpeg\\bin\\ffprobe.exe"


def mp4_to_wav(videofilename="v2.MP4"):  # working
    # Insert Local Video File Path
    clip = mp.VideoFileClip(videofilename)
    # Insert Local Audio File Path
    clip.audio.write_audiofile(videofilename + ".wav", codec='pcm_s16le')
    # AudioSegment.from_wav("v2.wav").export("v2.mp3", format="mp3")


def split():
    myaudio = AudioSegment.from_file("v2.wav", "wav")
    channel_count = myaudio.channels  # Get channels
    sample_width = myaudio.sample_width  # Get sample width
    duration_in_sec = len(myaudio) / 1000  # Length of audio in sec
    sample_rate = myaudio.frame_rate

    """print
    "sample_width=", sample_width
    print
    "channel_count=", channel_count
    print
    "duration_in_sec=", duration_in_sec
    print
    "frame_rate=", sample_rate"""
    bit_rate = 16  # assumption , you can extract from mediainfo("test.wav") dynamically

    wav_file_size = (sample_rate * bit_rate * channel_count * duration_in_sec) / 8
    """print
    "wav_file_size = ", wav_file_size"""

    file_split_size = 10000000  # 10Mb OR 10, 000, 000 bytes
    total_chunks = wav_file_size // file_split_size

    # Get chunk size by following method #There are more than one ofcourse
    # for  duration_in_sec (X) -->  wav_file_size (Y)
    # So   whats duration in sec  (K) --> for file size of 10Mb
    #  K = X * 10Mb / Y

    chunk_length_in_sec = math.ceil((duration_in_sec * 10000000) / wav_file_size)  # in sec
    chunk_length_ms = chunk_length_in_sec * 1000
    chunks = make_chunks(myaudio, chunk_length_ms)

    # Export all of the individual chunks as wav files

    for i, chunk in enumerate(chunks):
        chunk_name = "chunk{0}.wav".format(i)
        print("exporting", chunk_name)
        chunk.export(chunk_name, format="wav")


def test(wavfile):
    r = sr.Recognizer()
    with sr.AudioFile(wavfile) as source:
        audio = r.record(source)  # read the entire audio file
        text = r.recognize_google(audio, language="sv-SE", show_all=True)
        print(text)


#mp4_to_wav("v3_event_l258_g2379.mp4")
test("v3_event_l258_g2379.mp4.wav")
