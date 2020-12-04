from vidstab import VidStab

videos = ["v1", "v2", "v3", "v4"]
for video in videos:
    stabilizer = VidStab()
    stabilizer.stabilize(input_path=video + ".MP4",
                         output_path=video + "_stab.MP4",
                         border_type='reflect')
