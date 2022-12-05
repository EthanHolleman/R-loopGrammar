import multiprocessing
import importlib
import sys
import os
import glob
import pathlib
import dataclasses
import shutil
import json

from typing import *

region_extractor = importlib.import_module("01_regions_extractor")
region_threshold = importlib.import_module("02_regions_threshold")
training_set = importlib.import_module("03_training_set")
grammar_dict = importlib.import_module("04_grammar_dict")
union_dict = importlib.import_module("05_union_dict")
grammar_word = importlib.import_module("06_grammar_word")
grammar_training = importlib.import_module("06_grammar_training")
probabilistic_language = importlib.import_module("07_probabilistic_language")
in_loop_probs = importlib.import_module("08_in_loop_probs")

PLASMID_1 = "pFC53_GYRASECR"
PLASMID_2 = "pFC8_GYRASECR"
WINDOW_LENGTH = 4

START_INDEX_1 = 80
END_INDEX_1 = 1829
SEQ_LENGTH_1 = 1929
START_INDEX_2 = 80
END_INDEX_2 = 1512
SEQ_LENGTH_2 = 1612
NUMBER_OF_RUNS = 10

PADDINGS = [13]


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
    plasmid_1: str
    plasmid_2: str
    window_length: int
    padding_length: int
    start_index_1: int
    end_index_1: int
    start_index_2: int
    end_index_2: int


def do_workflow(workflow_parameters: WorkflowParameters) -> None:
    (
        run_number,
        plasmid_1,
        plasmid_2,
        window_length,
        padding_length,
        start_index_1,
        end_index_1,
        start_index_2,
        end_index_2,
    ) = dataclasses.astuple(workflow_parameters)

    # TODO: RUN_NUMBER IN EACH FILENAME
    print("RUNNING", dataclasses.astuple(workflow_parameters))
    print(f"[{padding_length}] Running with padding value: {padding_length}")

    # bed_extra_filename = f"{plasmid}_SUPERCOILED_p{padding_length}_w{window_length}_{run_number}.bed_extra.bed"
    weight_xlsx_filename_1 = (
        f"{plasmid_1}_p{padding_length}_w{window_length}_{run_number}_weight.xlsx"
    )
    weight_xlsx_filename_2 = (
        f"{plasmid_2}_p{padding_length}_w{window_length}_{run_number}_weight.xlsx"
    )
    weight_shannon_entropy_xlsx_filename_1 = f"{plasmid_1}_p{padding_length}_w{window_length}_{run_number}_weight_shannon.xlsx"
    weight_shannon_entropy_xlsx_filename_2 = f"{plasmid_2}_p{padding_length}_w{window_length}_{run_number}_weight_shannon.xlsx"
    bed_extra_training_set_filename_1 = f"{plasmid_1}_p{padding_length}_w{window_length}_{run_number}.bed_extra_training-set.bed"
    bed_extra_training_set_filename_2 = f"{plasmid_2}_p{padding_length}_w{window_length}_{run_number}.bed_extra_training-set.bed"
    directory_name_1 = f"{plasmid_1}_p{padding_length}_w{window_length}_{run_number}"
    directory_name_2 = f"{plasmid_2}_p{padding_length}_w{window_length}_{run_number}"
    dict_shannon_xlsx_filename_1 = (
        f"{plasmid_1}_p{padding_length}_w{window_length}_{run_number}_DICT_SHANNON.xlsx"
    )
    dict_shannon_json_filename_1 = f"{plasmid_1}_p{padding_length}_w{window_length}_{run_number}_DICT_SHANNON.xlsx.json"
    dict_shannon_xlsx_filename_2 = (
        f"{plasmid_2}_p{padding_length}_w{window_length}_{run_number}_DICT_SHANNON.xlsx"
    )
    dict_shannon_json_filename_2 = f"{plasmid_2}_p{padding_length}_w{window_length}_{run_number}_DICT_SHANNON.xlsx.json"
    all_rloops_filename_1 = f"{plasmid_1}_all_rloops_WORDS_union_SHANNON_p{padding_length}_w{window_length}_{run_number}.txt"
    all_rloops_filename_2 = f"{plasmid_2}_all_rloops_WORDS_union_SHANNON_p{padding_length}_w{window_length}_{run_number}.txt"
    union_dict_name = (
        f"out_union_w{window_length}_p{padding_length}_{run_number}_union.json"
    )
    training_set_words_filename_1 = f"{plasmid_1}_union_SUPERCOILED_p{padding_length}_w{window_length}_{run_number}_training-set_WORDS_SHANNON.txt"
    training_set_words_filename_2 = f"{plasmid_2}_union_SUPERCOILED_p{padding_length}_w{window_length}_{run_number}_training-set_WORDS_SHANNON.txt"
    probabilities_filename_1 = f"{plasmid_1}_union_SHANNON_p{padding_length}_w{window_length}_{run_number}_probabilities.json"
    probabilities_filename_2 = f"{plasmid_2}_union_SHANNON_p{padding_length}_w{window_length}_{run_number}_probabilities.json"
    av_probabilities_filename = f"SHANNON_p{padding_length}_w{window_length}_{run_number}_union_probabilities.json"
    prob_lang_filename_1 = f"{plasmid_1}_union_SHANNON_p{padding_length}_w{window_length}_{run_number}_prob_lang.py"
    prob_lang_filename_2 = f"{plasmid_2}_union_SHANNON_p{padding_length}_w{window_length}_{run_number}_prob_lang.py"
    base_in_loop_1 = f"{plasmid_1}_union_SHANNON_p{padding_length}_w{window_length}_{run_number}_base_in_loop.XLSX"
    base_in_loop_2 = f"{plasmid_2}_union_SHANNON_p{padding_length}_w{window_length}_{run_number}_base_in_loop.XLSX"
    base_in_loop_no_xlsx_1 = f"{plasmid_1}_union_SHANNON_p{padding_length}_w{window_length}_{run_number}_base_in_loop"
    base_in_loop_no_xlsx_2 = f"{plasmid_2}_union_SHANNON_p{padding_length}_w{window_length}_{run_number}_base_in_loop"
    input_file = f"{PLASMID_1}_{PLASMID_2}_union_w{WINDOW_LENGTH}_p{padding_length}_{run_number}_input.txt"

    # COPY FILES THAT WILL BE NEEDED TO LOCAL DIR

    local_dir = pathlib.Path(".")
    filedir_1 = f"{plasmid_1}_p{padding_length}_w{window_length}_{run_number}"
    filedir_2 = f"{plasmid_2}_p{padding_length}_w{window_length}_{run_number}"

    try:
        shutil.copy(
            os.path.join(local_dir, filedir_1, dict_shannon_xlsx_filename_1), local_dir
        )
        shutil.copy(
            os.path.join(local_dir, filedir_2, dict_shannon_xlsx_filename_2), local_dir
        )
        shutil.copy(
            os.path.join(local_dir, filedir_1, dict_shannon_json_filename_1), local_dir
        )
        shutil.copy(
            os.path.join(local_dir, filedir_2, dict_shannon_json_filename_2), local_dir
        )
        shutil.copy(
            os.path.join(local_dir, filedir_1, bed_extra_training_set_filename_1),
            local_dir,
        )
        shutil.copy(
            os.path.join(local_dir, filedir_2, bed_extra_training_set_filename_2),
            local_dir,
        )
        print("Files copied successfully.")

    except shutil.SameFileError:
        print("Source and destination represents the same file.")

    except PermissionError:
        print("Permission denied.")

    except Exception as e:
        print(f"Error occurred while copying file. {e}")

    # ADJUST BED FILE, THEN USE TRAINING SET BED FILE INSTEAD OF ENTIRE BED_EXTRA FILE.

    with open(
        f"{PLASMID_1}_{PLASMID_2}_union_w{WINDOW_LENGTH}_p{padding_length}_{run_number}_input.txt",
        "w",
    ) as file_handle:
        file_handle.write(
            f"{plasmid_1}_p{padding_length}_w{WINDOW_LENGTH}_{run_number}_DICT_SHANNON.xlsx.json\n"
        )
        file_handle.write(
            f"{plasmid_1}_p{padding_length}_w{WINDOW_LENGTH}_{run_number}_DICT_SHANNON.xlsx\n"
        )
        file_handle.write(
            f"{plasmid_2}_p{padding_length}_w{WINDOW_LENGTH}_{run_number}_DICT_SHANNON.xlsx.json\n"
        )
        file_handle.write(
            f"{plasmid_2}_p{padding_length}_w{WINDOW_LENGTH}_{run_number}_DICT_SHANNON.xlsx\n"
        )

    print(
        f"p[{padding_length}] w[{window_length}] run [{run_number}] Taking the union..."
    )
    union_dict.UnionDict.union_json(
        f"{PLASMID_1}_{PLASMID_2}_union_w{WINDOW_LENGTH}_p{padding_length}_{run_number}_input.txt",
        output_prefix="out_union_w"
        + str(window_length)
        + "_p"
        + str(padding_length)
        + "_"
        + str(run_number),
    )

    if not pathlib.Path(all_rloops_filename_1).is_file():
        print(
            f"p[{padding_length}] w[{window_length}] run [{run_number}] Extracting all words for the first plasmid..."
        )
        grammar_word.GrammarWord.extract_word(
            f"{plasmid_1.split('_')[0]}.fa",
            f"{plasmid_1}_w{window_length}_all_rloops.bed",
            union_dict_name,
            start_index_1,
            end_index_1,
            window_length,
            all_rloops_filename_1,
        )

    if not pathlib.Path(all_rloops_filename_2).is_file():
        print(
            f"p[{padding_length}] w[{window_length}] run [{run_number}] Extracting all words for the second plasmid..."
        )
        grammar_word.GrammarWord.extract_word(
            f"{plasmid_2.split('_')[0]}.fa",
            f"{plasmid_2}_w{window_length}_all_rloops.bed",
            union_dict_name,
            start_index_2,
            end_index_2,
            window_length,
            all_rloops_filename_2,
        )

    print(
        f"p[{padding_length}] w[{window_length}] run [{run_number}] Extracting training set 1 words..."
    )
    grammar_word.GrammarWord.extract_word(
        f"{plasmid_1.split('_')[0]}.fa",
        bed_extra_training_set_filename_1,
        union_dict_name,
        start_index_1,
        end_index_1,
        window_length,
        training_set_words_filename_1,
    )

    print(
        f"p[{padding_length}] w[{window_length}] run [{run_number}] Extracting training set 2 words..."
    )
    grammar_word.GrammarWord.extract_word(
        f"{plasmid_2.split('_')[0]}.fa",
        bed_extra_training_set_filename_2,
        union_dict_name,
        start_index_2,
        end_index_2,
        window_length,
        training_set_words_filename_2,
    )

    print(
        f"p[{padding_length}] w[{window_length}] run [{run_number}] Finding probabilities 1 ..."
    )
    grammar_training.GrammarTraining.find_probabilities(
        training_set_words_filename_1, window_length, probabilities_filename_1
    )

    print(
        f"p[{padding_length}] w[{window_length}] run [{run_number}] Finding probabilities 2 ..."
    )
    grammar_training.GrammarTraining.find_probabilities(
        training_set_words_filename_2, window_length, probabilities_filename_2
    )

    # CREATE FILE WITH AVERAGE PROBABILITIES
    print(
        f"p[{padding_length}] w[{window_length}] run [{run_number}] Finding average probabilities..."
    )

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

    print(
        f"p[{padding_length}] w[{window_length}] run [{run_number}] Finding word probabilities 1..."
    )

    with SupressOutput():
        probabilistic_language.Probabilistic_Language.word_probabilities(
            all_rloops_filename_1,  # Probably don't need multiple copies of this?
            av_probabilities_filename,
            window_length,
            prob_lang_filename_1,
        )

    print(
        f"p[{padding_length}] w[{window_length}] run [{run_number}] Finding word probabilities 2..."
    )

    with SupressOutput():
        probabilistic_language.Probabilistic_Language.word_probabilities(
            all_rloops_filename_2,  # Probably don't need multiple copies of this?
            av_probabilities_filename,
            window_length,
            prob_lang_filename_2,
        )

    print(
        f"p[{padding_length}] w[{window_length}] run [{run_number}] In loop probabilities 1..."
    )

    with SupressOutput():
        in_loop_probs.Loop_probabilities.in_loop_probabilities(
            all_rloops_filename_1,
            f"{plasmid_1}_w{window_length}_all_rloops.bed",
            # end_index - start_index,
            SEQ_LENGTH_1,
            start_index_1,
            end_index_1,
            prob_lang_filename_1,
            window_length,
            base_in_loop_no_xlsx_1,
        )

    print(
        f"p[{padding_length}] w[{window_length}] run [{run_number}] In loop probabilities 2..."
    )

    with SupressOutput():
        in_loop_probs.Loop_probabilities.in_loop_probabilities(
            all_rloops_filename_1,
            f"{plasmid_2}_w{window_length}_all_rloops.bed",
            # end_index - start_index,
            SEQ_LENGTH_2,
            start_index_2,
            end_index_2,
            prob_lang_filename_2,
            window_length,
            base_in_loop_no_xlsx_2,
        )
    print(
        f"p[{padding_length}] w[{window_length}] run [{run_number}] Cleaning up files..."
    )
    local_dir = pathlib.Path(".")
    # files = local_dir.glob(f'*_union_*')
    folder_name = f'{"UNION"}_p{padding_length}_w{window_length}_{run_number}'

    try:
        os.mkdir(folder_name)
    except FileExistsError:
        pass

    # for file in files:
    #    if file.is_file():
    #        if file != '05_union_dict.py':
    #            os.rename(file, local_dir / folder_name / file)

    os.rename(union_dict_name, local_dir / folder_name / union_dict_name)
    os.rename(all_rloops_filename_1, local_dir / folder_name / all_rloops_filename_1)
    os.rename(all_rloops_filename_2, local_dir / folder_name / all_rloops_filename_2)
    os.rename(base_in_loop_1, local_dir / folder_name / base_in_loop_1)
    os.rename(base_in_loop_2, local_dir / folder_name / base_in_loop_2)
    os.rename(prob_lang_filename_1, local_dir / folder_name / prob_lang_filename_1)
    os.rename(prob_lang_filename_2, local_dir / folder_name / prob_lang_filename_2)
    os.rename(
        probabilities_filename_1, local_dir / folder_name / probabilities_filename_1
    )
    os.rename(
        probabilities_filename_2, local_dir / folder_name / probabilities_filename_2
    )
    os.rename(
        training_set_words_filename_1,
        local_dir / folder_name / training_set_words_filename_1,
    )
    os.rename(
        training_set_words_filename_2,
        local_dir / folder_name / training_set_words_filename_2,
    )
    os.rename(input_file, local_dir / folder_name / input_file)
    os.rename(
        av_probabilities_filename, local_dir / folder_name / av_probabilities_filename
    )

    os.rename(
        dict_shannon_xlsx_filename_1,
        local_dir / folder_name / dict_shannon_xlsx_filename_1,
    )
    os.rename(
        dict_shannon_xlsx_filename_2,
        local_dir / folder_name / dict_shannon_xlsx_filename_2,
    )
    os.rename(
        dict_shannon_json_filename_1,
        local_dir / folder_name / dict_shannon_json_filename_1,
    )
    os.rename(
        dict_shannon_json_filename_2,
        local_dir / folder_name / dict_shannon_json_filename_2,
    )
    os.rename(
        bed_extra_training_set_filename_1,
        local_dir / folder_name / bed_extra_training_set_filename_1,
    )
    os.rename(
        bed_extra_training_set_filename_2,
        local_dir / folder_name / bed_extra_training_set_filename_2,
    )


def main() -> None:
    with open(f"{PLASMID_1}_w{WINDOW_LENGTH}_all_rloops.bed", "w") as file_handle:
        for x in range(START_INDEX_1 + WINDOW_LENGTH, END_INDEX_1 - 2 * WINDOW_LENGTH):
            for y in range(x + WINDOW_LENGTH, END_INDEX_1 - WINDOW_LENGTH):
                if (y - x) % WINDOW_LENGTH == 0:
                    file_handle.write(f"{PLASMID_1}\t{x}\t{y}\n")
    with open(f"{PLASMID_2}_w{WINDOW_LENGTH}_all_rloops.bed", "w") as file_handle:
        for x in range(START_INDEX_2 + WINDOW_LENGTH, END_INDEX_2 - 2 * WINDOW_LENGTH):
            for y in range(x + WINDOW_LENGTH, END_INDEX_2 - WINDOW_LENGTH):
                if (y - x) % WINDOW_LENGTH == 0:
                    file_handle.write(f"{PLASMID_2}\t{x}\t{y}\n")

    runs = [
        WorkflowParameters(
            r,
            PLASMID_1,
            PLASMID_2,
            WINDOW_LENGTH,
            p,
            START_INDEX_1,
            END_INDEX_1,
            START_INDEX_2,
            END_INDEX_2,
        )
        for r in range(NUMBER_OF_RUNS)
        for p in PADDINGS
    ]

    with multiprocessing.Pool(5) as pool:
        pool.map(do_workflow, runs)


"""
    for r in range(NUMBER_OF_RUNS):
        for p in PADDINGS:
            do_workflow(WorkflowParameters(
                r,
                PLASMID,
                WINDOW_LENGTH,
                p,
                TRAINING_SET_LINES,
                START_INDEX,
                END_INDEX
            ))
"""

if __name__ == "__main__":
    main()
