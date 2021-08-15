#!/usr/bin/env python3
import argparse

"""
Script to convert R-loop coordinates in a BED file.


Copyright 2020 Margherita Maria Ferrari.


This file is part of ConvertCoord

ConvertCoord is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ConvertCoord is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ConvertCoord.  If not, see <http://www.gnu.org/licenses/>.
"""


class ConvertCoord:
    @classmethod
    def get_args(cls):
        parser = argparse.ArgumentParser(description='Convert coord')
        parser.add_argument('-b', '--input-bed', metavar='BED_IN_FILE', type=str, required=True,
                            help='BED input file', default=None)
        parser.add_argument('-l', '--length-plasmid', metavar='LENGTH_PLASMID', type=int, required=True,
                            help='Length of the plasmid', default=0)
        parser.add_argument('-o', '--output-file', metavar='OUTPUT_FILE', type=str, required=False,
                            help='Output BED file', default='new_coordinates.bed')
        return parser.parse_args()

    @classmethod
    def convert_coord(cls, bed_in, length, out_file='new_coordinates.bed'):
        with open(bed_in, 'r') as fin, open(out_file, 'w') as fout:
            line = fin.readline()

            while line:
                parts = line.strip().split('\t')
                # idx_1 is beginning, idx_2 is end
                idx_1 = int(parts[1])
                idx_2 = int(parts[2])

                # new beginning and end
                new_idx_1 = length - idx_1
                new_idx_2 = length - idx_2

                # Write new end as first coordinate in BED file
                parts[1] = str(new_idx_2)
                parts[2] = str(new_idx_1)

                fout.write('\t'.join(parts) + '\n')

                line = fin.readline()


if __name__ == '__main__':
    args = vars(ConvertCoord.get_args())
    ConvertCoord.convert_coord(args.get('input_bed', None), args.get('length_plasmid', 0),
                               args.get('output_file', 'new_coordinates.bed'))
