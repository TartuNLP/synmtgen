#!/usr/bin/env python3

import re
import json
import sys

MIN_COMET_DEFAULT = 0.85

def tok(st):
    return re.sub(r'([.,!?;:"\'])', r" ▁\1", st)


def parse(line, ofh, min_com):
    data = json.loads(line.strip())

    if data['COMET'] < min_com:
        return 0

    sr = tok(data['src_segm'])
    tg = tok(data['tgt_segm'])
    print(f"{sr} ||| {tg}", file=ofh)
    return 1


def output_filename(output_pref, file_idx):
    return f"{output_pref}.{file_idx:03}.ali"

def doit(fh, output_pref, min_com):
    if output_pref is None:
        ofh = sys.stdout
        file_idx = None
    else:
        file_idx = 0
        ofh = open(output_filename(output_pref, file_idx), 'w')
    line_count = 0

    for l in fh:
        line_count += parse(l, ofh, min_com)

        if not line_count % 10000:
            print(f"Currently at line nr {line_count}", file=sys.stderr)

        if line_count >= 1000000 and file_idx is not None:
            ofh.close()
            file_idx += 1
            ofh = open(output_filename(output_pref, file_idx), 'w')

    if file_idx is not None:
        ofh.close()


if __name__ == "__main__":
    try:
        min_comet = float(sys.argv[1])
    except:
        min_comet = MIN_COMET_DEFAULT

    try:
        output_file_preffix = sys.argv[2]
    except:
        output_file_preffix = None

    doit(sys.stdin, output_file_preffix, min_comet)
