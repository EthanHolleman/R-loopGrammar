import multiprocessing
import sys
import os
import pathlib
import dataclasses
import configparser
import logging
import argparse

from typing import *

NUMBER_OF_PROCESSES = 10

import rloopgrammar.model.grammar_word as grammar_word
import rloopgrammar.model.probabilistic_language as probabilistic_language
import rloopgrammar.model.in_loop_probs as in_loop_probs

from rloopgrammar.config_reader import read_plasmids
from rloopgrammar.config_reader import Plasmid

CONFIG_MODEL_PARAMETER_NAME = "Model Parameters"
CONFIG_PREDICT_PARAMETER_NAME = "Predict Parameters"

PROGRAM_NAME = pathlib.Path(sys.argv[0]).parts[-1][:-4]
DESCRIPTION = "Form a prediction for a given collection of R-loop grammar models."


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
class PredictionParameters:
    model_folder: pathlib.Path
    prediction_collection_folder: pathlib.Path
    plasmid: Plasmid
    window_length: int
    padding_length: int


def do_prediction(pp: PredictionParameters) -> None:
    plot_region = pp.plasmid.gene_start + pp.plasmid.gene_end
    print(pp.plasmid.gene_start, pp.plasmid.gene_end, plot_region)

    run_folder = pp.prediction_collection_folder / str(
        pp.model_folder.parts[-1]
    ).replace("Model", "Prediction")

    try:
        os.mkdir(run_folder)
    except FileExistsError:
        pass

    logging.basicConfig(
        filename=pp.prediction_collection_folder / "prediction_log.txt",
        format=f"%(asctime)s [{pp.model_folder.parts[-1][-1]}] - %(message)s",
        level=logging.DEBUG,
    )

    logger = logging.getLogger("r-loop_grammar")
    logger.info(dataclasses.asdict(pp))

    model_files = next(os.walk(pp.model_folder))[2]

    model_files_find = lambda y: list(filter(lambda x: y in x, model_files))[0]

    all_rloops_bed_filename = (
        pp.prediction_collection_folder
        / f"{pp.plasmid.name}_w{pp.window_length}_all_rloops.bed"
    )

    dict_shannon_json_filename = str(
        pp.model_folder / model_files_find("DICT_SHANNON.xlsx.json")
    )
    probabilities_filename = str(
        pp.model_folder / model_files_find("probabilities.json")
    )

    all_rloops_filename = str(
        run_folder
        / f"{pp.plasmid.name}_SHANNON_p{pp.padding_length}_w{pp.window_length}_all_rloops_WORDS_SHANNON"
    )

    prob_lang_filename = str(
        run_folder
        / f"{pp.plasmid.name}_SHANNON_p{pp.padding_length}_w{pp.window_length}_prob_lang.py"
    )
    base_in_loop_no_xlsx = str(
        run_folder
        / f"{pp.plasmid.name}_SHANNON_p{pp.padding_length}_w{pp.window_length}_base_in_loop"
    )

    if not pathlib.Path(all_rloops_bed_filename).is_file():
        with open(all_rloops_bed_filename, "w") as file_handle:
            for x in range(
                pp.plasmid.gene_start + pp.window_length,
                pp.plasmid.gene_end - 2 * pp.window_length,
            ):
                for y in range(
                    x + pp.window_length, pp.plasmid.gene_end - pp.window_length
                ):
                    if (y - x) % pp.window_length == 0:
                        file_handle.write(f"{pp.plasmid.name}\t{x}\t{y}\n")

    logger.info("Finding word probabilities.")

    if not pathlib.Path(all_rloops_filename).is_file():
        logger.info("Extracting all words.")
        grammar_word.GrammarWord.extract_word(
            pp.plasmid.fasta_file,
            all_rloops_bed_filename,
            dict_shannon_json_filename,
            pp.plasmid.gene_start,
            pp.plasmid.gene_end,
            pp.window_length,
            str(all_rloops_filename),
        )

    with SupressOutput():
        probabilistic_language.Probabilistic_Language.word_probabilities(
            all_rloops_filename,
            probabilities_filename,
            pp.window_length,
            str(prob_lang_filename),
        )

    logger.info("In loop probabilities.")

    with SupressOutput():
        in_loop_probs.Loop_probabilities.in_loop_probabilities(
            all_rloops_filename,
            all_rloops_bed_filename,
            plot_region,
            pp.plasmid.gene_start,
            pp.plasmid.gene_end,
            prob_lang_filename,
            pp.window_length,
            str(base_in_loop_no_xlsx),
        )


parser = argparse.ArgumentParser(prog=PROGRAM_NAME, description=DESCRIPTION)
parser.add_argument("output_folder")
parser.add_argument("-i", "--input_folder", type=str)
parser.add_argument("--plasmids", type=str, nargs="+")


def main() -> None:
    args = parser.parse_args()

    plasmids = read_plasmids()

    model_collection_folder = pathlib.Path(args.input_folder)
    predict_plasmid_names = args.plasmids

    model_folders = [x[1] for x in os.walk(model_collection_folder)][0]

    model_config = configparser.ConfigParser()
    model_config.read(model_collection_folder / "model_settings.ini")

    window_length = int(model_config[CONFIG_MODEL_PARAMETER_NAME]["WindowLength"])
    padding = int(model_config[CONFIG_MODEL_PARAMETER_NAME]["Padding"])
    original_plasmid = model_config[CONFIG_MODEL_PARAMETER_NAME].get("Plasmid", None)

    predict_plasmids: list[Plasmid] = [
        list(filter(lambda x: x.name == k, plasmids))[0] for k in predict_plasmid_names
    ]

    for plasmid in predict_plasmids:
        runs = []

        prediction_folder = build_output_folder_name(
            args.output_folder,
            original_plasmid=original_plasmid,
            predict_plasmid=plasmid.name,
            padding=padding,
            width=window_length,
            number_of_models=len(model_folders),
        )
        os.mkdir(prediction_folder)

        for model_folder in model_folders:
            relative_path_model_folder = model_collection_folder / model_folder

            runs.append(
                PredictionParameters(
                    relative_path_model_folder,
                    prediction_folder,
                    plasmid,
                    window_length,
                    padding,
                )
            )

        with multiprocessing.Pool(NUMBER_OF_PROCESSES) as pool:
            pool.map(do_prediction, runs)


if __name__ == "__main__":
    main()
