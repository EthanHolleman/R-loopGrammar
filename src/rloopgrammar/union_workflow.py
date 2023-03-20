import multiprocessing
import sys
import os
import glob
import pathlib
import dataclasses
import shutil
import json
import configparser
import random

from typing import *

import model.union_dict as union_dict
import model.grammar_word as grammar_word
import model.grammar_training as grammar_training
import model.probabilistic_language as probabilistic_language
import model.in_loop_probs as in_loop_probs

NUMBER_OF_PROCESSES = 10

RIGHT_PADDING = 100
LEFT_PADDING = 80


class SupressOutput:
    def __init__(self):
        pass

    def __enter__(self):
        sys.stdout = open(os.devnull, "w")

    def __exit__(self, type, value, traceback):
        sys.stdout = sys.__stdout__


@dataclasses.dataclass
class UnionParameters:
    run_number: int
    plasmid_1: str
    plasmid_2: str
    window_length: int
    padding_length: int
    start_index_1: int
    end_index_1: int
    start_index_2: int
    end_index_2: int


def do_workflow(union_parameters: UnionParameters) -> None:
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
    ) = dataclasses.astuple(union_parameters)

    # TODO: RUN_NUMBER IN EACH FILENAME
    print("RUNNING", dataclasses.astuple(union_parameters))
    print(f"[{padding_length}] Running with padding value: {padding_length}")

    plot_region1 = RIGHT_PADDING + end_index_1
    plot_region2 = RIGHT_PADDING + end_index_2

    random.seed(run_number * 100)

    if not pathlib.Path(f"{plasmid_1}_w{window_length}_all_rloops.bed").is_file():
        with open(f"{plasmid_1}_w{window_length}_all_rloops.bed", "w") as file_handle:
            for x in range(
                start_index_1 + window_length, end_index_1 - 2 * window_length
            ):
                for y in range(x + window_length, end_index_1 - window_length):
                    if (y - x) % window_length == 0:
                        file_handle.write(f"{plasmid_1}\t{x}\t{y}\n")
    if not pathlib.Path(f"{plasmid_2}_w{window_length}_all_rloops.bed").is_file():
        with open(f"{plasmid_2}_w{window_length}_all_rloops.bed", "w") as file_handle:
            for x in range(
                start_index_2 + window_length, end_index_2 - 2 * window_length
            ):
                for y in range(x + window_length, end_index_2 - window_length):
                    if (y - x) % window_length == 0:
                        file_handle.write(f"{plasmid_2}\t{x}\t{y}\n")

    matches = glob.glob(
        f"aggregate_{plasmid_1}_p{padding_length}_w{window_length}_runs_*"
    )

    assert len(matches) == 1, f"Found multiple choices for {plasmid_1}'s' folder."

    plasmid1_folder_name = pathlib.Path(matches[0])

    matches = glob.glob(
        f"aggregate_{plasmid_2}_p{padding_length}_w{window_length}_runs_*"
    )
    assert len(matches) == 1, f"Found multiple choices for {plasmid_2}'s' folder."

    plasmid2_folder_name = pathlib.Path(matches[0])

    bed_extra_training_set_filename_1 = f"{plasmid_1}_p{padding_length}_w{window_length}_{run_number}.bed_extra_training-set.bed"
    bed_extra_training_set_filename_2 = f"{plasmid_2}_p{padding_length}_w{window_length}_{run_number}.bed_extra_training-set.bed"

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
    input_file = f"{plasmid_1}_{plasmid_2}_union_w{window_length}_p{padding_length}_{run_number}_input.txt"

    # COPY FILES THAT WILL BE NEEDED TO LOCAL DIR

    local_dir = pathlib.Path(".")
    filedir_1 = (
        plasmid1_folder_name
        / f"{plasmid_1}_p{padding_length}_w{window_length}_{run_number}"
    )
    filedir_2 = (
        plasmid2_folder_name
        / f"{plasmid_2}_p{padding_length}_w{window_length}_{run_number}"
    )

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
        f"{plasmid_1}_{plasmid_2}_union_w{window_length}_p{padding_length}_{run_number}_input.txt",
        "w",
    ) as file_handle:
        file_handle.write(
            f"{plasmid_1}_p{padding_length}_w{window_length}_{run_number}_DICT_SHANNON.xlsx.json\n"
        )
        file_handle.write(
            f"{plasmid_1}_p{padding_length}_w{window_length}_{run_number}_DICT_SHANNON.xlsx\n"
        )
        file_handle.write(
            f"{plasmid_2}_p{padding_length}_w{window_length}_{run_number}_DICT_SHANNON.xlsx.json\n"
        )
        file_handle.write(
            f"{plasmid_2}_p{padding_length}_w{window_length}_{run_number}_DICT_SHANNON.xlsx\n"
        )

    print(
        f"p[{padding_length}] w[{window_length}] run [{run_number}] Taking the union..."
    )
    union_dict.UnionDict.union_json(
        f"{plasmid_1}_{plasmid_2}_union_w{window_length}_p{padding_length}_{run_number}_input.txt",
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
            plot_region1,
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
            plot_region2,
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
    config = configparser.ConfigParser()
    config.read("union_workflow_settings.ini")

    window_length = int(config["Union Parameters"]["WindowLength"])
    number_of_runs = int(config["Union Parameters"]["NumberOfRuns"])
    padding = int(config["Union Parameters"]["Padding"])
    plasmid_groups = config["Union Parameters"]["Plasmids"]
    plasmid_tuples = []

    if "," in plasmid_groups:
        for pair in plasmid_groups.split(","):
            assert len(pair.split()) == 2
            plasmid_tuples.append(tuple(pair.split()))
    else:
        assert len(pair.split()) == 2
        plasmid_tuples.append(tuple(pair.split()))

    for plasmid1, plasmid2 in plasmid_tuples:
        runs = [
            UnionParameters(
                r,
                plasmid1,
                plasmid2,
                window_length,
                padding,
                int(config[plasmid1]["StartIndex"]),
                int(config[plasmid1]["EndIndex"]),
                int(config[plasmid2]["StartIndex"]),
                int(config[plasmid2]["EndIndex"]),
            )
            for r in range(number_of_runs)
        ]

        with multiprocessing.Pool(NUMBER_OF_PROCESSES) as pool:
            pool.map(do_workflow, runs)

        run_folders = glob.glob(f"UNION_p{padding}_w{window_length}_*")
        aggregate_folder_name = pathlib.Path(
            f"aggregate_{plasmid1}_{plasmid2}_p{padding}_w{window_length}_runs_{len(run_folders)}"
        )

        try:
            os.mkdir(aggregate_folder_name)
        except FileExistsError:
            pass

        for run_folder in run_folders:
            shutil.move(run_folder, aggregate_folder_name / run_folder)


if __name__ == "__main__":
    main()
