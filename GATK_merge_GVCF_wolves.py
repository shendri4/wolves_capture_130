#!/usr/bin/env python
#import argparse
#from glob import glob

#Usage: python ../fox_wgs/jointgenotyping_GATK.py 
#-s ./samples.txt 
#-b /mnt/lfs2/hend6746/wolves/reference/canfam31/canfam31.fa

from os.path import join as jp
from os.path import abspath
import os
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-s', "--samples", help="Samples.txt file with sample ID.", required=True)
parser.add_argument('-b', "--bwaindex", help="Path to bwa index file.", required=True)
args = parser.parse_args()

VERBOSE=False

#Function definitions:
def log(txt, out):
    if VERBOSE:
        print(txt)
    out.write(txt+'\n')
    out.flush()

## Read in samples and put them in a list:
# samples = []
# for l in open(args.samples):
#     if len(l) > 1:
#         samples.append(l.split('/')[-1].replace('.bam', '').strip())

# Setup folders and paths variables:
bamFolder = abspath('02-Mapped')
variantFolder = abspath('03-Calls')
mergedFolder = abspath('04-Merged_Calls')
jointFolder = abspath('05-Joint_Calls')
PBS_scripts = abspath('merged_GATK_PBS_scripts')
bwaIndex = abspath(args.bwaindex)
gatkCall = 'java -jar /opt/modules/biology/gatk/3.5/bin/GenomeAnalysisTK.jar -R %s' % bwaIndex

os.system('mkdir -p %s' % bamFolder)
os.system('mkdir -p %s' % variantFolder)
os.system('mkdir -p %s' % mergedFolder)
os.system('mkdir -p %s' % PBS_scripts)
os.system('mkdir -p %s' % jointFolder)

logFile = jp(jointFolder, 'merged_GATK.log')
logCommands = open(jp(PBS_scripts, 'merged_commands.sh'), 'w')

#Setup for qsub
log('#!/bin/bash', logCommands)
log('#PBS -N merged', logCommands)
log('#PBS -j oe', logCommands)
log('#PBS -o merged_job.log', logCommands)
log('#PBS -m abe', logCommands)
log('#PBS -M shendri4@gmail.com', logCommands)
log('#PBS -q reg', logCommands)
log('#PBS -l mem=100gb', logCommands)
log(". /usr/modules/init/bash", logCommands)
log("module load python/2.7.10", logCommands)
log("module load grc", logCommands)

variants = []
for sample in open(args.samples):
    sample = ' '.join(['--variant' + sample])
    variants.append(sample)
variantList = ' '.join(str(x) for x in variants)
print variantList
###########Merge Gvcf files
cmd = ' '.join([gatkCall, ' -T CombineGVCFs ', variantList, ' -o ' + jp(mergedFolder, 'merged_variants.vcf'), '>>', logFile, '2>&1'])
log(cmd, logCommands)

logCommands.close()