import subprocess
import os
import pandas as pd
import helper_functions as hf
import warnings
import numpy as np
import time
import random
import argparse
warnings.simplefilter(action='ignore', category=FutureWarning)




parser = argparse.ArgumentParser()
#module type
parser.add_argument('--module', type=str, required=True, help='Module type: hytgXX, hyttXX')
parser.add_argument('--temperature', type=str, required=True, help='Temp: 50, 60, etc.')
parser.add_argument('--apps_path', type=str, required=True, help='Path to the DSN_AE_APPS directory')
args = parser.parse_args()
module = args.module
temperature = args.temperature
apps_path = args.apps_path


exe_path ="MultiRowInit/"
exe_file ="find-open-rows-exe"

open_rows_file_name = apps_path + exe_path + "open_rows.txt"

out_file = apps_path + exe_path + 'multi_row.txt'
csv_file = apps_path + exe_path + f'multirow_{temperature}.csv'
os.system(f'rm {out_file}')
os.system(f'rm {csv_file}')



or_csv = f'{apps_path}../../../../experimental_data/{module}/open_rows_50.csv'
or_df = pd.read_csv(or_csv)
    
start_time = time.time()
end_time = time.time()
os.system(f'{apps_path}../ResetBoard/full_reset.sh')
num_iter = 1000
for rows in [2,4,8,16,32]:
    if temperature == '50':
        t_12_lst = [0,10,20,30,40]
        t_23_lst = [0,1,2,3]
    else:
        t_12_lst = [30]
        t_23_lst = [1]
    sample_csv = f'{apps_path}../../../../experimental_data/{module}/samples_{rows}.csv'
    if(os.path.isfile(sample_csv)):
        samples_df = pd.read_csv(sample_csv)
    else:
        samples_df = or_df.loc[or_df['total_open_row'] == rows]
        samples_df = samples_df.loc[samples_df['avg_success_rate'] == 1.0]
        samples_df = samples_df.loc[samples_df['t_12'] == 0]
        samples_df = samples_df.loc[samples_df['t_23'] == 1]        
        if len(samples_df) > 100:
            samples_df = samples_df.sample(n=100).reset_index(drop=True)
        else:
            samples_df = samples_df.sample(n=len(samples_df)).reset_index(drop=True)
        samples_df.to_csv(sample_csv)

    
    lst = pd.DataFrame(columns=['t_12','t_23','bank_id','s_id','r_first','r_second','all_0','all_1','random'])
    csv_file = f'multirow_{rows}_{temperature}.csv'
    lst.to_csv(csv_file)
    print(f'Open Rows: {rows}, #Sample: {len(samples_df)}, Temp: {temperature}')
    for sample_iter,e_idx in enumerate(samples_df.index):
        start_time = time.time()
        element     = samples_df.iloc[[e_idx]]
        r_first     = element['Rfirst'][e_idx]
        r_second    = element['Rsecond'][e_idx]
        n_open_rows = element['total_open_row'][e_idx]
        s_id = element['s_id'][e_idx]
        open_rows   = [int(e) for e in element['all_open_indices'][e_idx][1:-1].split(',')]
        hf.write_to_file(open_rows,open_rows_file_name)
        for t_12 in t_12_lst:
            for t_23 in t_23_lst:
                for bank_id in range(0,4):
                    os.system(f'touch {out_file}')
                    cmd = ( apps_path + exe_path + exe_file + " " + 
                            str(r_first)  + " " + str(r_second) + " " + 
                            str(n_open_rows) + " " +
                            str(open_rows_file_name) + " " + str(num_iter) + " " + 
                            str(bank_id) + " " + 
                            str(t_12) + " " + str(t_23) + " " +
                            str(out_file) 
                    )
                    sp = subprocess.run([cmd], shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True) 
                    if(os.stat(out_file).st_size != 0):
                        res_lst = hf.read_result_file(out_file)
                        temp_data = [[t_12,t_23,bank_id,s_id,r_first, r_second, res_lst[0], res_lst[1], res_lst[2]]]
                        df = pd.DataFrame(temp_data, columns=['t_12','t_23','bank_id','s_id','r_first','r_second','all_0','all_1','random'])
                        df.to_csv(csv_file, mode='a', header=False)
                        os.system(f'rm {out_file}')
            end_time = time.time()
        print(f'Open Rows: {rows}, Sample: {sample_iter}/{len(samples_df)} iter took {end_time-start_time} seconds')      
    send_path = apps_path + exe_path + csv_file
    cp_path = f'{apps_path}../../../../experimental_data/{module}/'             
    send_cmd = f'cp -r {send_path} {cp_path}'  
    sp = subprocess.run([send_cmd], shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
    
 
