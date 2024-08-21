## Synopsis
R-loops are transient three-stranded nucleic acids that form during transcription when the nascent RNA hybridizes to the template DNA, freeing the DNA non-template strand. There is growing evidence that R-loops play important roles in physiological processes such as control of gene expression, while also contributing to chromosomal instability and disease. It is known that R-loop formation is influenced by both the sequence and the topology of the DNA substrate, but many questions remain about how R-loops form and the 3-dimensional structures that they adopt. 

Here we represent an R-loop as a word in a formal grammar called the _R-loop grammar_ and predict R-loop formation. We train the R-loop grammar on experimental data obtained by single-molecule R-loop footprinting and sequencing (SMRF-seq). Despite not containing explicit topological information, the R-loop grammar accurately predicts R-loop formation on plasmids with varying starting topologies and outperforms previous methods in R-loop prediction. 

<!---
Might need a reference for the abstract.
-->

## Experimental data set:
[Fasta & BED files](https://github.com/Arsuaga-Vazquez-Lab/R-loopGrammar/releases/download/v0.0.1-alpha/fasta_bed.zip)

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
rloop-grammar-build-model Collection_Plasmid1_runs_30 -c 30 -p 13 -w 4 --plasmids Plasmid1 -tp 10
```
* `--plasmids` The plasmids which to build the model from, as defined in `plasmids.ini`.
* `-tp` The training set precentage to use for the accomponing BED file for each plasmid.
* `-c` The number of runs to generate for each model collection.
* `-w` The k-mer size.
* `-p` The padding used for the sliding windows in the critical regions.
* `-d` (Optional) To duplicate a run utilizing the same seed or training set, use this option to select a model to copy from; this will override `-c`.

2. To union two model collections together, we then run,
```sh
rloop-grammar-union-models UnionCollection_Plasmid1_Plasmid2 -m stochastic -i Collection_Plasmid1_runs_30 Collection_Plasmid2_runs_30
```
* `-i` The two input plasmids which are used to build the union model.
* `-m` The method used to take the union, the current supported options are stochastic and deterministic.
   
3. Then we can make a prediction.
```sh
rloop-grammar-predict UnionCollection_Plasmid1_Plasmid2_predict_on_Plasmid3 -i UnionCollection_Plasmid1_Plasmid2 --plasmids Plasmid3
```
* `-i` The input model used to build the prediction.
* `-p` The plasmid used to predict upon.

4. And finally we can graph the prediction.
```sh
rloop-grammar-graph-prediction UnionCollection_Plasmid1_Plasmid2_predict_on_Plasmid3 -n Prediction_Plasmid3
```
* `-n` The name displayed on the graph.

## References

1. Stolz R, Sulthana S, Hartono SR, Malig M, Benham CJ, Chedin F. Interplay between DNA sequence and negative superhelicity drives R-loop structures. Proc Natl Acad Sci U S A. 2019 Mar 26;116(13):6260-6269. doi: 10.1073/pnas.1819476116. Epub 2019 Mar 8. PMID: 30850542; PMCID: PMC6442632.
2. Jonoska N, Obatake N, Poznanovik S, Price C, Riehl M, Vazquez M. (2021). Modeling RNA:DNA Hybrids with Formal Grammars. 10.1007/978-3-030-57129-0_3.
3. Ferrari M, Poznanovik S, Riehl M, Lusk J, Hartono S, Gonzalez G, Chedin F, Vazquez M, Jonoska N. (Submitted). The R-loop Grammar predicts R-loop formation under different topological constraints.


