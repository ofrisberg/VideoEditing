import csv
import numpy as np


class DataFinder:
    def __init__(self, interval=1000, init_default=True):
        self.interval = interval  # in ms
        if init_default:
            self.acc = self.init_acc()
            self.gyro = self.init_gyro()
            self.elev = self.init_elev()
            self.dist = self.init_dist()
        self.gyro_vecs = None

    def init_acc(self):
        print("Initializing acc")
        res = {}
        with open("video_acc.csv", newline='\n') as fh:
            reader = csv.DictReader(fh)
            lastTime = -1000
            for row in reader:
                # print(row)
                ms = float(row['ï»¿Milliseconds'])
                if ms > lastTime + self.interval:
                    x = float(row['AcclX'])
                    y = float(row['AcclY'])
                    z = float(row['AcclZ'])
                    res[ms] = np.linalg.norm(np.array([x, y, z]))
                    lastTime = ms
        return res

    def init_gyro(self):
        print("Initializing gyro")
        res = {}
        with open("video_gyro.csv", newline='\n') as fh:
            reader = csv.DictReader(fh)
            lastTime = -1000
            for row in reader:
                ms = float(row['ï»¿Milliseconds'])
                if ms > lastTime + self.interval:
                    x = float(row['GyroX'])
                    y = float(row['GyroY'])
                    z = float(row['GyroZ'])
                    res[ms] = np.linalg.norm(np.array([x, y, z]))
                    lastTime = ms
        return res

    def init_gyro_vecs(self):
        print("Initializing gyro (vec)")
        self.gyro_vecs = {}
        with open("video_gyro.csv", newline='\n') as fh:
            reader = csv.DictReader(fh)
            lastTime = -1000
            for row in reader:
                ms = float(row['ï»¿Milliseconds'])
                if ms > lastTime + self.interval:
                    x = float(row['GyroX'])
                    y = float(row['GyroY'])
                    z = float(row['GyroZ'])
                    self.gyro_vecs[ms] = [x, y, z]
                    lastTime = ms

    def init_elev(self):
        print("Initializing elevation")
        res = {}
        with open("video_gps.csv", newline='\n') as fh:
            reader = csv.DictReader(fh)
            lastTime = -1000
            for row in reader:
                ms = float(row['ï»¿Milliseconds'])
                if ms > lastTime + self.interval:
                    el = float(row['Altitude'])
                    res[ms] = el
                    lastTime = ms
        return res

    def init_dist(self):
        print("Initializing distances")
        res = {}
        with open("video_gps.csv", newline='\n') as fh:
            reader = csv.DictReader(fh)
            lastTime = -1000
            lastLat = None
            lastLon = None
            d = 0.0
            for row in reader:
                ms = float(row['ï»¿Milliseconds'])
                if ms > lastTime + 10000:
                    lat = float(row['Latitude'])
                    lon = float(row['Longitude'])
                    if lastLat is not None and lastLon is not None:
                        d = d + self.haversine_distance(lat, lon, lastLat, lastLon)
                        res[ms] = d
                    else:
                        res[0.0] = 0.0
                    lastLat = lat
                    lastLon = lon
                    lastTime = ms
        return res

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
        return None

    def get_elev(self, ms):
        for key in self.elev:
            if key >= ms: return self.elev[key]
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
                print(key,"<",last_key)
                return
            last_key = key
        print("Success",last_key)

if __name__ == "__main__":
    df = DataFinder()
    #print(df.get_acc(5000))
    print("Check dist")
    df.check_ascending(df.dist)
