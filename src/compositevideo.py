import moviepy.editor as mp
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from moviepy.video.VideoClip import TextClip, DataVideoClip
from moviepy.video.io.bindings import mplfig_to_npimage
from datafinder import DataFinder

"""
Creates a video that contains
- GoPro video (full screen, fastforwarded)
- Table with data (top left)
- Plots with data (bottom left)
- Google earth tour (bottom right)

Note that all frames in the subvideos are synced with each other
so dont add intro or credits to avoid confusion.
"""

clip1 = mp.VideoFileClip("video_speed2.MP4")  # fast forwarded gopro video
clip2 = mp.VideoFileClip("tour.mp4")  # google earth video
speedup = 10  # how many times the video is fast forwarded compared to realtime
margin = 0.1  # from edge
subsize = 0.5  # of main clip
dpi = 96  # your dpi, find out at https://www.infobyip.com/detectmonitordpi.php
plotfps = 10  # how many times per "video second" that the graphs should be plotted
plotmask = True  # transparent plot
width_px = clip1.size[0]  # 1920
height_px = clip1.size[1]  # 1080
tablefontsize = 30

duration = clip1.duration

print("Reading data...")
df = DataFinder()

COLOR = 'black'
mpl.rcParams['text.color'] = COLOR
mpl.rcParams['axes.labelcolor'] = COLOR

figsizex = subsize * (1 - 2 * margin) * width_px / dpi
figsizey = subsize * (1 - 2 * margin) * height_px / dpi
if plotmask:  # if plot is transparent, make it larger since white bg padding isnt visible
    figsizex *= 1.1
    figsizey *= 1.1
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


# draw plots
def make_frame(t):
    global x, y1, y2, y3, y4, last_t, last_frame

    if t == last_t:
        return last_frame

    # print("makeframe", t)

    ax1.clear()
    ax2.clear()
    ax3.clear()
    ax4.clear()

    x.append(t)

    y1.append(df.get_acc(toMs(t)))
    ax1.plot(x, y1)
    ax1.set_title("Acceleration [m/s^2]")

    y2.append(df.get_gyro(toMs(t)))
    ax2.plot(x, y2, 'tab:orange')
    ax2.set_title("Gyro")

    y3.append(df.get_dist(toMs(t)))
    ax3.plot(x, y3, 'tab:green')
    ax3.set_title("Distance [m]")

    y4.append(df.get_elev(toMs(t)))
    ax4.plot(x, y4, 'tab:red')
    ax4.set_title("Elevation [m]")

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
    s += "Gyro: " + str(round(df.get_gyro(toMs(t)), 2)) + "\n"
    s += "Elevation [m]: " + str(round(df.get_elev(toMs(t)))) + "\n"
    s += "Time [s]: " + str(round(toMs(t) / 1000)) + "\n"
    txt = TextClip(txt=s, fontsize=tablefontsize, color="white", align='West', method='caption', size=(350, None))
    last_frame2 = txt.img
    return last_frame2


times = np.arange(0, clip1.duration, 1.0 / plotfps)
animation = DataVideoClip(times, make_frame, fps=plotfps, ismask=False)  # ismask=True not working
# animation.set_opacity(0.5) # not working

text_clip = DataVideoClip(times, make_frame2, fps=plotfps, ismask=False)  # ismask=True not working

print("Resize 80%")
clip2 = clip2.resize(1 - 2 * margin)
# animation = animation.resize(400, 400) # not working

print("Set start")
clip2 = clip2.subclip(10)
# text_clip = text_clip.subclip(0, 2)

print("Set position")
clip2 = clip2.set_position((0.5 + margin * 0.5, 0.5 + margin * 0.5), relative=True)  # 0.55, 0.55
animation = animation.set_position((margin * 0.5, 0.5 + margin * 0.5), relative=True)
text_clip = text_clip.set_position((margin * 0.5, margin * 0.5), relative=True)

print("Mask colors")
if plotmask:
    animation = mp.vfx.mask_color(animation, color=[255, 255, 255])  # remove white
text_clip = mp.vfx.mask_color(text_clip, color=[0, 0, 0])  # remove black

print("Composite")
video = mp.CompositeVideoClip([clip1, clip2, animation, text_clip])
video.write_videofile("video_gp_map_stab.mp4", audio=False)
