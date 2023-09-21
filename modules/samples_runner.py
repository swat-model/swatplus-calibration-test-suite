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
from cjfx import *


def get_data(parameter_list_file, input_txtinout, current_working_dir, tracked_fn, executable_path):

    dict_data = {}
    dict_data_nses = {}
    c_types = ['cal', 'direct']

    working_dir             = create_path('./output/model_runs/')

    src_txtinout_dir        = f"{os.path.dirname(parameter_list_file)}"
    file_cio_fname          = f"./inputs/file.cio"
    print_prt_fname         = f"./inputs/print.prt"
    calibration_fname       = f"{src_txtinout_dir}/calibration.cal"
    hru_tracked_outputs_fn  = tracked_fn
    
    parameters = pandas.read_csv(parameter_list_file)

    evaluation_dfs = {}
    for index, row in parameters.iterrows():
        
        dst_dirs = [f"{row['ParName']}_{row[f'Val{count}']}" for count in range(1,4)]
        copy_fns = list_files(f"{input_txtinout}/", "*")
        
        print(f"> copying model files for parameter {row['ParName']}")
        jobs = []

        for c_type in c_types:
            for dst_dir in dst_dirs:
                if not [f"{working_dir}/{c_type}_{dst_dir}", current_working_dir, executable_path] in jobs: jobs.append([f"{working_dir}/{c_type}_{dst_dir}", current_working_dir, executable_path])
                for fn in copy_fns:
                    copy_file(fn, f"{working_dir}/{c_type}_{dst_dir}/{file_name(fn)}", replace=True)
                
                file_cio_fs = ""
                fc_         = read_from(f"{input_txtinout}/file.cio")
                chg_ln      = fc_[21]
                chg_ln      = chg_ln.split()
                chg_ln[2]   = "calibration.cal" if c_type == 'cal' else "null"
                chg_ln      = "       ".join(chg_ln)
                fc_[21]     = "                  " + chg_ln + "\n"
                for line____ in fc_:
                    file_cio_fs += line____
                
                write_to(f"{working_dir}/{c_type}_{dst_dir}/file.cio", file_cio_fs)
                
                if c_type == 'cal':
                    calibration_cal_string = ""
                    for line in read_from(calibration_fname):
                        calibration_cal_string += line.format(parname = row['ParName'].ljust(18), chg_type = row['Change_Type'].rjust(10), value = dst_dir.split("_")[-1].rjust(12))
                    
                    write_to(f"{working_dir}/{c_type}_{dst_dir}/calibration.cal", calibration_cal_string)

                if not c_type == 'cal':
                    change_file_df = pandas.read_csv(f"{input_txtinout}/{row.Manual_File}", skiprows=int(row.SkipLines), delim_whitespace=True)
                    first_line = read_from(f"{input_txtinout}/{row.Manual_File}")[0]

                    for col_num__ in [int(n) for n in str(row.Cols).split(";")]:
                        if row.Change_Type == "abschg":
                            change_file_df.iloc[:,col_num__] = change_file_df.iloc[:,col_num__] + float(dst_dir.split("_")[-1])
                        elif row.Change_Type == "absval":
                            change_file_df.iloc[:,col_num__] = float(dst_dir.split("_")[-1])
                        elif row.Change_Type == "pctchg":
                            change_file_df.iloc[:,col_num__] = change_file_df.iloc[:,col_num__] * (1 + (float(dst_dir.split("_")[-1])/100))


                    final_str_f = first_line + change_file_df.to_string(index=False) + "\n"
                    write_to(f"{working_dir}/{c_type}_{dst_dir}/{row.Manual_File}", final_str_f)

                copy_file(print_prt_fname, f"{working_dir}/{c_type}_{dst_dir}/print.prt", replace=True)

        print(f"> runing model with different parameter values for {row['ParName']} in parallel")
        
        pool = multiprocessing.Pool(multiprocessing.cpu_count() - 2)
        results = pool.starmap_async(run_swat_plus, jobs)
        results.get()
        pool.close()
        
        hru_tracked_outputs_df = pandas.read_csv(hru_tracked_outputs_fn)

        # this is inefficient way of reading data as it reads the same file multiple times, but it is easy :)
        for index_2, row_2 in hru_tracked_outputs_df.iterrows():
            diff_check_cols = []
            if not f"{row['ParName']}" in evaluation_dfs:
                evaluation_dfs[f"{row['ParName']}"] = {}

            if not row_2.f_varname in evaluation_dfs[f"{row['ParName']}"]:
                evaluation_dfs[f"{row['ParName']}"][row_2.f_varname] = None

            for c_type in c_types:
                for dst_dir in dst_dirs:
                    # f"{dst_dir.split('_')[0]}_{'='.join(dst_dir.split('_')[1:])}"
                    diff_check_cols.append("{0}:{1}".format(f"{dst_dir.split('_')[0]}_{'='.join(dst_dir.split('_')[1:])}", c_type))

                    # print(f"{working_dir}/{c_type}_{dst_dir}/{row_2.file_name}")
                    if isinstance(row_2.unit, int):
                        out_df = get_swat_timeseries(f"{working_dir}/{c_type}_{dst_dir}/{row_2.file_name}", col_name=row_2.varname, object_number=row_2.unit)
                    else:
                        out_df = get_swat_timeseries(f"{working_dir}/{c_type}_{dst_dir}/{row_2.file_name}", col_name=row_2.varname)

                    out_df.rename(columns={row_2.varname: "{0}:{1}".format(f"{dst_dir.split('_')[0]}_{'='.join(dst_dir.split('_')[1:])}", c_type)}, inplace=True)
                    
                    if evaluation_dfs[f"{row['ParName']}"][row_2.f_varname] is None:
                        evaluation_dfs[f"{row['ParName']}"][row_2.f_varname] = out_df
                    else:
                        evaluation_dfs[f"{row['ParName']}"][row_2.f_varname] = \
                        pandas.merge(evaluation_dfs[f"{row['ParName']}"][row_2.f_varname], out_df, on="date", how='inner')

            seaborn.set_theme(style='darkgrid')
            subplots_long = evaluation_dfs[f"{row['ParName']}"][row_2.f_varname].melt(id_vars='date', var_name='id', value_name='value')
            subplots_long[['id', 'Change Type']] = subplots_long['id'].str.split(':', expand=True)

            ids = subplots_long['id'].unique()

            # Create subplots
            fig, axes = plt.subplots(1, len(ids), figsize=(len(ids) * 5, 3))

            # Iterate over ids and axes
            for i, (ax, id) in enumerate(zip(axes.flatten(), ids)):
                # Filter data
                df_id = subplots_long[subplots_long['id'] == id]
                
                # Plot data
                seaborn.lineplot(data=df_id, x='date', y='value', hue='Change Type', ax=ax, palette="muted")
                ax.set_title(f'{id}')

                # Set y-tick labels only on the left subplot
                if i != 0:
                    # ax.set_yticklabels([])
                    axes[i].set_ylabel('')
                else:
                    axes[i].set_ylabel(f"{row_2.f_varname}{f' ({row_2.units})' if not row_2.units == '-' else ''}")

                xticks = ax.get_xticks()
                ax.set_xticks([xticks[0], xticks[-1]])
                ax.set_xticklabels([df_id['date'].iloc[0].strftime('%Y-%m'), df_id['date'].iloc[-1].strftime('%Y-%m')])

            # Adjust layout
            plt.tight_layout()

            # save fig
            create_path(f"{working_dir}/../par-figures/{row['ParName']}-{row_2.varname}.png")
            plt.savefig(f"{working_dir}/../par-figures/{row['ParName']}-{row_2.varname}.png")

            # check if there is change
            change_in_cal_1 = get_nse(evaluation_dfs[f"{row['ParName']}"][row_2.f_varname], diff_check_cols[0], diff_check_cols[1])
            change_in_cal_2 = get_nse(evaluation_dfs[f"{row['ParName']}"][row_2.f_varname], diff_check_cols[0], diff_check_cols[2])
            change_in_cal_3 = get_nse(evaluation_dfs[f"{row['ParName']}"][row_2.f_varname], diff_check_cols[1], diff_check_cols[2])
            change_in_dir_1 = get_nse(evaluation_dfs[f"{row['ParName']}"][row_2.f_varname], diff_check_cols[3], diff_check_cols[4])
            change_in_dir_2 = get_nse(evaluation_dfs[f"{row['ParName']}"][row_2.f_varname], diff_check_cols[3], diff_check_cols[5])
            change_in_dir_3 = get_nse(evaluation_dfs[f"{row['ParName']}"][row_2.f_varname], diff_check_cols[4], diff_check_cols[5])
            change_across_1 = get_nse(evaluation_dfs[f"{row['ParName']}"][row_2.f_varname], diff_check_cols[0], diff_check_cols[3])
            change_across_2 = get_nse(evaluation_dfs[f"{row['ParName']}"][row_2.f_varname], diff_check_cols[1], diff_check_cols[4])
            change_across_3 = get_nse(evaluation_dfs[f"{row['ParName']}"][row_2.f_varname], diff_check_cols[2], diff_check_cols[5])

            # print(change_in_cal_1,change_in_cal_2,change_in_cal_3,change_in_dir_1,change_in_dir_2,change_in_dir_3,change_across_1,change_across_2,change_across_3)
            if not row['ParName'] in dict_data:
                dict_data[row['ParName']] = {}
                dict_data_nses[row['ParName']] = {}
            
            if not row_2.f_varname in dict_data[row['ParName']]:
                dict_data[row['ParName']][row_2.f_varname] = {}
                dict_data_nses[row['ParName']][row_2.f_varname] = {}
            
            if (change_in_cal_1 != change_in_cal_2) or (change_in_cal_1 != change_in_cal_3) or (change_in_cal_2 != change_in_cal_3):
                dict_data[row['ParName']][row_2.f_varname]["Cal File"] = True
            else:
                dict_data[row['ParName']][row_2.f_varname]["Cal File"] = False

            if (change_in_dir_1 != change_in_dir_2) or (change_in_dir_1 != change_in_dir_3) or (change_in_dir_2 != change_in_dir_3):
                dict_data[row['ParName']][row_2.f_varname]["Direct"] = True
            else:
                dict_data[row['ParName']][row_2.f_varname]["Direct"] = False

            if (change_across_1 < 1) or (change_across_2 < 1) or (change_across_3 < 1):
                if (not change_across_1 == -999) and (not change_across_2 == -999) and (not change_across_3 == -999):
                    dict_data[row['ParName']][row_2.f_varname]["Equal"] = False
                else:
                    dict_data[row['ParName']][row_2.f_varname]["Equal"] = True
            else:
                dict_data[row['ParName']][row_2.f_varname]["Equal"] = True

            dict_data_nses[row['ParName']][row_2.f_varname]["Cal File"] = {"First": change_in_cal_1, "Second": change_in_cal_2, "Third": change_in_cal_3}
            dict_data_nses[row['ParName']][row_2.f_varname]["Direct"]   = {"First": change_in_dir_1, "Second": change_in_dir_2, "Third": change_in_dir_3}
            dict_data_nses[row['ParName']][row_2.f_varname]["Across"]   = {"First": change_across_1, "Second": change_across_2, "Third": change_across_3}
            dict_data_nses[row['ParName']][row_2.f_varname]["ParNames"] = {"First": diff_check_cols[0], "Second": diff_check_cols[1], "Third": diff_check_cols[2]}

    return dict_data, dict_data_nses

