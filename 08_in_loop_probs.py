#!/usr/bin/env python3
import argparse
import numpy as np
import xlsxwriter


"""
Script to find probability of a base being in an R-loop based on an input probabilistic language. Probabilities are plotted with alpha on the left and omega on the right.


Copyright 2021 Svetlana Poznanovic


"""


class Loop_probabilities:

    @classmethod
    def get_args(cls):
        parser = argparse.ArgumentParser(description='Find probabilities')
        parser.add_argument('-w', '--input_words', metavar='WORDS_IN_FILE', type=str, required=True,
                            help='WORDS input file', default=None)
        parser.add_argument('-l', '--seq_length', metavar='NUM_BASES', type=int, required=True,
                            help='Number of bases', default=None)
        parser.add_argument('-p', '--input_probabilities', metavar='PROBABILITIES_IN_FILE', type=str, required=True,
                            help='Word probabilities input file', default=None)
        parser.add_argument('-o', '--output_file', metavar='OUTPUT_FILE', type=str, required=False,
                            help='Output XLSX file', default='output')
        return parser.parse_args()
        
    @classmethod
    def in_loop_probabilities(cls, words_in, seq_len, probabs_in, output_file='output'):
    
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
    


        with open(probabs_in, "r") as file:
            lines = file.readlines()

        probs = []
    
        for line in lines:
            prb = line.strip()
            probs.append(float(prb))
            
        
        def loop_location(word):
            i =0
            j = 0
            #print(word)
            while word[i] != 'O' and word[i] != 'P' and word[i] != 'Q' and word[i] != 'U' and word[i] != 'V':
                i +=1
                j +=5   
            if word[i] == 'O':
                i+=1
                j+=0
            if word[i] == 'P':
                i+=1
                j+=1 
            if word[i] == 'Q':
                i+=1
                j+=2 
            if word[i] == 'U':
                i+=1 
                j+=3
            if word[i] == 'V':
                i+=1 
                j+=4
            initial = j
            while word[i] != 'o' and word[i] != 'p' and word[i] != 'q' and word[i] != 'u' and word[i] != 'v':
                i +=1
                j +=5 
            final = j
            
            loop_vec = np.array([0] * seq_len) 
            
            for index in range(seq_len): 
                if (index >=initial) and (index < final):
                    loop_vec[index] = 1
                
            float_array = loop_vec.astype(np.float)
            return float_array
            
        summary = np.array([0] * seq_len)
        summary = summary.astype(np.float)
        #print('Type for summary:', type(summary))
        #print('Type of loop_location:', type(loop_location(language[0])))
        #print('Type of scaled:', type(loop_location(language[j])*probs[j]))
        
        for j in range(len(language)):
            print(j)
            #print(type(loop_location(language[j])))
            summary += loop_location(language[j])*probs[j]
            
        data = [list(range(1,seq_len +1)), summary.tolist()]
        headings = ['Base position', 'Probability'] 
        workbook = xlsxwriter.Workbook(output_file + '.XLSX')
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': 1})
        worksheet.write_row('A1', headings, bold)
        worksheet.write_column('A2', data[0]) 
        worksheet.write_column('B2', data[1]) 
        chart1 = workbook.add_chart({'type': 'line'}) 
        chart1.add_series({ 
            'name':       '=Sheet1!$B$1', 
            'categories': '=Sheet1!$A$2:$A$%d' % seq_len, 
            'values':     '=Sheet1!$B$2:$B$%d' % seq_len, 
        }) 
          
        chart1.set_title ({'name': 'Probabilities in R-loop'}) 
        chart1.set_x_axis({'name': 'Base position'}) 
        chart1.set_y_axis({'name': 'Probability'}) 
        chart1.set_style(11) 
    
        # add chart to the worksheet with given
        # offset values at the top-left corner of
        # a chart is anchored to cell D2 .  
        worksheet.insert_chart('D2', chart1, {'x_offset': 25, 'y_offset': 10}) 
        workbook.close() 
            
        #with open(out_file, "a") as file_handle:
        #    i =0
        #    while i < len(summary):
        #        file_handle.write(str(summary[i])+"\n")
        #        i += 1
        
            
if __name__ == '__main__':
    args = vars(Loop_probabilities.get_args())
    Loop_probabilities.in_loop_probabilities(args.get('input_words', None), args.get('seq_length', None), args.get('input_probabilities', None), args.get('output_file', 'output'))

    
