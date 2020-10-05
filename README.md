# Video editing for GoPro

## Summary
These scripts can 
- Extract metadata (e.g. gps, gyro, acc...) from multiple videos
- Merge videos and fastforward the result with arbitrary speedup/slowdown-factor
- Convert metadata to Google Earth files (kml) that can be played and recorded
- Composite plots from data, Google Earth tour and GoPro-videos into one video

## Dependencies
- ffmpeg.exe
- gpmd2csv.exe
- some python packages like moviepy, matplotlib, numpy...

## Todo
- Remove faulty GPS-locations, how?
- Remove slow dynamic text clip
- Add hooks, e.g. clap hands for playing 30 seconds realtime and not fast forward
- Add music from youtube-url
- Add main file with argparse
- Reduce metadata for long videos, average all data in one sec interval? 