## Dependencies:
- [Python3](https://www.python.org/downloads/)
- [matplotlib](https://pypi.org/project/matplotlib/)
- [openpyxl](https://pypi.org/project/openpyxl/)

_________________

## Installation
You can install directly from GitHub using the command below,
```sh
pip install git+https://github.com/Arsuaga-Vazquez-Lab/R-loopGrammar.git
```
Or you can clone the repo and install from the repository itself.
```sh
git clone https://github.com/Arsuaga-Vazquez-Lab/R-loopGrammar.git
cd R-loopGrammar
pip install .
```
Both of these methods will install the depedencies themselves.

## Usage

After installation, you'll have access to the following programs,
- `rloop-grammar-build-model`
- `rloop-grammar-union-models`
- `rloop-grammar-predict`

These programs depend on a configuration file of plasmids/genes named `plasmids.ini`.

This file will contain the information regarding the plasmids that each program operates on, 
e.g.
```
[Plasmid1]
GeneStart = 80
GeneEnd = 1829
FastaFile = Plasmid1.fa
BEDFile = Plasmid1.bed

[Plasmid2]
GeneStart = 80
GeneEnd = 1512
FastaFile = Plasmid2.fa
BEDFile = Plasmid2.bed
```
This file defines the start and end of the gene inside the plasmid (0-based indexing, start inclusive and end exclusive), the fasta file location, and the BED file containing the experimental R-loop data.

The BED files are of the form,
```
plasmid1_rloop1 85 125
plasmid1_rloop2 67 342
...
```
These will contain the experimental results where the first index and last index are where an R-loop has been experimentally found inside the given plasmid.

1. To build a model collection we run the following,
```sh
rloop-grammar-build-model ModelCollectionOutput_%plasmid_w%width_p%padding_%number_of_models --plasmids Plasmid1 Plasmid2 -tp 10 -c 10 -w 4 -p 13
```
* `--plasmids` The plasmids which to build the model from, as defined in `plasmids.ini`.
* `-tp` The training set precentage to use for the accomponing BED file for each plasmid.
* `-c` The number of runs to generate for each model collection.
* `-w` The k-mer size.
* `-p` The padding used for the sliding windows in the critical regions.

2. To union two model collections together, we then run,
```sh
rloop-grammar-union-models UnionModelCollection_%plasmid1_%plasmid2_%number_of_models -i ModelCollectionOutput_Plasmid1_w4_p13_10 ModelCollectionOutput_Plasmid2_w4_p13_10
```
* `-i` The two input plasmids which are used to build the union model.
   
3. And finally we can then make a prediction.
```sh
rloop-grammar-predict UnionModelCollection_%plasmid1_%plasmid2_Prediction_on_%predict_plasmid_%number_of_models -i UnionModelCollection_Plasmid1_Plasmid2_10 -p Plasmid1
```
* `-i` The input model used to build the prediction.
* `-p` The plasmid used to predict upon.

