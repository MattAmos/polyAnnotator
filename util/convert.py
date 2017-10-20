#! /usr/bin/env python

import os
import textwrap
import json
from progressbar import ProgressBar
pbar = ProgressBar()

files = sorted([f for f in os.listdir('/home/bidski/ownCloud/HORUS/4TEL_Videos/VIDEOS NOV 16/GoPro/') if f.endswith('.MP4')])

videos = None

for file in pbar(files):
    video = os.path.splitext(os.path.basename(file))[0]
    video_path = '"/home/bidski/ownCloud/HORUS/4TEL_Videos/VIDEOS NOV 16/GoPro/{0}.MP4"'.format(video)

    with open('./json/{0}.json'.format(video), 'w') as output:
        output.write('[\n')
        output.write('    "{0}",\n'.format(video))
        output.write('    [\n')
        output.write('        true,\n')
        output.write('        [\n')

        annotation_files = sorted([f for f in os.listdir('./output') if f.endswith('.txt') and f.startswith(video)])

        for annotation_file in annotation_files:
            with open('./output/{0}'.format(annotation_file)) as f:
                frame_number = int(os.path.splitext(annotation_file)[0].split('_')[1])
                output.write('            [\n')
                output.write('                {0},\n'.format(frame_number))
                output.write('                [\n')

                lines = f.readlines()
                for line in lines:
                    left, top, right, bottom = line.strip().split(' ')[4:8]

                    output.write('                    [\n')
                    output.write('                        "R",\n')
                    output.write('                        [\n')
                    output.write('                            {0}, {1}, {2}, {3}\n'.format(left, top, right, bottom))
                    output.write('                        ]\n')
                    output.write('                    ]')

                    if lines.index(line) != len(lines) - 1:
                        output.write(',\n')
                    else:
                        output.write('\n')

            output.write('                ]\n')
            output.write('            ]')

            if annotation_files.index(annotation_file) != len(annotation_files) - 1:
                output.write(',\n')
            else:
                output.write('\n')

        output.write('        ]\n')
        output.write('    ]\n')
        output.write(']\n')
