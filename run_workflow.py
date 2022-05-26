import multiprocessing
import importlib
import sys
import os
import glob
import pathlib
import dataclasses
import configparser
import shutil

from typing import *

NUMBER_OF_PROCESSES = 5

RIGHT_PADDING = 100
LEFT_PADDING = 80

region_extractor = importlib.import_module("01_regions_extractor")
region_threshold = importlib.import_module("02_regions_threshold")
training_set = importlib.import_module("03_training_set")
grammar_dict = importlib.import_module("04_grammar_dict")
grammar_word = importlib.import_module("06_grammar_word")
grammar_training = importlib.import_module("06_grammar_training")
probabilistic_language = importlib.import_module("07_probabilistic_language")
in_loop_probs = importlib.import_module("08_in_loop_probs")

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
    run_number, plasmid, window_length, padding_length, \
    training_set_size, start_index, end_index = \
        dataclasses.astuple(workflow_parameters)

    print("RUNNING", dataclasses.astuple(workflow_parameters))
    print(f"[{padding_length}] Running with padding value: {padding_length}")
    print(f"[{padding_length}] Extracting regions...")


    plot_start = start_index
    plot_end = end_index
    plot_region = RIGHT_PADDING + end_index

    all_rloops_bed_filename = f"{plasmid}_w{window_length}_all_rloops.bed"
    bed_extra_filename = f"{plasmid}_p{padding_length}_w{window_length}_{run_number}.bed_extra.bed"
    weight_xlsx_filename = f"{plasmid}_p{padding_length}_w{window_length}_{run_number}_weight.xlsx"
    weight_shannon_entropy_xlsx_filename = f"{plasmid}_p{padding_length}_w{window_length}_{run_number}_weight_shannon.xlsx"
    bed_extra_training_set_filename = f"{plasmid}_p{padding_length}_w{window_length}_{run_number}.bed_extra_training-set.bed"
    dict_shannon_xlsx_filename = f"{plasmid}_p{padding_length}_w{window_length}_{run_number}_DICT_SHANNON.xlsx"
    dict_shannon_json_filename = f"{plasmid}_p{padding_length}_w{window_length}_{run_number}_DICT_SHANNON.xlsx.json"
    all_rloops_filename = f"{plasmid}_all_rloops_WORDS_SHANNON_p{padding_length}_w{window_length}_{run_number}.txt"
    training_set_words_filename = f"{plasmid}_p{padding_length}_w{window_length}_{run_number}_training-set_WORDS_SHANNON.txt"
    probabilities_filename = f"{plasmid}_SHANNON_p{padding_length}_w{window_length}_{run_number}_probabilities.py"
    probabilities_filename_no_py = probabilities_filename[:-3]
    prob_lang_filename = f"{plasmid}_SHANNON_p{padding_length}_w{window_length}_{run_number}_prob_lang.py"
    base_in_loop_no_xlsx = f"{plasmid}_SHANNON_p{padding_length}_w{window_length}_{run_number}_base_in_loop"

    if not pathlib.Path(all_rloops_bed_filename).is_file():
        with open(all_rloops_bed_filename, "w") as file_handle:
            for x in range(80 + window_length, end_index - 2 * window_length):
                for y in range(x + window_length, end_index - window_length):
                    if (y - x) % window_length == 0:
                        file_handle.write(f"{plasmid}\t{x}\t{y}\n")

    region_extractor.RegionsExtractor.extract_regions(
        f"{plasmid}.fa",
        f"{plasmid}.bed",
        start_index,
        end_index,
        window_length=window_length,
        num_regions=4,
        padding=padding_length,
        bed_extra=True,
        bed_extra_output=bed_extra_filename,
        create_weights=False
    )

    print(f"[{padding_length}] Creating training set...")
    training_set.TrainingSet.training_set(
        bed_extra_filename,
        training_set_size,
        bed_extra_training_set_filename
    )

    region_extractor.RegionsExtractor.extract_regions(
        f"{plasmid}.fa",
        bed_extra_training_set_filename,
        start_index,
        end_index,
        window_length=window_length,
        out_pref=weight_xlsx_filename,
        num_regions=4,
        padding=padding_length,
        bed_extra=False,
        create_weights=True
    )

    print(f"[{padding_length}] Region threshold...")
    # TODO: Fix extension in regions_threshold.
    region_threshold.RegionsThreshold.extract_regions(
        weight_xlsx_filename,
        weight_shannon_entropy_xlsx_filename,
        True  # Shannon Entropy
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
            f"{plasmid}_w{window_length}_all_rloops.bed",
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
        window_length,
        probabilities_filename
    )

    print(f"[{padding_length}] Finding word probabilities...")

    with SupressOutput():
        probabilistic_language.Probabilistic_Language.word_probabilities(
            all_rloops_filename, # Probably don't need multiple copies of this?
            probabilities_filename_no_py,
            window_length,
            prob_lang_filename
        )

    print(f"[{padding_length}] In loop probabilities...")

    with SupressOutput():
        in_loop_probs.Loop_probabilities.in_loop_probabilities(
            all_rloops_filename,
            f"{plasmid}_w{window_length}_all_rloops.bed",
            plot_region,
            start_index,
            end_index,
            prob_lang_filename,
            window_length,
            base_in_loop_no_xlsx
        )

    local_dir = pathlib.Path('.')
    files = local_dir.glob(f'*_p{padding_length}_w{window_length}_{run_number}*')
    folder_name = f'{plasmid}_p{padding_length}_w{window_length}_{run_number}'

    try:
        os.mkdir(folder_name)
    except FileExistsError:
        pass

    try:
        for file in files:
            if file.is_file():
                os.rename(file, local_dir / folder_name / file)
    except Exception as e:
        print(e)


def main() -> None:
    config = configparser.ConfigParser()
    config.read('workflow_settings.ini')

    window_length = int(config['Run Parameters']['WindowLength'])
    number_of_runs = int(config['Run Parameters']['NumberOfRuns'])
    training_set_size = int(config['Run Parameters']['TrainingSetSize'])
    paddings = list(map(int, config['Run Parameters']['Paddings'].split()))
    plasmid = config['Run Parameters']['Plasmid']

    start_index = int(config[plasmid]['StartIndex'])
    end_index = int(config[plasmid]['EndIndex'])

    runs = [
        WorkflowParameters(
            r,
            plasmid,
            window_length,
            p,
            training_set_size,
            start_index,
            end_index
        ) for r in range(number_of_runs) for p in paddings
    ]

    print(f"TOTAL #RUNS = {len(runs)}")

    with multiprocessing.Pool(NUMBER_OF_PROCESSES) as pool:
        pool.map(do_workflow, runs)

    #aggregate runs in their own folders
    for padding in paddings:
        run_folders = glob.glob(f'{plasmid}_p{padding}_w{window_length}_*')
        aggregate_folder_name = f'aggregate_{plasmid}_p{padding}_w{window_length}_runs_{len(run_folders)}'

        try:
            os.mkdir(aggregate_folder_name)
        except FileExistsError:
            pass

        for run_folder in run_folders:
            shutil.copyfile(
                pathlib.Path(run_folder, f'{plasmid}_SHANNON_p{padding}_w{window_length}_base_in_loop.xlsx'),
                pathlib.Path(aggregate_folder_name, f'{plasmid}_SHANNON_p{padding}_w{window_length}_base_in_loop_{run_folder[-1]}.xlsx')
            )

if __name__ == "__main__":
    main()
