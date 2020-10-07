import os, sys
import moviepy.editor as mp


def speedup_and_merge(videos, speedup, newfilename):

    if os.path.exists(newfilename):
        print(newfilename+" already exists")
        return

    videos_speed = []
    for video in videos:

        # Too slow
        """speedup_inv = 1.0 / speedup
        s = str(speedup)
        s_inv = str(speedup_inv)
        syscall = 'ffmpeg -i '+video+'.MP4 -filter_complex "[0:v]setpts='+s_inv+'*PTS[v];[0:a]atempo='+s+'[a]" -map "[v]" -map "[a]" '+video+'_speed.MP4'
        print("System call", syscall)
        os.system(syscall)"""

        # Incorrect result
        """s = str((1.0 / speedup))
        syscall = 'ffmpeg -itsscale '+s+' -i '+video+'.MP4 -c copy '+video+'_speed.MP4'
        os.system(syscall)"""

        # Slow
        if os.path.exists(video + "_speed.MP4") is False:
            vfc = mp.VideoFileClip(video + ".MP4")
            vfc_speed = vfc.speedx(factor=speedup)
            vfc_speed.write_videofile(video + "_speed.MP4")
        else:
            print(video + "_speed.MP4 already exist. Skipping.")
        videos_speed.append(video + "_speed.MP4")

    vfcs = []
    for video in videos_speed:
        vfcs.append(mp.VideoFileClip(video))
    concat_clip = mp.concatenate_videoclips(vfcs, method="compose")
    concat_clip.write_videofile(newfilename)


if __name__ == "__main__":
    videos = ['v1', 'v2', 'v3']  # .MP4 files
    speedup_and_merge(videos, 10.0, "video_speed.MP4")
