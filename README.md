# Region Extractor
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
