#!/usr/bin/env python3
import argparse
import numpy as np
import xlsxwriter


def loop(ind_1, ind_2, seq_len):
        
    loop_vec = np.array([0] * seq_len) 
    initial = seq_len + 2 - ind_2
    final = seq_len + 2 - ind_1
            
    for index in range(seq_len): 
        if (index >=initial) and (index < final):
            loop_vec[index] = 1
                
    float_array = loop_vec.astype(np.float)
    return float_array  



class BedFileAnalysis:

    @classmethod
    def get_args(cls):
        parser = argparse.ArgumentParser(description='Regions extractor')
        parser.add_argument('-b', '--input_bed', metavar='BED_IN_FILE', type=str, required=True,
                            help='BED input file', default=None)
        parser.add_argument('-l', '--seq_length', metavar='NUM_BASES', type=int, required=True,
                            help='Number of bases', default=None)
        parser.add_argument('-o', '--output_file', metavar='OUTPUT_FILE', type=str, required=False,
                            help='Output XLSX file', default='output')
        return parser.parse_args()

    @classmethod
    def find_exp_prob(cls, bed_in, seq_len, out_file):
    
        with open(bed_in, 'r') as fin:
            lines = fin.readlines()
            rloops_count = len(lines)
            
        
        probs = 1/float(rloops_count)
        summary = np.array([0] * seq_len)
        summary = summary.astype(np.float)
        
        
        for i in range(rloops_count):
            print(i)
            parts = lines[i].strip().split('\t')
            ind_1 = int(parts[1])
            ind_2 = int(parts[2])
            summary += loop(ind_1, ind_2, seq_len)*probs
            
                
        
            
        data = [list(range(1,seq_len +1)), summary.tolist()]
        headings = ['Base position', 'Probability'] 
        workbook = xlsxwriter.Workbook(out_file + '.XLSX')
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
        
if __name__ == '__main__':
    args = vars(BedFileAnalysis.get_args())
    BedFileAnalysis.find_exp_prob(args.get('input_bed', None), args.get('seq_length', None), args.get('output_file', 'output'))
