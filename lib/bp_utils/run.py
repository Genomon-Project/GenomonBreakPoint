#! /usr/bin/env python

import sys, os, gzip, subprocess
import parse

def parse_main(args):

    parse.parse_bp_from_bam(args.bam_file, args.output_file + ".bp.tmp.txt", args.key_seq_size, args.min_major_clip_size, args.max_minor_clip_size)

    parse.cluster_breakpoint(args.output_file + ".bp.tmp.txt", args.output_file + ".bp.clustered.tmp.txt", args.check_interval)

    hout = open(args.output_file + ".bp.clustered.sorted.tmp.txt", 'w')
    s_ret = subprocess.call(["sort", "-k1,1", "-k2,2n", args.output_file + ".bp.clustered.tmp.txt"], stdout = hout)
    hout.close()

    if s_ret != 0:
        print >> sys.stderr, "Error in sorting merged junction file"
        sys.exit(1)

    hout = open(args.output_file, 'w')
    s_ret = subprocess.call(["bgzip", "-f", "-c", args.output_file + ".bp.clustered.sorted.tmp.txt"], stdout = hout)
    hout.close()

    if s_ret != 0:
        print >> sys.stderr, "Error in compression merged junction file"
        sys.exit(1)


    s_ret = subprocess.call(["tabix", "-p", "vcf", args.output_file])
    if s_ret != 0:
        print >> sys.stderr, "Error in indexing merged junction file"
        sys.exit(1)

    subprocess.call(["rm", "-f", args.output_file + ".bp.tmp.txt"])
    subprocess.call(["rm", "-f", args.output_file + ".bp.clustered.tmp.txt"])
    subprocess.call(["rm", "-f", args.output_file + ".bp.clustered.sorted.tmp.txt"])
   

def merge_control_main(args):

    # make directory for output if necessary
    if os.path.dirname(args.output_file) != "" and not os.path.exists(os.path.dirname(args.output_file)):
        os.makedirs(os.path.dirname(args.output_file))

    hout = open(args.output_file + ".unsorted", 'w')
    with open(args.bp_file_list, 'r') as hin:
        for line in hin:
            bp_file = line.rstrip('\n')
            with gzip.open(bp_file, 'r') as hin2:
                for line2 in hin2:

                    F = line2.rstrip('\n').split('\t')
                    support_num = len(F[6].split(';'))
                    if support_num < args.support_num_thres: continue 
                    print >> hout, F[0] + '\t' + F[1] + '\t' + F[2] + '\t' + F[3] + '\t' + str(support_num)
                

    hout = open(args.output_file + ".sorted", 'w')
    s_ret = subprocess.call(["sort", "-k1,1", "-k2,2n", "-k3,3n", "-k4,4", args.output_file + ".unsorted"], stdout = hout)
    hout.close()

    if s_ret != 0:
        print >> sys.stderr, "Error in sorting merged junction file"
        sys.exit(1)


    hout = open(args.output_file + ".merged", 'w')
    with open(args.output_file + ".sorted", 'r') as hin:
        temp_key = ""
        temp_read_num = []
        for line in hin:
            F = line.rstrip('\n').split('\t')
            key = F[0] + '\t' + F[1] + '\t' + F[2] + '\t' + F[3]
            support_num = int(F[4])
            if key != temp_key:
                if temp_key != "":
                    if len(temp_read_num) >= args.sample_num_thres:
                        print >> hout, temp_key + '\t' + ','.join(temp_read_num)
                temp_key = key
                temp_read_num = []
            else:
                temp_read_num.append(str(support_num))

        if len(temp_read_num) >= args.sample_num_thres:
            print >> hout, temp_key + '\t' + ','.join(temp_read_num)

    hout.close()



    hout = open(args.output_file, 'w')
    s_ret = subprocess.call(["bgzip", "-f", "-c", args.output_file + ".merged"], stdout = hout)
    hout.close()

    if s_ret != 0:
        print >> sys.stderr, "Error in compression merged junction file"
        sys.exit(1)


    s_ret = subprocess.call(["tabix", "-p", "vcf", args.output_file])
    if s_ret != 0:
        print >> sys.stderr, "Error in indexing merged junction file"
        sys.exit(1)

    subprocess.call(["rm", "-f", args.output_file + ".unsroted"])
    subprocess.call(["rm", "-f", args.output_file + ".sorted"])
    subprocess.call(["rm", "-f", args.output_file + ".merged"])
 
