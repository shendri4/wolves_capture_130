#!/usr/bin/env python
#import argparse
#from glob import glob

#-s /mnt/lfs2/hend6746/wolves_87+rena/reheadered_bams_for_SH/rena_43samples.txt
#-b /mnt/lfs2/hend6746/wolves_87+rena/bed_files/baits_canfam3.1_sorted_merged.bed

from os.path import join as jp
from os.path import abspath
import os
import sys
import argparse
import commands

parser = argparse.ArgumentParser()
parser.add_argument('-s', "--samples", help="Samples.txt file with sample ID.", required=True)
parser.add_argument('-b', "--beddata", help="Path to bed data.", required=True)
args = parser.parse_args()

VERBOSE=False

#Function definitions:
def log(txt, out):
    if VERBOSE:
        print(txt)
    out.write(txt+'\n')
    out.flush()

## Read in samples and put them in a list:
samples = []
for l in open(args.samples):
    if len(l) > 1:
        samples.append(l.split('/')[-1].replace('.bam', '').strip())

# Setup folders and paths variables:
bamFolder = abspath('02-Mapped')
depthFolder = abspath('depth')
PBS_scripts = abspath('depth_scripts')

os.system('mkdir -p %s' % bamFolder)
os.system('mkdir -p %s' % depthFolder)
os.system('mkdir -p %s' % PBS_scripts)

############################################### create file#################################

##### Run pipeline ###
for sample in samples:
    print "Processing", sample, "....."
    # Set up files:
    logFile = jp(depthFolder, sample + '_depth.log')
    logCommands = open(jp(PBS_scripts, sample + 'depth_commands.sh'), 'w')

    #Setup for qsub
    log('#!/bin/bash', logCommands)
    log('#PBS -N %s' % sample, logCommands)
    log('#PBS -j oe', logCommands)
    log('#PBS -o %s_job.log' % sample, logCommands)
    log('#PBS -m abe', logCommands)
    log('#PBS -M shendri4@gmail.com', logCommands)
    log('#PBS -q short', logCommands)
    log(". /usr/modules/init/bash", logCommands)
    log("module load python/2.7.10", logCommands)
    log("module load grc", logCommands)

###########################################################################
#### Number of raw reads
    cmd = ' '.join(["samtools depth -a ", jp(bamFolder, sample + '.bam'), "-b ", abspath(args.beddata), " | awk '{ sum += $3 } END { if (NR > 0) print sum / NR }'", '>>', logFile, '2>&1'])
    log(cmd, logCommands)
    logCommands.close()