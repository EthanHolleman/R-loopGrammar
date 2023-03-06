import openpyxl
import openpyxl.chart
import glob
import collections
import pathlib
import matplotlib.pyplot as pyplot
import re
import os

PLASMID = 'pFC53'
DATA = True
REGEX_PATTERN = r'p(\d*)_w(\d*)'


def main() -> None:
    files = glob.glob(f'{PLASMID}*base_in_loop_avg_probs.xlsx')
    print(files)
    average_probabilities_list = None

    for file in files:
        wb = openpyxl.load_workbook(file)
        ws = wb.active

        m = re.match(r'^.*_w\d_(\d*)_', file)
        run_number = int(m[1])

        row_value_iter = iter(ws.values)
        next(row_value_iter) # Skip the column header

        probabilities = collections.defaultdict(lambda : 0)
        for row in row_value_iter:
            base_position, probability = row
            base_position = int(base_position)
            probability = float(probability)

            probabilities[base_position] = probabilities[base_position] + probability

        probabilities_list = [probabilities[k] for k in range(1, len(probabilities.keys()) + 1)]
        if not average_probabilities_list:
            average_probabilities_list = probabilities_list
        else:
            average_probabilities_list = [sum(value) for value in zip(average_probabilities_list, probabilities_list)]

        if DATA:
            pyplot.plot(list(range(1, len(probabilities_list) + 1)), probabilities_list, label=f'Run {run_number}')

    div_by_file_len = lambda x: x / len(files)
    average_probabilities_list = list(map(div_by_file_len, average_probabilities_list))

    wb = openpyxl.load_workbook(F"{PLASMID}_gyrase_experimental.xlsx")
    ws = wb.active

    row_value_iter = iter(ws.values)
    next(row_value_iter) # Skip the column header

    probabilities = collections.defaultdict(lambda : 0)
    for row in row_value_iter:
        base_position, probability = row
        base_position = int(base_position)
        probability = float(probability)

        probabilities[base_position] = probability

    probabilities_list = [probabilities[k] for k in range(1, len(probabilities.keys()))]
    pyplot.plot(list(range(1, len(probabilities_list) + 1)), probabilities_list, label=f'Experimental')
    pyplot.plot(list(range(1, len(average_probabilities_list) + 1)), average_probabilities_list, '--', label=f'Average')

    row_value_iter = iter(ws.values)
    next(row_value_iter) # Skip the column header

    pyplot.plot()

    m = re.search(r'p(\d*)_w(\d*)', os.path.basename(os.getcwd()))

    padding = m[1]
    width = m[2]

    pyplot.figtext(.75, .2, f"Width = {width}\nPadding = {padding}")
    pyplot.legend()
    pyplot.title(f"(Avg Probs) (pFC8 $\cup$ pFC53) GYRASE Experimental & Prediction on {PLASMID}")
    pyplot.xlabel("Base Position")
    pyplot.ylabel("Probability")
    pyplot.savefig(f'{PLASMID}_{os.path.basename(os.getcwd())}_avg_exp{"_data" if DATA else ""}_avg_probs.png', dpi=1200)
    pyplot.show()

if __name__ == "__main__":
    main()