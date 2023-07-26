#!/usr/bin/env python3
import argparse
import json
import openpyxl
import random

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

import collections

assignments_made = collections.defaultdict(lambda: 0)


def binary_letter_assignment(letter1, letter2):
    global assignments_made

    letter_assignments = {
        ("SIGMA", "SIGMA^"): "DELTA",
        ("DELTA", "SIGMA"): "SIGMA",
        ("DELTA", "SIGMA^"): "SIGMA^",
        ("GAMMA", "SIGMA"): "SIGMA",
        ("GAMMA", "SIGMA^"): "SIGMA^",
        ("DELTA", "GAMMA"): "DELTA",
        ("TAU", "TAU^"): "BETA",
        ("BETA", "TAU"): "TAU",
        ("BETA", "TAU^"): "TAU^",
        ("RHO", "TAU"): "TAU",
        ("RHO", "TAU^"): "TAU^",
        ("BETA", "RHO"): "BETA",
    }

    assignment_key = tuple(sorted([letter1, letter2]))
    assignments_made[f"{assignment_key} = {letter_assignments[assignment_key]}"] += 1

    return letter_assignments[assignment_key]


class UnionDict:
    # Works only if "i" is a basic type instance (str, int, ...)
    # Item i is a tuple, d is the relocation dictionary
    # Determine if item i appears somewhere in dict d
    @classmethod
    def __item_in_dict(cls, i, d):
        ret = False

        for v in d.values():
            if ret:
                return True

            if isinstance(v, dict):
                return ret or cls.__item_in_dict(i, v)
            elif isinstance(v, list):
                ret = ret or i in v
            else:
                ret = ret or i == v

        return ret

    @classmethod
    # Read line from input file
    def __read_line_from_input_list(cls, fin, raise_error=True):
        line = fin.readline()

        if not line:
            if raise_error:
                raise AssertionError("Unexpected end of file")
            return line

        line = line.strip()

        if not line or line.startswith("#"):
            return cls.__read_line_from_input_list(fin, raise_error)

        return line

    @classmethod
    # Reads tuples and corresponding weight in each region from the xlsx file
    def __read_xlsx(cls, xlsx_in):
        region1_values = dict()
        region2_values = dict()
        region3_values = dict()
        region4_values = dict()
        wb_regions = openpyxl.load_workbook(xlsx_in, read_only=True)

        for ws_region in wb_regions.worksheets:
            if ws_region.title.endswith("1"):
                region1_values = {x[0].value: x[7].value for x in list(ws_region.rows)}
            elif ws_region.title.endswith("2"):
                region2_values = {x[0].value: x[7].value for x in list(ws_region.rows)}
            elif ws_region.title.endswith("3"):
                region3_values = {x[0].value: x[7].value for x in list(ws_region.rows)}
            elif ws_region.title.endswith("4"):
                region4_values = {x[0].value: x[7].value for x in list(ws_region.rows)}

        wb_regions.close()
        return region1_values, region2_values, region3_values, region4_values

    @classmethod
    # Read weights for a given tuple
    def __get_weights(
        cls, pattern, region1_values, region2_values, region3_values, region4_values
    ):
        return (
            region1_values.get(pattern, 0),
            region2_values.get(pattern, 0),
            region3_values.get(pattern, 0),
            region4_values.get(pattern, 0),
        )

    @classmethod
    # Find max weight for a given tuple
    def __get_max_weight(
        cls, pattern, region1_values, region2_values, region3_values, region4_values
    ):
        return max(
            cls.__get_weights(
                pattern, region1_values, region2_values, region3_values, region4_values
            )
        )

    @classmethod
    # Find tuples associated with same symbol in two dictionaries
    def __intersect_symbol_json(cls, grammar_dict_1, grammar_dict_2):
        intersect_dict = {"region1": dict(), "region2_3": dict(), "region4": dict()}

        for k in ["region1", "region2_3", "region4"]:
            # sub_k is a grammar symbol, sub_v is the list of corresponding tuples from dict_1
            for sub_k, sub_v in grammar_dict_1.get(k, dict()).items():
                # Collect tuples in sub_v in dict_1 that
                # correspond to sub_k in dict_2
                intersect_dict[k][sub_k] = [
                    i
                    for i in sub_v
                    if i in grammar_dict_2.get(k, dict()).get(sub_k, list())
                ]

        return intersect_dict

    @classmethod
    # Intersection across regions: find tuples appearing in both dicts and collect their symbols (may be equal or not)
    def __intersect_region_json(cls, full_r_dict_1, full_r_dict_2):
        intersect_region_dict = {
            "region1": dict(),
            "region2_3": dict(),
            "region4": dict(),
        }

        for k in ["region1", "region2_3", "region4"]:
            # For region k and for each tuple in k, create dictionary specifying the grammar symbol, weight, file_number
            r_dict_1 = full_r_dict_1.get(k, dict())
            r_dict_2 = full_r_dict_2.get(k, dict())

            for sub_k in list(
                r_dict_1.keys()
            ):  # For tuple sub_k in region k from dict_1
                # Check if tuple sub_k appears in the tuples from dict_2
                if sub_k in list(r_dict_2.keys()):
                    # Check if the grammar symbol corresponding to sub_k in dict_1 is the same as the one in dict_2
                    same_letters = [
                        i
                        for i in list(r_dict_1.get(sub_k, dict()).keys())
                        if i in list(r_dict_2.get(sub_k, dict()).keys())
                    ]

                    for funny in same_letters:
                        # Collect all weights for sub_k in dict_1 and dict_2
                        # We retain info about tuples corresponding to same symbol in dict_1 and dict_2
                        r_dict_1[sub_k][funny].update(
                            r_dict_2.get(sub_k, dict()).get(funny, dict())
                        )
                        # Delete info for sub_k from dict_2
                        r_dict_2.get(sub_k, dict()).pop(funny)

                    # Case in which sub_k has two distinct symbols in dict_1 and dict_2
                    r_dict_1[sub_k].update(r_dict_2.get(sub_k, dict()))
                # If tuple sub_k does not appear in the tuples from dict_2, delete sub_k info
                else:
                    del r_dict_1[sub_k]

            intersect_region_dict[k] = r_dict_1

        return intersect_region_dict

    @classmethod
    # Compute union for two dictionaries
    def __union_json(
        cls, grammar_dict_1, grammar_dict_2, weights_1, weights_2, method="stochastic"
    ):
        # Dictionary for random choices of symbols when max_weight_1 = max_weight_2
        random_relocation = {"region1": dict(), "region2_3": dict(), "region4": dict()}
        union_dict = {"region1": dict(), "region2_3": dict(), "region4": dict()}
        union_weights_dict = {"r1": dict(), "r2": dict(), "r3": dict(), "r4": dict()}

        for k in ["region1", "region2_3", "region4"]:
            # sub_k is a grammar symbol, sub_v is the list of corresponding tuples in dict_1
            for sub_k, sub_v in grammar_dict_1.get(k, dict()).items():
                tmp = set(sub_v)
                tmp.update(grammar_dict_2.get(k, dict()).get(sub_k, list()))
                union_list = list(tmp)

                for v in list(union_list):
                    # Lottery for tuples having distinct symbols in dict_1 and dict_2 but same max weight
                    funny_letters_lottery = {sub_k}
                    # Compute max weight for v in dict_1 and dict_2
                    w1_max = cls.__get_max_weight(
                        v,
                        weights_1.get("r1", dict()),
                        weights_1.get("r2", dict()),
                        weights_1.get("r3", dict()),
                        weights_1.get("r4", dict()),
                    )
                    w2_max = cls.__get_max_weight(
                        v,
                        weights_2.get("r1", dict()),
                        weights_2.get("r2", dict()),
                        weights_2.get("r3", dict()),
                        weights_2.get("r4", dict()),
                    )

                    # k2 is a grammar symbol different form sub_k
                    for k2 in [
                        i for i in grammar_dict_1.get(k, dict()).keys() if i != sub_k
                    ]:
                        # If v is associated to symbol k2 in region k of dict_1
                        if v in grammar_dict_1.get(k, dict()).get(k2, list()):
                            if w1_max == w2_max:
                                funny_letters_lottery.add(k2)
                            # Disassociate v from symbol sub_k if max_weight_1 > max_weight_2
                            elif w1_max > w2_max and union_list.count(v) > 0:
                                union_list.remove(v)

                    # Same procedure as above, but for dict_2
                    for k2 in [
                        i for i in grammar_dict_2.get(k, dict()).keys() if i != sub_k
                    ]:
                        if v in grammar_dict_2.get(k, dict()).get(k2, list()):
                            if w1_max == w2_max:
                                funny_letters_lottery.add(k2)
                            elif w1_max < w2_max and union_list.count(v) > 0:
                                union_list.remove(v)

                    # If funny_letters_lottery contains more than one symbol, and v is in the union, and v has not been
                    # already relocated in region k: we do not remove v from union_list if max_weight_1 = max_weight_2,
                    # so we don't want to relocate v again (once for every symbol associated to v)
                    if (
                        len(funny_letters_lottery) > 1
                        and union_list.count(v) > 0
                        and not cls.__item_in_dict(v, random_relocation.get(k, dict()))
                    ):
                        assert len(funny_letters_lottery) == 2
                        funny_letters_lottery_list = list(funny_letters_lottery)

                        if method == "deterministic":
                            k2 = binary_letter_assignment(
                                funny_letters_lottery_list[0],
                                funny_letters_lottery_list[1],
                            )
                        elif method == "stochastic":
                            k2 = list(funny_letters_lottery)[
                                random.randint(0, len(funny_letters_lottery) - 1)
                            ]
                        else:
                            raise Exception(f"Unsupported method: {method}")

                        tmp_list = random_relocation[k].get(k2, list())
                        tmp_list.append(v)
                        random_relocation[k][k2] = tmp_list
                        union_list.remove(v)

                    # If we detect again a conflict but we have already relocated v, remove v from union
                    if (
                        len(funny_letters_lottery) > 1
                        and union_list.count(v) > 0
                        and cls.__item_in_dict(v, random_relocation.get(k, dict()))
                    ):
                        union_list.remove(v)

                # If v is not associated with sub_k anymore, we will add it to the union when we consider
                # its new symbol in relocation dict
                union_list.extend(random_relocation[k].get(sub_k, list()))
                union_dict[k][sub_k] = union_list

            # Need to keep info about weights of the tuples appearing in union dict
            for values in union_dict.get(k, dict()).values():
                # v is a tuple, values is a list of tuples corresponding to a grammar symbol in region k
                for v in values:
                    if k.endswith("1"):
                        # Take max weight for v in region 1 for the given two dicts
                        union_weights_dict["r1"][v] = max(
                            cls.__get_max_weight(
                                v, weights_1.get("r1", dict()), dict(), dict(), dict()
                            ),
                            cls.__get_max_weight(
                                v, weights_2.get("r1", dict()), dict(), dict(), dict()
                            ),
                        )
                    elif k.endswith("2_3"):
                        # Take max weight for v in region 2 and 3 for the given two dicts
                        union_weights_dict["r2"][v] = max(
                            cls.__get_max_weight(
                                v,
                                dict(),
                                weights_1.get("r2", dict()),
                                weights_1.get("r3", dict()),
                                dict(),
                            ),
                            cls.__get_max_weight(
                                v,
                                dict(),
                                weights_2.get("r2", dict()),
                                weights_2.get("r3", dict()),
                                dict(),
                            ),
                        )
                    else:
                        # Take max weight for v in region 4 for the given two dicts
                        union_weights_dict["r4"][v] = max(
                            cls.__get_max_weight(
                                v, dict(), dict(), dict(), weights_1.get("r4", dict())
                            ),
                            cls.__get_max_weight(
                                v, dict(), dict(), dict(), weights_2.get("r4", dict())
                            ),
                        )

                # For simplicity, weights in region 2 and 3 are equal after union
                union_weights_dict["r3"] = dict(union_weights_dict.get("r2", dict()))

        return union_dict, union_weights_dict

    @classmethod
    def get_args(cls):
        parser = argparse.ArgumentParser(description="Union dict")
        parser.add_argument(
            "-i",
            "--input-file-list",
            metavar="INPUT_FILE_LIST",
            type=str,
            required=True,
            help="Text file containing input files (one per line)",
            default=None,
        )
        parser.add_argument(
            "-o",
            "--output-prefix",
            metavar="OUTPUT_PREFIX",
            type=str,
            required=False,
            help="Prefix for output JSON file",
            default="output_prefix",
        )
        return parser.parse_args()

    @classmethod
    # Find tuples associated with same symbol for input dictionaries
    def intersect_symbol_json(cls, file_list_in, output_prefix="out"):
        with open(file_list_in, "r") as fin:
            json_in_1 = cls.__read_line_from_input_list(fin)
            # Skip line about XLSX
            cls.__read_line_from_input_list(fin)
            json_in_2 = cls.__read_line_from_input_list(fin)
            cls.__read_line_from_input_list(fin)

            with open(json_in_1, "r") as fin1, open(json_in_2, "r") as fin2:
                grammar_dict_1 = json.load(fin1)
                grammar_dict_2 = json.load(fin2)

            intersect_dict = cls.__intersect_symbol_json(grammar_dict_1, grammar_dict_2)
            # Take next dict
            json_in_2 = cls.__read_line_from_input_list(fin, False)

            # Repeat for all other input files
            while json_in_2:
                with open(json_in_2, "r") as fin1:
                    grammar_dict_2 = json.load(fin1)

                intersect_dict = cls.__intersect_symbol_json(
                    intersect_dict, grammar_dict_2
                )

                cls.__read_line_from_input_list(fin)
                json_in_2 = cls.__read_line_from_input_list(fin, False)

        with open(output_prefix + "_symbol_intersection.json", "w") as fout:
            json.dump(intersect_dict, fout)

    @classmethod
    # Intersection across regions for input dictionaries
    def intersect_region_json(cls, file_list_in, output_prefix="out"):
        # Create dict with tuple info
        def __get_r_dict(
            grammar_dict,
            region,
            region1_values,
            region2_values,
            region3_values,
            region4_values,
            w_key,
        ):
            r_dict = dict()

            # For tuples in the dictionary, take the corresponding weight in 'region' specified in input
            for tmp_k, tmp_v in grammar_dict.get(region, dict()).items():
                for v in tmp_v:
                    w1, w2, w3, w4 = cls.__get_weights(
                        v,
                        region1_values,
                        region2_values,
                        region3_values,
                        region4_values,
                    )
                    weights = {
                        "r1_weight": w1,
                        "r2_weight": w2,
                        "r3_weight": w3,
                        "r4_weight": w4,
                    }

                    # dictionary: {tuple v : {grammar symbol in dictionary : {file_number : {r1: weight, ...}}}}
                    r_dict[v] = {tmp_k: {w_key: weights}}

            return r_dict

        with open(file_list_in, "r") as fin:
            json_in_1 = cls.__read_line_from_input_list(fin)
            xlsx_in_1 = cls.__read_line_from_input_list(fin)
            json_in_2 = cls.__read_line_from_input_list(fin)
            xlsx_in_2 = cls.__read_line_from_input_list(fin)

            with open(json_in_1, "r") as fin1, open(json_in_2, "r") as fin2:
                grammar_dict_1 = json.load(fin1)
                grammar_dict_2 = json.load(fin2)

            (
                wb1_r1_values,
                wb1_r2_values,
                wb1_r3_values,
                wb1_r4_values,
            ) = cls.__read_xlsx(xlsx_in_1)
            (
                wb2_r1_values,
                wb2_r2_values,
                wb2_r3_values,
                wb2_r4_values,
            ) = cls.__read_xlsx(xlsx_in_2)
            full_r_dict_1 = {"region1": dict(), "region2_3": dict(), "region4": dict()}
            full_r_dict_2 = {"region1": dict(), "region2_3": dict(), "region4": dict()}

            for k in ["region1", "region2_3", "region4"]:
                # For region k and for each tuple in k, create dict specifying the grammar symbol, weight, file_number
                full_r_dict_1[k] = __get_r_dict(
                    grammar_dict_1,
                    k,
                    wb1_r1_values,
                    wb1_r2_values,
                    wb1_r3_values,
                    wb1_r4_values,
                    "file1",
                )
                full_r_dict_2[k] = __get_r_dict(
                    grammar_dict_2,
                    k,
                    wb2_r1_values,
                    wb2_r2_values,
                    wb2_r3_values,
                    wb2_r4_values,
                    "file2",
                )

            intersect_region_dict = cls.__intersect_region_json(
                full_r_dict_1, full_r_dict_2
            )
            json_in_2 = cls.__read_line_from_input_list(fin, False)

            while json_in_2:
                with open(json_in_2, "r") as fin1:
                    grammar_dict_2 = json.load(fin1)

                xlsx_in_2 = cls.__read_line_from_input_list(fin)
                (
                    wb2_r1_values,
                    wb2_r2_values,
                    wb2_r3_values,
                    wb2_r4_values,
                ) = cls.__read_xlsx(xlsx_in_2)

                for k in ["region1", "region2_3", "region4"]:
                    # For region k and for each tuple in k, create dict specifying the grammar symbol,weight,file_number
                    full_r_dict_2[k] = __get_r_dict(
                        grammar_dict_2,
                        k,
                        wb2_r1_values,
                        wb2_r2_values,
                        wb2_r3_values,
                        wb2_r4_values,
                        "file2",
                    )

                intersect_region_dict = cls.__intersect_region_json(
                    intersect_region_dict, full_r_dict_2
                )

                json_in_2 = cls.__read_line_from_input_list(fin, False)

        with open(output_prefix + "_region_intersection.json", "w") as fout:
            json.dump(intersect_region_dict, fout)

    @classmethod
    # Compute union for input dictionaries
    def union_json(cls, file_list_in, output_filename, method="stochastic"):
        with open(file_list_in, "r") as fin:
            json_in_1 = cls.__read_line_from_input_list(fin)
            xlsx_in_1 = cls.__read_line_from_input_list(fin)
            json_in_2 = cls.__read_line_from_input_list(fin)
            xlsx_in_2 = cls.__read_line_from_input_list(fin)

            print(xlsx_in_1, xlsx_in_2)
            with open(json_in_1, "r") as fin1, open(json_in_2, "r") as fin2:
                grammar_dict_1 = json.load(fin1)
                grammar_dict_2 = json.load(fin2)

            (
                wb1_r1_values,
                wb1_r2_values,
                wb1_r3_values,
                wb1_r4_values,
            ) = cls.__read_xlsx(xlsx_in_1)
            weights_1 = {
                "r1": wb1_r1_values,
                "r2": wb1_r2_values,
                "r3": wb1_r3_values,
                "r4": wb1_r4_values,
            }
            (
                wb2_r1_values,
                wb2_r2_values,
                wb2_r3_values,
                wb2_r4_values,
            ) = cls.__read_xlsx(xlsx_in_2)
            weights_2 = {
                "r1": wb2_r1_values,
                "r2": wb2_r2_values,
                "r3": wb2_r3_values,
                "r4": wb2_r4_values,
            }

            union_dict, union_dict_weights = cls.__union_json(
                grammar_dict_1, grammar_dict_2, weights_1, weights_2, method
            )
            json_in_2 = cls.__read_line_from_input_list(fin, False)

            while json_in_2:
                with open(json_in_2, "r") as fin1:
                    grammar_dict_2 = json.load(fin1)

                xlsx_in_2 = cls.__read_line_from_input_list(fin)
                (
                    wb2_r1_values,
                    wb2_r2_values,
                    wb2_r3_values,
                    wb2_r4_values,
                ) = cls.__read_xlsx(xlsx_in_2)
                weights_2 = {
                    "r1": wb2_r1_values,
                    "r2": wb2_r2_values,
                    "r3": wb2_r3_values,
                    "r4": wb2_r4_values,
                }
                union_dict, union_dict_weights = cls.__union_json(
                    union_dict, grammar_dict_2, union_dict_weights, weights_2, method
                )

                json_in_2 = cls.__read_line_from_input_list(fin, False)

        with open(output_filename, "w") as fout:
            json.dump(union_dict, fout)

        global assignments_made
        print(json.dumps(assignments_made, indent=4))


if __name__ == "__main__":
    args = vars(UnionDict.get_args())
    UnionDict.intersect_symbol_json(
        args.get("input_file_list", None), args.get("output_prefix", "out")
    )
    UnionDict.intersect_region_json(
        args.get("input_file_list", None), args.get("output_prefix", "out")
    )
    UnionDict.union_json(
        args.get("input_file_list", None), args.get("output_prefix", "out")
    )
