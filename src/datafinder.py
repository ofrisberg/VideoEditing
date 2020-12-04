import csv
import numpy as np


class DataFinder:
    def __init__(self, interval=1000):
        self.interval = interval  # in ms
        self.acc = None
        self.gyro = None
        self.elev = None
        self.bpm = None
        self.dist = None
        self.gyro_vecs = None

    def _get_ms(self, row):
        if "ï»¿Milliseconds" in row:
            return float(row["ï»¿Milliseconds"])
        return float(row["Milliseconds"])

    def init_all(self):
        self.init_acc()
        self.init_bpm()
        self.init_dist()
        self.init_elev()
        self.init_gyro()
        self.init_gyro_vecs()

    def init_acc(self, csvfile="video_acc.csv"):
        print("Initializing acceleration", csvfile)
        self.acc = {}
        with open(csvfile, newline='\n') as fh:
            reader = csv.DictReader(fh)
            lastTime = -1000
            for row in reader:
                # print(row)
                ms = self._get_ms(row)
                if ms > lastTime + self.interval:
                    x = float(row['AcclX'])
                    y = float(row['AcclY'])
                    z = float(row['AcclZ'])
                    self.acc[ms] = np.linalg.norm(np.array([x, y, z]))
                    lastTime = ms

    def init_gyro(self, csvfile="video_gyro.csv"):
        print("Initializing gyro", csvfile)
        self.gyro = {}
        with open(csvfile, newline='\n') as fh:
            reader = csv.DictReader(fh)
            lastTime = -1000
            for row in reader:
                ms = self._get_ms(row)
                if ms > lastTime + self.interval:
                    x = float(row['GyroX'])
                    y = float(row['GyroY'])
                    z = float(row['GyroZ'])
                    self.gyro[ms] = np.linalg.norm(np.array([x, y, z]))
                    lastTime = ms

    def init_gyro_vecs(self, csvfile="video_gyro.csv"):
        print("Initializing gyro", csvfile, "(vec)")
        self.gyro_vecs = {}
        with open(csvfile, newline='\n') as fh:
            reader = csv.DictReader(fh)
            lastTime = -1000
            for row in reader:
                ms = self._get_ms(row)
                if ms > lastTime + self.interval:
                    x = float(row['GyroX'])
                    y = float(row['GyroY'])
                    z = float(row['GyroZ'])
                    self.gyro_vecs[ms] = [x, y, z]
                    lastTime = ms

    def init_elev(self, csvfile="video_garmin.csv"):
        print("Initializing elevation", csvfile)
        self.elev = {}
        with open(csvfile, newline='\n') as fh:
            reader = csv.DictReader(fh)
            lastTime = -1000
            for row in reader:
                ms = self._get_ms(row)
                if ms > lastTime + self.interval:
                    el = float(row['Altitude'])
                    self.elev[ms] = el
                    lastTime = ms

    def init_dist(self, csvfile="video_garmin.csv"):
        print("Initializing distances", csvfile)
        self.dist = {}
        with open(csvfile, newline='\n') as fh:
            reader = csv.DictReader(fh)
            lastTime = -1000
            lastLat = None
            lastLon = None
            d = 0.0
            for row in reader:
                ms = self._get_ms(row)
                if ms > lastTime + 10000:
                    lat = float(row['Latitude'])
                    lon = float(row['Longitude'])
                    if lastLat is not None and lastLon is not None:
                        d = d + self.haversine_distance(lat, lon, lastLat, lastLon)
                        self.dist[ms] = d
                    else:
                        self.dist[0.0] = 0.0
                    lastLat = lat
                    lastLon = lon
                    lastTime = ms

    def init_bpm(self, csvfile="video_garmin.csv"):
        print("Initializing heart rate", csvfile)
        self.bpm = {}
        with open(csvfile, newline='\n') as fh:
            reader = csv.DictReader(fh)
            lastTime = -1000
            for row in reader:
                ms = self._get_ms(row)
                if ms > lastTime + self.interval:
                    bpm = float(row['HeartRate'])
                    self.bpm[ms] = bpm
                    lastTime = ms

    def get_acc(self, ms):
        for key in self.acc:
            if key >= ms:
                # print("Found",key)
                return self.acc[key]
            else:
                pass
                # print(key,"<",ms)
        return 0.0  # if there is rounding errors at the end of the movie, we dont want the program to fail after several hours processing...

    def get_gyro(self, ms):
        for key in self.gyro:
            if key >= ms: return self.gyro[key]
        return 0.0

    def get_gyro_vec(self, ms):
        for key in self.gyro_vecs:
            if key >= ms: return self.gyro_vecs[key]
        return [0.0, 0.0, 0.0]

    def get_elev(self, ms):
        for key in self.elev:
            if key >= ms: return self.elev[key]
        return 0.0

    def get_bpm(self, ms):
        for key in self.bpm:
            if key >= ms: return self.bpm[key]
        return 0.0

    def get_dist(self, ms):
        for key in self.dist:
            if key >= ms: return self.dist[key]
        return 0.0

    def haversine_distance(self, lat1, lon1, lat2, lon2):
        r = 6371
        phi1 = np.radians(lat1)
        phi2 = np.radians(lat2)
        delta_phi = np.radians(lat2 - lat1)
        delta_lambda = np.radians(lon2 - lon1)
        a = np.sin(delta_phi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2) ** 2
        res = r * (2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a)))
        return np.round(res, 2)

    def check_ascending(self, dict):
        last_key = -1
        for key in dict:
            if key < last_key:
                print(key, "<", last_key)
                return
            last_key = key
        print("Success", last_key)


if __name__ == "__main__":
    df = DataFinder()
    # print(df.get_acc(5000))
    print("Check dist")
    df.check_ascending(df.dist)
