#!/usr/bin/env python3
import argparse
import json
import openpyxl

"""
Script to calculate union and intersection of two dictionaries.


Copyright 2021 Margherita Maria Ferrari.


This file is part of UnionDict.

UnionDict is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

UnionDict is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with UnionDict.  If not, see <http://www.gnu.org/licenses/>.
"""


class UnionDict:
    @classmethod
    # Reads tuples and corresponding weight in each region from the xlsx file
    def __read_xlsx(cls, xlsx_in):
        region1_values = dict()
        region2_values = dict()
        region3_values = dict()
        region4_values = dict()
        wb_regions = openpyxl.load_workbook(xlsx_in, read_only=True)

        for ws_region in wb_regions.worksheets:
            if ws_region.title.endswith('1'):
                region1_values = {x[0].value: x[7].value for x in list(ws_region.rows)}
            elif ws_region.title.endswith('2'):
                region2_values = {x[0].value: x[7].value for x in list(ws_region.rows)}
            elif ws_region.title.endswith('3'):
                region3_values = {x[0].value: x[7].value for x in list(ws_region.rows)}
            elif ws_region.title.endswith('4'):
                region4_values = {x[0].value: x[7].value for x in list(ws_region.rows)}

        wb_regions.close()
        return region1_values, region2_values, region3_values, region4_values

    @classmethod
    # Read weights for a given tuple
    def __get_weights(cls, pattern, region1_values, region2_values, region3_values, region4_values):
        return region1_values.get(pattern, 0), region2_values.get(pattern, 0), region3_values.get(pattern, 0), \
               region4_values.get(pattern, 0)

    @classmethod
    # Find max weight for a given tuple
    def __get_max_weight(cls, pattern, region1_values, region2_values, region3_values, region4_values):
        return max(cls.__get_weights(pattern, region1_values, region2_values, region3_values, region4_values))

    @classmethod
    def get_args(cls):
        parser = argparse.ArgumentParser(description='Regions extractor')
        parser.add_argument('-j1', '--input-json-1', metavar='JSON1_IN_FILE', type=str, required=True,
                            help='First JSON input file', default=None)
        parser.add_argument('-j2', '--input-json-2', metavar='JSON2_IN_FILE', type=str, required=True,
                            help='Second JSON input file', default=None)
        parser.add_argument('-x1', '--input-xlsx-1', metavar='XLSX1_IN_FILE', type=str, required=True,
                            help='First XLSX input file', default=None)
        parser.add_argument('-x2', '--input-xlsx-2', metavar='XLSX2_IN_FILE', type=str, required=True,
                            help='Second XLSX input file', default=None)
        parser.add_argument('-o', '--output-prefix', metavar='OUTPUT_PREFIX', type=str, required=False,
                            help='Prefix for output JSON file', default='output_prefix')
        return parser.parse_args()

    @classmethod
    # Determine intersection for each grammar symbol in the same region
    def intersect_symbol_json(cls, json_in_1, json_in_2, output_prefix='out'):
        intersect_dict = {'region1': dict(), 'region2_3': dict(), 'region4': dict()}

        with open(json_in_1, 'r') as fin1, open(json_in_2, 'r') as fin2:
            grammar_dict_1 = json.load(fin1)
            grammar_dict_2 = json.load(fin2)

        for k in ['region1', 'region2_3', 'region4']:
            # sub_k is a grammar symbol, sub_v is the list of corresponding tuples from dict_1
            for sub_k, sub_v in grammar_dict_1.get(k, dict()).items():
                # Collect tuples in sub_v in dict_1 that appear also
                # correspond to sub_k in dict_2
                intersect_dict[k][sub_k] = [i for i in sub_v if i in grammar_dict_2.get(k, dict()).get(sub_k, list())]

        with open(output_prefix + '_symbol_intersection.json', 'w') as fout:
            json.dump(intersect_dict, fout)

    @classmethod
    # Determine intersection across grammar symbols in the same region
    def intersect_region_json(cls, json_in_1, json_in_2, xlsx_in_1, xlsx_in_2, output_prefix='out'):
        def __get_r_dict(grammar_dict, region, region1_values, region2_values, region3_values, region4_values, w_key):
            r_dict = dict()

            # For tuples in the dictionary, take the corresponding weight in 'region' specified in input
            for tmp_k, tmp_v in grammar_dict.get(region, dict()).items():
                for v in tmp_v:
                    w1, w2, w3, w4 = cls.__get_weights(v, region1_values, region2_values, region3_values,
                                                       region4_values)
                    weights = {'r1_weight': w1, 'r2_weight': w2, 'r3_weight': w3, 'r4_weight': w4}

                    # dictionary: {tuple v : {grammar symbol in dictionary : {file_number : {r1: weight, ...}}}}
                    r_dict[v] = {tmp_k: {w_key: weights}}

            return r_dict

        intersect_region_dict = {'region1': dict(), 'region2_3': dict(), 'region4': dict()}

        with open(json_in_1, 'r') as fin1, open(json_in_2, 'r') as fin2:
            grammar_dict_1 = json.load(fin1)
            grammar_dict_2 = json.load(fin2)

        wb1_region1_values, wb1_region2_values, wb1_region3_values, wb1_region4_values = cls.__read_xlsx(xlsx_in_1)
        wb2_region1_values, wb2_region2_values, wb2_region3_values, wb2_region4_values = cls.__read_xlsx(xlsx_in_2)

        for k in ['region1', 'region2_3', 'region4']:
            # For region k and for each tuple in k, create dictionary specifying the grammar symbol, weight, file_number
            r_dict_1 = __get_r_dict(grammar_dict_1, k, wb1_region1_values, wb1_region2_values, wb1_region3_values,
                                    wb1_region4_values, 'file1')
            r_dict_2 = __get_r_dict(grammar_dict_2, k, wb2_region1_values, wb2_region2_values, wb2_region3_values,
                                    wb2_region4_values, 'file2')

            for sub_k in list(r_dict_1.keys()):  # For tuple sub_k in region k from dict_1
                # Check if tuple sub_k appears in the tuples from dict_2
                if sub_k in list(r_dict_2.keys()):
                    # Check if the grammar symbol corresponding to sub_k in dict_1 is the same as the one in dict_2
                    same_letters = [i for i in list(r_dict_1.get(sub_k, dict()).keys())
                                    if i in list(r_dict_2.get(sub_k, dict()).keys())]

                    for funny in same_letters:
                        # Collect all weights for sub_k in dict_1 and dict_2
                        # We retain info about tuples corresponding to same symbol in dict_1 and dict_2
                        r_dict_1[sub_k][funny].update(r_dict_2.get(sub_k, dict()).get(funny, dict()))
                        # Delete info for sub_k from dict_2
                        r_dict_2.get(sub_k, dict()).pop(funny)

                    # Case in which sub_k has two distinct symbols in dict_1 and dict_2
                    r_dict_1[sub_k].update(r_dict_2.get(sub_k, dict()))
                # If tuple sub_k does not appear in the tuples from dict_2, delete sub_k info
                else:
                    del r_dict_1[sub_k]

            intersect_region_dict[k] = r_dict_1

        with open(output_prefix + '_region_intersection.json', 'w') as fout:
            json.dump(intersect_region_dict, fout)

    @classmethod
    # Determine union of two dictionaries
    def union_json(cls, json_in_1, json_in_2, xlsx_in_1, xlsx_in_2, output_prefix='out'):
        union_dict = {'region1': dict(), 'region2_3': dict(), 'region4': dict()}

        with open(json_in_1, 'r') as fin1, open(json_in_2, 'r') as fin2:
            grammar_dict_1 = json.load(fin1)
            grammar_dict_2 = json.load(fin2)

        wb1_region1_values, wb1_region2_values, wb1_region3_values, wb1_region4_values = cls.__read_xlsx(xlsx_in_1)
        wb2_region1_values, wb2_region2_values, wb2_region3_values, wb2_region4_values = cls.__read_xlsx(xlsx_in_2)

        for k in ['region1', 'region2_3', 'region4']:
            # sub_k is a grammar symbol, sub_v is the list of corresponding tuples in dict_1
            for sub_k, sub_v in grammar_dict_1.get(k, dict()).items():
                tmp = set(sub_v)
                tmp.update(grammar_dict_2.get(k, dict()).get(sub_k, list()))
                union_list = list(tmp)

                for v in list(union_list):
                    # Compute max weight for v in dict_1 and dict_2
                    w1_max = cls.__get_max_weight(v, wb1_region1_values, wb1_region2_values, wb1_region3_values,
                                                  wb1_region4_values)
                    w2_max = cls.__get_max_weight(v, wb2_region1_values, wb2_region2_values, wb2_region3_values,
                                                  wb2_region4_values)

                    # k2 is a grammar symbol different form sub_k
                    for k2 in [i for i in grammar_dict_1.get(k, dict()).keys() if i != sub_k]:
                        # If v is associated to symbol k2 in region k of dict_1
                        if v in grammar_dict_1.get(k, dict()).get(k2, list()):
                            # Disassociate v from symbol sub_k if max_weight_1 > max_weight_2
                            if w1_max > w2_max:
                                if union_list.count(v) > 0:
                                    union_list.remove(v)

                    for k2 in [i for i in grammar_dict_2.get(k, dict()).keys() if i != sub_k]:
                        if v in grammar_dict_2.get(k, dict()).get(k2, list()):
                            if w1_max < w2_max:
                                if union_list.count(v) > 0:
                                    union_list.remove(v)

                union_dict[k][sub_k] = union_list

        with open(output_prefix + '_union.json', 'w') as fout:
            json.dump(union_dict, fout)


if __name__ == '__main__':
    args = vars(UnionDict.get_args())
    UnionDict.intersect_symbol_json(args.get('input_json_1', None), args.get('input_json_2', None),
                                    args.get('output_prefix', 'out'))
    UnionDict.intersect_region_json(args.get('input_json_1', None), args.get('input_json_2', None),
                                    args.get('input_xlsx_1', None), args.get('input_xlsx_2', None),
                                    args.get('output_prefix', 'out'))
    UnionDict.union_json(args.get('input_json_1', None), args.get('input_json_2', None),
                         args.get('input_xlsx_1', None), args.get('input_xlsx_2', None),
                         args.get('output_prefix', 'out'))
