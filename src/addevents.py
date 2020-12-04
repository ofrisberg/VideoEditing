import sys
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import csv
import json
import moviepy.editor as mp
import moviepy
import datetime


def _get_ms(row):
    if "ï»¿Milliseconds" in row:
        return float(row["ï»¿Milliseconds"])
    return float(row["Milliseconds"])


def get_events(gyrofile, do_plot=False):
    y = []
    x = []
    lastEvent = None
    eventMin = 5 * 1000
    eventMax = 40 * 1000
    noise = 3.7
    snr = 2.0
    interval = 50
    events = []
    with open(gyrofile, newline='\n') as fh:
        reader = csv.DictReader(fh)
        lastTime = -1000
        for row in reader:
            # print(row)
            ms = _get_ms(row)
            if ms > lastTime + interval:
                yx = float(row['GyroX'])
                yy = float(row['GyroY'])
                yz = float(row['GyroZ'])
                v = np.linalg.norm(np.array([yx, yy, yz]))

                if v / noise > snr:
                    if lastEvent is None:
                        lastEvent = ms
                    elif ms - lastEvent > eventMin:
                        # print("Event start:", lastEvent / 1000, " stop:", ms / 1000)
                        events.append({
                            'start': lastEvent / 1000,
                            'end': ms / 1000
                        })
                        lastEvent = None
                y.append(v)
                x.append(ms)
                lastTime = ms
                if lastEvent is not None and ms - lastEvent > eventMax:
                    # print("Event start:", lastEvent / 1000, " stop: none")
                    lastEvent = None
    if do_plot:
        plt.plot(x, y)
        plt.show()
    return events


def event2video(event, videos, vfcs, autosave=False):
    offset = 0
    for i in range(len(vfcs)):
        vfc = vfcs[i]
        currentMax = vfc.duration + offset
        if event['start'] < currentMax:
            localStart = event['start'] - offset
            localEnd = event['end'] - offset
            print(videos[i], "localStart", str(datetime.timedelta(seconds=localStart)), "localEnd",
                  str(datetime.timedelta(seconds=localEnd)))
            if autosave or input("Save to event video file? (y/N)") == "y":
                event2file(event, vfc, videos[i], localStart, localEnd)
            return
        offset += vfc.duration


def event2file(event, vfc, videoname, localstart, localend):
    vfcsub = vfc.subclip(localstart, localend)
    vfcsub.write_videofile(videoname + "_event_l" + str(round(localstart)) + "_g" + str(round(event['start'])) + ".mp4")
    vfcsub.reader.close()


def save_events(videos, gyrofile):
    events = get_events("video_gyro.csv")
    print(json.dumps(events, indent=4))
    vfcs = []
    for video in videos:
        vfcs.append(mp.VideoFileClip(video + ".MP4", fps_source="fps"))
    if len(events) < 50:
        for event in events:
            event2video(event, videos, vfcs, False)
    else:
        print("events > 50")


def add_events(mainvideo, eventvideos, speedup=10, outfilename="video_synced_events2.mp4"):
    def _tff(filename):
        return float(filename.split("g")[1].split(".")[0])

    def _resize(t):
        tMax = 1
        tNew = 0.5 + 0.5 * t / tMax
        if tNew > 1.0: return 1.0
        return tNew

    def _pos(t):
        tMax = 1
        posNew = 0.5 - 0.5 * t / tMax
        if posNew < 0.0: return 0.0
        return posNew

    eventclips = [mp.VideoFileClip(mainvideo, fps_source="fps")]
    for eventvideo in eventvideos:
        start = _tff(eventvideo) / speedup
        print("start", start)
        eventclip = mp.VideoFileClip(eventvideo, fps_source="fps").set_start(start) \
            .resize(lambda t: _resize(t)) \
            .set_position(lambda t: (_pos(t), _pos(t)), relative=True)
        eventclips.append(eventclip)
    mp.CompositeVideoClip(eventclips).set_fps(30).write_videofile(outfilename, threads=4)


if __name__ == "__main__":
    if False:
        save_events(['v1', 'v2', 'v3', 'v4'], "video_gyro.csv")
    if True:
        mainvideo = "video_synced.mp4"
        add_events(mainvideo, [
            "v1_event_l267_g267.mp4",
            "v1_event_l810_g810.mp4",
            "v2_event_l307_g1367.mp4",
            "v3_event_l258_g2379.mp4",
            "v3_event_l442_g2563.mp4",
            "v3_event_l515_g2636.mp4",
            "v4_event_l66_g3248.mp4"
        ])
