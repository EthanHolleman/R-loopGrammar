#!/usr/bin/env python3

import argparse
import importlib
import sys
import json
import enum


"""
Script to train a grammar based on a set of  words for R-loops.


Copyright 2021 Svetlana Poznanovic

"""


class GrammarSymbol(str, enum.Enum):
    SIGMA = "s"
    SIGMA_HAT = "h"
    TAU = "t"
    TAU_HAT = "T"
    DELTA = "d"
    BETA = "B"
    RHO = "R"
    GAMMA = "g"
    ALPHA = "O"
    OMEGA = "o"


def up_to_alpha(word):
    alpha_index = word.index(GrammarSymbol.ALPHA)
    return word[: alpha_index + 1]


def after_alpha_to_omega(word):
    alpha_index = word.index(GrammarSymbol.ALPHA)
    omega_index = word.index(GrammarSymbol.OMEGA)
    assert alpha_index < omega_index

    return word[alpha_index + 1 : omega_index + 1]


def after_omega(word):
    omega_index = word.index(GrammarSymbol.OMEGA)
    return word[omega_index + 1 :]


def translate_greek(language_greek, width):
    language = []

    for word in language_greek:
        word = word.replace("σ^", GrammarSymbol.SIGMA_HAT)
        word = word.replace("σ", GrammarSymbol.SIGMA)
        word = word.replace("δ", GrammarSymbol.DELTA)
        word = word.replace("γ", GrammarSymbol.GAMMA)
        word = word.replace("τ^", GrammarSymbol.TAU_HAT)
        word = word.replace("τ", GrammarSymbol.TAU)
        word = word.replace("ρ", GrammarSymbol.RHO)
        word = word.replace("β", GrammarSymbol.BETA)

        for i in range(width):
            word = word.replace(f"ω{i}", GrammarSymbol.OMEGA)
            word = word.replace(f"α{i}", GrammarSymbol.ALPHA)

        language.append(word[::-1])

    return language


def probability(probabilities, word):
    product = 1

    up_to_alpha_part = up_to_alpha(word)
    S_to_S_transitions = up_to_alpha_part[:-2]
    S_to_R_transitions = up_to_alpha_part[-2:]
    S_probabilities = probabilities["S_probabilities"]

    after_alpha_to_omega_part = after_alpha_to_omega(word)
    R_to_R_transitions = after_alpha_to_omega_part[:-2]
    R_to_Q_transitions = after_alpha_to_omega_part[-2:]
    R_probabilities = probabilities["R_probabilities"]

    after_omega_part = after_omega(word)
    Q_to_Q_transitions = after_omega_part[:-1]
    Q_to_end_transitions = after_omega_part[-1:]
    Q_probabilities = probabilities["Q_probabilities"]

    S_to_S_symbol_probability_map = {
        GrammarSymbol.SIGMA: S_probabilities["S_sigma_S"],
        GrammarSymbol.SIGMA_HAT: S_probabilities["S_sigma_hat_S"],
        GrammarSymbol.GAMMA: S_probabilities["S_gamma_S"],
        GrammarSymbol.DELTA: S_probabilities["S_delta_S"],
    }

    S_to_R_symbol_probability_map = {
        GrammarSymbol.SIGMA: S_probabilities["S_sigma_alpha_i_R"],
        GrammarSymbol.SIGMA_HAT: S_probabilities["S_sigma_hat_i_alpha_R"],
        GrammarSymbol.GAMMA: S_probabilities["S_gamma_alpha_i_R"],
        GrammarSymbol.DELTA: S_probabilities["S_delta_alpha_i_R"],
    }

    R_to_R_symbol_probability_map = {
        GrammarSymbol.TAU: R_probabilities["R_tau_R"],
        GrammarSymbol.TAU_HAT: R_probabilities["R_tau_hat_R"],
        GrammarSymbol.RHO: R_probabilities["R_rho_R"],
        GrammarSymbol.BETA: R_probabilities["R_beta_R"],
    }

    R_to_Q_symbol_probability_map = {
        GrammarSymbol.TAU: R_probabilities["R_tau_omega_i_Q"],
        GrammarSymbol.TAU_HAT: R_probabilities["R_tau_hat_i_omega_Q"],
        GrammarSymbol.RHO: R_probabilities["R_rho_omega_i_Q"],
        GrammarSymbol.BETA: R_probabilities["R_beta_omega_i_Q"],
    }

    Q_to_Q_symbol_probability_map = {
        GrammarSymbol.SIGMA: Q_probabilities["Q_sigma_Q"],
        GrammarSymbol.SIGMA_HAT: Q_probabilities["Q_sigma_hat_Q"],
        GrammarSymbol.GAMMA: Q_probabilities["Q_gamma_Q"],
        GrammarSymbol.DELTA: Q_probabilities["Q_delta_Q"],
    }

    Q_to_end_symbol_probability_map = {
        GrammarSymbol.SIGMA: Q_probabilities["Q_sigma_end"],
        GrammarSymbol.SIGMA_HAT: Q_probabilities["Q_sigma_hat_end"],
        GrammarSymbol.GAMMA: Q_probabilities["Q_gamma_end"],
        GrammarSymbol.DELTA: Q_probabilities["Q_delta_end"],
    }

    for transition in S_to_S_transitions:
        product *= S_to_S_symbol_probability_map[transition]

    product *= S_to_R_symbol_probability_map[S_to_R_transitions[0]]

    for transition in R_to_R_transitions:
        product *= R_to_R_symbol_probability_map[transition]

    product *= R_to_Q_symbol_probability_map[R_to_Q_transitions[0]]

    for transition in Q_to_Q_transitions:
        product *= Q_to_Q_symbol_probability_map[transition]

    product *= Q_to_end_symbol_probability_map[Q_to_end_transitions[0]]

    return product


class Probabilistic_Language:
    @classmethod
    def get_args(cls):
        parser = argparse.ArgumentParser(description="Find probabilities")
        parser.add_argument(
            "-i",
            "--input_words",
            metavar="WORDS_IN_FILE",
            type=str,
            required=True,
            help="WORDS input file",
            default=None,
        )
        parser.add_argument(
            "-p",
            "--input_probabilities",
            metavar="PROBABILITIES_IN_FILE",
            type=str,
            required=True,
            help="Probabilities input file",
            default=None,
        )
        parser.add_argument(
            "-o",
            "--output_file",
            metavar="OUTPUT_FILE",
            type=str,
            required=False,
            help="Output TXT file",
            default="output",
        )
        parser.add_argument(
            "-w",
            "--width",
            metavar="WIDTH",
            type=int,
            required=True,
            help="N-Tuple size",
        )
        return parser.parse_args()

    @classmethod
    def word_probabilities(cls, words_in, probabs_in, width, out_file="output"):
        with open(probabs_in, "r", encoding="utf-8") as file_handle:
            probabilities = json.load(file_handle)

        with open(words_in, "r", encoding="utf-8") as file:
            lines = file.readlines()

        language_greek = []

        for line in lines:
            parsing = line.split(":")[1].strip()
            language_greek.append(parsing)

        language = translate_greek(language_greek, width)

        probabilities = [probability(probabilities, word) for word in language]
        filtered_probabilities = list(filter(lambda x: x > 0, probabilities))

        assert (
            len(filtered_probabilities) > 0
        ), f"All probabilities are 0. #language: {len(language)} {(words_in, probabs_in)}"

        partition_function = sum(probabilities)
        assert partition_function > 0

        print("#probabilities:", len(probabilities))
        print("The partition function is: ", partition_function)

        if partition_function > 0:
            probs = [term / partition_function for term in probabilities]
        else:
            probs = probabilities

        with open(out_file, "a") as file_handle:
            for i in probs:
                file_handle.write(str(i) + "\n")


if __name__ == "__main__":
    args = vars(Probabilistic_Language.get_args())
    Probabilistic_Language.word_probabilities(
        args.get("input_words", None),
        args.get("input_probabilities", None),
        args["width"],
        args.get("output_file", "output"),
    )
