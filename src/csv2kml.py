import os
import sys
import csv
from datetime import timezone
from datetime import datetime
import simplekml

"""
Create a google earth track from gopro gps file and a zoomin-effect for intro
"""


def _create_track(res, parent, iconTitle):
    trk = parent.newgxtrack(name=iconTitle)
    trk.lookat.gxtimespan.begin = res[0][3]
    trk.lookat.gxtimespan.end = res[len(res) - 1][3]

    when = []
    gxcoord = []
    for arr in res:
        when.append(arr[3])
        gxcoord.append((arr[0], arr[1], 0))  # height over ground, dont use arr[2]

    trk.newwhen(when)
    trk.newgxcoord(gxcoord)
    trk.stylemap.normalstyle.iconstyle.icon.href = 'https://earth.google.com/images/kml-icons/track-directional/track-0.png'
    trk.stylemap.normalstyle.linestyle.color = '99ffac59'
    trk.stylemap.normalstyle.linestyle.width = 6
    trk.stylemap.highlightstyle.iconstyle.icon.href = 'https://earth.google.com/images/kml-icons/track-directional/track-0.png'
    trk.stylemap.highlightstyle.iconstyle.scale = 1.2
    trk.stylemap.highlightstyle.linestyle.color = '99ffac59'
    trk.stylemap.highlightstyle.linestyle.width = 8


def read_csv(csvfile):
    """
    :param csvfile: gopro gps file
    :return: multidim array with [lon, lat, alt, dt]
    """
    res = []
    lastTs = -1
    with open(csvfile, newline='\n') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            # Latitude,Longitude,Altitude
            lat = row['Latitude']
            lon = row['Longitude']
            alt = row['Altitude']
            ts = int(int(row['TS']) / 1000000)
            utc_time = datetime.fromtimestamp(ts, timezone.utc)
            local_time = utc_time.astimezone()
            dt = local_time.strftime('%Y-%m-%d %H:%M:%S')
            dt = dt.replace(' ', 'T') + 'Z'
            if lastTs == -1 or ts - lastTs > 1:
                res.append([lon, lat, alt, dt])
                lastTs = ts
    return res


def csv2kml(csvfile, kmlfile):
    """
    :param csvfile: csv file to read
    :param kmlfile: new kml file name to be created
    """
    res = read_csv(csvfile)
    kml = simplekml.Kml(name=csvfile)
    _create_track(res, kml, "")
    kml.save(kmlfile)


def create_zoom(csvfile, kmlfile, tilt=0, range=10000):
    res = read_csv(csvfile)
    kml = simplekml.Kml(name=csvfile)
    pnt = kml.newpoint(name=kmlfile)
    pnt.lookat = simplekml.LookAt(gxaltitudemode=simplekml.GxAltitudeMode.relativetoseafloor,
                                  latitude=res[0][1], longitude=res[0][0],
                                  range=range, heading=0.0027, tilt=tilt)
    kml.save(kmlfile)


if __name__ == "__main__":
    pass
    # create_zoom("video_gps.csv", "video_intro.kml", 60)
    # csv2kml("video_gps.csv", "video_coords.kml")
