#!/bin/bash
### The goal of this script is to generate phased data and recombination rate file for finestructure
### Written by SAH
### Last modified: 01/16/17
### Usage: ./00_prep4fs.sh [RUN_DATE] [FILE_NAME]

module load finestructure
module load chromopainter
module load vcftools
module load plink

### user-defined variables ###
RUN_DATE=$1
FILE_NAME=$2

### Directories
beagle_dir="/mnt/lfs2/hend6746/modules/beagle/4.1/"
chromo_dir="/mnt/lfs2/hend6746/modules/chromopainter/"
proj_dir="/mnt/lfs2/hend6746/wolves_87+rena"
in_dir=${proj_dir}/coastal_genotypes_FINAL/data_files/126indiv_allSites/
results_dir=${proj_dir}/fineStructure/${RUN_DATE}/phased_beagle/
fs_in_dir=${proj_dir}/fineStructure/${RUN_DATE}/fs_input/

mkdir -p $results_dir
mkdir -p $fs_in_dir
mkdir -p $fs_out_dir

### Beagle 4.1
### estimate posterior genotype probabilities
java -jar $beagle_dir/"beagle.22Feb16.8ef.jar" nthreads=60 gtgl=$in_dir/$FILE_NAME out=$results_dir/"out_gtgl.gl"

### phase the genotypes
java -jar $beagle_dir/"beagle.22Feb16.8ef.jar" gt=$results_dir/"out_gtgl.gl.vcf.gz" out=$results_dir/"phased"

### create ped/map files
vcftools --gzvcf $results_dir/"phased.vcf.gz" --out $results_dir/"phased" --plink

### plink file needs to be run with recode12 for plink2chromopainter conversion
plink --file $results_dir/"phased" --out $results_dir/"phased_recode12" --recode12 --dog

### convert plink to chromopainter haps file
$chromo_dir/"plink2chromopainter.pl" -p=$results_dir/"phased_recode12.ped" -m=$results_dir/"phased_recode12.map" -o=$results_dir/"phased.phase"

### need to delete first line of phase file (there should only be three not four header lines); need to multiply number of individuals by 2; need to remove SSSSSSSSSS line(?)
###Run to make uniform recombination map
#$chromo_dir/"makeuniformrecfile.pl" $results_dir/"phased.phase" $fs_in_dir/"phased.recomrates"

### run fineStructure
#fs outputfile.cp --idfile indsfile.inds -phasefiles filename_recode12.phase -recombfiles filename_recode12.recombfile -go

