# wolves_capture_130
Scripts to process from bqsr, gatk, analyses of my 96 + rena's 43 samples

Mapped reads to GATK:
Run bam2vcf_GATK_wolves.py to create bash scripts (then created another batch pbs script to run on cluster)
Example bash script: recal_RKW977_addRG_realign_fixMate.reheadered_min2var_FIXED_GATK_commands.sh


Merge individual GVCF files:
Run GATK_merge_GVCF_wolves.py to create bash script to run on cluster


Joint genotyping: (I got lazy and ran it in the commandline and didn't write a script, but this is an example)
jointgenotyping_GATK.py (might not work properly, yet)


Filter genotypes:
Run GATK_variantFilters_wolves.py to create bash script to run on cluster
Example: joint_130_variants_GATK_filter_commands.sh