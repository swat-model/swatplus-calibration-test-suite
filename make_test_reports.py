#!/bin/python3

'''
This script tests parameter sensitivity
if changed in calibration.cal

Author  : Celray James CHAWANDA
Email   : celray.chawanda@outlook.com
Licence : MIT
Repo    : https://github.com/celray

Date    : 2023-05-23
'''

# imports
from cjfx import *
from modules import samples_runner, summary_plot

ignore_warnings()

if __name__ == "__main__":

    # set default working directory to the script location
    os.chdir(os.path.dirname(__file__))

    # variables
    out_dir         = create_path('./output/')                          # output directory
    summary_fig_dir = create_path(f'./{out_dir}/summary-figures/')      # summary figures directory
    executable_path = "./executables/SWATPlus64_linux"                  # replace with your executable path

    txtinout        = "./models/07020011_Lesueur"                       # SWAT+ txtinout directory, you can add your own here

    revision        = "Rev 60.5.7"
    rev_date        = "25/05/2023"

    case_details    = "This is an axample case study."

    
    dict_data_archive = []
    dict_data_archive_nses = []

    batches = [
        ["HRU Tile and Field Parameters",           "./inputs/hru_parameters-tile-and-fld.csv",    "./inputs/hru_tracked_outputs-tile-and-fld.csv"],
        ["General HRU Water Balance Parameters",    "./inputs/hru_parameters-wb.csv",              "./inputs/hru_tracked_outputs-wb.csv"],
        ["HRU Water Quality Parameters",            "./inputs/hru_parameters-wq.csv",              "./inputs/hru_tracked_outputs-wq.csv"],                     # Check against channel and include Organic Nitrogen
        ["Aquifer Parameters",                      "./inputs/aqu_parameters.csv",                 "./inputs/aqu_tracked_outputs.csv"],
        ["BSN Parameters (Part 1)",                 "./inputs/bsn_parameters_1.csv",               "./inputs/bsn_tracked_outputs.csv"],
        ["BSN Parameters (Part 2)",                 "./inputs/bsn_parameters_2.csv",               "./inputs/bsn_tracked_outputs.csv"],
    ]

    # make change_types for report
    change_types = {}
    for batch in batches:
        for index, row in pandas.read_csv(batch[1]).iterrows():
            change_types[row["ParName"]] = row["Change_Type"]

    for batch in batches:
        dict_data, dict_data_nses = samples_runner.get_data(batch[1], txtinout, os.path.dirname(__file__), batch[2], os.path.abspath(executable_path))
        dict_data_archive.append(dict_data)
        dict_data_archive_nses.append(dict_data_nses)
        Done = summary_plot.make_plot(dict_data, f'{summary_fig_dir}/hru-{batch[0]}.png', ncols=7,)

    doc     = word_document(f"{out_dir}/documents/report.docx")
    doc2    = word_document(f"{out_dir}/documents/report-extended.docx")

    doc.add_heading(f"Report for Tests on {revision} ({rev_date})", level=1)
    doc2.add_heading(f"Report for Tests on {revision} ({rev_date})", level=1)
    doc.add_paragraph(f"This report (generated on {datetime.date.today()}) highlights which parameters are sensitive if changed via direct means vs if changed via calibration.cal. It also highlights which parameters are disconnected (dummy).")
    doc2.add_paragraph(f"This report (generated on {datetime.date.today()}) highlights which parameters are sensitive if changed via direct means vs if changed via calibration.cal. It also highlights which parameters are disconnected (dummy).")

    doc.add_paragraph(f"Note that these results might have been influenced by the choice of the case study used in the study. {case_details}")
    doc2.add_paragraph(f"Note that these results might have been influenced by the choice of the case study used in the study. {case_details}")
    
    doc.add_paragraph("Of all parameters tested, the following list highlights which parameters might have problems:")
    doc2.add_paragraph("Of all parameters tested, the following list highlights which parameters might have problems:")
    
    for i in range(0, len(batches)):
        is_batch_added = False

        for par in dict_data_archive[i]:
            has_issue           = False

            sensitive_cal       = True
            sensitive_dir       = True
            different_dir_cal   = False

            cal_file_track      = []
            direct_track        = []

            for tracked_out in dict_data_archive[i][par]:
                if not dict_data_archive[i][par][tracked_out]["Equal"]:
                    different_dir_cal = True
                
                cal_file_track.append(dict_data_archive[i][par][tracked_out]["Cal File"])
                direct_track.append(dict_data_archive[i][par][tracked_out]["Direct"])

            if (len(list(set(cal_file_track))) == 1) and (list(set(cal_file_track))[0] == False):
                sensitive_cal = False
            if (len(list(set(direct_track))) == 1) and (list(set(direct_track))[0] == False):
                sensitive_dir = False

            if (not sensitive_cal) or (not sensitive_dir) or (different_dir_cal):
                has_issue = True

            if has_issue:     
                if not is_batch_added:
                    doc.add_paragraph(f"")
                    doc2.add_paragraph(f"")
                    doc.add_text(f"{batches[i][0]}", italic=True)
                    doc2.add_text(f"{batches[i][0]}", italic=True)
                    is_batch_added = True

                doc.add_list_item()
                doc.add_text(f"{par} :", bold=True)

                doc2.add_list_item()
                doc2.add_text(f"{par} :", bold=True)

                if not sensitive_cal:
                    doc.add_text(' not sensitive with calibration.cal')
                    doc2.add_text(' not sensitive with calibration.cal')

                if not sensitive_dir:
                    if not sensitive_cal:
                        doc.add_text(', not sensitive with direct changes')
                        doc2.add_text(', not sensitive with direct changes')
                    else:
                        doc.add_text(' not sensitive with direct changes')
                        doc2.add_text(' not sensitive with direct changes')

                if different_dir_cal:
                    if (not sensitive_cal) or (not sensitive_dir):
                        doc.add_text(', calibration.cal results are different from direct change results')
                        doc2.add_text(', calibration.cal results are different from direct change results')
                    else:
                        doc.add_text(' calibration.cal results are different from direct change results')
                        doc2.add_text(' calibration.cal results are different from direct change results')


    count = 0
    figures_number = 1
    figures_number_extended = 1
    for i in range(0, len(batches)):

        count += 1

        var_lookup = {}
        for index, row in pandas.read_csv(batches[i][2]).iterrows():
            var_lookup[row.f_varname] = row.varname

        doc.add_heading(f"{count}. {batches[i][0]}")
        doc.add_paragraph("The parameters considered include the following: ")

        doc.add_text(", ".join(pandas.read_csv(batches[i][1])['ParName'].to_list()), italic=True)

        doc.add_heading("Summary", level=3)
        doc.add_paragraph(f"Figure {figures_number} provides a summary of how calibration using direct manipulation of input files vs changing the calibration.cal compares for")
        doc.add_text(f" {batches[i][0]}", italic=True)

        doc.add_image(f'{summary_fig_dir}/hru-{batches[i][0]}.png', 16)

        doc.add_paragraph()
        doc.add_text(f"Figure {figures_number}: summary parameter sensitivity for {batches[i][0]}", italic=True)

        doc2.add_heading(f"{count}. {batches[i][0]}")
        doc2.add_paragraph("The parameters considered include the following: ")

        doc2.add_text(", ".join(pandas.read_csv(batches[i][1])['ParName'].to_list()), italic=True)

        doc2.add_heading("Summary", level=3)
        doc2.add_paragraph(f"Figure {figures_number_extended} provides a summary of how calibration using direct manipulation of input files vs changing the calibration.cal compares for")
        doc2.add_text(f" {batches[i][0]}", italic=True)

        doc2.add_image(f'{summary_fig_dir}/hru-{batches[i][0]}.png', 17)

        doc2.add_paragraph()
        doc2.add_text(f"Figure {figures_number_extended}: summary parameter sensitivity for {batches[i][0]}.", italic=True)

        figures_number += 1
        figures_number_extended += 1
    
    doc.add_heading("Details", level=3); doc2.add_heading("Details", level=3)

    for i in range(0, len(batches)):
        var_lookup = {}
        for index, row in pandas.read_csv(batches[i][2]).iterrows():
            var_lookup[row.f_varname] = row.varname

        for par in dict_data_archive[i]:
            doc.add_heading(par, level=4); doc2.add_heading(par, level=4)
            doc.add_paragraph(); doc2.add_paragraph()

            for tracked_out in dict_data_archive[i][par]:
                doc.add_text(f"The ")
                doc.add_text(f"{tracked_out} ", bold=True, italic=True)
                doc.add_text(f"from ")
                doc.add_text(f"direct ", italic=True)
                doc.add_text(f"{par} ", bold=True, italic=True)
                doc.add_text(f"changes is ")

                doc2.add_text(f"The ")
                doc2.add_text(f"{tracked_out} ", bold=True, italic=True)
                doc2.add_text(f"from ")
                doc2.add_text(f"direct ", italic=True)
                doc2.add_text(f"{par} ", bold=True, italic=True)
                doc2.add_text(f"changes is ")

                if dict_data_archive[i][par][tracked_out]["Equal"]:
                    doc.add_text("the same as that from")
                    doc2.add_text("the same as that from")

                    doc.add_text(" calibration.cal", italic=True)
                    doc.add_text(" changes. ")

                    doc2.add_text(" calibration.cal", italic=True)
                    doc2.add_text(f" changes (Figure {figures_number_extended}). ")

                else:
                    doc.add_text("NOT", bold=True)
                    doc.add_text(" the same as that from")

                    doc2.add_text("NOT", bold=True)
                    doc2.add_text(" the same as that from")
                    # more description

                    doc.add_text(" calibration.cal", italic=True)
                    doc.add_text(" changes. ")

                    doc2.add_text(" calibration.cal", italic=True)
                    doc2.add_text(f" changes (Figure {figures_number_extended}). ")
                    
                    first_apparent = False
                    second_apparent = False
                    third_apparent = False

                    first_val = dict_data_archive_nses[i][par][tracked_out]["Across"]["First"]
                    second_val = dict_data_archive_nses[i][par][tracked_out]["Across"]["Second"]
                    third_val = dict_data_archive_nses[i][par][tracked_out]["Across"]["Third"]
                    
                    apparent = False

                    slightly_apparent       = []
                    slightly_apparent_par   = []
                    very_apparent           = []
                    very_apparent_par       = []

                    mark_1 = 0.97
                    mark_2 = 0.70

                    if first_val < mark_1:
                        apparent = True
                        if first_val > mark_2:
                            first_apparent = "slightly apparent"
                            slightly_apparent.append("left")
                            slightly_apparent_par.append(dict_data_archive_nses[i][par][tracked_out]["ParNames"]["First"].split(':')[0])
                        else:
                            first_apparent = "very apparent"
                            very_apparent.append("left")
                            very_apparent_par.append(dict_data_archive_nses[i][par][tracked_out]["ParNames"]["First"].split(':')[0])

                    if second_val < mark_1:
                        apparent = True
                        if second_val > mark_2:
                            second_apparent = "slightly apparent"
                            slightly_apparent.append("middle")
                            slightly_apparent_par.append(dict_data_archive_nses[i][par][tracked_out]["ParNames"]["Second"].split(':')[0])
                        else:
                            second_apparent = "very apparent"
                            very_apparent.append("middle")
                            very_apparent_par.append(dict_data_archive_nses[i][par][tracked_out]["ParNames"]["Second"].split(':')[0])

                    if third_val < mark_1:
                        apparent = True
                        if third_val > mark_2:
                            third_apparent = "slightly apparent"
                            slightly_apparent.append("right")
                            slightly_apparent_par.append(dict_data_archive_nses[i][par][tracked_out]["ParNames"]["Third"].split(':')[0])
                        else:
                            third_apparent = "very apparent"
                            very_apparent.append("right")
                            very_apparent_par.append(dict_data_archive_nses[i][par][tracked_out]["ParNames"]["Third"].split(':')[0])

                    
                    if len(slightly_apparent) > 0:
                        if len(slightly_apparent) == 1:
                            doc.add_text(f" This is slightly apparent in the {slightly_apparent[0]} ({slightly_apparent_par[0]}) plot (Figure {figures_number})")
                            doc2.add_text(f" This is slightly apparent in the {slightly_apparent[0]} ({slightly_apparent_par[0]}) plot (Figure {figures_number})")
                        if len(slightly_apparent) == 2:
                            doc.add_text(f" This is slightly apparent in the {slightly_apparent[0]} ({slightly_apparent_par[0]}) and {slightly_apparent[1]} ({slightly_apparent_par[1]}) plots (Figure {figures_number})")
                            doc2.add_text(f" This is slightly apparent in the {slightly_apparent[0]} ({slightly_apparent_par[0]}) and {slightly_apparent[1]} ({slightly_apparent_par[1]}) plots (Figure {figures_number})")
                        if len(slightly_apparent) == 3:
                            doc.add_text(f" This is slightly apparent in all plots (Figure {figures_number})")
                            doc2.add_text(f" This is slightly apparent in all plots (Figure {figures_number})")
                    
                    if len(very_apparent) > 0:
                        if len(slightly_apparent) > 0:
                            if len(very_apparent) == 1:
                                doc.add_text(f" , and very apparent in the {very_apparent[0]} ({very_apparent_par[0]}) plot (Figure {figures_number})")
                                doc2.add_text(f" , and very apparent in the {very_apparent[0]} ({very_apparent_par[0]}) plot (Figure {figures_number})")
                            if len(very_apparent) == 2:
                                doc.add_text(f" , and very apparent in the {very_apparent[0]} ({very_apparent_par[0]}) and {very_apparent[1]} ({very_apparent_par[1]}) plots (Figure {figures_number})")
                            if len(very_apparent) == 3:
                                doc.add_text(f" , and very apparent in all plots (Figure {figures_number})")
                                doc2.add_text(f" , and very apparent in all plots (Figure {figures_number})")
                        
                        else:
                            if len(very_apparent) == 1:
                                doc.add_text(f" This is very apparent in the {very_apparent[0]} ({very_apparent_par[0]}) plot (Figure {figures_number})")
                                doc2.add_text(f" This is very apparent in the {very_apparent[0]} ({very_apparent_par[0]}) plot (Figure {figures_number})")
                            if len(very_apparent) == 2:
                                doc.add_text(f" This is very apparent in the {very_apparent[0]} ({very_apparent_par[0]}) and {very_apparent[1]} ({very_apparent_par[1]}) plots (Figure {figures_number})")
                                doc2.add_text(f" This is very apparent in the {very_apparent[0]} ({very_apparent_par[0]}) and {very_apparent[1]} ({very_apparent_par[1]}) plots (Figure {figures_number})")
                            if len(very_apparent) == 3:
                                doc.add_text(f" This is very apparent in all plots (Figure {figures_number})")
                                doc2.add_text(f" This is very apparent in all plots (Figure {figures_number})")


                if not dict_data_archive[i][par][tracked_out]["Equal"]:
                    doc.add_image(f'./{out_dir}/par-figures/{par}-{var_lookup[tracked_out]}.png', width_=17)

                    doc.add_paragraph()
                    doc.add_text(f"Figure {figures_number}: plots for {tracked_out} for different {par} values (change type is {change_types[par]}).", italic=True)
                    figures_number += 1
                    doc.add_paragraph()
                
                doc2.add_image(f'./{out_dir}/par-figures/{par}-{var_lookup[tracked_out]}.png', width_=17)

                doc2.add_paragraph()
                doc2.add_text(f"Figure {figures_number_extended}: plots for {tracked_out} for different {par} values (change type is {change_types[par]}).", italic=True)
                figures_number_extended += 1
                doc2.add_paragraph()

    doc.set_margins(margin=2); doc2.set_margins(margin=2)

    doc.save(); doc2.save()

print()
