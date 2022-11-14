#!/usr/bin/env python3
import argparse
import enum
import json

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


def sigma_count(word):
    return word.count("s")


def sigma_hat_count(word):
    return word.count("h")


def gamma_count(word):
    return word.count("g")


def delta_count(word):
    return word.count("d")


def tau_count(word):
    return word.count("T")


def tau_hat_count(word):
    return word.count("H")


def rho_count(word):
    return word.count("R")


def beta_count(word):
    return word.count("B")


def omega_count(word):
    return word.count("o")


def alpha_count(word):
    return word.count("O")


class GrammarTraining:
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
    def find_probabilities(cls, words_in, width, out_file="output"):
        with open(words_in, "r", encoding="utf-8") as fin:
            lines = fin.readlines()

        training_words_greek = []
        for line in lines:
            parsing = line.split(":")[1].strip()
            training_words_greek.append(parsing)

        training_words = []
        for word in training_words_greek:
            word = word.replace("σ^", "h")
            word = word.replace("σ", "s")
            word = word.replace("δ", "d")
            word = word.replace("γ", "g")
            word = word.replace("τ^", "H")
            word = word.replace("τ", "T")
            word = word.replace("ρ", "R")
            word = word.replace("β", "B")

            for i in range(width):
                word = word.replace(f"ω{i}", "o")
                word = word.replace(f"\xcf\x89{i}", "o")
                word = word.replace(f"α{i}", "O")
                word = word.replace(f"\xce\xb1{i}", "O")

            word = word.replace("\xcf\x83^", "h")
            word = word.replace("\xcf\x83", "s")
            word = word.replace("\xce\xb4", "d")
            word = word.replace("\xce\xb3", "g")
            word = word.replace("\xcf\x84^", "H")
            word = word.replace("\xcf\x84", "T")
            word = word.replace("\xcf\x81", "R")
            word = word.replace("\xce\xb2", "B")
            word = word.replace("\xcf\x890", "o")
            word = word.replace("\xcf\x891", "p")
            word = word.replace("\xcf\x892", "q")
            word = word.replace("\xcf\x893", "u")
            word = word.replace("\xcf\x894", "v")
            word = word.replace("\xce\xb10", "O")
            word = word.replace("\xce\xb11", "P")
            word = word.replace("\xce\xb12", "Q")
            word = word.replace("\xce\xb13", "U")
            word = word.replace("\xce\xb14", "V")
            training_words.append(word)

        sigma_ct = 0
        sigma_hat_ct = 0
        gamma_ct = 0
        delta_ct = 0

        sigma_alpha_ct = 0
        sigma_hat_alpha_ct = 0
        gamma_alpha_ct = 0
        delta_alpha_ct = 0

        # reverse each so we read from left to right
        for word in map(lambda x: x[::-1], training_words):
            up_to_alpha_part = up_to_alpha(word)[
                :-2
            ]  # remove alpha and the letter before it
            S_to_S_rules = up_to_alpha_part[:-2]
            S_to_R_rules = up_to_alpha_part[-2:]

            sigma_ct += sigma_count(S_to_S_rules)
            sigma_hat_ct += sigma_hat_count(S_to_S_rules)
            gamma_ct += gamma_count(S_to_S_rules)
            delta_ct += delta_count(S_to_S_rules)

            sigma_alpha_ct += sigma_count(S_to_R_rules)
            sigma_hat_alpha_ct += sigma_hat_count(S_to_R_rules)
            gamma_alpha_ct += gamma_count(S_to_R_rules)
            delta_alpha_ct += delta_count(S_to_R_rules)

        total_len = (
            sigma_ct
            + sigma_hat_ct
            + delta_ct
            + gamma_ct
            + sigma_alpha_ct
            + sigma_hat_alpha_ct
            + gamma_alpha_ct
            + delta_alpha_ct
        )

        S_probabilities_counts = {
            "S_sigma_S": sigma_ct,
            "S_sigma_hat_S": sigma_hat_ct,
            "S_gamma_S": gamma_ct,
            "S_delta_S": delta_ct,
            "S_sigma_alpha_R": sigma_alpha_ct,
            "S_sigma_hat_alpha_R": sigma_hat_alpha_ct,
            "S_gamma_alpha_R": gamma_alpha_ct,
            "S_delta_alpha_R": delta_alpha_ct,
        }

        S_probabilities = {
            k: (v / float(total_len)) for k, v in S_probabilities_counts.items()
        }

        tau_ct = 0
        tau_hat_ct = 0
        rho_ct = 0
        beta_ct = 0

        tau_omega_ct = 0
        tau_hat_omega_ct = 0
        rho_omega_ct = 0
        beta_omega_ct = 0

        for word in map(lambda x: x[::-1], training_words):
            after_alpha_to_omega_part = after_alpha_to_omega(word)
            R_to_R_rules = after_alpha_to_omega_part[:-2]
            R_to_Q_rules = after_alpha_to_omega_part[-2:]

            tau_ct += tau_count(R_to_R_rules)
            tau_hat_ct += tau_hat_count(R_to_R_rules)
            rho_ct += rho_count(R_to_R_rules)
            beta_ct += beta_count(R_to_R_rules)

            tau_omega_ct += tau_count(R_to_R_rules)
            tau_hat_omega_ct += tau_hat_count(R_to_Q_rules)
            rho_omega_ct += rho_count(R_to_Q_rules)
            beta_omega_ct += beta_count(R_to_Q_rules)

        total_len = (
            tau_ct
            + tau_hat_ct
            + rho_ct
            + beta_ct
            + tau_omega_ct
            + tau_hat_omega_ct
            + rho_omega_ct
            + beta_omega_ct
        )

        R_probabilities_counts = {
            "R_tau_R": tau_ct,
            "R_tau_hat_R": tau_hat_ct,
            "R_rho_R": rho_ct,
            "R_beta_R": beta_ct,
            "R_tau_omega_Q": tau_omega_ct,
            "R_tau_hat_omega_Q": tau_hat_omega_ct,
            "R_rho_omega_Q": rho_omega_ct,
            "R_beta_omega_Q": beta_omega_ct,
        }

        R_probabilities = {
            k: (v / float(total_len)) for k, v in R_probabilities_counts.items()
        }

        sigma_ct = 0
        sigma_hat_ct = 0
        gamma_ct = 0
        delta_ct = 0

        sigma_end_ct = 0
        sigma_hat_end_ct = 0
        gamma_end_ct = 0
        delta_end_ct = 0

        # reverse each so we read from left to right
        for word in map(lambda x: x[::-1], training_words):
            after_omega_part = after_omega(word)
            Q_to_Q_rules = after_omega_part[:-1]
            Q_to_end_rules = after_omega_part[-1:]

            sigma_ct += sigma_count(Q_to_Q_rules)
            sigma_hat_ct += sigma_hat_count(Q_to_Q_rules)
            gamma_ct += gamma_count(Q_to_Q_rules)
            delta_ct += delta_count(Q_to_Q_rules)

            sigma_end_ct += sigma_count(Q_to_end_rules)
            sigma_hat_end_ct += sigma_hat_count(Q_to_end_rules)
            gamma_end_ct += gamma_count(Q_to_end_rules)
            delta_end_ct += delta_count(Q_to_end_rules)

        total_len = (
            sigma_ct
            + sigma_hat_ct
            + delta_ct
            + gamma_ct
            + sigma_end_ct
            + sigma_hat_end_ct
            + gamma_end_ct
            + delta_end_ct
        )

        Q_probabilities_counts = {
            "Q_sigma_Q": sigma_ct,
            "Q_sigma_hat_Q": sigma_hat_ct,
            "Q_gamma_Q": gamma_ct,
            "Q_delta_Q": delta_ct,
            "Q_sigma_end": sigma_end_ct,
            "Q_sigma_hat_end": sigma_hat_end_ct,
            "Q_gamma_end": gamma_end_ct,
            "Q_delta_end": delta_end_ct,
        }

        Q_probabilities = {
            k: (v / float(total_len)) for k, v in Q_probabilities_counts.items()
        }

        with open(out_file, "w", encoding="utf-8") as file_handle:
            data = dict(
                S_probabilities_counts=S_probabilities_counts,
                R_probabilities_counts=R_probabilities_counts,
                Q_probabilities_counts=Q_probabilities_counts,
                S_probabilities=S_probabilities,
                R_probabilities=R_probabilities,
                Q_probabilities=Q_probabilities,
            )

            json.dump(data, file_handle, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    args = vars(GrammarTraining.get_args())
    GrammarTraining.find_probabilities(
        args.get("input_words", None), args["width"], args.get("output_file", "output")
    )
