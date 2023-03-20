import collections
import json

files = ["pfc53_supercoiledcr.bed", "pfc8_supercoiledcr.bed"]

def read_all_rloops(bed_file):
    return [tuple(map(int, t.split()[1:3])) for t in bed_file.readlines()]

rloop_counts = collections.defaultdict(lambda: 0)

for file in files:
	with open(file, 'r') as f:
		rloops = read_all_rloops(f)
		for rloop in rloops:
			rloop_counts[rloop] += 1

reversed_order = {
    k : v for k, v in sorted(rloop_counts.items(), key=lambda x: x[1], reverse=True)
}

print(list(reversed_order.items())[:5])