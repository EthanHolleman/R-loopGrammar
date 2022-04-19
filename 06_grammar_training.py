#!/usr/bin/env python3
import argparse


"""
Script to train a grammar based on a set of  words for R-loops.


Copyright 2021 Svetlana Poznanovic

"""

def split_word(word):
    temp = word.replace('o', '-')
    temp = temp.replace('p', '-')
    temp = temp.replace('q', '-')
    temp = temp.replace('u', '-')
    temp = temp.replace('v', '-')
    temp = temp.replace('O', '-')
    temp = temp.replace('P', '-')
    temp = temp.replace('Q', '-')
    temp = temp.replace('U', '-')
    temp = temp.replace('V', '-')
 
    
    return temp.split('-')
    
def initial_part(word):
    begin = split_word(word)[2]
    return begin[:-1]
    
def r_loop_start(word):
    inside = split_word(word)[1]
    after_alpha = inside[-1]
    return after_alpha
    
def inside_rloop(word):
    inside = split_word(word)[1]
    really_inside = inside[:-1]
    return really_inside

def after_omega(word):
    end = split_word(word)[0]
    after_omega = end[-1]
    return after_omega
    
def end_loop(word):
    end = split_word(word)[0]
    end_of_loop = end[:-1]
    return end_of_loop

    
def sigma_count(word):
    return word.count('s')
    
def sigma_hat_count(word):
    return word.count('h')
    
def gamma_count(word):
    return word.count('g')
    
def delta_count(word):
    return word.count('d')
    
def tau_count(word):
    return word.count('T')
    
def tau_hat_count(word):
    return word.count('H')
    
def rho_count(word):
    return word.count('R')
    
def beta_count(word):
    return word.count('B')
    
def omega_count(word):
    return word.count('o')
    
def alpha_count(word):
    return word.count('O')
    
    

class GrammarTraining:


    @classmethod
    def get_args(cls):
        parser = argparse.ArgumentParser(description='Find probabilities')
        parser.add_argument('-i', '--input_words', metavar='WORDS_IN_FILE', type=str, required=True,
                            help='WORDS input file', default=None)
        parser.add_argument('-o', '--output_file', metavar='OUTPUT_FILE', type=str, required=False,
                            help='Output TXT file', default='output')
        parser.add_argument('-w', '--width', metavar='WIDTH', type=int, required=True, help='N-Tuple size')
        return parser.parse_args()

    @classmethod
    def find_probabilities(cls, words_in, width, out_file='output'):
        with open(words_in, 'r', encoding='utf-8') as fin:
            lines = fin.readlines()
            
        
        training_words_greek =[]
        for line in lines:    
            parsing = line.split(":")[1].strip()
            training_words_greek.append(parsing)
            
        training_words = []
        for word in training_words_greek:
            word = word.replace('σ^', 'h')
            word = word.replace('σ', 's')
            word = word.replace('δ', 'd')
            word = word.replace('γ', 'g')
            word = word.replace('τ^', 'H')
            word = word.replace('τ', 'T')
            word = word.replace('ρ', 'R')
            word = word.replace('β', 'B')

            for i in range(width):
                word = word.replace(f'ω{i}', 'o')
                word = word.replace(f'\xcf\x89{i}', 'o')
                word = word.replace(f'α{i}', 'O')
                word = word.replace(f'\xce\xb1{i}', 'O')

            word = word.replace('\xcf\x83^', 'h')
            word = word.replace('\xcf\x83', 's')
            word = word.replace('\xce\xb4', 'd')
            word = word.replace('\xce\xb3', 'g')
            word = word.replace('\xcf\x84^', 'H')
            word = word.replace('\xcf\x84', 'T')
            word = word.replace('\xcf\x81', 'R')
            word = word.replace('\xce\xb2', 'B')
            word = word.replace('\xcf\x890', 'o')
            word = word.replace('\xcf\x891', 'p')
            word = word.replace('\xcf\x892', 'q')
            word = word.replace('\xcf\x893', 'u')
            word = word.replace('\xcf\x894', 'v')
            word = word.replace('\xce\xb10', 'O')
            word = word.replace('\xce\xb11', 'P')
            word = word.replace('\xce\xb12', 'Q')
            word = word.replace('\xce\xb13', 'U')
            word = word.replace('\xce\xb14', 'V')
            training_words.append(word)
            
        p01 = 0.25
        p02 = 0.25
        p03 = 0.25
        p04 = 0.25    
            
            
        sigma_ct = 0   
        sigma_hat_ct = 0 
        gamma_ct = 0
        delta_ct =0
        alpha_ct = 0

        for word in training_words:
            sigma_ct += sigma_count(initial_part(word))
            sigma_hat_ct += sigma_hat_count(initial_part(word))
            gamma_ct += gamma_count(initial_part(word))
            delta_ct += delta_count(initial_part(word))
            alpha_ct += alpha_count(word)

        total_len = sigma_ct + sigma_hat_ct + gamma_ct + delta_ct + alpha_ct
        
        p05 = sigma_ct/float(total_len)
        p06 = sigma_hat_ct/float(total_len)
        p07 = gamma_ct/float(total_len)
        p08 = delta_ct/float(total_len)

        alpha_probability = 1 - ((alpha_ct / total_len) / width)

        
        tau_ct = 0
        tau_hat_ct = 0
        rho_ct = 0
        beta_ct =0
        for word in training_words:
            tau_ct += tau_count(r_loop_start(word))
            tau_hat_ct += tau_hat_count(r_loop_start(word))
            rho_ct += rho_count(r_loop_start(word))
            beta_ct += beta_count(r_loop_start(word))
        total_len = tau_ct + tau_hat_ct + rho_ct + beta_ct
        p14 = tau_ct/float(total_len)
        p15 = tau_hat_ct/float(total_len)
        p16 = rho_ct/float(total_len)
        p17 = beta_ct/float(total_len)
        
        tau_ct = 0   
        tau_hat_ct = 0 
        rho_ct = 0
        beta_ct =0
        omega_ct = 0

        for word in training_words:
            tau_ct += tau_count(inside_rloop(word))
            tau_hat_ct += tau_hat_count(inside_rloop(word))
            rho_ct += rho_count(inside_rloop(word))
            beta_ct += beta_count(inside_rloop(word))
            omega_ct += omega_count(word)

        total_len = tau_ct + tau_hat_ct + rho_ct + beta_ct + omega_ct
        
        p18 = tau_ct/float(total_len)
        p19 = tau_hat_ct/float(total_len)
        p20 = rho_ct/float(total_len)
        p21 = beta_ct/float(total_len)

        omega_probability = 1 - ((omega_ct / total_len) / width)
        
        sigma_ct = 0   
        sigma_hat_ct = 0 
        gamma_ct = 0
        delta_ct =0
        
        for word in training_words:
            sigma_ct += sigma_count(after_omega(word))
            sigma_hat_ct += sigma_hat_count(after_omega(word))
            gamma_ct += gamma_count(after_omega(word))
            delta_ct += delta_count(after_omega(word))
            
        total_len = sigma_ct + sigma_hat_ct + gamma_ct + delta_ct 
        
        p27 = sigma_ct/float(total_len)
        p28 = sigma_hat_ct/float(total_len)
        p29 = gamma_ct/float(total_len)
        p30 = delta_ct/float(total_len)
        
        sigma_ct = 0   
        sigma_hat_ct = 0 
        gamma_ct = 0
        delta_ct =0
        
        for word in training_words:
            sigma_ct += sigma_count(end_loop(word))
            sigma_hat_ct += sigma_hat_count(end_loop(word))
            gamma_ct += gamma_count(end_loop(word))
            delta_ct += delta_count(end_loop(word))
            
        total_len = sigma_ct + sigma_hat_ct + gamma_ct + delta_ct +len(training_words)
        
        p31 = sigma_ct/float(total_len)
        p32 = sigma_hat_ct/float(total_len)
        p33 = gamma_ct/float(total_len)
        p34 = delta_ct/float(total_len)
        p35 = len(training_words)/float(total_len)
        
        
            
        with open(out_file, 'a') as fout:
            fout.write('p01 = ' +  str(p01) +'\n')  
            fout.write('p02 = ' +  str(p02) +'\n') 
            fout.write('p03 = ' +  str(p03) +'\n')
            fout.write('p04 = ' +  str(p04) +'\n')
            fout.write('p05 = ' +  str(p05) +'\n')
            fout.write('p06 = ' +  str(p06) +'\n')
            fout.write('p07 = ' +  str(p07) +'\n')
            fout.write('p08 = ' +  str(p08) +'\n')

            fout.write('alpha_probability = ' +  str(alpha_probability) +'\n')
           
            fout.write('p14 = ' +  str(p14) +'\n')
            fout.write('p15 = ' +  str(p15) +'\n')
            fout.write('p16 = ' +  str(p16) +'\n')
            fout.write('p17 = ' +  str(p17) +'\n')
            fout.write('p18 = ' +  str(p18) +'\n')
            fout.write('p19 = ' +  str(p19) +'\n')
            fout.write('p20 = ' +  str(p20) +'\n')
            fout.write('p21 = ' +  str(p21) +'\n')
            
            fout.write('omega_probability = ' +  str(omega_probability) +'\n')

            fout.write('p27 = ' +  str(p27) +'\n')
            fout.write('p28 = ' +  str(p28) +'\n')
            fout.write('p29 = ' +  str(p29) +'\n')
            fout.write('p30 = ' +  str(p30) +'\n')    
            fout.write('p31 = ' +  str(p31) +'\n')
            fout.write('p32 = ' +  str(p32) +'\n')
            fout.write('p33 = ' +  str(p33) +'\n')
            fout.write('p34 = ' +  str(p34) +'\n')
            fout.write('p35 = ' +  str(p35) +'\n')    
            
            
                   
        


if __name__ == '__main__':
    args = vars(GrammarTraining.get_args())
    GrammarTraining.find_probabilities(args.get('input_words', None), args['width'], args.get('output_file', 'output'))



