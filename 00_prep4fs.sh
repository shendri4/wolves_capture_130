#!/bin/bash
module load finestructure
module load chromopainter
module load vcftools
module load plink

beagle_dir="/mnt/lfs2/hend6746/modules/beagle/4.1/"
chromo_dir="/mnt/lfs2/hend6746/modules/chromopainter/"
in_dir="/mnt/lfs2/hend6746/wolves_87+rena/"
results_dir="/mnt/lfs2/hend6746/wolves_87+rena/fineStructure/phased_beagle/"
fs_in_dir="/mnt/lfs2/hend6746/wolves_87+rena/fineStructure/fs_input/"
fs_out_dir="/mnt/lfs2/hend6746/wolves_87+rena/fineStructure/fs_output/"

mkdir -p $results_dir
mkdir -p $fs_in_dir
mkdir -p $fs_out_dir

#Beagle 4.1
# estimate posterior genotype probabilities
java -jar $beagle_dir/"beagle.22Feb16.8ef.jar" gtgl=$in_dir/"filename.vcf" out=$results_dir/"out_gtgl.gl"

'''
# phase the genotypes
java -jar $beagle_dir/"beagle.22Feb16.8ef.jar" gt=$results_dir/"out_gtgl.gl" out=$results_dir/"phased"

# create ped/map files
vcftools --gzvcf $results_dir/"phased.vcf.gz" --out $results_dir/"phased" --plink

# plink file needs to be run with recode12 for plink2chromopainter conversion
plink --file $results_dir/"phased" --out $results_dir/"phased_recode12" --recode12 --dog

#convert plink to chromopainter haps file
$chromo_dir/"plink2chromopainter.pl" -p=$results_dir/"phased_recode12.ped" -m=$results_dir/"phased_recode12.map" -o=$results_dir/"phased.phase"

# make recombination map?
$chromo_dir/"makeuniformrecfile.pl" $results_dir/"phased.phase" $fs_in_dir/"phased.recomrates"

# Found 96071 SNPS
# Note: No absolute recombination rate.
# You must perform EM estimation of Ne (e.g. -in -i 10) using chromopainter to use this recombination file
# ~ looks messed up

# run chromopainter
fs cp -g $results_dir/"phased.phase" -r $fs_in_dir/"phased.recomrates" -a 0 0 -in -i10 -o $fs_out_dir/"fs_output"
'''