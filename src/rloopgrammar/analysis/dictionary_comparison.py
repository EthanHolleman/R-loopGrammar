import json
import argparse
import pathlib
import collections
import pprint

class DictionaryEntry:
    def __init__(self, symbol: str, number: int):
        self.symbol = symbol
        self.number = number

    def __eq__(self, other):
        return self.symbol == other.symbol
    
    def __hash__(self):
        return hash(self.symbol)

    def __repr__(self):
        return f"({self.number}, {self.symbol})"


parser = argparse.ArgumentParser(
                    prog = 'dictionary_comparison',
                    description = 'Compares two or more dictionaries.')

parser.add_argument('dictionary_paths', metavar='D', type=str, nargs='+', help='a dictionary to compare')

pp = pprint.PrettyPrinter(indent=4)

def main():
    args = parser.parse_args()
    paths = list(map(pathlib.Path, args.dictionary_paths))
    if any((not p.exists() for p in paths)):
        print("Path provided does not exist.")
        return
    
    diff_dictionary = dict(
        region1=collections.defaultdict(lambda : set()),
        region2_3=collections.defaultdict(lambda : set()),
        region4=collections.defaultdict(lambda : set())
    )

    for n, p in enumerate(paths):
        print(n, p)
        with open(p) as f:
            d = json.load(f)
            for k in diff_dictionary.keys():
                print(f"{k}: {len(diff_dictionary[k])}")
                for i, j in d[k].items():
                    for v in j:
                        diff_dictionary[k][v].add(DictionaryEntry(i, n))

    diff_dictionary_differences = dict(
        region1=collections.defaultdict(lambda : []),
        region2_3=collections.defaultdict(lambda : []),
        region4=collections.defaultdict(lambda : [])
    )

    for k, v in diff_dictionary.items():
        for i, j in v.items():
            if len(j) > 1:
                diff_dictionary_differences[k][i].extend(sorted(j, key=lambda x:x.number))

    pp.pprint(diff_dictionary_differences)
        

if __name__ == "__main__":
    main()

