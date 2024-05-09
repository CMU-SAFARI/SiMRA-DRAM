import subprocess
import os
import pandas as pd
import helper_functions as hf
import argparse
import warnings
import time
warnings.simplefilter(action='ignore')





parser = argparse.ArgumentParser()
#module type
parser.add_argument('--module', type=str, required=True, help='Module type: hytgXX, hyttXX')
parser.add_argument('--temperature', type=str, required=True, help='Temp: 50, 60, etc.')
parser.add_argument('--apps_path', type=str, required=True, help='Path to the DSN_AE_APPS directory')
args = parser.parse_args()
module = args.module
temperature = args.temperature
apps_path = args.apps_path

exe_path ="MajOperations/"
exe_file ="maj-exe"


open_rows_file_name = apps_path + exe_path + "open_rows.txt"
r_frac_idx_file_name = apps_path + exe_path + "r_frac_indices.txt"

out_file = apps_path + exe_path + "maj.txt"
os.system(f'rm {out_file}')


    


or_csv = f'{apps_path}../../../../experimental_data/{module}/open_rows_50.csv'
or_df = pd.read_csv(or_csv)

try:
    os.mkdir(apps_path + exe_path + 'patterns')
except:
    pass

os.system(f'{apps_path}../ResetBoard/full_reset.sh')






stability_iter_count = 1000
bank_id = 1
n_frac_times = 3
t_frac = 0

for rows in [4,8,16,32]:
    if temperature == '50':
        t_12_lst = [0,1,2,3]
        t_23_lst = [0,1,2,3]
        bank_lst = [0,1,2,3]
    else:
        t_12_lst = [0]
        t_23_lst = [1]
        bank_lst = [0,1,2,3]
    sample_csv = f'{apps_path}../../../../experimental_data/{module}/samples_{rows}.csv'
    samples_df = or_df.loc[or_df['total_open_row'] == rows]
    samples_df = samples_df.loc[samples_df['avg_success_rate'] == 1.0]
    samples_df = samples_df.loc[samples_df['t_12'] == 0]
    samples_df = samples_df.loc[samples_df['t_23'] == 1]        
    if len(samples_df) > 100:
        samples_df = samples_df.sample(n=100).reset_index(drop=True)
    else:
        samples_df = samples_df.sample(n=len(samples_df)).reset_index(drop=True)
    samples_df.to_csv(sample_csv)
    #send_cmd = f'cp {sample_csv} {main_dir_path}/experimental_data/{module}/'  
    #sp = subprocess.run([send_cmd], shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
    lst = pd.DataFrame(columns=['t_12','t_23','n_frac_times','t_frac','bank_id','r_first','r_second','s_id','majX','avg_coverage','full_coverage_cells','avg_stability','full_stable_cells'])
    csv_file = f'maj_coverage_{rows}_{temperature}.csv'
    lst.to_csv(csv_file)
    for majX in [3,5,7,9]:
        if (majX > rows):
            break
        r_frac_idx = [i for i in range(rows%majX)]
        os.system('rm ./patterns/*')
        for i,pattern in enumerate(range(1,2**majX-1)):
            wr_pattern = hf.maj_all_1_0_pattern_creator(rows,majX,r_frac_idx,pattern)
            #print(i,wr_pattern,majX,2**majX-1,rows)
            pattern_file_name = apps_path + exe_path + f'./patterns/pattern_{i}.txt'
            hf.write_to_file(wr_pattern,pattern_file_name)
            current_time = time.time()
            end_time = 0
        print(f'Open Rows: {rows}, #Sample: {len(samples_df)}, #MAJ: {majX}, Pattern: {pattern}')
        for sample_iter,e_idx in enumerate(samples_df.index):
            start_time = time.time()
            element     = samples_df.iloc[[e_idx]]
            r_first     = element['Rfirst'][e_idx]
            r_second    = element['Rsecond'][e_idx]
            n_open_rows = element['total_open_row'][e_idx]
            min_row_idx = element['min_row_addr'][e_idx]
            max_row_idx = element['max_row_addr'][e_idx]
            s_id = element['s_id'][e_idx]
            open_rows   = [int(e) for e in element['all_open_indices'][e_idx][1:-1].split(',')]
            hf.write_to_file(open_rows,open_rows_file_name)
            hf.write_to_file(r_frac_idx,r_frac_idx_file_name)
            for t_12 in t_12_lst:
                for t_23 in t_23_lst:
                    for bank_id in bank_lst:
                        os.system(f'touch {out_file}')
                        cmd = ( apps_path + exe_path + exe_file + " " + str(pattern_file_name) + " " + 
                                str(r_frac_idx_file_name) + " " + str(r_first)  + " " + str(r_second) + " " + 
                                str(min_row_idx) + " " + str(max_row_idx)  + " " + str(n_open_rows) + " " +
                                str(open_rows_file_name) + " " + str(1) + " " + str(bank_id) + " " + 
                                str(majX) + " " + str(t_12) + " " + str(t_23) + " " +
                                str(n_frac_times) + " " + str(t_frac) + " " +str(out_file) 
                        )
                        sp = subprocess.run([cmd], shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True) 
                        if(os.stat(out_file).st_size != 0):
                            res_lst = (hf.read_result_file(out_file))
                            temp_data = [[t_12,t_23,n_frac_times,t_frac,bank_id, r_first, r_second, s_id, majX, res_lst[0], res_lst[1], res_lst[2], res_lst[3]]]
                            df = pd.DataFrame(temp_data, columns=['t_12','t_23','n_frac_times','t_frac','bank_id','r_first','r_second','s_id','majX','avg_coverage','full_coverage_cells','avg_stability','full_stable_cells'])
                            df.to_csv(csv_file, mode='a', header=False)
                            os.system(f'rm {out_file}')
            end_time = time.time()
            print(f'Open Rows: {rows}, Sample: {sample_iter}/{len(samples_df)} iter took {end_time-start_time} seconds')           
    send_path = apps_path + exe_path + csv_file
    cp_path = f'{apps_path}../../../../experimental_data/{module}/ '           
    send_cmd = f'cp -r {send_path} {cp_path}'  
    sp = subprocess.run([send_cmd], shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
    
    

