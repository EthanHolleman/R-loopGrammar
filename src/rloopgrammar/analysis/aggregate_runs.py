import glob
import shutil
import os
import pathlib

PLASMID = 'pFC53'
WINDOW_SIZE = 3

def main() -> None:
	paddings = [6, 12, 18]
	for padding in paddings:
		run_folders = glob.glob(f'{PLASMID}_p{padding}_w{WINDOW_SIZE}_*')
		aggregate_folder_name = f'aggregate_{PLASMID}_p{padding}_w{WINDOW_SIZE}_runs_{len(run_folders)}'

		try:
			os.mkdir(aggregate_folder_name)
		except FileExistsError:
			pass

		for run_folder in run_folders:
			shutil.copyfile(
				pathlib.Path(run_folder, f'{PLASMID}_SHANNON_p{padding}_w{WINDOW_SIZE}_base_in_loop.xlsx'),
				pathlib.Path(aggregate_folder_name, f'{PLASMID}_SHANNON_p{padding}_w{WINDOW_SIZE}_base_in_loop_{run_folder[-1]}.xlsx')
			)

if __name__ == "__main__":
	main()