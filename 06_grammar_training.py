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
    
def omega_0_count(word):
    return word.count('o')
    
def omega_1_count(word):
    return word.count('p')
    
def omega_2_count(word):
    return word.count('q')
    
def omega_3_count(word):
    return word.count('u')
    
def omega_4_count(word):
    return word.count('v')
    
def alpha_0_count(word):
    return word.count('O')
    
def alpha_1_count(word):
    return word.count('P')
    
def alpha_2_count(word):
    return word.count('Q')
    
def alpha_3_count(word):
    return word.count('U')
    
def alpha_4_count(word):
    return word.count('V')
            
    
    

class GrammarTraining:


    @classmethod
    def get_args(cls):
        parser = argparse.ArgumentParser(description='Find probabilities')
        parser.add_argument('-w', '--input_words', metavar='WORDS_IN_FILE', type=str, required=True,
                            help='WORDS input file', default=None)
        parser.add_argument('-o', '--output_file', metavar='OUTPUT_FILE', type=str, required=False,
                            help='Output TXT file', default='output')
        return parser.parse_args()

    @classmethod
    def find_probabilities(cls, words_in, out_file='output'):
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
        a0_ct = 0
        a1_ct = 0
        a2_ct = 0
        a3_ct = 0
        a4_ct = 0
        for word in training_words:
            sigma_ct += sigma_count(initial_part(word))
            sigma_hat_ct += sigma_hat_count(initial_part(word))
            gamma_ct += gamma_count(initial_part(word))
            delta_ct += delta_count(initial_part(word))
            a0_ct += alpha_0_count(word)
            a1_ct += alpha_1_count(word)
            a2_ct += alpha_2_count(word)
            a3_ct += alpha_3_count(word)
            a4_ct += alpha_4_count(word)
        total_len = sigma_ct + sigma_hat_ct + gamma_ct + delta_ct + a0_ct + a1_ct + a2_ct + a3_ct + a4_ct
        
        p05 = sigma_ct/float(total_len)
        p06 = sigma_hat_ct/float(total_len)
        p07 = gamma_ct/float(total_len)
        p08 = delta_ct/float(total_len)
        p09 = a0_ct/float(total_len)
        p10 = a1_ct/float(total_len)
        p11 = a2_ct/float(total_len)
        p12 = a3_ct/float(total_len)
        p13 = a4_ct/float(total_len)
        
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
        w0_ct = 0
        w1_ct = 0
        w2_ct = 0
        w3_ct = 0
        w4_ct = 0
        for word in training_words:
            tau_ct += tau_count(inside_rloop(word))
            tau_hat_ct += tau_hat_count(inside_rloop(word))
            rho_ct += rho_count(inside_rloop(word))
            beta_ct += beta_count(inside_rloop(word))
            w0_ct += omega_0_count(word)
            w1_ct += omega_1_count(word)
            w2_ct += omega_2_count(word)
            w3_ct += omega_3_count(word)
            w4_ct += omega_4_count(word)
        total_len = tau_ct + tau_hat_ct + rho_ct + beta_ct + w0_ct + w1_ct + w2_ct + w3_ct + w4_ct
        
        p18 = tau_ct/float(total_len)
        p19 = tau_hat_ct/float(total_len)
        p20 = rho_ct/float(total_len)
        p21 = beta_ct/float(total_len)
        p22 = w0_ct/float(total_len)
        p23 = w1_ct/float(total_len)
        p24 = w2_ct/float(total_len)
        p25 = w3_ct/float(total_len)
        p26 = w4_ct/float(total_len)
        
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
            fout.write('p09 = ' +  str(p09) +'\n')
            fout.write('p10 = ' +  str(p10) +'\n')
            fout.write('p11 = ' +  str(p11) +'\n')
            fout.write('p12 = ' +  str(p12) +'\n')
            fout.write('p13 = ' +  str(p13) +'\n')
            fout.write('p14 = ' +  str(p14) +'\n')
            fout.write('p15 = ' +  str(p15) +'\n')
            fout.write('p16 = ' +  str(p16) +'\n')
            fout.write('p17 = ' +  str(p17) +'\n')
            fout.write('p18 = ' +  str(p18) +'\n')
            fout.write('p19 = ' +  str(p19) +'\n')
            fout.write('p20 = ' +  str(p20) +'\n')
            fout.write('p21 = ' +  str(p21) +'\n')
            fout.write('p22 = ' +  str(p22) +'\n')
            fout.write('p23 = ' +  str(p23) +'\n')
            fout.write('p24 = ' +  str(p24) +'\n')
            fout.write('p25 = ' +  str(p25) +'\n')
            fout.write('p26 = ' +  str(p26) +'\n')
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
    GrammarTraining.find_probabilities(args.get('input_words', None), args.get('output_file', 'output'))



