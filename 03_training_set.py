#!/usr/bin/env python3
import argparse
import random

"""
Script to select a training set from a BED file.


Copyright 2020 Margherita Maria Ferrari.


This file is part of TrainingSet.

TrainingSet is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

TrainingSet is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with TrainingSet.  If not, see <http://www.gnu.org/licenses/>.
"""

# FIX SEED
#random.seed(0)

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
