#!/usr/bin/env python
#import argparse
#from glob import glob

#-s ./joint_vcfs_list.txt 
#-b /mnt/lfs2/hend6746/wolves/reference/canfam31/canfam31.fa

from os.path import join as jp
from os.path import abspath
import os
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-s', "--variants", help="List of joint (raw) variant (.vcf) files", required=True)
parser.add_argument('-b', "--bwaindex", help="Path to bwa index file.", required=True)
parser.add_argument('-l', "--lowcovlist", help="Path to txt file of low coverage individuals to remove.", required=True)
args = parser.parse_args()

VERBOSE=False

#Function definitions:
def log(txt, out):
    if VERBOSE:
        print(txt)
    out.write(txt+'\n')
    out.flush()

## Read in samples and put them in a list:
variants = []
for l in open(args.variants):
    if len(l) > 1:
        variants.append(l.split('/')[-1].replace('.vcf', '').strip())
print variants

# Setup folders and paths variables:
jointFolder = abspath('joint_vcf')
filteredFolder = abspath('joint_vcf/filtered')
PBS_scripts = abspath('filter_GATK_PBS_scripts')
bwaIndex = abspath(args.bwaindex)
lowCovList = abspath(args.lowcovlist)
gatkCall = 'java -jar /opt/modules/biology/gatk/3.5/bin/GenomeAnalysisTK.jar -R %s' % bwaIndex

os.system('mkdir -p %s' % jointFolder)
os.system('mkdir -p %s' % filteredFolder)
os.system('mkdir -p %s' % PBS_scripts)

##### Run pipeline ###
for variant in variants:
	print "Processing", variant, "....."
	# Set up files:
	logFile = jp(filteredFolder, variant + '_GATK_filter.log')
	logCommands = open(jp(PBS_scripts, variant + '_GATK_filter_commands.sh'), 'w')

	#Setup for qsub
	log('#!/bin/bash', logCommands)
	log('#PBS -N %s_filter' % variant, logCommands)
	log('#PBS -j oe', logCommands)
	log('#PBS -o %s_filter_job.log' % variant, logCommands)
	log('#PBS -m abe', logCommands)
	log('#PBS -M shendri4@gmail.com', logCommands)
	log('#PBS -q reg', logCommands)
	log('#PBS -l mem=100gb', logCommands)
	log(". /usr/modules/init/bash", logCommands)
	log("module load python/2.7.10", logCommands)
	log("module load grc", logCommands)

	################################## 
	## Evaluate all raw variants in file to see quality of variants before filters are applied (OPTIONAL)
	################################## 
	cmd = ' '.join([gatkCall, ' -T VariantEval ', 
	' -o ' + jp(jointFolder, variant + '.raw.eval.gatkreport.grp'), 
	' --eval: ' + jp(jointFolder, variant + '.vcf'), 
	' --doNotUseAllStandardStratifications ', ' --doNotUseAllStandardModules ', ' --evalModule CountVariants ',
	'>>', logFile, '2>&1'])
	log(cmd, logCommands)

	###########################################################################
	#### Exclude low cov samples
	cmd = ' '.join([gatkCall, ' -T SelectVariants ', 
	' -o ' + jp(jointFolder, variant + '_noLowCovInd.vcf'), 
	' -V ' + jp(jointFolder, variant + '.vcf'), 
	' --exclude_sample_file ' + lowCovList,
	'>>', logFile, '2>&1'])
	log(cmd, logCommands)
	
	###########################################################################
	#### Extract the SNPs from the call set
	cmd = ' '.join([gatkCall, ' -T SelectVariants ', 
	' -o ' + jp(jointFolder, variant + '_raw_SNPs_noLowCovInd.vcf'), 
	' -V ' + jp(jointFolder, variant + '_noLowCovInd.vcf'), 
	' -selectType SNP ',
	'>>', logFile, '2>&1'])
	log(cmd, logCommands)

	###########################################################################
	#### High quality filters
	#### Filter variant sites from raw variants
	cmd = ' '.join([gatkCall, ' -T VariantFiltration ', 
	' -V ' + jp(jointFolder, variant + '_raw_SNPs_noLowCovInd.vcf'), 
	' -o ' + jp(filteredFolder, variant + '_filtered_SNPs_noLowCovInd.vcf'), 
	' --filterExpression "QD < 2.0 || FS > 60.0 || MQ < 40.0 || MQRankSum < -12.5 || ReadPosRankSum < -8.0" ', 
	' --filterName "BadSNP" ',
	'>>', logFile, '2>&1'])
	log(cmd, logCommands)

	#### GQ20
	cmd = ' '.join([gatkCall, ' -T VariantFiltration ', 
	' -o ' + jp(filteredFolder, variant + '_GQ20_filtered_SNPs_noLowCovInd.vcf'), 
	' -V ' + jp(filteredFolder, variant + '_filtered_SNPs_noLowCovInd.vcf'), 
	' -G_filter "GQ < 20.0" ',
	' -G_filterName "lowGQ" ',
	'>>', logFile, '2>&1'])
	log(cmd, logCommands)

	#### Filter variant sites from raw variants
	cmd = ' '.join([gatkCall, ' -T VariantFiltration ', 
	' -V ' + jp(filteredFolder, variant + '_GQ20_filtered_SNPs_noLowCovInd.vcf'), 
	' -o ' + jp(filteredFolder, variant + '_minDP10_GQ20_filtered_SNPs_noLowCovInd.vcf'), 
	' --filterExpression "DP < 10.0" ', 
	' --filterName "BadSNP" ',
	'>>', logFile, '2>&1'])
	log(cmd, logCommands)
	
	# the DP threshold should be set a 5 or 6 sigma from the mean coverage across all samples, 
	# so that the DP > X threshold eliminates sites with excessive coverage caused by alignment artifacts.

	###########################################################################
	#### Exclude non-variant loci and filtered loci (trim remaining alleles by default):
	cmd = ' '.join([gatkCall, ' -T SelectVariants ', 
	' -o ' + jp(filteredFolder, variant + '_selected_minDP10_GQ20_filtered_SNPs_noLowCovInd.vcf'), 
	'  -V ' + jp(filteredFolder, variant + '_minDP10_GQ20_filtered_SNPs_noLowCovInd.vcf'), 
	' --env', ' --ef',
	'>>', logFile, '2>&1'])
	log(cmd, logCommands)

	###########################################################################
	################################## 
	## Evaluate all variants in file 
	################################## 
	cmd = ' '.join([gatkCall, ' -T VariantEval ', 
	' -o ' + jp(filteredFolder, variant + '_selected_GQ20_filtered_SNPs_noLowCovInd.eval.gatkreport.grp'), 
	' --eval: ' + jp(filteredFolder, variant + '_selected_minDP10_GQ20_filtered_SNPs_noLowCovInd.vcf'), 
	' --doNotUseAllStandardStratifications', ' --doNotUseAllStandardModules',
	' --evalModule CountVariants ',
	' --evalModule TiTvVariantEvaluator ',
	' --stratificationModule CompRod ',
	' --stratificationModule EvalRod ',
	' --stratificationModule Sample ',
	' --stratificationModule Filter ',
	' --stratificationModule FunctionalClass ',
	'>>', logFile, '2>&1'])
	log(cmd, logCommands)

	logCommands.close()