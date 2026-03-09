#!/usr/bin/python3

import random
import sys
from operator import itemgetter


def parse_ali_pt(raw_pt):
    from_raw, to_raw = raw_pt.split('-')
    return int(from_raw), int(to_raw)


def parse_ali(ali_raw_line):
    ali_line = ali_raw_line.strip()
    raw_pts = ali_line.split(' ') if ali_line else []
    pts = [parse_ali_pt(raw_pt) for raw_pt in raw_pts]
    return pts


def measure_monotonicity(ali):
    result = []

    sorted_ali = [pt[1] for pt in sorted(ali, key=itemgetter(0))]

    for i in range(len(sorted_ali)):
        pt = sorted_ali[i]

        if i > 0 and pt < sorted_ali[i-1]:
            penalty = 0
            j = i

            while j > 0 and pt < sorted_ali[j-1]:
                penalty += 1
                sorted_ali[j], sorted_ali[j-1] = sorted_ali[j-1], sorted_ali[j]
                j -= 1

            result.append(penalty)

    return result


def do_sampling(ali_pts, nr=5, mul_factor=2):
    if len(ali_pts) < mul_factor:
        return []

    nr_to_sample = min(int(len(ali_pts) / mul_factor), nr)
    assert nr_to_sample < len(ali_pts)

    result_idxs = set()

    while len(result_idxs) < nr_to_sample:
        result_idxs.add(random.randint(0, len(ali_pts) - 1))

    return [ali_pts[i] for i in result_idxs]


def doit(alifile):
    ali_fh = open(alifile, 'r')

    for i, ali_raw_line in enumerate(ali_fh):
        #try:

        ali_pts = parse_ali(ali_raw_line)

        non_monos = measure_monotonicity(ali_pts)

        if not non_monos:
            samples = do_sampling(ali_pts)

            if samples:
                for sample in samples:
                    print(i, *sample)


        #except Exception as e:
        #    print(f"Exception on line nr {i}, with row `{ali_raw_line.strip()}'")
        #    raise e

if __name__ == "__main__":
    doit(sys.argv[1])
