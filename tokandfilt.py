#!/usr/bin/env python3

import re
import json
import sys

MIN_COMET_DEFAULT = 0.85


def tok(st):
    return re.sub(r'([.,!?;:"\'])', r" ▁\1", st)


def parse(line, min_com):
    data = json.loads(line.strip())

    if data['COMET'] >= min_com:
        sr = tok(data['src_segm'])
        tg = tok(data['tgt_segm'])
        print(f"{sr} ||| {tg}")


def doit(fh, min_com):
    for l in fh:
        parse(l, min_com)


if __name__ == "__main__":
    try:
        min_comet = float(sys.argv[1])
    except:
        min_comet = MIN_COMET_DEFAULT

    doit(sys.stdin, min_comet)
