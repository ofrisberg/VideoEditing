import os, sys
import moviepy.editor as mp
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from moviepy.video.VideoClip import TextClip, DataVideoClip
from moviepy.video.io.bindings import mplfig_to_npimage
from datafinder import DataFinder
import moviepy

"""
Creates a video that contains
- GoPro video (full screen, fastforwarded)
- Table with data (top left)
- Plots with data (bottom left)
- Google earth tour (bottom right)

Note that all frames in the subvideos are synced with each other
so dont add intro or credits to avoid confusion.
"""

fullscreen_gopro = False  # else fullscreen map
clip1 = mp.VideoFileClip("v_x10.MP4")  # fast forwarded gopro video
clip2 = mp.VideoFileClip("video_tour.mp4")  # google earth video
speedup = 10  # how many times the video is fast forwarded compared to realtime
margin = 0.1  # from edge
subsize = 0.5  # of main clip
dpi = 96  # your dpi, find out at https://www.infobyip.com/detectmonitordpi.php
mainfps = 30  # the final video output
plotfps = 10  # how many times per "video second" that the graphs should be plotted
plotmask = True  # transparent plot
tablefontsize = 30
debug = False
mpl.rcParams['text.color'] = 'black'
mpl.rcParams['axes.labelcolor'] = 'black'
mpl.rcParams['axes.titlesize'] = 25
outfilename = "video_synced.mp4"

if debug: plotfps = 1

width_px = clip1.size[0]  # 1920
height_px = clip1.size[1]  # 1080
duration = clip1.duration

print("Checking fps...")
if clip1.fps > 31:
    print("clip1.fps > 31")
    sys.exit()
if clip2.fps > 31:
    print("clip2.fps > 31")
    sys.exit()
if os.path.exists(outfilename):
    print(outfilename, "exists")
    sys.exit()

print("Reading data...")
df = DataFinder()
df.init_all()

figsizex = subsize * (1 - 2 * margin) * width_px / dpi
figsizey = subsize * (1 - 2 * margin) * height_px / dpi
if plotmask:  # if plot is transparent, make it larger since white bg padding isnt visible
    figsizex *= 1.2
    figsizey *= 1.2
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(figsizex, figsizey), dpi=dpi)
fig.tight_layout(pad=3.0)
x = []
y1 = []
y2 = []
y3 = []
y4 = []


def toMs(t): return speedup * t * 1000


last_t = None
last_frame = None


def update_plot(ax, x, y, new_val, title, min_val=None, max_val=None):
    ax.clear()
    if min_val is not None and max_val is not None:
        ax.set_ylim(min_val, max_val)
    y.append(new_val)
    ax.plot(x, y)
    ax.set_title(title)


# draw plots
def make_frame(t):
    global x, y1, y2, y3, y4, last_t, last_frame

    if t == last_t:
        return last_frame

    x.append(t)

    update_plot(ax1, x, y1, df.get_acc(toMs(t)), "Acceleration [m/s^2]")
    update_plot(ax2, x, y2, df.get_gyro(toMs(t)), "Gyro [rad/s]")
    update_plot(ax3, x, y3, df.get_bpm(toMs(t)), "Heart rate [bpm]")
    update_plot(ax4, x, y4, df.get_elev(toMs(t)), "Elevation [m]")

    last_t = t
    last_frame = mplfig_to_npimage(fig)
    return last_frame


last_t2 = None
last_frame2 = None


# draw table with data
def make_frame2(t):
    global last_t2, last_frame2
    if t == last_t2:
        return last_frame2

    last_t2 = t

    s = "Distance [km]: " + str(round(df.get_dist(toMs(t)), 2)) + "\n"
    s += "Acc [m/s^2]: " + str(round(df.get_acc(toMs(t)), 2)) + "\n"
    s += "Gyro [rad/s]: " + str(round(df.get_gyro(toMs(t)), 2)) + "\n"
    s += "Heart rate [bpm]: " + str(round(df.get_bpm(toMs(t)), 2)) + "\n"
    s += "Elevation [m]: " + str(round(df.get_elev(toMs(t)))) + "\n"
    s += "Time [s]: " + str(round(toMs(t) / 1000)) + "\n"
    txt = TextClip(txt=s, fontsize=tablefontsize, color="white", align='West', method='caption', size=(350, None))
    last_frame2 = txt.img
    return last_frame2


times = np.arange(0, clip1.duration, 1.0 / plotfps)
animation = DataVideoClip(times, make_frame, fps=plotfps, ismask=False)  # ismask=True not working
# animation.set_opacity(0.5) # not working

text_clip = DataVideoClip(times, make_frame2, fps=plotfps, ismask=False)  # ismask=True not working


def resize_subclip(clip):
    global margin
    print("Resizing subclip")
    if clip1.size[0] < 1920:  # already half size
        clip = clip.resize(1 - 2 * margin)
    else:
        clip = clip.resize(0.5 - margin)
    clip = clip.set_position((0.5 + margin * 0.5, 0.5 + margin * 0.5), relative=True)  # 0.55, 0.55
    return clip


if fullscreen_gopro:
    clip2 = resize_subclip(clip2)
else:
    clip1 = resize_subclip(clip1)
# animation = animation.resize(400, 400) # not working

# When creating a movie in Google earth from a tour, they add a 10 seconds delay for some reason...
clip2 = clip2.subclip(10)
# text_clip = text_clip.subclip(0, 2)

animation = animation.set_position((margin * 0.25, 0.5), relative=True)
text_clip = text_clip.set_position((margin * 0.5, margin * 0.5), relative=True)

print("Mask colors")
if plotmask:
    animation = mp.vfx.mask_color(animation, color=[255, 255, 255])  # remove white
text_clip = mp.vfx.mask_color(text_clip, color=[0, 0, 0])  # remove black

print("Composite")
if fullscreen_gopro:
    video = mp.CompositeVideoClip([clip1, clip2, animation, text_clip])
else:
    video = mp.CompositeVideoClip([clip2, clip1, animation, text_clip])

if debug:
    video = moviepy.video.fx.all.speedx(video, factor=10.0)

if video.fps > 31:
    print("final video fps > 31")
    sys.exit()
video.write_videofile(outfilename, audio=False)
