import os
import re

from pathlib import Path

RUNS = 10

if __name__ == "__main__":
    m = re.search(r'p(\d*)_w(\d*)', os.path.basename(os.getcwd()))

    padding = m[1]
    width = m[2]

    run_folders = [(r, Path('_'.join(map(str, ["UNION", f'p{padding}', f'w{width}', r])))) for r in range(RUNS)]

    prob_keys = None
    probs = None

    for run, folder in run_folders:
        probs_lang_filename = Path('_'.join(map(str, 
            ['SHANNON', f'p{padding}', f'w{width}', f'{run}', 'union', 'probabilities.py']))
        )

        with open(folder / probs_lang_filename, 'r') as probs_file:
            file_lines = probs_file.readlines()

            #extract the key's e.g key = value
            if not prob_keys:
                prob_keys = list(map(lambda x: x.split('=')[0], file_lines))

            file_probs = list(map(lambda x: float(x.split('=')[1]), file_lines))
            if not probs:
                probs = file_probs
            else:
                probs = [sum(value) for value in zip(probs, file_probs)]

    probs_avg = list(map(lambda x: x / RUNS, probs))
    key_values = zip(prob_keys, probs_avg)

    with open('_'.join(map(str, ["UNION", f'p{padding}', f'w{width}', 'probabilities_average.py'])), 'w') as probs_avg:
        for k, v in key_values:
            probs_avg.write(f'{k} = {v}\n')





