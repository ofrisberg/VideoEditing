import moviepy
import moviepy.editor as mp


def create_intro(videofilename, title, newfilename):
    def resize(t):
        tmp = (1 - t / duration)
        if tmp < 0.5:
            return 0.5
        return tmp

    def pos(t):
        return 0.5 * t / duration

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
    #create_intro("video_intro.mp4", "Running trip 2020-09-30", newintroname)
    vfc = mp.VideoFileClip("video_gp_map_stab.mp4")
    vfc = vfc.speedx(factor=2.0)
    vfcs = [mp.VideoFileClip(newintroname), vfc]
    concat_clip = mp.concatenate_videoclips(vfcs, method="compose")
    concat_clip.write_videofile("video_final_without_audio.mp4")
