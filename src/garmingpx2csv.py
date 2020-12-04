import os, sys, csv
import gpxpy
import time
import datetime


def _get_heart_rate(pointEl):
    heartRate = 0.0
    try:
        heartRate = float(pointEl.extensions[0].getchildren()[0].text)
    except:
        pass  # no heart rate... lol
    return heartRate


def _interpolate(t, i_before, i_after, gp_millis, gp_gps_ts):
    dy = gp_millis[i_after] - gp_millis[i_before]
    dx = gp_gps_ts[i_after] - gp_gps_ts[i_before]
    k = dy / dx
    # m = y - kx
    m = gp_millis[i_after] - k * gp_gps_ts[i_after]
    return k * t + m


def _get_time(pointEl, gp_millis, gp_gps_ts):
    t = pointEl.time.strftime("%Y-%m-%d %H:%M:%S")
    t = time.mktime(datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S").timetuple())
    t += 3600 * 2
    t *= 1000000
    ms = 0.0
    if len(gp_millis) == 0 or len(gp_millis) != len(gp_gps_ts):
        return (ms, t)
    length = len(gp_millis)
    for i in range(length):
        if i == 0 and t < gp_gps_ts[0]:
            # extrapolate before
            return (_interpolate(t, 0, 1, gp_millis, gp_gps_ts), t)
        if i == length - 1:
            # extrapolate after
            return (_interpolate(t, length - 2, length - 1, gp_millis, gp_gps_ts), t)
        if t > gp_gps_ts[i] and t < gp_gps_ts[i + 1]:
            return (_interpolate(t, i, i + 1, gp_millis, gp_gps_ts), t)
    print("Unreachable statement........")


def garmin_gpx_to_csv(gpxfile, newfile="video_garmin.csv", gopro_csv_path=None):
    file = open(gpxfile, 'r')
    coordTimes = []
    gpx = gpxpy.parse(file)

    gp_gps_time_vec = []
    gp_millis_vec = []
    if gopro_csv_path is not None:
        with open(gopro_csv_path, newline='\n') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                gp_millis_vec.append(float(row["ï»¿Milliseconds"]))
                gp_gps_time_vec.append(float(row['TS']))

    with open(newfile, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["Milliseconds", "Latitude", "Longitude", "Altitude", "HeartRate", "TS"])
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    lat = str(point.latitude)
                    lon = str(point.longitude)
                    alt = point.elevation
                    heartrate = _get_heart_rate(point)
                    (ms, time) = _get_time(point, gp_millis_vec, gp_gps_time_vec)
                    writer.writerow([ms, lat, lon, alt, heartrate, time])


if __name__ == "__main__":
    gpxfile = "../data/Running_20201013/activity_5672302775.gpx"
    newfilename = "video_garmin.csv"
    garmin_gpx_to_csv(gpxfile, newfilename, gopro_csv_path="video_gps.csv")
