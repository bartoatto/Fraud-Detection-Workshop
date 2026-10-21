/*****************************************************************************
* qc_t_dm1.sas - QC program (double programming)
* Table 14.1: Summary of Demographic and Baseline Characteristics
* ----------------------------------------------------------------------------
* Written independently of the production program. Statistics come from PROC SQL,
* PROC UNIVARIATE and PROC FREQ instead of PROC MEANS and SQL counts.
*
* Input : ADAM.ADSL
* Output: TFLQC.QC_T_DM1 (sas7bdat) and qc_t_dm1.csv in the qc/tfl/ folder
*
* Run as a Domino Job:  exercises_sas/b_ProdAndQC/qc_t_dm1.sas
*
* Presenters can set the environment variable QC_INTRODUCE_DIFF=1 to plant one
* wrong number and show the compare program catching it.
*****************************************************************************/

%let wd = %sysget(DOMINO_WORKING_DIR);
%include "&wd/exercises_sas/setup/domino_setup.sas";

%let sec1 = Age (years);
%let sec2 = Age group, n (#);
%let sec3 = Sex, n (#);
%let sec4 = Race, n (#);
%let sec5 = Ethnicity, n (#);
%let sec6 = Baseline weight (kg);
%let sec7 = Baseline BMI (kg/m2);

/* --- Safety population, stacked: arms 1-3 plus Total as column 4 --- */
proc sql;
  create table qpop as
  select age, agegr1, sex, race, ethnic, weightbl, bmibl,
         case arm when 'Placebo' then 1
                  when 'Xanomeline Low Dose' then 2
                  else 3 end as colno
  from adam.adsl
  where saffl = 'Y' and arm in ('Placebo', 'Xanomeline Low Dose', 'Xanomeline High Dose')
  union all
  select age, agegr1, sex, race, ethnic, weightbl, bmibl, 4 as colno
  from adam.adsl
  where saffl = 'Y';

  create table qdenom as
  select colno, count(*) as n from qpop group by colno;
quit;

proc sort data=qpop; by colno; run;

/* --- Continuous: PROC SQL for n/mean/SD/min/max, PROC UNIVARIATE for the median --- */
%macro qcont(var=, k=);
  proc sql;
    create table _s as
    select colno, count(&var) as n, mean(&var) as mean, std(&var) as sd, min(&var) as mn, max(&var) as mx
    from qpop group by colno;
  quit;

  proc univariate data=qpop noprint;
    by colno;
    var &var;
    output out=_med median=med;
  run;

  data _l;
    merge _s _med;
    by colno;
    length section characteristic $60 value $40;
    section = "&&sec&k";
    ord = &k * 10 + 1; characteristic = 'n';
    value = strip(put(n, 8.)); output;
    ord = &k * 10 + 2; characteristic = 'Mean (SD)';
    value = catx(' ', strip(put(round(mean, 0.1), 8.1)), cats('(', strip(put(round(sd, 0.01), 8.2)), ')')); output;
    ord = &k * 10 + 3; characteristic = 'Median';
    value = strip(put(round(med, 0.1), 8.1)); output;
    ord = &k * 10 + 4; characteristic = 'Min - Max';
    value = catx(' ', strip(put(mn, 8.0)), '-', strip(put(mx, 8.0))); output;
    keep ord section characteristic colno value;
  run;

  proc append base=qlong data=_l force; run;
%mend qcont;

/* --- Categorical: PROC FREQ with SPARSE so empty cells show as 0 --- */
%macro qcat(var=, k=, type=);
  proc freq data=qpop noprint;
    tables colno * &var / sparse out=_f(drop=percent rename=(&var=level));
  run;

  proc sql;
    create table _lv as
    select distinct &var as level length=60 from qpop where not missing(&var) order by &var;
  quit;

  data _lv;
    set _lv;
    length lvlabel $60;
    %if &type = age %then %do; lvord = whichc(level, '<65', '65-80', '>80'); %end;
    %else %if &type = sex %then %do; lvord = whichc(level, 'F', 'M'); %end;
    %else %do; lvord = _n_; %end;
    lvlabel = level;
    if level = 'F' then lvlabel = 'Female';
    if level = 'M' then lvlabel = 'Male';
  run;

  proc sql;
    create table _l as
    select &k * 10 + v.lvord as ord length=8,
           "&&sec&k" as section length=60,
           v.lvlabel as characteristic length=60,
           f.colno as colno,
           catx(' ', strip(put(f.count, 8.)),
                cats('(', strip(put(round(100 * f.count / d.n, 0.1), 8.1)), byte(37), ')')) as value length=40
    from _f as f, qdenom as d, _lv as v
    where f.colno = d.colno and f.level = v.level;
  quit;

  proc append base=qlong data=_l force; run;
%mend qcat;

proc datasets lib=work nolist; delete qlong; quit;

%qcont(var=age,      k=1);
%qcat (var=agegr1,   k=2, type=age);
%qcat (var=sex,      k=3, type=sex);
%qcat (var=race,     k=4, type=alpha);
%qcat (var=ethnic,   k=5, type=alpha);
%qcont(var=weightbl, k=6);
%qcont(var=bmibl,    k=7);

data _n;
  set qdenom;
  length section characteristic $60 value $40;
  ord = 0; section = ''; characteristic = 'Subjects in population'; value = strip(put(n, 8.));
  keep ord section characteristic colno value;
run;
proc append base=qlong data=_n force; run;

proc sort data=qlong; by ord section characteristic colno; run;
proc transpose data=qlong out=qwide(drop=_name_) prefix=c;
  by ord section characteristic;
  id colno;
  var value;
run;

data qhdr;
  length section characteristic $60;
  do k = 1 to 7;
    ord = k * 10;
    section = symget(cats('sec', k));
    characteristic = '';
    output;
  end;
  keep ord section characteristic;
run;

data qfinal;
  length section characteristic $60 c1 c2 c3 c4 $40;
  set qwide qhdr;
  section = translate(section, byte(37), '#');
run;
proc sort data=qfinal; by ord; run;

/* --- Presenter demo: plant one wrong number --- */
%let planted = %sysget(QC_INTRODUCE_DIFF);
%macro plant;
  %if %length(&planted) > 0 %then %do;
    data qfinal;
      set qfinal;
      if section = 'Age (years)' and characteristic = 'Median' then c4 = '99.9';
    run;
    %put NOTE: QC_INTRODUCE_DIFF set - changed Age median (Total) to 99.9;
  %end;
%mend plant;
%plant;

data tflqc.qc_t_dm1;
  set qfinal;
  keep ord section characteristic c1-c4;
run;

data _null_;
  file "&DATA_DIR/qc/tfl/qc_t_dm1.csv" lrecl=2000;
  put 'Section,Characteristic,Placebo,Xanomeline Low Dose,Xanomeline High Dose,Total';
run;
data _null_;
  set tflqc.qc_t_dm1;
  file "&DATA_DIR/qc/tfl/qc_t_dm1.csv" dsd mod lrecl=2000;
  put section characteristic c1 c2 c3 c4;
run;

%put NOTE: Wrote &DATA_DIR/qc/tfl/qc_t_dm1.csv;
