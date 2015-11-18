__author__ = 'Tiannan Guo, ETH Zurich 2015'

import gzip
import sys
import csv
import numpy as np
import time
import swath_quant
from collections import defaultdict
import io_swath
import peaks
import peak_groups
import r_code
import chrom
import parameters

# name of files
# chrom_file = 'com_chrom_10_test.txt.gz'    #sys.argv[1]
# chrom_file = 'com_chrom_2.txt.gz'    #sys.argv[1]
# chrom_file = sys.argv[1]
chrom_file = 'debug_png_id_3.txt.gz'
id_mapping_file = 'goldenSets90.txt'
# id_mapping_file = 'goldenSets90_test.txt'
out_R_file = chrom_file.replace('.txt.gz', '.R')
out_file_poor_tg = chrom_file.replace('.txt.gz', '.poor.txt')
quant_file = chrom_file.replace('.txt.gz', '.quant.txt')


def write_tmp_bat_file(out_R_file):
    with open('tmp_run.bat','w') as o:
        cmd = '''C:\\R\\R-2.15.1\\bin\\x64\\Rcmd.exe BATCH %s\n''' % out_R_file
        o.write(cmd)

def main():

    # read input file of sample inforamtion
    sample_id, id_mapping = io_swath.read_id_file(id_mapping_file)

    # read input chrom file,
    # build chrom_data, find peaks when the class is initialized
    ref_sample_data, chrom_data, peptide_data = io_swath.read_com_chrom_file(chrom_file, sample_id)

    # based on peaks of fragments, keep peak groups with at least MIN_FRAGMENT fragment, find out peak boundary of each fragment
    peak_group_candidates = peak_groups.find_peak_group_candidates(chrom_data, sample_id)

    # based on peak groups found in the reference sample, find out fragments that form good peaks, remove the rest fragments
    ref_sample_data, chrom_data, peptide_data, peak_group_candidates = \
        peak_groups.refine_peak_forming_fragments_based_on_reference_sample(ref_sample_data, chrom_data, peptide_data, peak_group_candidates)

    #TODO
    #read library file to get annotation for the fragments

    # compute the peak boundary for the reference sample, write to display_pg
    display_data = chrom.compute_reference_sample_peak_boundary(ref_sample_data, chrom_data, peptide_data, peak_group_candidates)

    # based on the display_data for reference sample, get the best matched peak groups from all other samples
    # and then write to display_data
    display_data = peak_groups.find_best_peak_group_based_on_reference_sample(
        display_data, ref_sample_data, chrom_data, peptide_data, peak_group_candidates, sample_id)

    # compute peak area for display_pg
    display_data = chrom.compute_peak_area_for_all(display_data)

    for tg in display_data.keys():
        if len(display_data[tg][sample_id[0]]['ms2']['rt_list'].keys()) > parameters.MIN_FRAGMENTS:
            # write r code into a file
            r_code.write_r_code_for_all_samples(display_data, sample_id, out_R_file)

            # write quantitation table
            d = swath_quant.quant(display_data, quant_file)
        else:
            print 'not enough fragments for ' + tg

start_time = time.time()
main()
write_tmp_bat_file(out_R_file)  #########3tmp
print "--- %s seconds ---" % (time.time() - start_time)
