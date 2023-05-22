import multiprocessing
import sys
import os
import pathlib
import dataclasses
import json
import configparser
import logging
import argparse

from typing import *

import rloopgrammar.model.union_dict as union_dict
import rloopgrammar.model.grammar_word as grammar_word
import rloopgrammar.model.grammar_training as grammar_training

from rloopgrammar.config_reader import read_plasmids
from rloopgrammar.config_reader import Plasmid

NUMBER_OF_PROCESSES = 10

CONFIG_UNION_PARAMETER_NAME = "Union Parameters"
CONFIG_MODEL_PARAMETER_NAME = "Model Parameters"

PROGRAM_NAME = pathlib.Path(sys.argv[0]).parts[-1][:-4]
DESCRIPTION = "Build a hybrid model based off the union of two dictionaries."


class SupressOutput:
    def __init__(self):
        pass

    def __enter__(self):
        sys.stdout = open(os.devnull, "w")

    def __exit__(self, type, value, traceback):
        sys.stdout = sys.__stdout__


@dataclasses.dataclass
class UnionParameters:
    union_collection_folder: pathlib.Path
    plasmid_1: Plasmid
    plasmid_2: Plasmid
    plasmid_1_model_folder: pathlib.Path
    plasmid_2_model_folder: pathlib.Path
    window_length: int
    padding_length: int


def build_union_model(up: UnionParameters) -> None:
    run_number = up.plasmid_1_model_folder.parts[-1].split("_")[-1]
    run_folder = (
        up.union_collection_folder
        / f"UnionModel_{up.plasmid_1.name}_{up.plasmid_2.name}_p{up.padding_length}_w{up.window_length}_{run_number}"
    )

    print(f"Building Union Model {run_number}")

    os.mkdir(run_folder)

    plasmid_1_model_files = next(os.walk(up.plasmid_1_model_folder))[2]
    plasmid_2_model_files = next(os.walk(up.plasmid_2_model_folder))[2]

    plasmid_1_model_files_find = lambda y: list(
        filter(lambda x: y in x, plasmid_1_model_files)
    )[0]
    plasmid_2_model_files_find = lambda y: list(
        filter(lambda x: y in x, plasmid_2_model_files)
    )[0]

    print(f"Finding files {run_number}")

    bed_extra_training_set_filename_1 = (
        up.plasmid_1_model_folder
        / plasmid_1_model_files_find("bed_extra_training-set.bed")
    )
    bed_extra_training_set_filename_2 = (
        up.plasmid_2_model_folder
        / plasmid_2_model_files_find("bed_extra_training-set.bed")
    )

    dict_shannon_xlsx_filename_1 = (
        up.plasmid_1_model_folder / plasmid_1_model_files_find("DICT_SHANNON.xlsx")
    )
    dict_shannon_json_filename_1 = (
        up.plasmid_1_model_folder / plasmid_1_model_files_find("DICT_SHANNON.xlsx.json")
    )

    dict_shannon_xlsx_filename_2 = (
        up.plasmid_2_model_folder / plasmid_2_model_files_find("DICT_SHANNON.xlsx")
    )
    dict_shannon_json_filename_2 = (
        up.plasmid_2_model_folder / plasmid_2_model_files_find("DICT_SHANNON.xlsx.json")
    )

    union_dict_name = run_folder / (
        f"out_union_w{up.window_length}_p{up.padding_length}_union.DICT_SHANNON.xlsx.json"
    )

    training_set_words_filename_1 = str(
        run_folder
        / f"{up.plasmid_1.name}_union_p{up.padding_length}_w{up.window_length}_{run_number}_training-set_WORDS_SHANNON.txt"
    )
    training_set_words_filename_2 = str(
        run_folder
        / f"{up.plasmid_2.name}_union_p{up.padding_length}_w{up.window_length}_{run_number}_training-set_WORDS_SHANNON.txt"
    )
    probabilities_filename_1 = str(
        run_folder
        / f"{up.plasmid_1.name}_union_SHANNON_p{up.padding_length}_w{up.window_length}_{run_number}_probabilities.json"
    )
    probabilities_filename_2 = str(
        run_folder
        / f"{up.plasmid_2.name}_union_SHANNON_p{up.padding_length}_w{up.window_length}_{run_number}_probabilities.json"
    )
    av_probabilities_filename = str(
        run_folder
        / f"SHANNON_p{up.padding_length}_w{up.window_length}_{run_number}_union_probabilities.json"
    )

    union_input_file = str(
        run_folder
        / f"{up.plasmid_1.name}_{up.plasmid_2.name}_union_w{up.window_length}_p{up.padding_length}_{run_number}_input.txt"
    )

    print("Unioning dictionaries.")

    with open(
        union_input_file,
        "w",
    ) as file_handle:
        file_handle.write(f"{dict_shannon_json_filename_1}\n")
        file_handle.write(f"{dict_shannon_xlsx_filename_1}\n")
        file_handle.write(f"{dict_shannon_json_filename_2}\n")
        file_handle.write(f"{dict_shannon_xlsx_filename_2}\n")

    union_dict.UnionDict.union_json(union_input_file, output_filename=union_dict_name)

    print("Extracting training set 1 words.")

    grammar_word.GrammarWord.extract_word(
        up.plasmid_1.fasta_file,
        bed_extra_training_set_filename_1,
        union_dict_name,
        up.plasmid_1.gene_start,
        up.plasmid_1.gene_end,
        up.window_length,
        training_set_words_filename_1,
    )

    print("Extracting training set 2 words.")

    grammar_word.GrammarWord.extract_word(
        up.plasmid_2.fasta_file,
        bed_extra_training_set_filename_2,
        union_dict_name,
        up.plasmid_2.gene_start,
        up.plasmid_2.gene_end,
        up.window_length,
        training_set_words_filename_2,
    )

    print("Finding probabilities 1.")

    grammar_training.GrammarTraining.find_probabilities(
        training_set_words_filename_1, up.window_length, probabilities_filename_1
    )

    print("Finding probabilities 2.")

    grammar_training.GrammarTraining.find_probabilities(
        training_set_words_filename_2, up.window_length, probabilities_filename_2
    )

    # CREATE FILE WITH AVERAGE PROBABILITIES
    print(f"Finding average probabilities.")

    with open(probabilities_filename_1, "r", encoding="utf-8") as file_handle:
        probabilities_1 = json.load(file_handle)

    with open(probabilities_filename_2, "r", encoding="utf-8") as file_handle:
        probabilities_2 = json.load(file_handle)

    for k, v in probabilities_1.items():
        if "probabilities" in k:
            for l, b in v.items():
                probabilities_2[k][l] = (probabilities_2[k][l] + b) / 2

    with open(av_probabilities_filename, "w") as fout:
        json.dump(probabilities_2, fout)


parser = argparse.ArgumentParser(prog=PROGRAM_NAME, description=DESCRIPTION)
parser.add_argument("output_folder")
parser.add_argument("-i", "--input_folders", type=str, nargs="+")


def main() -> None:
    args = parser.parse_args()

    plasmids = read_plasmids()

    model_folder_name_tuples = [args.input_folders]

    for model_folder_tuple in model_folder_name_tuples:
        model1_config = configparser.ConfigParser()
        model1_config.read(pathlib.Path(model_folder_tuple[0]) / "model_settings.ini")

        model2_config = configparser.ConfigParser()
        model2_config.read(pathlib.Path(model_folder_tuple[1]) / "model_settings.ini")

        plasmid_name_tuple = (
            model1_config[CONFIG_MODEL_PARAMETER_NAME]["PLASMID"],
            model2_config[CONFIG_MODEL_PARAMETER_NAME]["PLASMID"],
        )

        assert (
            model1_config[CONFIG_MODEL_PARAMETER_NAME]["WindowLength"]
            == model2_config[CONFIG_MODEL_PARAMETER_NAME]["WindowLength"]
        ), f"{model_folder_tuple[0]} model settings do not match {model_folder_tuple[1]}."

        assert (
            model1_config[CONFIG_MODEL_PARAMETER_NAME]["Padding"]
            == model2_config[CONFIG_MODEL_PARAMETER_NAME]["Padding"]
        ), f"{model_folder_tuple[0]} model settings do not match {model_folder_tuple[1]}."

        window_length = int(model1_config[CONFIG_MODEL_PARAMETER_NAME]["WindowLength"])
        padding_length = int(model1_config[CONFIG_MODEL_PARAMETER_NAME]["Padding"])

        plasmid_tuple: list[Plasmid] = [
            list(filter(lambda x: x.name == k, plasmids))[0] for k in plasmid_name_tuple
        ]

        # sort by the run number
        model1_folders = sorted(
            [x[1] for x in os.walk(model_folder_tuple[0])][0],
            key=lambda x: int(x.split("_")[-1]),
        )
        model2_folders = sorted(
            [x[1] for x in os.walk(model_folder_tuple[1])][0],
            key=lambda x: int(x.split("_")[-1]),
        )

        assert len(model1_folders) == len(
            model2_folders
        ), "Model folder lengths don't match"

        union_model_collection_folder = pathlib.Path(args.output_folder)
        os.mkdir(union_model_collection_folder)

        run_config = configparser.ConfigParser()
        run_config[CONFIG_MODEL_PARAMETER_NAME] = {}
        run_config[CONFIG_MODEL_PARAMETER_NAME][
            "Plasmids"
        ] = f"{plasmid_name_tuple[0]} {plasmid_name_tuple[1]}"
        run_config[CONFIG_MODEL_PARAMETER_NAME]["WindowLength"] = str(window_length)
        run_config[CONFIG_MODEL_PARAMETER_NAME]["Padding"] = str(padding_length)
        run_config[CONFIG_MODEL_PARAMETER_NAME]["NumberOfModels"] = str(
            len(model1_folders)
        )

        with open(
            union_model_collection_folder / "model_settings.ini", "w"
        ) as configfile:
            run_config.write(configfile)

        union_runs: list[UnionParameters] = []
        for run_folder_tuple in zip(model1_folders, model2_folders):
            union_runs.append(
                UnionParameters(
                    union_collection_folder=union_model_collection_folder,
                    plasmid_1=plasmid_tuple[0],
                    plasmid_2=plasmid_tuple[1],
                    plasmid_1_model_folder=pathlib.Path(model_folder_tuple[0])
                    / run_folder_tuple[0],
                    plasmid_2_model_folder=pathlib.Path(model_folder_tuple[1])
                    / run_folder_tuple[1],
                    window_length=window_length,
                    padding_length=padding_length,
                )
            )

        with multiprocessing.Pool(NUMBER_OF_PROCESSES) as pool:
            pool.map(build_union_model, union_runs)


if __name__ == "__main__":
    main()
