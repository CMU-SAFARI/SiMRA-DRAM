import subprocess
import os


apps_path = os.path.dirname(os.path.abspath(__file__)) + "/"
reset_board = apps_path + "../ResetBoard/full_reset.sh"
module = 'new_data_tested_module'
experiment_lst = ['RowClone','FindOpenRows','MajOperations','MultiRowInit']
#experiment_lst = ['MajOperations','MultiRowInit']
#If one of the experiments is gave an error and the last successfull experiment sent its output to experimental_data/new_data_tested_module, you can remove the error experiment from the experiment_lst and start from the last successfull experiment
#As an example, RowClone experiment is successful and FindOpenRows experiment gave an error (and you fix the error):
## 1.Check whether the output (which is all_subarrays.csv for RowClone) is sent to experimental_data/new_data_tested_module
## 2.1 If yes, remove the RowClone from the experiment_lst and start the script again
## 2.2 If no, start the script from RowClone experiment

#temperature_lst = [50,60,70,80,90]
temperature_lst = [50]

for experiment in experiment_lst:
    print(f'Running {experiment} experiment')
    for temperature in temperature_lst:
        ### SET THE TEMPERATURE
        cmd = f'cd {apps_path}{experiment} && make && python3 run_script.py --module {module} --temperature {temperature} --apps_path {apps_path}'
        print(cmd)
        try:
            print(f'ONGOING {experiment} at {temperature}C')
            os.system(f'{reset_board}')
            sp = subprocess.run([cmd], shell=True, check=True)
        except:
            print(f'Error in {experiment} at {temperature}C')
            print('Experiments terminated!')
            print('If the previous experiments are done, you can start from that point by removing the previous experiments from the experiment_lst')
            print('Please check the DRAM-Bender/sources/apps/DSN_AE_APPS/run_all_scripts.py line 14 for more information')
            exit(0)

print('#############################################')
print('All experiments are done!')
print('#############################################')


