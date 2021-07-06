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
    def intersect_json(cls, json_in_1, json_in_2, output_prefix='out'):
        intersect_dict = {'region1': dict(), 'region2': dict(), 'region3': dict()}

        with open(json_in_1, 'r') as fin1, open(json_in_2, 'r') as fin2:
            grammar_dict_1 = json.load(fin1)
            grammar_dict_2 = json.load(fin2)

        for k in ['region1', 'region2', 'region3']:
            for sub_k, sub_v in grammar_dict_1.get(k, dict()).items():
                intersect_dict[k][sub_k] = [i for i in sub_v if i in grammar_dict_2.get(k, dict()).get(sub_k, list())]

        with open(output_prefix + '_intersection.json', 'w') as fout:
            json.dump(intersect_dict, fout)

    @classmethod
    def union_json(cls, json_in_1, json_in_2, xlsx_in_1, xlsx_in_2, output_prefix='out'):
        union_dict = {'region1': dict(), 'region2': dict(), 'region3': dict()}

        with open(json_in_1, 'r') as fin1, open(json_in_2, 'r') as fin2:
            grammar_dict_1 = json.load(fin1)
            grammar_dict_2 = json.load(fin2)

        wb1_region1_values = dict()
        wb1_region2_values = dict()
        wb1_region3_values = dict()
        wb1_region4_values = dict()
        wb_regions = openpyxl.load_workbook(xlsx_in_1, read_only=True)
        for ws_region in wb_regions.worksheets:
            if ws_region.title.endswith('1'):
                wb1_region1_values = {x[0].value: x[7].value for x in list(ws_region.rows)}
            elif ws_region.title.endswith('2'):
                wb1_region2_values = {x[0].value: x[7].value for x in list(ws_region.rows)}
            elif ws_region.title.endswith('3'):
                wb1_region3_values = {x[0].value: x[7].value for x in list(ws_region.rows)}
            elif ws_region.title.endswith('4'):
                wb1_region4_values = {x[0].value: x[7].value for x in list(ws_region.rows)}
        wb_regions.close()

        wb2_region1_values = dict()
        wb2_region2_values = dict()
        wb2_region3_values = dict()
        wb2_region4_values = dict()
        wb_regions = openpyxl.load_workbook(xlsx_in_2, read_only=True)
        for ws_region in wb_regions.worksheets:
            if ws_region.title.endswith('1'):
                wb2_region1_values = {x[0].value: x[7].value for x in list(ws_region.rows)}
            elif ws_region.title.endswith('2'):
                wb2_region2_values = {x[0].value: x[7].value for x in list(ws_region.rows)}
            elif ws_region.title.endswith('3'):
                wb2_region3_values = {x[0].value: x[7].value for x in list(ws_region.rows)}
            elif ws_region.title.endswith('4'):
                wb2_region4_values = {x[0].value: x[7].value for x in list(ws_region.rows)}
        wb_regions.close()

        for k in ['region1', 'region2', 'region3']:
            for sub_k, sub_v in grammar_dict_1.get(k, dict()).items():
                tmp = set(sub_v)
                tmp.update(grammar_dict_2.get(k, dict()).get(sub_k, list()))
                union_list = list(tmp)
                for v in sub_v:
                    problem = False
                    for k2 in [i for i in grammar_dict_2.get(k, dict()).keys() if i not in sub_k]:
                        if v in grammar_dict_2.get(k, dict()).get(k2, list()):
                            problem = True
                            break
                    if problem:
                        if k.endswith('1') and wb1_region1_values.get(v, 0) < wb2_region1_values.get(v, 0):
                            union_list.remove(v)
                        elif k.endswith('2'):
                            weight_1 = max(wb1_region2_values.get(v, 0), wb1_region3_values.get(v, 0))
                            weight_2 = max(wb2_region2_values.get(v, 0), wb2_region3_values.get(v, 0))
                            if weight_1 < weight_2:
                                union_list.remove(v)
                        elif wb1_region4_values.get(v, 0) < wb2_region4_values.get(v, 0):
                            union_list.remove(v)
                union_dict[k][sub_k] = union_list

        with open(output_prefix + '_union.json', 'w') as fout:
            json.dump(union_dict, fout)


if __name__ == '__main__':
    args = vars(UnionDict.get_args())
    UnionDict.intersect_json(args.get('input_json_1', None), args.get('input_json_2', None),
                             args.get('output_prefix', 'out'))
    UnionDict.union_json(args.get('input_json_1', None), args.get('input_json_2', None),
                         args.get('input_xlsx_1', None), args.get('input_xlsx_2', None),
                         args.get('output_prefix', 'out'))
