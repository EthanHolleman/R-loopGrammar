import multiprocessing
import importlib
import sys
import os
import glob
import pathlib
import dataclasses

#15, and 21, complete 10 runs.
#consult with Gina reguarding outliers.
#run p18, w3 on pfc8, also increase training set size

from typing import *

region_extractor = importlib.import_module("01_regions_extractor")
region_threshold = importlib.import_module("02_regions_threshold")
training_set = importlib.import_module("03_training_set")
grammar_dict = importlib.import_module("04_grammar_dict")
grammar_word = importlib.import_module("06_grammar_word")
grammar_training = importlib.import_module("06_grammar_training")
probabilistic_language = importlib.import_module("07_probabilistic_language")
in_loop_probs = importlib.import_module("08_in_loop_probs")

PLASMID = "pFC53"
WINDOW_LENGTH = 5
TRAINING_SET_LINES = 63
START_INDEX = 1
END_INDEX = 1929

class SupressOutput:
    def __init__(self):
        pass

    def __enter__(self):
        sys.stdout = open(os.devnull, "w")

    def __exit__(self, type, value, traceback):
        sys.stdout = sys.__stdout__


@dataclasses.dataclass
class WorkflowParameters:
    run_number: int
    plasmid: str
    window_length: int
    padding_length: int
    training_set_size: int
    start_index: int
    end_index: int


def do_workflow(workflow_parameters: WorkflowParameters) -> None:
    run_number, plasmid, window_length, padding_length, training_set_size, start_index, end_index = \
        dataclasses.astuple(workflow_parameters)

    #TODO: RUN_NUMBER IN EACH FILENAME
    print("RUNNING", dataclasses.astuple(workflow_parameters))
    print(f"[{padding_length}] Running with padding value: {padding_length}")
    print(f"[{padding_length}] Extracting regions...")

    bed_extra_filename = f"{plasmid}_SUPERCOILED_p{padding_length}_w{window_length}_{run_number}.bed_extra.bed"
    weight_xlsx_filename = f"{plasmid}_SUPERCOILED_p{padding_length}_w{window_length}_{run_number}_weight.xlsx"
    weight_shannon_entropy_xlsx_filename = f"{plasmid}_SUPERCOILED_p{padding_length}_w{window_length}_{run_number}_weight_shannon.xlsx"
    bed_extra_training_set_filename = f"{plasmid}_SUPERCOILED_p{padding_length}_w{window_length}_{run_number}.bed_extra_training-set.bed"
    dict_shannon_xlsx_filename = f"{plasmid}_SUPERCOILED_p{padding_length}_w{window_length}_{run_number}_DICT_SHANNON.xlsx"
    dict_shannon_json_filename = f"{plasmid}_SUPERCOILED_p{padding_length}_w{window_length}_{run_number}_DICT_SHANNON.xlsx.json"
    all_rloops_filename = f"{plasmid}_all_rloops_WORDS_SHANNON_p{padding_length}_w{window_length}_{run_number}.txt"
    training_set_words_filename = f"{plasmid}_SUPERCOILED_p{padding_length}_w{window_length}_{run_number}_training-set_WORDS_SHANNON.txt"
    probabilities_filename = f"{plasmid}_SHANNON_p{padding_length}_w{window_length}_{run_number}_probabilities.py"
    probabilities_filename_no_py = probabilities_filename[:-3]
    prob_lang_filename = f"{plasmid}_SHANNON_p{padding_length}_w{window_length}_{run_number}_prob_lang.py"
    base_in_loop_no_xlsx = f"{plasmid}_SHANNON_p{padding_length}_w{window_length}_{run_number}_base_in_loop"

    region_extractor.RegionsExtractor.extract_regions(
        f"{plasmid}.fa",
        f"{plasmid}_SUPERCOILED.bed",
        start_index,
        end_index,
        window_length,
    weight_xlsx_filename,
        4,
        padding=padding_length,
        bed_extra=True,
        bed_extra_output=bed_extra_filename
    )

    print(f"[{padding_length}] Region threshold...")
    # TODO: Fix extension in regions_threshold.
    region_threshold.RegionsThreshold.extract_regions(
        weight_xlsx_filename,
        weight_shannon_entropy_xlsx_filename,
        True  # Shannon Entropy
    )

    print(f"[{padding_length}] Creating training set...")
    training_set.TrainingSet.training_set(
        bed_extra_filename,
        training_set_size,
        bed_extra_training_set_filename
    )

    print(f"[{padding_length}] Creating dictionary...")
    grammar_dict.GrammarDict.extract_regions(
        f"{plasmid}.fa",
        bed_extra_training_set_filename,
        weight_xlsx_filename,
        start_index,
        end_index,
        window_length,
        weight_shannon_entropy_xlsx_filename,
        dict_shannon_xlsx_filename
    )

    if not pathlib.Path(all_rloops_filename).is_file():
        print(f"[{padding_length}] Extracting all words...")
        grammar_word.GrammarWord.extract_word(
            f"{plasmid}.fa",
            f"{plasmid}_all_rloops.bed",
            dict_shannon_json_filename,
            start_index,
            end_index,
            window_length,
            all_rloops_filename
        )

    print(f"[{padding_length}] Extracting training set words...")
    grammar_word.GrammarWord.extract_word(
        f"{plasmid}.fa",
        bed_extra_training_set_filename,
        dict_shannon_json_filename,
        start_index,
        end_index,
        window_length,
        training_set_words_filename
    )

    print(f"[{padding_length}] Finding probabilities...")
    grammar_training.GrammarTraining.find_probabilities(
        training_set_words_filename,
        probabilities_filename
    )

    print(f"[{padding_length}] Finding word probabilities...")

    with SupressOutput():
        probabilistic_language.Probabilistic_Language.word_probabilities(
            all_rloops_filename, # Probably don't need multiple copies of this?
            probabilities_filename_no_py,
            prob_lang_filename
        )

    print(f"[{padding_length}] In loop probabilities...")

    with SupressOutput():
        in_loop_probs.Loop_probabilities.in_loop_probabilities(
            all_rloops_filename,
            end_index - start_index,
            prob_lang_filename,
            base_in_loop_no_xlsx
        )

    local_dir = pathlib.Path('.')
    files = local_dir.glob(f'*_p{padding_length}_w{window_length}_{run_number}*')
    folder_name = f'{plasmid}_p{padding_length}_w{window_length}_{run_number}'

    try:
        os.mkdir(folder_name)
    except FileExistsError:
        pass

    for file in files:
        if file.is_file():
            os.rename(file, local_dir / folder_name / file)


def main() -> None:
    """
    runs = [
        WorkflowParameters(
            r,
            PLASMID,
            WINDOW_LENGTH,
            p,
            TRAINING_SET_LINES,
            START_INDEX,
            END_INDEX
        ) for r in range(10) for p in [15]
    ]

    with multiprocessing.Pool(1) as pool:
        pool.map(do_workflow, runs)
    """

    for r in range(10):
        for p in [15]:
            do_workflow(WorkflowParameters(
                r,
                PLASMID,
                WINDOW_LENGTH,
                p,
                TRAINING_SET_LINES,
                START_INDEX,
                END_INDEX
            ))


if __name__ == "__main__":
    main()
