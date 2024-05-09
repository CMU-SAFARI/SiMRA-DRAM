# %% [markdown]
# ### Import necessary libraries and define paths

# %%
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')
#main_dir_path = "/home/dsn_aevaluator2/DSN_ARTIFACT/experimental_data/"

dsn_artifact_path = "<set the path to the DSN_ARTIFACT folder>"
#e.g.:
#dsn_artifact_path = "/home/ismail/dsn_artifact"

exp_data_dir_path = dsn_artifact_path + "/experimental_data"
existing_all_data_path = exp_data_dir_path + "/existing_all_data_except_tested_module"
new_module_data_path = exp_data_dir_path + "/new_data_tested_module"
new_all_data_path = exp_data_dir_path + "/new_all_data"
plot_path = dsn_artifact_path + "/analysis/plots_new/"
try:
    os.system(f'mkdir {plot_path}')
except OSError:
    print ("Folder already exists or could not be created. It will try to remove the files in the folder (if there is any). Please check the folder names and paths.")
    os.system(f'rm {plot_path}/*')
    pass

# %% [markdown]
# # Section IV

# %% [markdown]
# ### Fig.3 (The effect of timing delay on Simultaneous Many-Row Activation(MRA))

# %%
#### Replace the tested modules' data

csv_file = 'mra_timing.csv'
print(f'{existing_all_data_path}/{csv_file}')
df_mra_timing = pd.read_csv(existing_all_data_path+"/"+csv_file)


t_df = pd.read_csv(open(os.path.join(f'{new_module_data_path}/open_rows_50.csv') , errors='replace')) 
t_df.drop(columns=["Unnamed: 0", "Rfirst", "Rsecond", "min_row_addr", "max_row_addr", "all_open_indices", "success_rates", "s_id"], inplace=True)
t_df = t_df[t_df["total_open_row"].isin([2, 4, 8, 16, 32])]
t_df['avg_success_rate'] *= 100
for i in [2, 4, 8, 16, 32]:
    for t_12 in [0, 1, 2, 3]:
        for t_23 in [0, 1, 2, 3]:
            t_df = pd.concat([t_df, pd.DataFrame({'total_open_row': [i], 'avg_success_rate': [np.nan], 't_12': [t_12], 't_23': [t_23]})], ignore_index=True)

df_mra_timing = pd.concat([df_mra_timing, t_df], ignore_index=True)


#### Start Plotting

sns.set(font='sans-serif', style='white')
sns.set_theme(style="ticks", rc={'xtick.bottom': True,'ytick.left': True})


fig, axs = plt.subplots(2, 4, figsize=(7, 2.5))
for t_12 in [0, 1]:
    for t_23 in [0, 1, 2, 3]:
        plot_df = df_mra_timing[(df_mra_timing['t_12'] == t_12) & (df_mra_timing['t_23'] == t_23)]
        sns.boxplot(x='total_open_row', y='avg_success_rate',
                    data=plot_df, 
                    palette='pastel', linewidth=1.5, whis=[0, 99], width=0.8, showfliers=True,
                    capprops={"linewidth":1.5, "color":"black"},
                    boxprops={"linewidth":1.5, "edgecolor":"black"},
                    whiskerprops={"linewidth":1.5, "color":"black"},
                    fliersize=2.5,
                    medianprops={"linewidth":1.5, "color":"black"},
                    showmeans=True, meanprops={"marker":"o","markerfacecolor":"white", "markeredgecolor":"black", "markersize":"5"}, ax=axs[t_12][t_23])


        axs[t_12][t_23].set_title('')
        axs[t_12][t_23].set_xlabel('')
        axs[t_12][t_23].set_ylabel('')

        axs[t_12][t_23].set_ylim(-10, 110)

        axs[t_12][t_23].set_yticklabels("")
        axs[t_12][t_23].set_xticklabels("")
        axs[t_12][t_23].tick_params(axis="x", direction="out", size=0, color='black')
        axs[t_12][t_23].tick_params(axis="y", direction="out", size=0, color='black')

        y_labels = [0, 50, 100]
        axs[t_12][t_23].set_yticks(y_labels, [], fontsize=10)
        if t_23 == 0:
            axs[t_12][t_23].set_yticks(y_labels, y_labels, fontsize=10)
            axs[t_12][t_23].tick_params(axis="y", direction="out", size=5, color='black')
        if t_12 == 1:
            axs[t_12][t_23].set_xticklabels([2, 4, 8, 16, 32], fontsize=10)
            axs[t_12][t_23].tick_params(axis="x", direction="out", size=5, color='black')

        for axis in ['top','bottom','left','right']:
            axs[t_12][t_23].spines[axis].set_linewidth(3)
            axs[t_12][t_23].spines[axis].set_color('black')
        axs[t_12][t_23].grid(axis='y', alpha=0.8)

        if t_12 == 0:
            axs[t_12][t_23].set_title(f"$t_2 = {t_23*1.5 + 1.5}$", fontsize=12)
        if t_23 == 3:
            axs[t_12][t_23].text(1.05, 0.5, f"$t_1={t_12*1.5 + 1.5}$", fontsize=12, rotation=90, va='center', ha='left', transform=axs[t_12][t_23].transAxes)

fig.tight_layout()
plt.subplots_adjust(wspace=0, hspace=0)

fig.supylabel('Success Rate (%)', fontsize=14, x=-0.015)
fig.text(0.5, 0.02, r"Number of Open Rows", fontsize=14, color='black', ha='center', va='center')
plt.savefig('./plots_new/csv_mra_timingparameters.png', bbox_inches='tight', pad_inches=0.01)
plt.savefig('./plots_new/csv_mra_timingparameters.pdf', bbox_inches='tight', pad_inches=0.01)

# %% [markdown]
# # Section V

# %% [markdown]
# ### Fig.6 (Majority Timing Parameters)

# %%
#### Replace the tested modules' data
i=0
csv_file = 'maj_timing.csv'
df_maj = pd.read_csv(os.path.join(f'{existing_all_data_path}/{csv_file}'))
for numrows in [4, 8, 16, 32]:
    t_df = pd.read_csv(os.path.join(f'{new_module_data_path}/maj_coverage_{numrows}_50.csv'))
    t_df.drop(columns=["Unnamed: 0", "r_first", "r_second", "bank_id", "n_frac_times", "t_frac", "s_id"], inplace=True)
    for t_12 in [0, 1, 2, 3]:
        for t_23 in [0, 1, 2, 3]:
            for majx in [i for i in [3, 5, 7, 9]]:
                t_df = pd.concat([t_df, pd.DataFrame({'total_open_row': [i], 'avg_stability': [np.nan], 'avg_coverage': [np.nan],
                                                        'full_coverage_cells': [np.nan], 'full_stable_cells': [np.nan],  
                                                        't_12': [t_12], 't_23': [t_23], 'majX': [majx]})], ignore_index=True)
    t_df['numrows'] = numrows
    df_maj = pd.concat([df_maj, t_df], ignore_index=True)
    

#### Start plotting

sns.set(font='sans-serif', style='white')
sns.set_theme(style="ticks", rc={'xtick.bottom': True,'ytick.left': True})

fig, axs = plt.subplots(2, 4, figsize=(7, 2.5))
for t_12 in [0, 1]:
    for t_23 in [0, 1, 2, 3]:
        plot_df = df_maj[(df_maj['majX'] == 3) & (df_maj['t_12'] == t_12) & (df_maj['t_23'] == t_23)]
        sns.boxplot(x='numrows', y='full_stable_cells',
                    data=plot_df, 
                    palette='pastel', linewidth=1.5, whis=[0, 99], width=0.8, showfliers=True,
                    capprops={"linewidth":1.5, "color":"black"},
                    boxprops={"linewidth":1.5, "edgecolor":"black"},
                    whiskerprops={"linewidth":1.5, "color":"black"},
                    fliersize=2.5,
                    medianprops={"linewidth":1.5, "color":"black"},
                    showmeans=True, meanprops={"marker":"o","markerfacecolor":"white", "markeredgecolor":"black", "markersize":"5"}, ax=axs[t_12][t_23])

        axs[t_12][t_23].set_title('')
        axs[t_12][t_23].set_xlabel('')
        axs[t_12][t_23].set_ylabel('')

        axs[t_12][t_23].set_ylim(-10, 110)

        axs[t_12][t_23].set_yticklabels("")
        axs[t_12][t_23].set_xticklabels("")
        axs[t_12][t_23].tick_params(axis="x", direction="out", size=0, color='black')
        axs[t_12][t_23].tick_params(axis="y", direction="out", size=0, color='black')

        y_labels = [0, 50, 100]
        axs[t_12][t_23].set_yticks(y_labels, [], fontsize=11)
        if t_23 == 0:
            axs[t_12][t_23].set_yticks(y_labels, y_labels, fontsize=11)
            axs[t_12][t_23].tick_params(axis="y", direction="out", size=5, color='black')
        if t_12 == 1:
            axs[t_12][t_23].set_xticklabels([4, 8, 16, 32], fontsize=11)
            axs[t_12][t_23].tick_params(axis="x", direction="out", size=5, color='black')

        for axis in ['top','bottom','left','right']:
            axs[t_12][t_23].spines[axis].set_linewidth(3)
            axs[t_12][t_23].spines[axis].set_color('black')
        axs[t_12][t_23].grid(axis='y', alpha=0.8)

        if t_12 == 0:
            axs[t_12][t_23].set_title(f"$t_2 = {t_23*1.5 + 1.5}$", fontsize=12)
        if t_23 == 3:
            axs[t_12][t_23].text(1.05, 0.5, f"$t_1={t_12*1.5 + 1.5}$", fontsize=12, rotation=90, va='center', ha='left', transform=axs[t_12][t_23].transAxes)

fig.tight_layout()
plt.subplots_adjust(wspace=0, hspace=0)

fig.text(0.5, 0.02, r"Number of Open Rows", fontsize=14, color='black', ha='center', va='center')
fig.supylabel('Success Rate (%)', fontsize=14, x=-0.01)
# fig.supxlabel('Number of Open Rows', fontsize=18, y=-0.015)
plt.savefig('./plots_new/maj_timingparameters.png', bbox_inches='tight', pad_inches=0.01)
plt.savefig('./plots_new/maj_timingparameters.pdf', bbox_inches='tight', pad_inches=0.01)


# %% [markdown]
# ### Fig.7 (MAJX Data Pattern)

# %%
csv_file = 'maj_datapattern.csv'
df_maj_dp = pd.read_csv(os.path.join(f'{existing_all_data_path}/{csv_file}'))

for numrows in [4, 8, 16, 32]:
    t_df = pd.read_csv(os.path.join(f'{new_module_data_path}/maj_coverage_{numrows}_50.csv'))
    t_df.drop(columns=["Unnamed: 0", "r_first", "r_second", "bank_id", "n_frac_times", "t_frac", "s_id", "avg_stability", "avg_coverage"], inplace=True)
    t_df = t_df[(t_df['t_12'] == 0) & (t_df['t_23'] == 1)]
    t_df.drop(columns=["t_12", "t_23"], inplace=True)
    for majx in [i for i in [3, 5, 7, 9] if i <= numrows]:
        t_df = pd.concat([t_df, pd.DataFrame({'full_coverage_cells': [np.nan], 'full_stable_cells': [np.nan],  
                                            'majX': [majx]})], ignore_index=True)
    t_df['numrows'] = numrows
    t_df.rename(columns={"full_coverage_cells": "All 0s/1s", "full_stable_cells": "Random"}, inplace=True)
    t_df = t_df.melt(id_vars=['majX', 'numrows'], var_name='data_pattern', value_name='success_rate')
    
    df_maj_dp = pd.concat([df_maj_dp, t_df], ignore_index=True)



sns.set(font='sans-serif', style='white')
sns.set_theme(style="ticks", rc={'xtick.bottom': True,'ytick.left': True})

fig, axs = plt.subplots(1, 4, figsize=(10, 3), width_ratios=[4, 3, 3, 2])
for i, majx in enumerate([3, 5, 7, 9]):
    plot_df = df_maj_dp[(df_maj_dp['majX'] == majx)]
    sns.boxplot(x='numrows', y='success_rate', hue='data_pattern',
                data=plot_df, 
                palette='pastel', linewidth=1.5, whis=[0, 99], width=0.8, showfliers=True,
                capprops={"linewidth":1.5, "color":"black"},
                boxprops={"linewidth":1.5, "edgecolor":"black"},
                whiskerprops={"linewidth":1.5, "color":"black"},
                fliersize=2.5,
                medianprops={"linewidth":1.5, "color":"black"},
                showmeans=True, meanprops={"marker":"o","markerfacecolor":"white", "markeredgecolor":"black", "markersize":"6"}, ax=axs[i])


    axs[i].set_title('')
    axs[i].set_xlabel('')
    axs[i].set_ylabel('')
    axs[i].set_ylim(-5, 110)
    axs[i].get_legend().remove()

    if i == 0:
        axs[i].set_xticklabels([4, 8, 16, 32], fontsize=14)
    elif i == 1 or i == 2:
        axs[i].set_xticklabels([8, 16, 32], fontsize=14)
    elif i == 3:
        axs[i].set_xticklabels([16, 32], fontsize=14)

    axs[i].tick_params(axis="x", direction="out", size=5, color='black')
    y_labels = [0, 50, 100]
    axs[i].set_yticks(y_labels, [], fontsize=14)
    axs[i].tick_params(axis="y", direction="out", size=0, color='black')
    if i == 0:
        axs[i].set_ylabel('Success Rate (%)', fontsize=18)
        axs[i].set_yticks(y_labels, y_labels, fontsize=14)
        axs[i].tick_params(axis="y", direction="out", size=5, color='black')
        
    if i == 3:
        axs[i].legend(title=r"Data Pattern", fontsize=11, title_fontsize=11, loc='upper right', edgecolor='black', 
                        ncols=1, frameon=True, borderpad=0.2, labelspacing=0.2, handletextpad=0.2, borderaxespad=0.2, columnspacing=0.4,
                        handlelength=1.4)

    axs[i].set_title(f"MAJ{majx}", fontsize=18)

    for axis in ['top','bottom','left','right']:
        axs[i].spines[axis].set_linewidth(3)
        axs[i].spines[axis].set_color('black')
    axs[i].grid(axis='y', alpha=0.8)

fig.tight_layout()
plt.subplots_adjust(wspace=0, hspace=0)

fig.text(0.5, 0.0, r"Number of Open Rows", fontsize=18, color='black', ha='center', va='center')
plt.savefig('./plots_new/maj_datapattern.png', bbox_inches='tight', pad_inches=0.01)
plt.savefig('./plots_new/maj_datapattern.pdf', bbox_inches='tight', pad_inches=0.01)

# %% [markdown]
# # Section VI

# %% [markdown]
# ### Fig.10 (MultiRowInit Timing Effect)

# %%
csv_file = 'mri_timing.csv'
df_mri_timing = pd.read_csv(os.path.join(f'{existing_all_data_path}/{csv_file}'))

for numrows in [2, 4, 8, 16, 32]:
    t_df = pd.read_csv(os.path.join(f'{new_module_data_path}/multirow_{numrows}_50.csv'))
    t_df.drop(columns=["Unnamed: 0", "bank_id", "r_first", "r_second", "all_0", "all_1", "s_id"], inplace=True)
    t_df['random'] *= 100
    for t_12 in [0, 10, 20, 30, 40]:
        for t_23 in [0, 1, 2, 3]:
            t_df = pd.concat([t_df, pd.DataFrame({'random': [np.nan], 't_12': [t_12],  
                                                't_23': [t_23]})], ignore_index=True)
    t_df['numrows'] = numrows

    df_mri_timing = pd.concat([df_mri_timing, t_df], ignore_index=True)


sns.set(font='sans-serif', style='white')
sns.set_theme(style="ticks", rc={'xtick.bottom': True,'ytick.left': True})

fig, axs = plt.subplots(3, 4, figsize=(7, 3.5))
for t_12 in [0, 1, 2]:
    for t_23 in [0, 1, 2, 3]:
        plot_df = df_mri_timing[(df_mri_timing['t_12'] == t_12*10) & (df_mri_timing['t_23'] == t_23)]
        sns.boxplot(x='numrows', y='random',
                    data=plot_df, 
                    palette='pastel', linewidth=1.5, whis=[0, 99], width=0.8, showfliers=True,
                    capprops={"linewidth":1.5, "color":"black"},
                    boxprops={"linewidth":1.5, "edgecolor":"black"},
                    whiskerprops={"linewidth":1.5, "color":"black"},
                    fliersize=2.5,
                    medianprops={"linewidth":1.5, "color":"black"},
                    showmeans=True, meanprops={"marker":"o","markerfacecolor":"white", "markeredgecolor":"black", "markersize":"5"}, ax=axs[t_12][t_23])

        axs[t_12][t_23].set_title('')
        axs[t_12][t_23].set_xlabel('')
        axs[t_12][t_23].set_ylabel('')

        axs[t_12][t_23].set_ylim(-10, 110)

        axs[t_12][t_23].set_yticklabels("")
        axs[t_12][t_23].set_xticklabels("")
        axs[t_12][t_23].tick_params(axis="x", direction="out", size=0, color='black')
        axs[t_12][t_23].tick_params(axis="y", direction="out", size=0, color='black')

        y_labels = [0, 50, 100]
        axs[t_12][t_23].set_yticks(y_labels, [], fontsize=10)
        if t_23 == 0:
            axs[t_12][t_23].set_yticks(y_labels, y_labels, fontsize=10)
            axs[t_12][t_23].tick_params(axis="y", direction="out", size=5, color='black')
        if t_12 == 2:
            axs[t_12][t_23].set_xticklabels([2, 4, 8, 16, 32], fontsize=10)
            axs[t_12][t_23].tick_params(axis="x", direction="out", size=5, color='black')

        for axis in ['top','bottom','left','right']:
            axs[t_12][t_23].spines[axis].set_linewidth(3)
            axs[t_12][t_23].spines[axis].set_color('black')
        axs[t_12][t_23].grid(axis='y', alpha=0.8)

        if t_12 == 0:
            axs[t_12][t_23].set_title(f"$t_2 = {t_23*1.5 + 1.5}$", fontsize=12)
        t_12_list = [1.5, 18, 36, 54, 72]
        if t_23 == 3:
            axs[t_12][t_23].text(1.05, 0.5, f"$t_1 = {t_12_list[t_12]}$", fontsize=12, rotation=90, va='center', ha='left', transform=axs[t_12][t_23].transAxes)

fig.tight_layout()
plt.subplots_adjust(wspace=0, hspace=0)

fig.supylabel('Success Rate (%)', fontsize=14, x=-0.01)
fig.text(0.5, 0.02, r"Number of Open Rows", fontsize=14, color='black', ha='center', va='center')
plt.savefig('./plots_new/mri_timingparameters.png', bbox_inches='tight', pad_inches=0.01)
plt.savefig('./plots_new/mri_timingparameters.pdf', bbox_inches='tight', pad_inches=0.01)


# %% [markdown]
# ### Fig.11 (MRI Data Pattern)

# %%
csv_file = 'mri_datapattern.csv'
df_mri_dp = pd.read_csv(os.path.join(f'{existing_all_data_path}/{csv_file}'))

for numrows in [2, 4, 8, 16, 32]:
    t_df = pd.read_csv(os.path.join(f'{new_module_data_path}/multirow_{numrows}_50.csv'))
    t_df.drop(columns=["Unnamed: 0", "bank_id", "r_first", "r_second", "s_id"], inplace=True)
    t_df['random'] *= 100
    t_df['all_0'] *= 100
    t_df['all_1'] *= 100
    t_df = t_df[(t_df['t_12'] == 30) & (t_df['t_23'] == 1)]
    t_df.drop(columns=["t_12", "t_23"], inplace=True)
    t_df = pd.concat([t_df, pd.DataFrame({'random': [np.nan], 'all_0': [np.nan],  
                                            'all_1': [np.nan]})], ignore_index=True)
    t_df['numrows'] = numrows

    t_df = t_df.melt(id_vars=['numrows'], var_name='data_pattern', value_name='success_rate')

    df_mri_dp = pd.concat([df_mri_dp, t_df], ignore_index=True)


####################### PLOTTING #######################

sns.set(font='sans-serif', style='white')
sns.set_theme(style="ticks", rc={'xtick.bottom': True,'ytick.left': True})

fig, ax = plt.subplots(figsize=(6, 1.8))
plot_df = df_mri_dp
sns.lineplot(x='numrows', y='success_rate', hue='data_pattern', data=plot_df, ax=ax, 
             linewidth=2.5, marker='o', markersize=6, markerfacecolor='white', 
             markeredgewidth=1.5, markeredgecolor='black', palette='pastel')

ax.set_ylim(97.9, 100.1)
ax.get_legend().remove()


y_labels = [98, 99, 100]
ax.set_yticks(y_labels, y_labels, fontsize=11)
ax.tick_params(axis="y", direction="out", size=5, color='black')
ax.set_ylabel('Success Rate (%)', fontsize=12, labelpad=0)
ax.set_xscale('log', base=2)
ax.set_xticks([2, 4, 8, 16, 32], [2, 4, 8, 16, 32], fontsize=12)
ax.tick_params(axis="x", direction="out", size=5, color='black')
ax.set_xlabel('Number of Rows', fontsize=12, labelpad=0)

handles, labels = ax.get_legend_handles_labels()
ax.legend(handles, ["All 0s", "All 1s", "Random"], title=r"Data Pattern", fontsize=11, title_fontsize=11, loc='lower left', edgecolor='black', 
                  ncols=5, frameon=True, borderpad=0.2, labelspacing=0.2, handletextpad=0.2, borderaxespad=0.2, columnspacing=0.4,
                  handlelength=1.4)

for axis in ['top','bottom','left','right']:
    ax.spines[axis].set_linewidth(3)
    ax.spines[axis].set_color('black')
ax.grid(axis='both', alpha=0.8)

# fig.tight_layout()

plt.savefig('./plots_new/mri_datapattern.png', bbox_inches='tight', pad_inches=0.01)
plt.savefig('./plots_new/mri_datapattern.pdf', bbox_inches='tight', pad_inches=0.01)



