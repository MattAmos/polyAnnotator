#! /usr/bin/env python

import os
files = [f for f in os.listdir('./output') if f.endswith('.txt') and f.startswith('GOPR0396')]

for file in files:
    video = os.path.splitext(file)[0].split('_')[0]
    video = '"/home/bidski/ownCloud/HORUS/4TEL_Videos/VIDEOS NOV 16/GoPro/{0}.MP4"'.format(video)

    with open('./json/{0}'.format(file.replace('.txt', '.json')), 'w') as out:
        data = '[\n\t[{0}, {1},\n\t\t['.format(video, int(file.replace('.txt', '').split('_')[1]))
        with open('./output/{0}'.format(file)) as f:
            for line in f:
                left, top, right, bottom = line.strip().split(' ')[4:8]
                data = '{0}\n\t\t\t[[{1}, {2}], [{3}, {4}], [{5}, {6}], [{7}, {8}]],'.format(data,
                    left, top, right, top, right, bottom, left, bottom)
        out.write('{0}\n\t\t]\n\t]\n]'.format(data[:-1]))
