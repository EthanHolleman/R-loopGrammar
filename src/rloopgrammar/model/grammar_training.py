#!/usr/bin/env python3
import argparse
import enum
import json
import collections

"""
Script to train a grammar based on a set of  words for R-loops.


Copyright 2021 Svetlana Poznanovic

"""

smoothing_parameter = 1


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

        omega_counts = collections.defaultdict(int)
        alpha_counts = collections.defaultdict(int)

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
                omega_counts[i] += word.count(f"ω{i}")
                alpha_counts[i] += word.count(f"α{i}")

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

        sigma_ct = smoothing_parameter
        sigma_hat_ct = smoothing_parameter
        gamma_ct = smoothing_parameter
        delta_ct = smoothing_parameter

        sigma_alpha_ct = smoothing_parameter
        sigma_hat_alpha_ct = smoothing_parameter
        gamma_alpha_ct = smoothing_parameter
        delta_alpha_ct = smoothing_parameter

        # reverse each so we read from left to right
        for word in map(lambda x: x[::-1], training_words):
            up_to_alpha_part = up_to_alpha(word)
            S_to_S_transitions = up_to_alpha_part[:-2]
            S_to_R_transitions = up_to_alpha_part[-2:]

            sigma_ct += sigma_count(S_to_S_transitions)
            sigma_hat_ct += sigma_hat_count(S_to_S_transitions)
            gamma_ct += gamma_count(S_to_S_transitions)
            delta_ct += delta_count(S_to_S_transitions)

            sigma_alpha_ct += sigma_count(S_to_R_transitions)
            sigma_hat_alpha_ct += sigma_hat_count(S_to_R_transitions)
            gamma_alpha_ct += gamma_count(S_to_R_transitions)
            delta_alpha_ct += delta_count(S_to_R_transitions)

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

        def alter_key_name(key):
            segments = key.split("_")
            new_segments = segments[:3] + ["i"] + segments[3:]
            return "_".join(new_segments)

        S_probabilities = {
            k
            if "alpha" not in k
            else alter_key_name(k): (v / float(total_len))
            if "alpha" not in k
            else (v / float(total_len) / width)
            for k, v in S_probabilities_counts.items()
        }

        tau_ct = smoothing_parameter
        tau_hat_ct = smoothing_parameter
        rho_ct = smoothing_parameter
        beta_ct = smoothing_parameter

        tau_omega_ct = smoothing_parameter
        tau_hat_omega_ct = smoothing_parameter
        rho_omega_ct = smoothing_parameter
        beta_omega_ct = smoothing_parameter

        for word in map(lambda x: x[::-1], training_words):
            after_alpha_to_omega_part = after_alpha_to_omega(word)
            R_to_R_transitions = after_alpha_to_omega_part[:-2]
            R_to_Q_transitions = after_alpha_to_omega_part[-2:]

            tau_ct += tau_count(R_to_R_transitions)
            tau_hat_ct += tau_hat_count(R_to_R_transitions)
            rho_ct += rho_count(R_to_R_transitions)
            beta_ct += beta_count(R_to_R_transitions)

            tau_omega_ct += tau_count(R_to_Q_transitions)
            tau_hat_omega_ct += tau_hat_count(R_to_Q_transitions)
            rho_omega_ct += rho_count(R_to_Q_transitions)
            beta_omega_ct += beta_count(R_to_Q_transitions)

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
            k
            if "omega" not in k
            else alter_key_name(k): (v / float(total_len))
            if "omega" not in k
            else (v / float(total_len) / width)
            for k, v in R_probabilities_counts.items()
        }

        sigma_ct = smoothing_parameter
        sigma_hat_ct = smoothing_parameter
        gamma_ct = smoothing_parameter
        delta_ct = smoothing_parameter

        sigma_end_ct = smoothing_parameter
        sigma_hat_end_ct = smoothing_parameter
        gamma_end_ct = smoothing_parameter
        delta_end_ct = smoothing_parameter

        # reverse each so we read from left to right
        for word in map(lambda x: x[::-1], training_words):
            after_omega_part = after_omega(word)
            Q_to_Q_transitions = after_omega_part[:-1]
            Q_to_end_transitions = after_omega_part[-1:]

            sigma_ct += sigma_count(Q_to_Q_transitions)
            sigma_hat_ct += sigma_hat_count(Q_to_Q_transitions)
            gamma_ct += gamma_count(Q_to_Q_transitions)
            delta_ct += delta_count(Q_to_Q_transitions)

            sigma_end_ct += sigma_count(Q_to_end_transitions)
            sigma_hat_end_ct += sigma_hat_count(Q_to_end_transitions)
            gamma_end_ct += gamma_count(Q_to_end_transitions)
            delta_end_ct += delta_count(Q_to_end_transitions)

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
