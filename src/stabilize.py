import vidstab
from vidstab import VidStab, layer_overlay

stabilizer = VidStab()

stabilizer.stabilize(input_path='v2sub.mp4',
                     output_path='v2substab.mp4',
                     border_type='black')
