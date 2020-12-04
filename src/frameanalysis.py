import moviepy.editor as mp
from datafinder import DataFinder
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from moviepy.video.VideoClip import TextClip, DataVideoClip
from moviepy.video.io.bindings import mplfig_to_npimage

clip1 = mp.VideoFileClip("gyro2.MP4",fps_source="fps")
speedup = 1.0
duration = clip1.duration
margin = 0.1  # from edge
dpi = 96  # your dpi, find out at https://www.infobyip.com/detectmonitordpi.php
plotfps = 30  # how many times per "video second" that the graphs should be plotted
plotmask = True  # transparent plot
width_px = clip1.size[0]  # 1920
height_px = clip1.size[1]  # 1080

print("duration", clip1.duration)
print("fps", clip1.fps)
print("width", clip1.size[0])
print("height", clip1.size[1])

df = DataFinder(10, False, timekey="Milliseconds")
df.init_gyro_vecs(csvpath="gyro2-gyro.csv")


def toMs(t): return speedup * t * 1000 + 1000


figsizex = (1 - 2 * margin) * width_px / dpi
figsizey = (1 - 2 * margin) * height_px / dpi
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
    gyro_vec = df.get_gyro_vec(toMs(t))
    minlim = -5.0
    maxlim = 5.0

    update_plot(ax1, x, y1, gyro_vec[0], "Gyro X", minlim, maxlim)
    update_plot(ax2, x, y2, gyro_vec[1], "Gyro Y", minlim, maxlim)
    update_plot(ax3, x, y3, gyro_vec[2], "Gyro Z", minlim, maxlim)

    last_t = t
    last_frame = mplfig_to_npimage(fig)
    return last_frame


times = np.arange(0, clip1.duration, 1.0 / plotfps)
animation = DataVideoClip(times, make_frame, fps=plotfps, ismask=False)  # ismask=True not working
animation = animation.set_position((margin * 0.5, margin * 0.5), relative=True)
if plotmask:
    animation = mp.vfx.mask_color(animation, color=[255, 255, 255])  # remove white

video = mp.CompositeVideoClip([clip1, animation])
video.write_videofile("gyro2e.mp4", audio=False)
