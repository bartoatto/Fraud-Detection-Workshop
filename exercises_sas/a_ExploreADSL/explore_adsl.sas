/*****************************************************************************
* explore_adsl.sas - Explore ADSL (CDISC pilot study, CDISCPILOT01)
* ----------------------------------------------------------------------------
* ADSL is the ADaM subject-level analysis dataset: one row per subject. This
* program runs the checks a programmer does before building any table, then
* saves a few plots to the artifacts folder.
*
* Run in SAS Studio (open the file and press Run), or as a Domino Job:
*   exercises_sas/a_ExploreADSL/explore_adsl.sas
*****************************************************************************/

%let wd = %sysget(DOMINO_WORKING_DIR);
%include "&wd/exercises_sas/setup/domino_setup.sas";

%ensure_dir(&ART_DIR, a_explore_adsl);

/* --- What is in the dataset? --- */
title "ADSL contents";
proc contents data=adam.adsl varnum; run;

/* --- Population and treatment arms --- */
title "Subjects by treatment arm and population flags";
proc freq data=adam.adsl;
  tables arm saffl efffl complfl eosstt;
run;

/* --- Data checks: each line in the log should say OK --- */
proc sql noprint;
  select count(*), count(distinct usubjid) into :n_rows trimmed, :n_subj trimmed from adam.adsl;
  select count(*) into :n_noarm trimmed from adam.adsl where missing(arm);
  select count(*) into :n_baddates trimmed from adam.adsl where not missing(trtedt) and not missing(trtsdt) and trtedt < trtsdt;
  select count(*) into :n_badage trimmed from adam.adsl
         where (age < 65 and agegr1 ne '<65') or (age > 80 and agegr1 ne '>80')
            or (65 <= age <= 80 and agegr1 ne '65-80');
  select count(*) into :n_compl_reas trimmed from adam.adsl where eosstt = 'COMPLETED' and not missing(dcsreas);
  select count(*) into :n_odd trimmed from adam.adsl where complfl = 'Y' and eosstt = 'DISCONTINUED';
quit;

%macro check(label, bad);
  %if &bad = 0 %then %put NOTE: OK    - &label;
  %else %put WARNING: FAIL  - &label (&bad rows);
%mend check;

%let dups = %eval(&n_rows - &n_subj);
%check(One row per subject (USUBJID unique), &dups);
%check(Every subject has an arm, &n_noarm);
%check(Treatment end is not before treatment start, &n_baddates);
%check(Age group agrees with AGE, &n_badage);
%check(Subjects who completed the study have no discontinuation reason, &n_compl_reas);

%put NOTE: &n_odd subjects are flagged as completers (COMPLFL=Y) but discontinued the study (EOSSTT).;
%put NOTE: Check the definition of COMPLFL before using it for a completer analysis.;

title "Flagged as completers but discontinued the study";
proc print data=adam.adsl noobs;
  where complfl = 'Y' and eosstt = 'DISCONTINUED';
  var usubjid arm complfl eosstt dcsreas trtdurd;
run;

/* --- Demographics by arm: plots saved to artifacts --- */
ods listing gpath="&ART_DIR/a_explore_adsl";
ods graphics / imagefmt=png width=800px height=500px;

ods graphics / imagename="age_by_arm";
title "Age by treatment arm";
proc sgpanel data=adam.adsl;
  panelby arm / columns=3;
  histogram age;
run;

ods graphics / imagename="sex_by_arm";
title "Sex by treatment arm";
proc sgplot data=adam.adsl;
  vbar arm / group=sex groupdisplay=cluster;
run;

ods graphics / imagename="disposition_by_arm";
title "Disposition by treatment arm";
proc sgplot data=adam.adsl;
  vbar arm / group=eosstt groupdisplay=cluster;
run;

ods graphics / imagename="exposure_by_arm";
title "Treatment duration (days) by arm";
proc sgplot data=adam.adsl;
  vbox trtdurd / category=arm;
run;

ods listing close;
title;
