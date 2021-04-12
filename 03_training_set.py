#!/usr/bin/env python3
import argparse
import random


class TrainingSet:
    @classmethod
    def get_args(cls):
        parser = argparse.ArgumentParser(description='Training set')
        parser.add_argument('-i', '--input-bed', metavar='BED_IN_FILE', type=str, required=True,
                            help='BED input file', default=None)
        parser.add_argument('-n', '--num-lines', metavar='NUM_LINES', type=int, required=False,
                            help='Create training set with NUM_LINES lines', default=10)
        parser.add_argument('-o', '--output-file', metavar='OUTPUT_FILE', type=str, required=False,
                            help='Output BED file', default='training_set.bed')
        return parser.parse_args()

    @classmethod
    def training_set(cls, bed_in, num=10, out_file='training_set.bed'):
        with open(bed_in, 'r') as fin:
            lines = fin.readlines()

        with open(out_file, 'w') as fout:
            fout.writelines([i for i in random.sample(lines, num if num <= len(lines) else len(lines))])


if __name__ == '__main__':
    args = vars(TrainingSet.get_args())
    TrainingSet.training_set(args.get('input_bed', None), args.get('num_lines', 10),
                             args.get('output_file', 'training_set.bed'))
