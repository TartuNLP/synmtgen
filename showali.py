#!/usr/bin/python3

import sys

def parse_ali_txt_line(line):
	src, tgt = line.strip().split(' ||| ')

	src_tok = src.split(' ')
	tgt_tok = tgt.split(' ')

	return src, tgt, src_tok, tgt_tok


def doit(txtfile, alifile):
	txt_fh = open(txtfile, 'r')
	ali_fh = open(alifile, 'r')
	
	for txt_raw_line in txt_fh:
		src, tgt, src_tok, tgt_tok = parse_ali_txt_line(txt_raw_line)

		ali_raw_line = ali_fh.readline()
		ali_line = ali_raw_line.strip()

		ali_list = ali_line.split(' ') if ali_line else []
		
		word_pairs = []
		for raw_ali_p in ali_list:
			src_i, tgt_i = raw_ali_p.split('-')
			src_ii = int(src_i)
			tgt_ii = int(tgt_i)
			word_pairs.append(f"{src_tok[src_ii]}->{tgt_tok[tgt_ii]}")
		
		print(f"{src} /// {tgt} /// {', '.join(word_pairs)}")
		print("")

if __name__ == "__main__":
	doit(sys.argv[1], sys.argv[2])
