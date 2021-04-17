# 01 Regions Extractor
### Dependencies
* [OpenPyXL](https://openpyxl.readthedocs.io/en/stable/) (https://pypi.org/project/openpyxl/)

### Usage
```text
usage: 01_regions_extractor.py [-h] -f FASTA_IN_FILE -b BED_IN_FILE
                               [-ws WINDOW_LENGTH_SMALL]
                               [-wl WINDOW_LENGTH_LARGE] [-o OUTPUT_FILE] [-m]
                               -s START_INDEX -e END_INDEX [-t THRESHOLD]
                               [-p MAX_PADDING] [-l]

Regions extractor

optional arguments:
  -h, --help            show this help message and exit
  -f FASTA_IN_FILE, --input-fasta FASTA_IN_FILE
                        FASTA input file
  -b BED_IN_FILE, --input-bed BED_IN_FILE
                        BED input file
  -ws WINDOW_LENGTH_SMALL, --window_length_small WINDOW_LENGTH_SMALL
                        Number of nucleotides in small single region
  -wl WINDOW_LENGTH_LARGE, --window_length_large WINDOW_LENGTH_LARGE
                        Number of nucleotides in large single region
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Output XLSX file
  -m, --merge-regions   Merge first 1st and 2nd regions (resp. 3rd and 4th)
  -s START_INDEX, --start-index START_INDEX
                        Start index of gene region
  -e END_INDEX, --end-index END_INDEX
                        End index of gene region
  -t THRESHOLD, --threshold THRESHOLD
                        Threshold on word counts
  -p MAX_PADDING, --max-padding MAX_PADDING
                        Maximum number of nucleotides to be padded for each
                        region
  -l, --compute_large_region
                        Compute output file for large region
```

### Example
`python3 01_regions_extractor.py -f pFC53.fa -b pFC53_SUPERCOILED.bed -o pFC53_SUPERCOILED -ws 5 -s 1 -e 1929 -p 5`


# 02 Regions Threshold
### Dependencies
* [OpenPyXL](https://openpyxl.readthedocs.io/en/stable/) (https://pypi.org/project/openpyxl/)

### Usage
```text
usage: 02_regions_threshold.py [-h] [-i XLSX_IN_FILE] [-s] [-o OUTPUT_FILE]

Regions threshold

optional arguments:
  -h, --help            show this help message and exit
  -i XLSX_IN_FILE, --input-xlsx XLSX_IN_FILE
                        XLSX input file
  -s, --shannon-entropy
                        Use Shannon entropy
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Output XLSX file
```

### Example
Thresholding based on weight jump:
`python3 02_regions_threshold.py -i pFC53_SUPERCOILED_w5_weight.xlsx -o pFC53_SUPERCOILED_w5_weight_threshold`

Thresholding based on Shannon entropy:
`python3 02_regions_threshold.py -i pFC53_SUPERCOILED_w5_weight.xlsx -s -o pFC53_SUPERCOILED_w5_weight_shannon`


# 03 Training Set

### Usage
```text
usage: 03_training_set.py [-h] -i BED_IN_FILE [-n NUM_LINES] [-o OUTPUT_FILE]

Training set

optional arguments:
  -h, --help            show this help message and exit
  -i BED_IN_FILE, --input-bed BED_IN_FILE
                        BED input file
  -n NUM_LINES, --num-lines NUM_LINES
                        Create training set with NUM_LINES lines
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Output BED file
```

### Example
`python3 03_training_set.py -i pFC53_SUPERCOILED.bed_extra.bed -n 63 -o pFC53_SUPERCOILED.bed_extra_training-set.bed`


# 04 Grammar Dict
### Dependencies
* [OpenPyXL](https://openpyxl.readthedocs.io/en/stable/) (https://pypi.org/project/openpyxl/)

### Usage
```text
usage: 04_grammar_dict.py [-h] -f FASTA_IN_FILE -b BED_IN_FILE -x XLSX_IN_FILE
                          [-t XLSX_THRESHOLD_IN_FILE] -s START_INDEX -e
                          END_INDEX -w WINDOW_LENGTH [-o OUTPUT_FILE]

Regions extractor

optional arguments:
  -h, --help            show this help message and exit
  -f FASTA_IN_FILE, --input-fasta FASTA_IN_FILE
                        FASTA input file
  -b BED_IN_FILE, --input-bed BED_IN_FILE
                        BED input file
  -x XLSX_IN_FILE, --input-xlsx XLSX_IN_FILE
                        XLSX input file
  -t XLSX_THRESHOLD_IN_FILE, --input-xlsx-threshold XLSX_THRESHOLD_IN_FILE
                        XLSX threshold input file
  -s START_INDEX, --start-index START_INDEX
                        Start index of gene region
  -e END_INDEX, --end-index END_INDEX
                        End index of gene region
  -w WINDOW_LENGTH, --window-length WINDOW_LENGTH
                        Number of nucleotides in single region
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Output XLSX file
```

### Example
Without threshold input file:
`python3 04_grammar_dict.py -f pFC53.fa -b pFC53_SUPERCOILED.bed_extra_training-set.bed -o pFC53_SUPERCOILED_DICT_FULL.xlsx -s 1 -e 1929 -x pFC53_SUPERCOILED_w5_weight.xlsx -w 5`

Using threshold input file:
`python3 04_grammar_dict.py -f pFC53.fa -b pFC53_SUPERCOILED.bed_extra_training-set.bed -o pFC53_SUPERCOILED_DICT_SHANNON.xlsx -s 1 -e 1929 -x pFC53_SUPERCOILED_w5_weight.xlsx -t pFC53_SUPERCOILED_w5_weight_shannon.xlsx -w 5`


# 05 Grammar Word
### Dependencies
* [OpenPyXL](https://openpyxl.readthedocs.io/en/stable/) (https://pypi.org/project/openpyxl/)

### Usage
```text
usage: 05_grammar_word.py [-h] -f FASTA_IN_FILE -b BED_IN_FILE -j JSON_IN_FILE
                          -s START_INDEX -e END_INDEX [-w WINDOW_LENGTH]
                          [-o OUTPUT_FILE]

Regions extractor

optional arguments:
  -h, --help            show this help message and exit
  -f FASTA_IN_FILE, --input-fasta FASTA_IN_FILE
                        FASTA input file
  -b BED_IN_FILE, --input-bed BED_IN_FILE
                        BED input file
  -j JSON_IN_FILE, --input-json JSON_IN_FILE
                        JSON input file
  -s START_INDEX, --start-index START_INDEX
                        Start index of gene region
  -e END_INDEX, --end-index END_INDEX
                        End index of gene region
  -w WINDOW_LENGTH, --window-length WINDOW_LENGTH
                        Number of nucleotides in single region
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Output TXT file
```

### Example
`python3 grammar_word.py -f pFC53.fa -b pFC53_SUPERCOILED.bed_extra.bed -o pFC53_SUPERCOILED_WORDS_SHANNON.txt -s 1 -e 1929 -j pFC53_SUPERCOILED_DICT_SHANNON.xlsx.json -w 5`


# Regions Extractor
### Dependencies
* [OpenPyXL](https://openpyxl.readthedocs.io/en/stable/) (https://pypi.org/project/openpyxl/)

### Usage
```text
usage: regions_extractor.py [-h] -f FASTA_IN_FILE -b BED_IN_FILE
                            [-ws WINDOW_LENGTH_SMALL]
                            [-wl WINDOW_LENGTH_LARGE] [-o OUTPUT_FILE] [-m] -s
                            START_INDEX -e END_INDEX [-t THRESHOLD]
                            [-p MAX_PADDING] [-l]

Regions extractor

optional arguments:
  -h, --help            show this help message and exit
  -f FASTA_IN_FILE, --input-fasta FASTA_IN_FILE
                        FASTA input file
  -b BED_IN_FILE, --input-bed BED_IN_FILE
                        BED input file
  -ws WINDOW_LENGTH_SMALL, --window_length_small WINDOW_LENGTH_SMALL
                        Number of nucleotides in small single region
  -wl WINDOW_LENGTH_LARGE, --window_length_large WINDOW_LENGTH_LARGE
                        Number of nucleotides in large single region
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Output XLSX file
  -m, --merge-regions   Merge first 1st and 2nd regions (resp. 3rd and 4th)
  -s START_INDEX, --start-index START_INDEX
                        Start index of gene region
  -e END_INDEX, --end-index END_INDEX
                        End index of gene region
  -t THRESHOLD, --threshold THRESHOLD
                        Threshold on word counts
  -p MAX_PADDING, --max-padding MAX_PADDING
                        Maximum number of nucleotides to be padded for each
                        region
  -l, --compute_large_region
                        Compute output file for large region
```

### Example
`python3 regions_extractor.py -f pFC53.fa -b pFC53_SUPERCOILED.bed -o pFC53_SUPERCOILED -ws 5 -s 1 -e 1929 -p 5`


# Grammar Symbols
### Dependencies
* [OpenPyXL](https://openpyxl.readthedocs.io/en/stable/) (https://pypi.org/project/openpyxl/)

### Usage
```text
usage: grammar_symbols.py [-h] -f FASTA_IN_FILE -b BED_IN_FILE
                          [-x XLSX_IN_FILE] -s START_INDEX -e END_INDEX
                          [-n NUM_RLOOPS] [-r] [-o OUTPUT_FILE]

Regions extractor

optional arguments:
  -h, --help            show this help message and exit
  -f FASTA_IN_FILE, --input-fasta FASTA_IN_FILE
                        FASTA input file
  -b BED_IN_FILE, --input-bed BED_IN_FILE
                        BED input file
  -x XLSX_IN_FILE, --input-xlsx XLSX_IN_FILE
                        XLSX input file
  -s START_INDEX, --start-index START_INDEX
                        Start index of gene region
  -e END_INDEX, --end-index END_INDEX
                        End index of gene region
  -n NUM_RLOOPS, --num-rloops NUM_RLOOPS
                        Consider only NUM_RLOOPS rloops inside the BED file
  -r, --random-rloops   Consider only NUM_RLOOPS random rloops inside the BED
                        file
  -w WINDOW_LENGTH, --window-length WINDOW_LENGTH
                        Number of nucleotides in single region
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Output XLSX file
```

### Example
`python3 grammar_symbols.py -f pFC53.fa -b pFC53_SUPERCOILED.bed_extra.bed -o pFC53_SUPERCOILED_GRAMMAR.xlsx -n 63 -r -s 1 -e 1929 -x pFC53_SUPERCOILED_w5_weight_extra.xlsx -w 5`


# Grammar Dict
### Dependencies
* [OpenPyXL](https://openpyxl.readthedocs.io/en/stable/) (https://pypi.org/project/openpyxl/)

### Usage
```text
usage: grammar_dict.py [-h] -f FASTA_IN_FILE -b BED_IN_FILE [-x XLSX_IN_FILE]
                       -s START_INDEX -e END_INDEX [-n NUM_RLOOPS] [-r]
                       [-w WINDOW_LENGTH] [-o OUTPUT_FILE]

Regions extractor

optional arguments:
  -h, --help            show this help message and exit
  -f FASTA_IN_FILE, --input-fasta FASTA_IN_FILE
                        FASTA input file
  -b BED_IN_FILE, --input-bed BED_IN_FILE
                        BED input file
  -x XLSX_IN_FILE, --input-xlsx XLSX_IN_FILE
                        XLSX input file
  -s START_INDEX, --start-index START_INDEX
                        Start index of gene region
  -e END_INDEX, --end-index END_INDEX
                        End index of gene region
  -n NUM_RLOOPS, --num-rloops NUM_RLOOPS
                        Consider only NUM_RLOOPS rloops inside the BED file
  -r, --random-rloops   Consider only NUM_RLOOPS random rloops inside the BED
                        file
  -w WINDOW_LENGTH, --window-length WINDOW_LENGTH
                        Number of nucleotides in single region
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Output XLSX file
```

### Example
`python3 grammar_dict.py -f pFC53.fa -b pFC53_SUPERCOILED.bed_extra.bed -o pFC53_SUPERCOILED_DICT.xlsx -n 63 -r -s 1 -e 1929 -x pFC53_SUPERCOILED_w5_weight_extra.xlsx -w 5`