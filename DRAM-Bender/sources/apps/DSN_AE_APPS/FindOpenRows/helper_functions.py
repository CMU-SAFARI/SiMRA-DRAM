import pandas as pd
import numpy as np

def create_subarray_list(df):
    subarrays = []
    for i in range(len(df)):
        a = df.iloc[[i]]['rows'][i]
        a = a[1:-1].split(',')
        subarrays.append([int(ii) for ii in a])
    return subarrays

def df_process(r_first,out_file,last_subarray_addr,s_id,t_12,t_23):
    df = pd.read_csv(out_file,header=None)
    df.columns = ['Rfirst','Rsecond','open_row_addr','success_rate']
    lst = []
    for i in range(r_first+1,last_subarray_addr):
        dram_rows = df.loc[df['Rsecond'] == i, 'open_row_addr']
        dram_rows = [int(ii) for ii in dram_rows]
        if(len(dram_rows) > 1):
            success_rates = df.loc[df['Rsecond'] == i, 'success_rate'].to_list()
            sucesss_rates = [float(ii) for ii in success_rates]
            avg_success_rate = float(np.mean(success_rates))
            lst.append([r_first, i, len(dram_rows),
                        min(dram_rows),max(dram_rows),
                        dram_rows, success_rates, avg_success_rate
                        ])
        
    a_lst = pd.DataFrame(lst, columns=['Rfirst','Rsecond','total_open_row',
                                    'min_row_addr', 'max_row_addr', 
                                    'all_open_indices','success_rates','avg_success_rate'])
    a_lst['s_id'] = s_id
    a_lst['t_12'] = t_12
    a_lst['t_23'] = t_23
    return a_lst

def create_random_subarray_csv(s_df, random_subarray_pairs, csv_name):
    #drop Unnamed: 0 column
    s_df = s_df.drop(s_df.columns[0], axis=1)
    s_df.iloc[[random_subarray_pairs[0]]].to_csv(csv_name)
    for s_id in random_subarray_pairs:
        if s_id == random_subarray_pairs[0]:
            continue
        s_df.iloc[[s_id]].to_csv(csv_name, mode='a', header=False)