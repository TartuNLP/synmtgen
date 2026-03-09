#!/usr/bin/python3

import sys
import json
import re
import random

from collections import defaultdict

from rapidfuzz.distance import Levenshtein
from datetime import datetime


def detok(toks, until_inclusive=-1):
    if until_inclusive == -1:
        sub_toks = toks
    else:
        sub_toks = toks[:until_inclusive] + [toks[until_inclusive]]

    return " ".join(sub_toks).replace(" ▁", "")


def parse_ali_txt_line(line):
    src, tgt = line.strip().split(' ||| ')

    src_tok = src.split(' ')
    tgt_tok = tgt.split(' ')

    return src, tgt, src_tok, tgt_tok


def parse_ali_txt_file(txtfile):
    with open(txtfile, 'r') as fh:
        result = []

        for txt_raw_line in fh:
            _, _, src_toks, tgt_toks = parse_ali_txt_line(txt_raw_line)

            #src = detok(src_toks)
            #tgt = detok(tgt_toks)

            #result.append((src, tgt, len(src_toks)))

            result.append((src_toks, tgt_toks, len(src_toks)))

        return result


def simp(str):
    return str

    #res1 = re.sub(r'[^a-zäöüšžõа-я ]', '', str.lower())
    #res2 = re.sub(r' {2,}', ' ', res1)
    #res3 = re.sub(r'(^ | $)', '', res2)
    #return res3


class CacheLev:
    """
    This class implements computing the Levenshtein distance between two strings,
    but with caching of the results, to avoid re-computing it.
    """

    def __init__(self, cutoff=0.0):
        self.cache = defaultdict(lambda: defaultdict(float))
        self.cutoff = cutoff

    def dist(self, s1, s2):
        sts1 = str(s1)
        sts2 = str(s2)

        if sts2 in self.cache[sts1]:
            result = self.cache[sts1][sts2]
        else:
            result = Levenshtein.normalized_similarity(s1, s2, score_cutoff=self.cutoff)
            self.cache[sts1][sts2] = result
        return result


def do_lev_sims_snt(pair_list, i, src, tgt, lev_func, match_idx_list, max_per_snt, cutoff_score):
    """
    Find pairs of sentences, similar to pair_list[i],
    by looking through the list of indexes in match_idx_list,
    yielding a maximum of max_per_snt matches.
    """
    nr_of_attempts = 0
    yield_len = 0

    #to avoid duplicate matches, store the already found matches
    matches = set()

    while nr_of_attempts < len(match_idx_list) and yield_len < max_per_snt:
        j = match_idx_list[nr_of_attempts]
        nr_of_attempts += 1

        srcx, tgtx, _ = pair_list[j]

        # has to be a different sentence
        if src != srcx and tgt != tgtx:
            sSrc = simp(src)
            sSrcx = simp(srcx)

            # source has to be different from already found matches
            if str(sSrcx) not in matches and sSrc != sSrcx:
                sTgt = simp(tgt)
                sTgtx = simp(tgtx)

                # target has to be different from already found matches
                if str(sTgtx) not in matches and sTgt != sTgtx:
                    score = lev_func.dist(src, srcx)

                    # cutoff_score speeds up Levenshtein computation --
                    # if it turns out that score will be lower that cutoff,
                    # the Levenshtein computation stops
                    if score >= cutoff_score:
                        s2 = lev_func.dist(tgt, tgtx)

                        # same cutoff optimization for target
                        if s2 >= cutoff_score:
                            matches.add(str(sTgtx))
                            matches.add(str(sSrcx))

                            yield_len += 1

                            print(f"Match! {i}, {j}", file=sys.stderr)
                            yield j, score, s2


def do_lev_sims(pair_list, cutoff_score=0.6, min_src_len=6, max_attempts=10000, max_per_snt=5):
    lev = CacheLev(cutoff=cutoff_score)

    for i, (src, tgt, srclen) in enumerate(pair_list):
        if not i % 100:
            print(f"{datetime.now()}: {i}", file=sys.stderr)

        res = list()

        if srclen >= min_src_len:
            match_idx_list = list(range(i + 1, len(pair_list)))
            random.shuffle(match_idx_list)
            match_idx_list = match_idx_list[:max_attempts]

            for match_idx, src_score, tgt_score in do_lev_sims_snt(pair_list, i, src, tgt,
                                                                   lev, match_idx_list,
                                                                   max_per_snt, cutoff_score):
                res.append((match_idx, src_score, tgt_score))

        if len(res) > 0:
            yield i, res




def doit(txtfile):
    # this returns a list of tuples like (source_tokens, target_tokens, length_of_src_toks)
    list_of_pairs = parse_ali_txt_file(txtfile)

    print(f"Parsing done, processing (takes time)", file=sys.stderr)

    t1 = datetime.now()

    # this
    for i, matches in do_lev_sims(list_of_pairs):
        data = { 'idx': i, 'matches': matches }
        print(json.dumps(data))

    t2 = datetime.now()

    print(f"It took {str(t2 - t1)} to process the file", file=sys.stderr)


if __name__ == '__main__':
    doit(sys.argv[1])
    #doit("ali/et-ru.tmp")
