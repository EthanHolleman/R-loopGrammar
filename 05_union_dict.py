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
        intersect_dict = {'region1': dict(), 'region2': dict(), 'region3': dict()}

        with open(json_in_1, 'r') as fin1, open(json_in_2, 'r') as fin2:
            grammar_dict_1 = json.load(fin1)
            grammar_dict_2 = json.load(fin2)

        for k in ['region1', 'region2', 'region3']:
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
                    if region.endswith('1'):
                        weight = region1_values.get(v, 0)
                    elif region.endswith('2'):
                        weight = max(region2_values.get(v, 0), region3_values.get(v, 0))
                    else:
                        weight = region4_values.get(v, 0)

                    # dictionary: {tuple v : {grammar symbol in dictionary : {file_number : weight in 'region'}}}
                    r_dict[v] = {tmp_k: {w_key: weight}}

            return r_dict

        intersect_region_dict = {'region1': dict(), 'region2': dict(), 'region3': dict()}

        with open(json_in_1, 'r') as fin1, open(json_in_2, 'r') as fin2:
            grammar_dict_1 = json.load(fin1)
            grammar_dict_2 = json.load(fin2)

        wb1_region1_values, wb1_region2_values, wb1_region3_values, wb1_region4_values = cls.__read_xlsx(xlsx_in_1)
        wb2_region1_values, wb2_region2_values, wb2_region3_values, wb2_region4_values = cls.__read_xlsx(xlsx_in_2)

        for k in ['region1', 'region2', 'region3']:
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
                        # Collect both weights for sub_k
                        # We retain info about different tuples corresponding to same symbol
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
        def __manage_conflict(grammar_dict, region, symbol, pattern, union_list_tmp,
                              wb1_region1_values_tmp, wb1_region2_values_tmp, wb1_region3_values_tmp,
                              wb1_region4_values_tmp, wb2_region1_values_tmp, wb2_region2_values_tmp,
                              wb2_region3_values_tmp, wb2_region4_values_tmp):
            # Take grammar symbols in dict_2 different from sub_k
            for k2 in [i for i in grammar_dict.get(region, dict()).keys() if i not in symbol]:
                # Check if v appears in the list of tuples corresponding to the grammar symbol k2 in dict_2
                if pattern in grammar_dict.get(region, dict()).get(k2, list()):
                    # Resolve conflicts by removing v from the tuples corresponding to sub_k in the union
                    # if weight_1 < weight_2: v is still in the union and corresponds to k2
                    if region.endswith('1'):
                        if wb1_region1_values_tmp.get(pattern, 0) < wb2_region1_values_tmp.get(pattern, 0):
                            union_list_tmp.remove(pattern)
                        # else:  # If w1 > w2, remove v from dict_2
                        #     grammar_dict.get(region, dict()).get(k2, list()).remove(pattern)
                    # k = region_2 : take max among region_2 and region_3 in xlsx
                    elif region.endswith('2'):
                        weight_1 = max(wb1_region2_values_tmp.get(pattern, 0), wb1_region3_values_tmp.get(pattern, 0))
                        weight_2 = max(wb2_region2_values_tmp.get(pattern, 0), wb2_region3_values_tmp.get(pattern, 0))
                        if weight_1 < weight_2:
                            union_list_tmp.remove(pattern)
                        # else:
                        #     grammar_dict.get(region, dict()).get(k2, list()).remove(pattern)
                    else:
                        if wb1_region4_values_tmp.get(pattern, 0) < wb2_region4_values_tmp.get(pattern, 0):
                            union_list_tmp.remove(pattern)
                        # else:
                        #     grammar_dict.get(region, dict()).get(k2, list()).remove(pattern)

                    # dict_2: v appears at most once in region k, so we have at most one grammar symbol k2
                    break
            return union_list_tmp

        union_dict = {'region1': dict(), 'region2': dict(), 'region3': dict()}

        with open(json_in_1, 'r') as fin1, open(json_in_2, 'r') as fin2:
            grammar_dict_1 = json.load(fin1)
            grammar_dict_2 = json.load(fin2)

        wb1_region1_values, wb1_region2_values, wb1_region3_values, wb1_region4_values = cls.__read_xlsx(xlsx_in_1)
        wb2_region1_values, wb2_region2_values, wb2_region3_values, wb2_region4_values = cls.__read_xlsx(xlsx_in_2)

        for k in ['region1', 'region2', 'region3']:
            # sub_k is a grammar symbol, sub_v is the list of corresponding tuples in dict_1
            for sub_k, sub_v in grammar_dict_1.get(k, dict()).items():
                tmp = set(sub_v)
                tmp.update(grammar_dict_2.get(k, dict()).get(sub_k, list()))
                union_list = list(tmp)
                # v is a tuple in sub_v corresponding to the grammar symbol sub_k in region k
                for v in sub_v:
                    union_list = __manage_conflict(grammar_dict_1, k, sub_k, v, union_list, wb1_region1_values, wb1_region2_values,
                                      wb1_region3_values, wb1_region4_values, wb2_region1_values, wb2_region2_values,
                                      wb2_region3_values, wb2_region4_values)
                    union_list =__manage_conflict(grammar_dict_2, k, sub_k, v, union_list, wb1_region1_values, wb1_region2_values,
                                      wb1_region3_values, wb1_region4_values, wb2_region1_values, wb2_region2_values,
                                      wb2_region3_values, wb2_region4_values)

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
