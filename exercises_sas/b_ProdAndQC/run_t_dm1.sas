/*****************************************************************************
* run_t_dm1.sas - run the whole Table 14.1 workflow as one Domino Job
* ----------------------------------------------------------------------------
* Production, then QC, then the comparison, in that order. Each step is the same
* program you can also run on its own.
*
* Run as a Domino Job:  exercises_sas/b_ProdAndQC/run_t_dm1.sas
*****************************************************************************/

%let wd = %sysget(DOMINO_WORKING_DIR);

%put NOTE: ===== 1/3 Production program =====;
%include "&wd/exercises_sas/b_ProdAndQC/prod_t_dm1.sas";

%put NOTE: ===== 2/3 QC program (independent) =====;
%include "&wd/exercises_sas/b_ProdAndQC/qc_t_dm1.sas";

%put NOTE: ===== 3/3 Compare production and QC =====;
%include "&wd/exercises_sas/b_ProdAndQC/compare_t_dm1.sas";
