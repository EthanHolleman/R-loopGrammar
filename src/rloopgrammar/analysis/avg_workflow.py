import multiprocessing
import importlib
import sys
import os
import glob
import pathlib
import dataclasses
import shutil
import re

from typing import *

NUMBER_OF_PROCESSES = 5

PLASMID_1 = "pFC53_GYRASE"
PLASMID_2 = "pFC8_GYRASE"

RIGHT_PADDING = 100
LEFT_PADDING = 80

START_INDEX_1 = 80  
END_INDEX_1 = 1829
SEQ_LENGTH_1 =  1929

START_INDEX_2 = 80  
END_INDEX_2 = 1512
SEQ_LENGTH_2 =  1612

NUMBER_OF_RUNS = 10

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

    plasmid1: str
    plasmid2: str

    window_length: int
    padding_length: int

    plasmid1_start_index: int
    plasmid1_end_index: int

    plasmid2_start_index: int
    plasmid2_end_index: int


def do_workflow(wp: WorkflowParameters) -> None:
    print(f"[{wp.padding_length}] Running with padding value: {wp.padding_length}")

    plasmid1_all_rloops_bed_filename = f"{wp.plasmid1}_w{wp.window_length}_all_rloops.bed"

    if not os.path.exists(plasmid1_all_rloops_bed_filename):
        with open(plasmid1_all_rloops_bed_filename, "w") as file_handle:
            for x in range(80 + wp.window_length, wp.plasmid1_end_index - 2 * wp.window_length):
                for y in range(x + wp.window_length, wp.plasmid1_end_index - wp.window_length):
                    if (y - x) % wp.window_length == 0:
                        file_handle.write(f"{wp.plasmid1}\t{x}\t{y}\n")

    plasmid2_all_rloops_bed_filename = f"{wp.plasmid2}_w{wp.window_length}_all_rloops.bed"

    if not os.path.exists(plasmid2_all_rloops_bed_filename):
        with open(plasmid2_all_rloops_bed_filename, "w") as file_handle:
            for x in range(80 + wp.window_length, wp.plasmid2_end_index - 2 * wp.window_length):
                for y in range(x + wp.window_length, wp.plasmid2_end_index - wp.window_length):
                    if (y - x) % wp.window_length == 0:
                        file_handle.write(f"{wp.plasmid2}\t{x}\t{y}\n")

    run_folder = f"UNION_p{wp.padding_length}_w{wp.window_length}_{wp.run_number}"

    plasmid1_all_rloops_filename = f'{run_folder}/' + f"{wp.plasmid1}_all_rloops_WORDS_union_SHANNON_p{wp.padding_length}_w{wp.window_length}_{wp.run_number}.txt"
    plasmid2_all_rloops_filename = f'{run_folder}/' + f"{wp.plasmid2}_all_rloops_WORDS_union_SHANNON_p{wp.padding_length}_w{wp.window_length}_{wp.run_number}.txt"

    probabilities_filename = '_'.join(map(str, ["UNION", f'p{wp.padding_length}', f'w{wp.window_length}', 'probabilities_average.py']))
    probabilities_filename_no_py = probabilities_filename[:-3]

    plasmid1_prob_lang_filename = f'{run_folder}/' + f"{wp.plasmid1}_SHANNON_p{wp.padding_length}_w{wp.window_length}_{wp.run_number}_prob_lang_avg_probs.py"
    plasmid1_base_in_loop_no_xlsx = f'{run_folder}/' + f"{wp.plasmid1}_SHANNON_p{wp.padding_length}_w{wp.window_length}_{wp.run_number}_base_in_loop_avg_probs"

    plasmid2_prob_lang_filename = f'{run_folder}/' + f"{wp.plasmid2}_SHANNON_p{wp.padding_length}_w{wp.window_length}_{wp.run_number}_prob_lang_avg_probs.py"
    plasmid2_base_in_loop_no_xlsx = f'{run_folder}/' + f"{wp.plasmid2}_SHANNON_p{wp.padding_length}_w{wp.window_length}_{wp.run_number}_base_in_loop_avg_probs"

    print(f"[{wp.padding_length}] Finding word probabilities...")

    with SupressOutput():
        probabilistic_language.Probabilistic_Language.word_probabilities(
            plasmid1_all_rloops_filename,
            probabilities_filename_no_py,
            wp.window_length,
            plasmid1_prob_lang_filename
        )

        probabilistic_language.Probabilistic_Language.word_probabilities(
            plasmid2_all_rloops_filename,
            probabilities_filename_no_py,
            wp.window_length,
            plasmid2_prob_lang_filename
        )

    print(f"[{wp.padding_length}] In loop probabilities...")

    with SupressOutput():
        in_loop_probs.Loop_probabilities.in_loop_probabilities(
            plasmid1_all_rloops_filename,
            plasmid1_all_rloops_bed_filename,
            SEQ_LENGTH_1,
            wp.plasmid1_start_index,
            wp.plasmid1_end_index,
            plasmid1_prob_lang_filename,
            wp.window_length,
            plasmid1_base_in_loop_no_xlsx
        )

        in_loop_probs.Loop_probabilities.in_loop_probabilities(
            plasmid2_all_rloops_filename,
            plasmid2_all_rloops_bed_filename,
            SEQ_LENGTH_2,
            wp.plasmid2_start_index,
            wp.plasmid2_end_index,
            plasmid2_prob_lang_filename,
            wp.window_length,
            plasmid2_base_in_loop_no_xlsx
        )

@dataclasses.dataclass
class WorkflowParameters:
    run_number: int

    plasmid1: str
    plasmid2: str

    window_length: int
    padding_length: int

    plasmid1_start_index: int
    plasmid1_end_index: int

    plasmid2_start_index: int
    plasmid2_end_index: int

def main() -> None:
    m = re.search(r'p(\d*)_w(\d*)', os.path.basename(os.getcwd()))

    padding = m[1]
    width = m[2]

    window_length = int(width)
    paddings = [int(padding)]

    runs = [
        WorkflowParameters(
            r,
            PLASMID_1,
            PLASMID_2,
            window_length,
            p,
            START_INDEX_1,
            END_INDEX_1,
            START_INDEX_2,
            END_INDEX_2
        ) for r in range(NUMBER_OF_RUNS) for p in paddings
    ]

    print(f"TOTAL #RUNS = {len(runs)}")

    with multiprocessing.Pool(NUMBER_OF_PROCESSES) as pool:
        pool.map(do_workflow, runs)

if __name__ == "__main__":
    main()
