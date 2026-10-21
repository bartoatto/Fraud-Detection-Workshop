/*****************************************************************************
* compare_t_dm1.sas - compare production and QC versions of Table 14.1
* ----------------------------------------------------------------------------
* Input : TFL.T_DM1 and TFLQC.QC_T_DM1
* Output: compare/t_dm1_summary.json and compare/t_dm1_compare.csv on the volume,
*         a PROC COMPARE report (PDF) in artifacts, and dominostats.json so the
*         result shows on the Domino Jobs screen.
*
* Run as a Domino Job:  exercises_sas/b_ProdAndQC/compare_t_dm1.sas
*****************************************************************************/

%let wd = %sysget(DOMINO_WORKING_DIR);
%include "&wd/exercises_sas/setup/domino_setup.sas";

%ensure_dir(&ART_DIR, b_prod_and_qc);

proc sort data=tfl.t_dm1   out=_prod(drop=ord); by section characteristic; run;
proc sort data=tflqc.qc_t_dm1 out=_qc(drop=ord);   by section characteristic; run;

/* --- Formal PROC COMPARE report --- */
ods pdf file="&ART_DIR/b_prod_and_qc/t_dm1_compare.pdf";
title "Table 14.1: production vs QC";
proc compare base=_prod compare=_qc listall;
  id section characteristic;
run;
ods pdf close;
title;

/* --- Cell-by-cell differences, for the summary and the review app --- */
data _diffs(keep=section characteristic column production qc)
     _counts(keep=cells only_prod only_qc);
  merge _prod(in=p rename=(c1=p1 c2=p2 c3=p3 c4=p4))
        _qc  (in=q rename=(c1=q1 c2=q2 c3=q3 c4=q4)) end=last;
  by section characteristic;
  length column $30 production qc $40;
  array pv {4} $40 p1-p4;
  array qv {4} $40 q1-q4;
  array nm {4} $30 _temporary_ ('Placebo' 'Xanomeline Low Dose' 'Xanomeline High Dose' 'Total');
  retain cells only_prod only_qc 0;

  if p and not q then only_prod + 1;
  else if q and not p then only_qc + 1;
  else do;
    do i = 1 to 4;
      cells + 1;
      if pv{i} ne qv{i} then do;
        column = nm{i}; production = pv{i}; qc = qv{i};
        output _diffs;
      end;
    end;
  end;
  if last then output _counts;
run;

proc sql noprint;
  select count(*) into :n_diffs trimmed from _diffs;
  select cells, only_prod, only_qc into :n_cells trimmed, :n_only_prod trimmed, :n_only_qc trimmed from _counts;
quit;

%let rows = %eval(&n_cells / 4);
%let status = Clean;
%macro set_status;
  %if &n_diffs > 0 or &n_only_prod > 0 or &n_only_qc > 0 %then %let status = Issues;
%mend set_status;
%set_status;

/* --- Differences as CSV (header only when there are none) --- */
data _null_;
  file "&DATA_DIR/compare/t_dm1_compare.csv" lrecl=2000;
  put 'Section,Characteristic,Column,Production,QC';
run;
data _null_;
  set _diffs;
  file "&DATA_DIR/compare/t_dm1_compare.csv" dsd mod lrecl=2000;
  put section characteristic column production qc;
run;

/* --- Summary JSON (same fields as the Python version) --- */
data _null_;
  file "&DATA_DIR/compare/t_dm1_summary.json";
  put '{';
  line = cats('  "table": "t_dm1",');                                 put line;
  line = cats('  "status": "', "&status", '",');                      put line;
  line = cats('  "rows_compared": ', "&rows", ',');                   put line;
  line = cats('  "cells_compared": ', "&n_cells", ',');               put line;
  line = cats('  "cell_differences": ', "&n_diffs", ',');             put line;
  line = cats('  "rows_only_in_production": ', "&n_only_prod", ',');  put line;
  line = cats('  "rows_only_in_qc": ', "&n_only_qc");                 put line;
  put '}';
run;

%write_dominostats(table=t_dm1, status=&status, cells=&n_cells, diffs=&n_diffs);

%put NOTE: Table t_dm1 comparison status = &status (&n_diffs cell differences in &n_cells cells);
title "Differences between production and QC";
proc print data=_diffs noobs; run;
title;
