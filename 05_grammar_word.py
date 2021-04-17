#!/usr/bin/env python3
import argparse
import json

"""
Script to generated words for R-loops in a BED file using a dictionary.


Copyright 2020 Margherita Maria Ferrari.


This file is part of GrammarSymbols.

GrammarSymbols is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

GrammarSymbols is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with GrammarSymbols.  If not, see <http://www.gnu.org/licenses/>.
"""


class GrammarWord:
    __alpha = '\u03B1'
    __beta = '\u03B2'
    __gamma = '\u03B3'
    __delta = '\u03B4'
    __rho = '\u03C1'
    __rho_hat = __rho + '^'
    __sigma = '\u03C3'
    __sigma_hat = __sigma + '^'
    __tau = '\u03C4'
    __tau_hat = __tau + '^'
    __omega = '\u03C9'

    GREEK_TO_ASCII = {
        __alpha: 'ALPHA',
        __beta: 'BETA',
        __gamma: 'GAMMA',
        __delta: 'DELTA',
        __rho: 'RHO',
        __rho_hat: 'RHO^',
        __sigma: 'SIGMA',
        __sigma_hat: 'SIGMA^',
        __tau: 'TAU',
        __tau_hat: 'TAU^',
        __omega: 'OMEGA'
    }

    ASCII_TO_GREEK = {v: k for k, v in GREEK_TO_ASCII.items()}

    @classmethod
    def __get_order_key(cls, x):
        if not x:
            return 0

        return int(x.split('_')[2])

    @classmethod
    def __get_regions(cls, gene_seq, bed_start, bed_end):
        if not gene_seq:
            raise AssertionError('Specify a gene sequence')
        if bed_start > bed_end:
            raise AssertionError('Start index must be lower or equal than end index')
        if len(gene_seq) < bed_end:
            raise AssertionError('End index too large')

        return gene_seq[:bed_start], gene_seq[bed_start:bed_end], gene_seq[bed_end:]

    @classmethod
    def get_args(cls):
        parser = argparse.ArgumentParser(description='Regions extractor')
        parser.add_argument('-f', '--input-fasta', metavar='FASTA_IN_FILE', type=str, required=True,
                            help='FASTA input file', default=None)
        parser.add_argument('-b', '--input-bed', metavar='BED_IN_FILE', type=str, required=True,
                            help='BED input file', default=None)
        parser.add_argument('-j', '--input-json', metavar='JSON_IN_FILE', type=str, required=True,
                            help='JSON input file', default=None)
        parser.add_argument('-s', '--start-index', metavar='START_INDEX', type=int, required=True,
                            help='Start index of gene region', default=0)
        parser.add_argument('-e', '--end-index', metavar='END_INDEX', type=int, required=True,
                            help='End index of gene region', default=0)
        parser.add_argument('-w', '--window-length', metavar='WINDOW_LENGTH', type=int, required=False,
                            help='Number of nucleotides in single region', default=5)
        parser.add_argument('-o', '--output-file', metavar='OUTPUT_FILE', type=str, required=False,
                            help='Output TXT file', default='output')
        return parser.parse_args()

    @classmethod
    def extract_word(cls, fasta_in, bed_in, json_in, start_idx, end_idx, window_length=5, out_file='output'):
        res = dict()
        with open(fasta_in, 'r') as fin:
            fin.readline()
            gene_seq = fin.readline().strip().upper()

        gene_seq = gene_seq[start_idx:end_idx]

        with open(bed_in, 'r') as fin:
            line = fin.readline()

            i = 1  # We keep track of the row we are reading in the BED file
            while line:
                parts = line.strip().split('\t')
                idx_1 = int(parts[1])
                idx_2 = int(parts[2])

                r1, r2, r3 = cls.__get_regions(gene_seq, idx_1 - start_idx, idx_2 - start_idx)
                r1_rev = r1[::-1]
                r2_rev = r2[::-1]
                r3_rev = r3[::-1]

                # res contains info from all the R-loops in BED file
                res[str(idx_1) + '_' + str(idx_2) + '_' + str(i)] = {'r1': [r1[i:i + window_length] for
                                                                            i in range(0, len(r1), window_length)],
                                                                     'r1_rev': [r1_rev[i:i + window_length][::-1] for i
                                                                                in range(0, len(r1), window_length)],
                                                                     'r2': [r2[i:i + window_length] for
                                                                            i in range(0, len(r2), window_length)],
                                                                     'r2_rev': [r2_rev[i:i + window_length][::-1] for i
                                                                                in range(0, len(r2), window_length)],
                                                                     'r3': [r3[i:i + window_length] for
                                                                            i in range(0, len(r3), window_length)],
                                                                     'r3_rev': [r3_rev[i:i + window_length][::-1] for i
                                                                                in range(0, len(r3), window_length)]
                                                                     }

                line = fin.readline()
                i += 1

        with open(json_in, 'r') as fin:
            grammar_dict = json.load(fin)

        sorted_keys = list(res.keys())  # Need sorted keys bc we iterate on them (if not ordered, result not consistent)
        sorted_keys.sort(key=cls.__get_order_key)
        word_dict = dict()

        for k in sorted_keys:
            if not word_dict.get(k, None):
                word_dict[k] = {'r1_funny_letters': list(), 'r2_funny_letters': list(), 'r3_funny_letters': list()}

            last_val = None
            for val in res[k]['r1']:
                last_val = val

                if len(val) != window_length:
                    funny_letter = cls.__omega + str(len(val))
                else:
                    funny_letter = cls.__gamma

                    for letter, v in grammar_dict.get('region1', dict()).items():
                        if val in v:
                            funny_letter = cls.ASCII_TO_GREEK.get(letter, '?')
                            break

                word_dict[k]['r1_funny_letters'].append(funny_letter)

            if last_val and len(last_val) == window_length:
                word_dict[k]['r1_funny_letters'][-1] = word_dict[k]['r1_funny_letters'][-1] + cls.__omega + '0'

            for val in res[k]['r2_rev']:
                if len(val) != window_length:
                    funny_letter = '?' + str(len(val))
                else:
                    funny_letter = cls.__rho

                    for letter, v in grammar_dict.get('region2', dict()).items():
                        if val in v:
                            funny_letter = cls.ASCII_TO_GREEK.get(letter, '?')
                            break

                word_dict[k]['r2_funny_letters'].append(funny_letter)

            last_val = None
            for val in res[k]['r3_rev']:
                last_val = val

                if len(val) != window_length:
                    funny_letter = cls.__alpha + str(len(val))
                else:
                    funny_letter = cls.__gamma

                    for letter, v in grammar_dict.get('region3', dict()).items():
                        if val in v:
                            funny_letter = cls.ASCII_TO_GREEK.get(letter, '?')
                            break

                word_dict[k]['r3_funny_letters'].append(funny_letter)

            if last_val and len(last_val) == window_length:
                word_dict[k]['r3_funny_letters'][-1] = cls.__alpha + '0' + word_dict[k]['r3_funny_letters'][-1]

        with open(out_file, 'w') as fout:
            for k, v in word_dict.items():
                line = k + ': ' + ''.join(v['r1_funny_letters']) + ''.join(reversed(v['r2_funny_letters'])) + \
                       ''.join(reversed(v['r3_funny_letters']))
                fout.write(line + '\n')


if __name__ == '__main__':
    args = vars(GrammarWord.get_args())
    GrammarWord.extract_word(args.get('input_fasta', None), args.get('input_bed', None), args.get('input_json', None),
                             args.get('start_index', 0), args.get('end_index', 0), args.get('window_length', 5),
                             args.get('output_file', 'output'))
