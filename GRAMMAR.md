# Generating Grammar

## Parsing Block

For each R-Loop in the bed file (bed_extra.bed) the plasmid's sequence is partitioned into **before**, **inside** and **after** based on the start and ends of the genomic region in the bed file.

*We trim the sequence from the FASTA file to match the sequence of the gene.*

**TODO: INVESTIGATE START AND END, 0 BASED?**

Let `sequence = sequence[gene_start:gene_end]`

For each genomic region,

- **Before** consists of `sequence[0:start]`
- **Inside** consists of `sequence[start:end]`
- **After** consists of `sequence[end:]`

We then also make note of the reverse of each of these parsing blocks, **Before-Reversed**, **Inside-Reversed**, and **After-Reversed**.

We create a dictionary, where each key is a string consisting of the the start of the region, the end of the region, and the current row of the bed file.

The value of each key, being a object consistening of every possible contiguous n-tuple inside each parsing block, and it's reverse.

#### Example Parsing Block Dictionary Entry

For example, suppose we have the sequence 

`ATCGATCGATCGATCG`

**TODO: (N % n-tuple_size != 0) NUMBER OF CHARACTERS**

 with n-tuple size 2, and and start and end starting at 8 to 12.

 Entry-Key: `8_12_0` (0th R-Loop)

- Before: `ATCGATCG`
	- `['AT', 'CG', 'AT', 'CG']`
- Before-Reversed: `GCTAGCTA`
	- `['GC', 'TA', 'GC', 'TA']`	
- Inside: `ATCG`
	- `['AT', 'CG']`
- Inside-Reversed: `GCTA`
	- `['GC', 'TA']`
- After: `ATCG`
	- `['AT', 'CG']`
- After-Reversed: `GCTA` 
	- `['GC', 'TA']`

### Reading Thresholded Weights and Non-thresholded Weight Files

Read in n-tuples and weights from all 4 regions in both the thresholded and non-thresholded weight files.

Let **regions** be the regions from the thresholded weights, and **extra-regions** be the regions from the non-thresholded weighted file.

### Generating Symbols

For each key in the parsing block dictionary, we look at the the **i**th entry for
- Before, **N1**
- Inside-Reversed, **N2**
- After-Reversed, **N3** 

If there is an **i**th entry for that respective section, we first find the occurences of that entry in each region.

For each region that it may be in, we obtain the weight, and place it in a list.

#### Example in Thresholded Regions

Suppose for `AT`, it exists in region 1 with weight 0.2 and in region 4 with weight 0.3,

We'd generate the following: `W4_0.3_W1_0.2`

#### Not in Thresholded Regions

If the entry is not in any thresholded region, we then check how often this occurs in each parsing block. 

#### Example

In the above example, for entry `'AT'`,

We'd generate the following: `N1_2_N2_0_N3_0`

#### Continued

If the entry was found in either the parsing blocks, or the thresholded weight file we take the maximum values respectively.

If the max is achieved for more than one N-Value, we then instead look to the non-thresholded file. If the entry is not found in this file, we assign $$\gamma$$ to this entry; otherwise we generate an entry similar to the example where it was found in the thresholded region, e.g `W4_0.3_W1_0.2`.

**TODO: INVESTIGATE LINES 394-402**

Next, we assign possible letters for this entry, since it's parsing block 1 (**N1**), we are only expecting to see $$\sigma$$, and $$\hat{\sigma}$$.

We use the following mapping,

    GREEK_MAPPING_R1 = {
        'W1': __sigma_hat,
        'W2': __sigma_hat,
        'W3': __sigma,
        'W4': __sigma,
        'N1': __sigma_hat, # after R-loop
        'N2': __gamma,     # This may not be needed
        'N3': __sigma,     # before R-loop
        'FORCE_GAMMA': __gamma
    }

In the event we have both a $$\sigma$$, and $$\hat{\sigma}$$, we instead replace this with a $$\delta$$.

**TODO: DOES THIS ONLY HAPPEN WHEN THE WEIGHTS ARE THE SAME?**

#### Example Symbols

For example, suppose we have the entry with the following, `N1_2_N2_0_N3_0`

We'd know that this would be assigned $$\hat{\sigma}$$.

If instead we had found this in our thresholded values and obtained, `W4_0.3_W1_0.2`, we'd see that we generate the symbol $$\sigma$$.

#### Next Parsing Block

For **N2**, we do much the same as for **N1**, except for $$\gamma$$, we generate $$\rho$$ when the entry is not found in the non-thresholded weights.

**TODO: INSPECT ALPHA AND OMEGA AND HOW THEY RELATE THE LAST CELL, APPEARS TO ONLY BE VALUES FROM RANGE 0 TO N-TUPLE SIZE.**

# Grammar Word

Do the exact same dictionary generation, relating back to the parsing block regions; except using a random sample of `TRAINING_SET_SIZE` of the original bed file (bed extra), in this case 63, roughly 10% of the data. 

For each of the the dictionary object entries, we interate through **Before**, **Inside-Reversed**, and **After-Reversed**.

For each entry in **Before** (inside the training set), we check the coresponding grammar dictionary entry for **Before** parsing block we find compare n-tuples until we have a match, if a match is found we use the resulting symbol, otherwise we use $$\gamma$$. 

We do the same for **Inside-Reversed**, and **After-Reversed**; except replacing $$\gamma$$ with $$\rho$$ for the inside region, respectively.

Then we output a new file, containing the dictionary key name, and the concatenated symbols together, for each line of the training set bed file.

We do this same logic for every possible R-Loop as well.

# Grammar Training

For each line in the grammar training set file, we count the number of sigmas, sigma_hats, gammas, etc.

We then count the number of taus, tau_hats, rho's, betas, etc.


