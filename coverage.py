import argparse

from typing import *

PROGRAM_DESCRIPTION = "Find coverage"

class GenomicRegion:
    def __init__(self, scaffold: str, start: int, end: int, *optional: List[any]):
        self.scaffold = scaffold
        self.start = start
        self.end = end
        self.optional_columns = optional

    def __str__(self):
        return str([self.scaffold, self.start, self.end, *self.optional_columns])

    def __repr__(self):
        return str(self)


class BEDReader:
    def __init__(self, file):
        self.file = file
        self.genomic_regions: List[GenomicRegion] = []

        lines = self.file.readlines()
        for line in lines:
            columns = line.split()
            genomic_region = GenomicRegion(columns[0], int(columns[1]), int(columns[2]), *columns[3:])
            self.genomic_regions.append(genomic_region)


def get_all_ntuples(sequence, start, end, window_length, padding):
    start_first_region = start - window_length if start - window_length >= 0 else 0
    end_first_region = start + window_length if start + window_length <= len(sequence) else len(sequence)

    start_second_region = end - window_length if end - window_length >= 0 else 0
    end_second_region = end + window_length if end + window_length <= len(sequence) else len(sequence)

    sequences = set()

    start_region = sequence[start_first_region - padding:end_first_region + padding]
    end_region = sequence[start_second_region - padding:end_second_region + padding]

    for i in range(0, len(start_region) - window_length + 1):
        sequences.add(start_region[i: i + window_length])
        sequences.add(end_region[i: i + window_length])

    return sequences


def modify_genomic_regions(genomic_regions, width):
    for genomic_region in genomic_regions:
        i = 0
        while ((genomic_region.end - (genomic_region.start + i)) % width) != 0:  # modify first index in R-loop
            if i >= 0:
                i += 1

                if (genomic_region.start - i) < 0:
                    continue

            i *= -1

        genomic_region.start += i


def main():
    parser = argparse.ArgumentParser(description=PROGRAM_DESCRIPTION)
    parser.add_argument('-b', '--bed_file', metavar='BED_FILE', type=str, help='bed file to read', required=True)
    parser.add_argument('-f', '--fasta_file', metavar='FASTA_FILE', type=str, help='fasta file to read', required=True)
    parser.add_argument('-w', '--width', metavar='WIDTH', type=int, help='n-tuple size', required=True)

    args = parser.parse_args()
    with open(args.bed_file, 'r') as bed_file:
        bed_reader = BEDReader(bed_file)

    modify_genomic_regions(bed_reader.genomic_regions, args.width)

    with open(args.fasta_file, 'r') as fasta_file:
        sequence = fasta_file.read()

    ntuples = set()

    for genomic_region in bed_reader.genomic_regions:
        ntuples |= get_all_ntuples(sequence, genomic_region.start, genomic_region.end, args.width, 20)

    print(len(ntuples))
    print(len(ntuples) / (4 ** args.width))


if __name__ == "__main__":
    main()