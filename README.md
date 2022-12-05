## Dependencies:
- [Python3](https://www.python.org/downloads/)
- [matplotlib](https://pypi.org/project/matplotlib/)
- [openpyxl](https://pypi.org/project/openpyxl/)

_________________

## Running the pipeline:

To run the pipe line, you will need pFC53.fa and pFC8.fa fasta files.

You will need to modify or create your own `workflow_settings.ini` file, this will contain information about the gene location, and fasta file for each plasmid that the pipeline will run on.

Each `workflow_settings.ini` should contain a section for `Run Parameters`, e.g
```text
[Run Parameters]
WindowLength = 4
Paddings = 13
NumberOfRuns = 10
Plasmid = pFC53_SUPERCOILEDCR
```

These parameters specify the plasmid, window length, various paddings, and the number of runs the pipeline will do.
Each plasmid should have it's own section, e.g
```text
[pFC53_SUPERCOILED]
StartIndex = 80
EndIndex = 1829
FastaFile = pFC53
```
Each section will contain the plasmid's gene location and the associated fasta file.

To run the pipeline execute the following command,
```text
python run_workflow.py
```
This will execute batches of runs in parallel spawning 10 processes for each batch. (This can be adjusted by modifying `NUMBER_OF_PROCESSES` in the `run_workflow.py` script)

After execution, each run will be collected into folders according to run number.
Repeat above for the other plasmid, by changing the `Plasmid` parameter in the `Run Parameters` section of the `workflow_settings.ini`.

_________________

### Running the union pipeline:

To execute the `union_workflow.py` to union these runs together, we specify which runs we are merging by modifying the parameters in the `union_workflow.py` script.



