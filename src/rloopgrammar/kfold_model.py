import multiprocessing
import sys
import os
import pathlib
import dataclasses
import configparser
import math
import random
import logging
import argparse
import shutil

from typing import *

NUMBER_OF_PROCESSES = 10

import rloopgrammar.model.regions_extractor as region_extractor
import rloopgrammar.model.regions_threshold as region_threshold
import rloopgrammar.model.training_set as training_set
import rloopgrammar.model.grammar_dict as grammar_dict
import rloopgrammar.model.grammar_word as grammar_word
import rloopgrammar.model.grammar_training as grammar_training

from rloopgrammar.config_reader import read_plasmids
from rloopgrammar.config_reader import Plasmid

CONFIG_MODEL_PARAMETER_NAME = "Model Parameters"

PROGRAM_NAME = pathlib.Path(sys.argv[0]).parts[-1][:-4]
DESCRIPTION = "Build a collection of R-loop grammar models using k-folds."


def build_output_folder_name(output_folder_name, **kwargs):
    for key, value in kwargs.items():
        output_folder_name = output_folder_name.replace(f"%{key}", str(value))

    return pathlib.Path(output_folder_name)


class SupressOutput:
    def __init__(self):
        pass

    def __enter__(self):
        sys.stdout = open(os.devnull, "w")

    def __exit__(self, type, value, traceback):
        sys.stdout = sys.__stdout__


@dataclasses.dataclass
class ModelParameters:
    parent_folder: pathlib.Path
    folds: int
    fold_number: int
    plasmid: Plasmid
    window_length: int
    padding_length: int
    seed_file: pathlib.Path


def build_model(mp: ModelParameters) -> None:
    run_folder = (
        mp.parent_folder
        / f"Model_{mp.plasmid.name}_p{mp.padding_length}_w{mp.window_length}_{mp.fold_number}"
    )

    try:
        os.mkdir(run_folder)
    except FileExistsError:
        pass

    logging.basicConfig(
        filename=mp.parent_folder / "model_build_log.txt",
        format=f"%(asctime)s [{mp.fold_number}] - %(message)s",
        level=logging.DEBUG,
    )
    logger = logging.getLogger("r-loop_grammar")

    logger.info(dataclasses.asdict(mp))
    logger.info(f"Extracting critical regions.")

    with open(mp.seed_file, "rb") as seed_file_handle:
        seed = seed_file_handle.read()

    random.seed(seed)

    bed_extra_filename = str(
        run_folder
        / f"{mp.plasmid.name}_p{mp.padding_length}_w{mp.window_length}_{mp.fold_number}.bed_extra.bed"
    )
    weight_xlsx_filename = str(
        run_folder
        / f"{mp.plasmid.name}_p{mp.padding_length}_w{mp.window_length}_{mp.fold_number}_weight.xlsx"
    )
    weight_shannon_entropy_xlsx_filename = str(
        run_folder
        / f"{mp.plasmid.name}_p{mp.padding_length}_w{mp.window_length}_{mp.fold_number}_weight_shannon.xlsx"
    )
    bed_extra_training_set_filename = str(
        run_folder
        / f"{mp.plasmid.name}_p{mp.padding_length}_w{mp.window_length}_{mp.fold_number}.bed_extra_training-set.bed"
    )
    bed_extra_test_set_filename = str(
        run_folder
        / f"{mp.plasmid.name}_p{mp.padding_length}_w{mp.window_length}_{mp.fold_number}.bed_extra_test-set.bed"
    )
    dict_shannon_xlsx_filename = str(
        run_folder
        / f"{mp.plasmid.name}_p{mp.padding_length}_w{mp.window_length}_{mp.fold_number}_DICT_SHANNON.xlsx"
    )
    dict_shannon_json_filename = str(
        run_folder
        / f"{mp.plasmid.name}_p{mp.padding_length}_w{mp.window_length}_{mp.fold_number}_DICT_SHANNON.xlsx.json"
    )
    training_set_words_filename = str(
        run_folder
        / f"{mp.plasmid.name}_p{mp.padding_length}_w{mp.window_length}_{mp.fold_number}_training-set_WORDS_SHANNON.txt"
    )
    probabilities_filename = str(
        run_folder
        / f"{mp.plasmid.name}_SHANNON_p{mp.padding_length}_w{mp.window_length}_{mp.fold_number}_probabilities.json"
    )

    with SupressOutput():
        region_extractor.RegionsExtractor.extract_regions(
            mp.plasmid.fasta_file,
            mp.plasmid.bed_file,
            mp.plasmid.gene_start,
            mp.plasmid.gene_end,
            window_length=mp.window_length,
            num_regions=4,
            padding=mp.padding_length,
            bed_extra=True,
            bed_extra_output=bed_extra_filename,
            create_weights=False,
        )

    logger.info(f"Creating {mp.fold_number} training set.")
    with open(bed_extra_filename, "r") as fin:
        lines = fin.readlines()

    random.shuffle(lines)

    test_size = math.ceil(len(lines) * (1 / mp.folds))
    nfold_test_sets = [
        lines[i : min(i + test_size, len(lines))]
        for i in range(0, len(lines), test_size)
    ]

    nfold_train_sets = [
        nfold_test_sets[i] for i in range(len(nfold_test_sets)) if i != mp.fold_number
    ]

    nfold_training_set = sum(nfold_train_sets, [])
    with open(bed_extra_training_set_filename, "w") as fout:
        fout.writelines(nfold_training_set)
    with open(bed_extra_test_set_filename, "w") as fout:
        fout.writelines(nfold_test_sets[mp.fold_number])

    with SupressOutput():
        region_extractor.RegionsExtractor.extract_regions(
            mp.plasmid.fasta_file,
            bed_extra_training_set_filename,
            mp.plasmid.gene_start,
            mp.plasmid.gene_end,
            window_length=mp.window_length,
            out_pref=weight_xlsx_filename,
            num_regions=4,
            padding=mp.padding_length,
            bed_extra=False,
            create_weights=True,
        )

    logger.info("Thresholding critical regions.")

    with SupressOutput():
        region_threshold.RegionsThreshold.extract_regions(
            weight_xlsx_filename,
            weight_shannon_entropy_xlsx_filename,
            True,  # Shannon Entropy
        )

    logger.info("Creating dictionary.")

    with SupressOutput():
        grammar_dict.GrammarDict.extract_regions(
            mp.plasmid.fasta_file,
            bed_extra_training_set_filename,
            weight_xlsx_filename,
            mp.plasmid.gene_start,
            mp.plasmid.gene_end,
            mp.window_length,
            weight_shannon_entropy_xlsx_filename,
            dict_shannon_xlsx_filename,
        )

    logger.info("Extracting training set words.")

    with SupressOutput():
        grammar_word.GrammarWord.extract_word(
            mp.plasmid.fasta_file,
            bed_extra_training_set_filename,
            dict_shannon_json_filename,
            mp.plasmid.gene_start,
            mp.plasmid.gene_end,
            mp.window_length,
            training_set_words_filename,
        )

    logger.info("Finding probabilities.")
    grammar_training.GrammarTraining.find_probabilities(
        training_set_words_filename, mp.window_length, probabilities_filename
    )


parser = argparse.ArgumentParser(prog=PROGRAM_NAME, description=DESCRIPTION)
parser.add_argument("output_folder")
parser.add_argument("-f", "--folds", type=int, default=3)
parser.add_argument("-p", "--paddings", type=int, nargs="+", default=[13])
parser.add_argument("-w", "--width", type=int, default=4)
parser.add_argument("--plasmids", type=str, nargs="+")


def main() -> None:
    args = parser.parse_args()
    print(args)

    plasmids = read_plasmids()

    window_length = args.width
    number_of_folds = args.folds
    paddings = args.paddings
    model_plasmid_names = args.plasmids

    model_plasmids: list[Plasmid] = [
        list(filter(lambda x: x.name == k, plasmids))[0] for k in model_plasmid_names
    ]

    for plasmid in model_plasmids:
        for padding in paddings:
            parent_folder = build_output_folder_name(
                args.output_folder,
                plasmid=plasmid.name,
                padding=padding,
                width=window_length,
                number_of_folds=number_of_folds,
            )
            os.mkdir(parent_folder)

            random_seed = os.urandom(32)
            with open(parent_folder / "random_seed", "wb") as seedfile:
                seedfile.write(random_seed)

            run_config = configparser.ConfigParser()
            run_config[CONFIG_MODEL_PARAMETER_NAME] = {}
            run_config[CONFIG_MODEL_PARAMETER_NAME]["Plasmid"] = plasmid.name
            run_config[CONFIG_MODEL_PARAMETER_NAME]["WindowLength"] = str(window_length)
            run_config[CONFIG_MODEL_PARAMETER_NAME]["Padding"] = str(padding)
            run_config[CONFIG_MODEL_PARAMETER_NAME]["NumberOfFolds"] = str(
                number_of_folds
            )

            with open(parent_folder / "model_settings.ini", "w") as configfile:
                run_config.write(configfile)

        runs = [
            ModelParameters(
                parent_folder,
                number_of_folds,
                fold_number,
                plasmid,
                window_length,
                padding,
                parent_folder / "random_seed",
            )
            for fold_number in range(number_of_folds)
            for padding in paddings
        ]

        with multiprocessing.Pool(NUMBER_OF_PROCESSES) as pool:
            pool.map(build_model, runs)


if __name__ == "__main__":
    main()
