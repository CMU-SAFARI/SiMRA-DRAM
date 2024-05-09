import subprocess
import os
import pandas as pd
import warnings
import rowclone_functions as rf
from random import randrange
import argparse
warnings.simplefilter(action='ignore', category=FutureWarning)

parser = argparse.ArgumentParser()
#module type
parser.add_argument('--module', type=str, required=True, help='Module codename, e.g., new_data_tested_module')
parser.add_argument('--temperature', type=int, required=True, help='Temperature: 50, 60, 70, 80, 90')
parser.add_argument('--apps_path', type=str, required=True, help='Path to the DSN_AE_APPS directory')
args = parser.parse_args()
module = args.module
temperature = args.temperature
apps_path = args.apps_path


exe_path ="RowClone/"
exe_file ="row-clone-exe"

exe = apps_path + exe_path + exe_file
out_file = apps_path + exe_path + "row_clone.txt"
rc_csv = apps_path + exe_path + 'row-clone.csv'
sa_csv = apps_path + exe_path+ 'all_subarrays.csv'

r_first = 0
num_rows = 1024
counter = 0
csv_lst = []

os.system(f'rm {out_file}')
os.system(f'rm {rc_csv}')
os.system(f'rm {sa_csv}')
os.system(f'{apps_path}../ResetBoard/full_reset.sh')


csv_lst = []
while r_first < 65000:
    lst = pd.DataFrame(columns=['r_first','r_second','t_12','t_23'])
    lst.to_csv(rc_csv)
    print(f'Search in {r_first} - {r_first+num_rows}')
    rf.first_search(lst,r_first,r_first+num_rows,r_first,num_rows,rc_csv,out_file,exe)
    subarray_list = rf.subarray_list(r_first,rc_csv)
    csv_lst.append([len(subarray_list),counter,subarray_list])
    r_first = subarray_list[-1] + 1
    
csv_lst = pd.DataFrame(csv_lst,columns=['n_rows','group','rows'])
csv_lst.to_csv(sa_csv)


send_file = sa_csv
cp_path = f'{apps_path}../../../../experimental_data/{module}/'          
send_cmd = f'cp -r {send_file} {cp_path}'  
sp = subprocess.run([send_cmd], shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
