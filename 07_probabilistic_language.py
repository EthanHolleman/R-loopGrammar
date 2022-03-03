#!/usr/bin/env python3

import argparse
import importlib
import sys


"""
Script to train a grammar based on a set of  words for R-loops.


Copyright 2021 Svetlana Poznanovic

"""


class Probabilistic_Language:

    @classmethod
    def get_args(cls):
        parser = argparse.ArgumentParser(description='Find probabilities')
        parser.add_argument('-w', '--input_words', metavar='WORDS_IN_FILE', type=str, required=True,
                            help='WORDS input file', default=None)
        parser.add_argument('-p', '--input_probabilities', metavar='PROBABILITIES_IN_FILE', type=str, required=True,
                            help='Probabilities input file', default=None)
        parser.add_argument('-o', '--output_file', metavar='OUTPUT_FILE', type=str, required=False,
                            help='Output TXT file', default='output')
        return parser.parse_args()
        
    @classmethod
    def word_probabilities(cls, words_in, probabs_in, out_file='output'):

        
        module = importlib.import_module(probabs_in, package=None)

        p01 = module.p01
        p02 = module.p02
        p03 = module.p03
        p04 = module.p04
        p05 = module.p05
        p06 = module.p06
        p07 = module.p07
        p08 = module.p08
        p09 = module.p09
        p10 = module.p10
        p11 = module.p11
        p12 = module.p12
        p13 = module.p13
        p14 = module.p14
        p15 = module.p15
        p16 = module.p16
        p17 = module.p17
        p18 = module.p18
        p19 = module.p19
        p20 = module.p20
        p21 = module.p21
        p22 = module.p22
        p23 = module.p23
        p24 = module.p24
        p25 = module.p25
        p26 = module.p26
        p27 = module.p27
        p28 = module.p28
        p29 = module.p29
        p30 = module.p30
        p31 = module.p31
        p32 = module.p32
        p33 = module.p33
        p34 = module.p34
        p35 = module.p35
        
        
        with open(words_in, "r", encoding='utf-8') as file:
            lines = file.readlines()

        language_greek = []
      
        for line in lines:
            parsing = line.split(":")[1].strip()
            language_greek.append(parsing)
    
        language = []
    
        for word in language_greek:
            word = word.replace('σ^', 'h')
            word = word.replace('σ', 's')
            word = word.replace('δ', 'd')
            word = word.replace('γ', 'g')
            word = word.replace('τ^', 'H')
            word = word.replace('τ', 'T')
            word = word.replace('ρ', 'R')
            word = word.replace('β', 'B')
            word = word.replace('ω0', 'o')
            word = word.replace('ω1', 'p')
            word = word.replace('ω2', 'q')
            word = word.replace('ω3', 'u')
            word = word.replace('ω4', 'v')
            word = word.replace('α0', 'O')
            word = word.replace('α1', 'P')
            word = word.replace('α2', 'Q')
            word = word.replace('α3', 'U')
            word = word.replace('α4', 'V')
            language.append(word[::-1])
        
        def prob(word):
            product = 1
            i=1
            while word[i] != 'O' and word[i] != 'P' and word[i] != 'Q' and word[i] != 'U' and word[i] != 'V':
                if word[i] == 's':
                    product = product *p05
                elif word[i] == 'h':
                    product = product *p06
                elif word[i] == 'g':
                    product = product *p07
                elif word[i] == 'd':
                    product = product *p08
                i+=1
            if word[i] == 'O':
                product = product *p09
            elif word[i] == 'P':
                product = product *p10
            elif word[i] == 'Q':
                product = product *p11
            elif word[i] == 'U':
                product = product *p12
            elif word[i] == 'V':
                product = product *p13
            i+=1
            if word[i] == 'T':
                product = product *p14
            elif word[i] == 'H':
                product = product *p15
            elif word[i] == 'R':
                product = product *p16
            elif word[i] == 'B':
                product = product *p17
            i+=1
            while word[i] != 'o' and word[i] != 'p' and word[i] != 'q' and word[i] != 'u' and word[i] != 'v':
                if word[i] == 'T':
                    product = product *p18
                elif word[i] == 'H':
                    product = product *p19
                elif word[i] == 'R':
                    product = product *p20
                elif word[i] == 'B':
                    product = product *p21
                i+=1
            if word[i] == 'o':
                product = product *p22
            elif word[i] == 'p':
                product = product *p23
            elif word[i] == 'q':
                product = product *p24
            elif word[i] == 'u':
                product = product *p25
            elif word[i] == 'v':
                product = product *p26
            i+=1
            if word[i] == 's':
                product = product *p27
            elif word[i] == 'h':
                product = product *p28
            elif word[i] == 'g':
                product = product *p29
            elif word[i] == 'd':
                product = product *p30
            i+=1
            while i < len(word):
                if word[i] == 's': 
                    product = product *p31
                elif word[i] == 'h':
                    product = product *p32
                elif word[i] == 'g':
                    product = product *p33
                elif word[i] == 'd':
                    product = product *p34
                i+=1
            return product
        
        probabilities = []

        i=0
        while i < len(language):
            print(i)
            #print(language[i])
            c = prob(language[i])
            probabilities.append(c) 
            i +=1
            print(c)
            #sys.exit()
    
        partition_function =  0
        for term in probabilities:
             partition_function += term
    
        print("The partition function is: ", partition_function)
    
        probs = [term/partition_function for term in probabilities]  

        with open(out_file, "a") as file_handle:
            for i in probs:
                file_handle.write(str(i)+"\n")
    
        
    

if __name__ == '__main__':
    args = vars(Probabilistic_Language.get_args())
    Probabilistic_Language.word_probabilities(args.get('input_words', None), args.get('input_probabilities', None), args.get('output_file', 'output'))

