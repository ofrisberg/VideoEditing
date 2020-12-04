import moviepy
import moviepy.editor as mp
import os


def create_intro(videofilename, title, newfilename):
    def resize(t):
        tmp = (1 - t / duration)
        if tmp < 0.5:
            return 0.5
        return tmp

    def pos(t):
        return 0.5 * t / duration

    if os.path.exists(newfilename): return

    vfc = mp.VideoFileClip(videofilename)
    width = vfc.size[0]
    height = vfc.size[1]
    duration = vfc.duration

    tc = mp.TextClip(title, color='white', size=(width, height), bg_color='black', fontsize=80)
    tc = tc.set_duration(duration - 0.5)
    tc = mp.vfx.mask_color(tc, color=[0, 0, 0])  # remove black

    vfc = vfc.resize(lambda t: resize(t))
    vfc = vfc.set_position(lambda t: (pos(t), pos(t)), relative=True)
    vfc = moviepy.video.fx.all.fadeout(vfc, duration, final_color=[0, 0, 0])
    concat_clip = mp.CompositeVideoClip([vfc, tc])
    concat_clip.write_videofile(newfilename)


if __name__ == "__main__":
    newintroname = "video_intro_edit.mp4"
    outroname = "video_outro.mp4"
    create_intro("video_intro.mp4", "Running trip 2020-10-13", newintroname)
    vfc = mp.VideoFileClip("video_synced_events2.mp4")
    # vfc = vfc.speedx(factor=2.0)

    vfcs = [mp.VideoFileClip(newintroname), vfc, mp.VideoFileClip(outroname)]
    concat_clip = mp.concatenate_videoclips(vfcs, method="compose")

    new_audioclip = mp.AudioFileClip("a.mp3")
    new_audioclip = mp.CompositeAudioClip([new_audioclip, vfc.audio.set_start(vfcs[0].duration)])
    concat_clip.audio = new_audioclip

    concat_clip = concat_clip.afx(moviepy.audio.fx.audio_fadeout.audio_fadeout, 3)

    concat_clip.write_videofile("video_final.mp4", threads=4)
