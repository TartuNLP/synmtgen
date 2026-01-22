import sys
import json
import re
import random

from collections import defaultdict

from rapidfuzz.distance import Levenshtein
from datetime import datetime

from applysimt import detok
from showali import parse_ali_txt_line


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


def do_lev_sims_snt(pair_list, i, src, tgt, lev, match_idx_list, max_per_snt, cutoff_score):
    nr_of_attempts = 0
    yield_len = 0

    matches = set()

    while nr_of_attempts < len(match_idx_list) and yield_len < max_per_snt:
        j = match_idx_list[nr_of_attempts]
        nr_of_attempts += 1

        srcx, tgtx, _ = pair_list[j]

        if src != srcx and tgt != tgtx:
            sSrc = simp(src)
            sSrcx = simp(srcx)

            if str(sSrcx) not in matches and sSrc != sSrcx:
                sTgt = simp(tgt)
                sTgtx = simp(tgtx)

                if str(sTgtx) not in matches and sTgt != sTgtx:
                    score = lev.dist(src, srcx)

                    if score >= cutoff_score:
                        s2 = lev.dist(tgt, tgtx)

                        if s2 >= cutoff_score:
                            matches.add(str(sTgtx))
                            matches.add(str(sSrcx))

                            yield_len += 1
                            # print(f"{datetime.now()} DEBUG {i}-{j}: {src} / {srcx} --> {score} ({tgt} / {tgtx} / {s2})")
                            print({'i1': i, 'i2': j, 'src1': src, 'tgt1': tgt, 'src2': srcx, 'tgt2': tgtx,
                                   'src_score': score, 'tgt_score': s2})


def do_lev_sims(pair_list, cutoff_score=0.6, min_src_len=6, max_attempts=10000, max_per_snt=5):
    lev = CacheLev(cutoff=cutoff_score)

    for i, (src, tgt, srclen) in enumerate(pair_list):
        if not i % 1000:
            print(f"{datetime.now()}: {i}")

        if srclen >= min_src_len:

            match_idx_list = list(range(i + 1, len(pair_list)))
            random.shuffle(match_idx_list)
            match_idx_list = match_idx_list[:max_attempts]

            do_lev_sims_snt(pair_list, i, src, tgt, lev, match_idx_list, max_per_snt, cutoff_score)

def doit(txtfile):
    list_of_pairs = parse_ali_txt_file(txtfile)

    t1 = datetime.now()

    sims = do_lev_sims(list_of_pairs)

    t2 = datetime.now()

    print(t2 - t1)

    che = defaultdict(int)
    for i in sims:
        che[len(sims[i])] += 1

    print(che)


if __name__ == '__main__':
    #doit(sys.argv[1])

    doit("ali/et-ru.tmp")

    #s = "- «On kõik korras? »"
    #o = simp(s)
    #print(f"'{s}' --> '{o}'")
