import subprocess
import os
import pandas as pd
import helper_functions as hf
import warnings
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


exe_path ="FindOpenRows/"
exe_file ="find-open-rows-exe"

add_voltage = 0
voltage=2.500



out_file = apps_path + exe_path + 'open_rows.txt'
if add_voltage == '1':
    
    csv_file = apps_path + exe_path + f'open_rows_{voltage}.csv'
else:
    csv_file = apps_path + exe_path + f'open_rows_{temperature}.csv'
    
os.system(f'rm {out_file}')
os.system(f'rm {csv_file}')




sa_csv = f'{apps_path}../../../../experimental_data/{module}/all_subarrays.csv'
s_df = pd.read_csv(sa_csv)
subarrays = hf.create_subarray_list(s_df)



lst = pd.DataFrame(columns=['Rfirst','Rsecond','total_open_row',
                                    'min_row_addr', 'max_row_addr', 
                                    'all_open_indices','success_rates','avg_success_rate','s_id','t_12','t_23'])
lst.to_csv(csv_file)


random_subarray_csv = f'{apps_path}../../../../experimental_data/{module}/random_subarrays_list.csv'

if(os.path.isfile(random_subarray_csv)):
    random_subarray_df = pd.read_csv(random_subarray_csv)
    subarray_list = hf.create_subarray_list(random_subarray_df)
else:
    n_subarrays = 3
    #randomly select n_subarrays subarrays and save their index to a list
    s_ids = random.sample(range(0, len(s_df)), n_subarrays)
    subarray_list = [subarrays[s_id] for s_id in s_ids]
    #save the subarrays to a csv file
    hf.create_random_subarray_csv(s_df, s_ids, random_subarray_csv)  
    

os.system(f'{apps_path}../ResetBoard/full_reset.sh')
t_12_lst = [0,1,2,3]
t_23_lst = [0,1,2,3]
for s_id,subarray in enumerate(subarray_list):
    first_subarray_addr = subarray[0]
    last_subarray_addr = subarray[-1]
    num_rows = last_subarray_addr - first_subarray_addr
    print(f'Searching between row {first_subarray_addr} - {last_subarray_addr}')
    for t_12 in t_12_lst:
        for t_23 in t_23_lst:
            for r_first in range(first_subarray_addr,last_subarray_addr-1):
                os.system(f'touch {out_file}')
                print(f'Subarray No. {s_id}, num_rows: {num_rows}, last_addr: {last_subarray_addr}, r_first: {r_first}')
                cmd = (apps_path + exe_path + exe_file + " " + 
                        str(t_12) + " " + str(t_23) + " " + 
                        str(first_subarray_addr) + " " + str(last_subarray_addr)  + " " + 
                        str(r_first)  + " " + out_file
                        )
                sp = subprocess.run([cmd], shell=True, capture_output=True) 

                
                if(os.stat(out_file).st_size != 0):
                    hf.df_process(r_first,out_file,last_subarray_addr,s_id,t_12,t_23).to_csv(csv_file, mode='a', header=False)
                    os.system(f'rm {out_file}')
            
if add_voltage == '1':
    send_path_lst = [csv_file]
else:
    send_path_lst = [csv_file, random_subarray_csv]           
for send_path in send_path_lst:
    if add_voltage == '1':
        cp_path = f'{apps_path}../../../../experimental_data/{module}/voltage/'
    else:
        cp_path = f'{apps_path}../../../../experimental_data/{module}/'             
    send_cmd = f'cp -r {send_path} {cp_path}'  
    sp = subprocess.run([send_cmd], shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)


