import hashlib
import re
import sys
import time

import bencodepy

import config
from manager import Manager
from tracker import Tracker


def torrent(path):
    regex = re.compile('.+.torrent$')
    if not regex.match(path):
        print('Not a .torrent file')
        sys.exit()
    with open(path, 'rb') as stream:
        data = bencodepy.bdecode(bytes(stream.read()))

        print(data)
        print(data['comment'])
        print('\033[1m{}\033[0m'.format(data['info']['name']))

        return data['announce'], data['info'], hashlib.sha1(bencode.bencode(data['info'])).digest()


if __name__ == '__main__':
    config.START_TIME = time.time()

    url, info, info_hash = torrent(sys.argv[1])

    config.tracker = Tracker(info_hash, url)
    config.tracker.start()

    config.manager = Manager(info)
    config.manager.start()