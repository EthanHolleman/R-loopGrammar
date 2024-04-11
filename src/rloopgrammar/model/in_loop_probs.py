#!/usr/bin/env python3
import argparse
import numpy as np
import xlsxwriter
import json

"""
Script to find probability of a base being in an R-loop based on an input probabilistic language. Probabilities are plotted with alpha on the left and omega on the right.


Copyright 2021 Svetlana Poznanovic


"""


class Loop_probabilities:
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
            "-b",
            "--input_bed",
            metavar="BED_FILE",
            type=str,
            required=True,
            help="BED file which input file is based on",
            default=None,
        )
        parser.add_argument(
            "-l",
            "--seq_length",
            metavar="NUM_BASES",
            type=int,
            required=True,
            help="Number of bases",
            default=None,
        )
        parser.add_argument(
            "-s",
            "--plot_start",
            metavar="PLOT_START",
            type=int,
            required=True,
            help="First base to be plotted",
            default=None,
        )
        parser.add_argument(
            "-e",
            "--plot_end",
            metavar="PLOT_END",
            type=int,
            required=True,
            help="End of plot",
            default=None,
        )
        parser.add_argument(
            "-p",
            "--input_probabilities",
            metavar="PROBABILITIES_IN_FILE",
            type=str,
            required=True,
            help="Word probabilities input file",
            default=None,
        )
        parser.add_argument(
            "-o",
            "--output_file",
            metavar="OUTPUT_FILE",
            type=str,
            required=False,
            help="Output XLSX file",
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
    def in_loop_probabilities(
        cls,
        words_in,
        bed_in,
        seq_len,
        plot_start,
        plot_end,
        probabs_in,
        width,
        output_file="output",
    ):
        with open(bed_in, "r", encoding="utf-8") as file:
            bed_all_rloops = [
                list(map(int, line.split("\t")[1:3])) for line in file.readlines()
            ]

        with open(probabs_in, "r") as file:
            lines = file.readlines()

        probs = []

        for line in lines:
            prb = line.strip()
            probs.append(float(prb))

        def convert_coords(start, end):
            initial = seq_len - end[1]
            final = seq_len - start[0]

            return initial, final

        def loop_location(rloop_location):
            loop_vec = np.array([0] * seq_len)

            initial, final = convert_coords(rloop_location[1], rloop_location[0])

            for index in range(seq_len):
                if (index >= initial) and (index < final):
                    loop_vec[index] = 1

            float_array = loop_vec.astype(np.float64)
            return float_array

        expected_length = 0
        expected_start = 0
        expected_end = 0

        summary = np.array([0] * seq_len)
        summary = summary.astype(np.float64)

        for j in range(len(bed_all_rloops)):
            initial, final = convert_coords(bed_all_rloops[j][1], bed_all_rloops[j][0])

            expected_length += abs(final - initial) * probs[j]
            expected_start += initial * probs[j]
            expected_end += final * probs[j]

            summary += (
                loop_location([bed_all_rloops[j][0], bed_all_rloops[j][1]]) * probs[j]
            )

        json_dict = {
            "expected_length": expected_length,
            "expected_start": expected_start,
            "expected_end": expected_end
        }

        with open(f"{output_file}_stats.json", "w") as outfile:
            outfile.write(json.dumps(json_dict))

        data = [
            list(range(0, plot_end - plot_start)),
            summary[plot_start:plot_end].tolist(),
        ]

        headings = ["Base position", "Probability"]
        workbook = xlsxwriter.Workbook(output_file + ".XLSX")
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({"bold": 1})
        worksheet.write_row("A1", headings, bold)
        worksheet.write_column("A2", data[0])
        worksheet.write_column("B2", data[1])
        chart1 = workbook.add_chart({"type": "line"})
        chart1.add_series(
            {
                "name": "=Sheet1!$B$1",
                "categories": "=Sheet1!$A$2:$A$%d" % (plot_end - plot_start + 1),
                "values": "=Sheet1!$B$2:$B$%d" % (plot_end - plot_start + 1),
            }
        )

        chart1.set_title({"name": "Probabilities in R-loop"})
        chart1.set_x_axis({"name": "Base position"})
        chart1.set_y_axis({"name": "Probability"})
        chart1.set_style(11)

        # add chart to the worksheet with given
        # offset values at the top-left corner of
        # a chart is anchored to cell D2 .
        worksheet.insert_chart("D2", chart1, {"x_offset": 25, "y_offset": 10})
        workbook.close()


if __name__ == "__main__":
    args = vars(Loop_probabilities.get_args())
    print(args)
    Loop_probabilities.in_loop_probabilities(
        args.get("input_words", None),
        args["input_bed"],
        args.get("seq_length", None),
        args.get("plot_start", None),
        args.get("plot_end", None),
        args.get("input_probabilities", None),
        args["width"],
        args.get("output_file", "output"),
    )
