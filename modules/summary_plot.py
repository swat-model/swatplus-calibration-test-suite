#!/bin/python3

'''
-

Author  : Celray James CHAWANDA
Email   : celray.chawanda@outlook.com
Licence : All rights Reserved
Repo    : https://github.com/celray

Date    : 2023-05-24
'''

# imports
import pandas as pd
import seaborn as sns
import numpy as np
from matplotlib import pyplot as plt

def make_plot(dict_data, out_fn, ncols = 8, subplot_width = 2, subplot_height = 5):
    
    # Get number of parameters
    num_params = len(dict_data)

    if ncols > num_params:
        ncols = num_params
    
    if ncols > 8:
        ncols = 8

    num_cols = ncols
    num_rows = int(np.ceil(num_params / num_cols))

    fig_width = subplot_width * num_cols
    fig_height = subplot_height * num_rows

    # Setup subplot grid
    fig, axs = plt.subplots(num_rows, num_cols, figsize=(fig_width, fig_height))

    # Make axs a 1D array for easier indexing
    axs = axs.flatten()

    # Iterate over parameters
    for i, (param, param_dict) in enumerate(dict_data.items()):
        # Convert the parameter dictionary to a dataframe
        df = pd.DataFrame(param_dict).T  # Transpose so that subdictionary keys become rows

        # Replace boolean with int
        df = df.replace({False: 0, True: 1})
        df = df.apply(pd.to_numeric, errors='coerce')

        # Create the heatmap
        sns.heatmap(df, annot=False, cmap='coolwarm_r', ax=axs[i], linecolor='blue', cbar=False, vmin=-0.3, vmax=1.1)

        # Labels
        axs[i].set_ylabel('')
        axs[i].set_xlabel('')

        if i % num_cols != 0:
            axs[i].set_yticklabels([])

        # Remove x tick labels for subplots that aren't in the bottom-most row
        if i < num_params - num_cols:
            axs[i].set_xticklabels([])

        # Title
        axs[i].set_title(f'{param}')

    # Remove unused subplots
    for i in range(num_params, num_rows*num_cols):
        fig.delaxes(axs[i])

    plt.tight_layout()
    # plt.show()
    plt.savefig(out_fn)
    plt.close()

    return True

