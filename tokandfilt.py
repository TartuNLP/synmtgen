#!/usr/bin/env python3

import re
import json
import sys

MIN_COMET_DEFAULT = 0.85
SHARD_SIZE_DEFAULT = 1<<20


def tok(st):
    return re.sub(r'([.,!?;:"\'])', r" ▁\1", st)


def parse(line, min_com):
    data = json.loads(line.strip())

    if data['COMET'] < min_com:
        return None

    sr = tok(data['src_segm'])
    tg = tok(data['tgt_segm'])

    return f"{sr} ||| {tg}"


def get_ofh(output_pref, file_idx):
    output_file = f"{output_pref}.{file_idx:03}.ali"
    ofh = open(output_file, 'w')
    print(f"Writing to {output_file}", file=sys.stderr)
    return ofh


def parse_into_shards(fh, min_com, shard_size):
    shard = list()

    for l in fh:
        line = parse(l, min_com)

        if line is not None:
            shard.append(line)

        if len(shard) >= shard_size:
            yield shard
            shard = list()

    if len(shard) > 0:
        yield shard


def dump_shard_to_file(shard, fh):
    for l in shard:
        print(l, file=fh)


def doit(output_file_preffix, shard_size, min_comet):
    output_file_idx = 0
    ofh = None

    for shard in parse_into_shards(sys.stdin, min_comet, shard_size):
        if len(shard) > shard_size / 2 or ofh is None:
            output_file_idx += 1
            if ofh is not None:
                ofh.close()
            ofh = get_ofh(output_file_preffix, output_file_idx)

        dump_shard_to_file(shard, ofh)
    ofh.close()


if __name__ == "__main__":
    output_file_preffix = sys.argv[1]

    try:
        shard_size = int(sys.argv[2])
    except:
        shard_size = SHARD_SIZE_DEFAULT

    try:
        min_comet = float(sys.argv[3])
    except:
        min_comet = MIN_COMET_DEFAULT

    doit(output_file_preffix, shard_size, min_comet)

