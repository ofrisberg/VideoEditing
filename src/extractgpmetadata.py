import os
import sys
import pandas
import csv

def create_csv_files(videos, doMerge, doDeleteTmpFiles = True):
    """
    1. Extract bin file from every video file with ffmpeg
    2. Convert bin to 4 different CSV-files (if there was 2 videos, it will not be 8 csv files) using gpmd2csv
    3. Merge csv files, in total there will only be 4 csv files after this, independent of number video files
    :param videos:
    :param doMerge:
    """

    def merge_csv_files(files, newname):
        if os.path.exists(newname):
            print(newname + " exists. Skipping step.")
        else:
            combined_csv = pandas.concat([pandas.read_csv(f) for f in files])
            combined_csv.to_csv(newname, index=False, encoding='utf-8-sig')
            reader = csv.reader(open(newname))  # Here your csv file
            lines = list(reader)
            lastMs = float(lines[1][0])
            offset = 0.0
            for i in range(1,len(lines)):
                ms = float(lines[i][0]) + offset
                if ms < lastMs:
                    offset = lastMs
                    ms = float(lines[i][0]) + offset
                lines[i][0] = ms
                lastMs = ms
            writer = csv.writer(open(newname, 'w', newline=''))
            writer.writerows(lines)

        if doDeleteTmpFiles:
            for file in files: os.remove(file)

    for video in videos:
        if os.path.exists(video + ".MP4") is False:
            print(video + ".MP4 doesnt exists.")
            sys.exit()

    # Extract metadata in csv format
    for video in videos:
        if os.path.exists(video + ".bin") is False:
            os.system("ffmpeg -y -i " + video + ".MP4 -codec copy -map 0:3 -f rawvideo " + video + ".bin")
        else:
            print(video + ".bin already exists. Skipping step.")
        if os.path.exists(video + "-gps.csv") is False:
            os.system("gpmd2csv -i " + video + ".bin -o " + video + ".csv")
        else:
            print(video + "-gps.csv already exists. Skipping step.")

        # Delete .bin file, its not needed anymore
        if doDeleteTmpFiles: os.remove(video + ".bin")

    gpsFiles = []
    accFiles = []
    gyroFiles = []
    tempFiles = []
    for video in videos:
        gpsFiles.append(video + "-gps.csv")
        accFiles.append(video + "-accl.csv")
        gyroFiles.append(video + "-gyro.csv")
        tempFiles.append(video + "-temp.csv")

    if doMerge:
        merge_csv_files(gpsFiles, "video_gps.csv")
        merge_csv_files(accFiles, "video_acc.csv")
        merge_csv_files(gyroFiles, "video_gyro.csv")
        merge_csv_files(tempFiles, "video_temp.csv")

if __name__ == "__main__":
    videos = ['v1', 'v2', 'v3']  # .MP4 files
    create_csv_files(videos, True, False)
