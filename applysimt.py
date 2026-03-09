#!/usr/bin/python3

import sys

from collections import defaultdict
from showali import parse_ali_txt_line


def read_ali_samples(alifile):
    with open(alifile) as fh:
        result = defaultdict(set)

        for raw_line in fh:
            snt_idx, ali_i, ali_j = [int(a) for a in raw_line.strip().split(' ')]
            result[snt_idx].add((ali_i, ali_j))

        return result


def detok(toks, until_inclusive=-1):
    if until_inclusive == -1:
        sub_toks = toks
    else:
        sub_toks = toks[:until_inclusive] + [toks[until_inclusive]]

    return " ".join(sub_toks).replace(" ▁", "")


def doit(txtfile, alifile):
    txt_fh = open(txtfile, 'r')

    ali_samples = read_ali_samples(alifile)

    for i, txt_raw_line in enumerate(txt_fh):
        if i in ali_samples:
            src, tgt, src_toks, tgt_toks = parse_ali_txt_line(txt_raw_line)

            src_len = len(src_toks)
            tgt_len = len(tgt_toks)

            ali_set = ali_samples[i] | { (src_len-1, tgt_len-1) }

            for sample_i, sample_j in sorted(ali_set, key=lambda x: x[0]):
                src_piece = detok(src_toks, until_inclusive=sample_i)
                tgt_piece = detok(tgt_toks, until_inclusive=sample_j)

                delim = "|||" if (sample_i == src_len - 1 and sample_j == tgt_len - 1) else "///"

                print(f"{src_piece} {delim} {tgt_piece}")


if __name__ == "__main__":
    doit(sys.argv[1], sys.argv[2])
