/*****************************************************************************
* prod_t_dm1.sas - PRODUCTION program
* Table 14.1: Summary of Demographic and Baseline Characteristics
*             Safety population, by treatment arm
* ----------------------------------------------------------------------------
* Input : ADAM.ADSL
* Output: TFL.T_DM1 (sas7bdat), t_dm1.csv and t_dm1.html in the tfl/ folder
*
* Run as a Domino Job:  exercises_sas/b_ProdAndQC/prod_t_dm1.sas
*****************************************************************************/

%let wd = %sysget(DOMINO_WORKING_DIR);
%include "&wd/exercises_sas/setup/domino_setup.sas";

/* Section titles. '#' stands for a percent sign and is replaced at the end. */
%let sec1 = Age (years);
%let sec2 = Age group, n (#);
%let sec3 = Sex, n (#);
%let sec4 = Race, n (#);
%let sec5 = Ethnicity, n (#);
%let sec6 = Baseline weight (kg);
%let sec7 = Baseline BMI (kg/m2);

/* --- Analysis population: safety set. COLNO 1-3 = arms, 4 = Total --- */
data pop;
  set adam.adsl;
  where saffl = 'Y';
  select (arm);
    when ('Placebo')              colno = 1;
    when ('Xanomeline Low Dose')  colno = 2;
    when ('Xanomeline High Dose') colno = 3;
    otherwise                     colno = .;
  end;
  if colno ne . then output;
  colno = 4;
  output;
run;

proc sql;
  create table denom as
  select colno, count(*) as n from pop group by colno;
quit;

/* --- Continuous variable: n, Mean (SD), Median, Min - Max --- */
%macro cont(var=, k=);
  proc means data=pop noprint nway;
    class colno;
    var &var;
    output out=_m n=n mean=mean std=std median=median min=min max=max;
  run;

  data _l;
    set _m;
    length section characteristic $60 value $40;
    section = "&&sec&k";
    ord = &k * 10 + 1; characteristic = 'n';
    value = strip(put(n, 8.)); output;
    ord = &k * 10 + 2; characteristic = 'Mean (SD)';
    value = catx(' ', strip(put(round(mean, 0.1), 8.1)), cats('(', strip(put(round(std, 0.01), 8.2)), ')')); output;
    ord = &k * 10 + 3; characteristic = 'Median';
    value = strip(put(round(median, 0.1), 8.1)); output;
    ord = &k * 10 + 4; characteristic = 'Min - Max';
    value = catx(' ', strip(put(min, 8.0)), '-', strip(put(max, 8.0))); output;
    keep ord section characteristic colno value;
  run;

  proc append base=long data=_l force; run;
%mend cont;

/* --- Categorical variable: n (%) for each level in dataset LV --- */
%macro cat(var=, k=, lv=);
  proc sql;
    create table _l as
    select &k * 10 + l.lvord as ord length=8,
           "&&sec&k" as section length=60,
           l.lvlabel as characteristic length=60,
           d.colno as colno,
           catx(' ', strip(put(coalesce(c.cnt, 0), 8.)),
                cats('(', strip(put(round(100 * coalesce(c.cnt, 0) / d.n, 0.1), 8.1)), byte(37), ')')) as value length=40
    from &lv as l
         cross join denom as d
         left join (select colno, &var as level, count(*) as cnt from pop group by colno, &var) as c
           on c.colno = d.colno and c.level = l.level;
  quit;

  proc append base=long data=_l force; run;
%mend cat;

/* Level lists */
data lv_age;
  length level lvlabel $60;
  input lvord level $ 3-10;
  lvlabel = level;
  datalines;
1 <65
2 65-80
3 >80
;
run;

data lv_sex;
  length level lvlabel $60;
  lvord = 1; level = 'F'; lvlabel = 'Female'; output;
  lvord = 2; level = 'M'; lvlabel = 'Male';   output;
run;

proc sql;
  create table lv_race as
  select distinct race as level length=60, race as lvlabel length=60 from pop where not missing(race) order by race;
  create table lv_ethnic as
  select distinct ethnic as level length=60, ethnic as lvlabel length=60 from pop where not missing(ethnic) order by ethnic;
quit;
data lv_race;   set lv_race;   lvord = _n_; run;
data lv_ethnic; set lv_ethnic; lvord = _n_; run;

/* --- Build the long table --- */
proc datasets lib=work nolist; delete long; quit;

%cont(var=age,      k=1);
%cat (var=agegr1,   k=2, lv=lv_age);
%cat (var=sex,      k=3, lv=lv_sex);
%cat (var=race,     k=4, lv=lv_race);
%cat (var=ethnic,   k=5, lv=lv_ethnic);
%cont(var=weightbl, k=6);
%cont(var=bmibl,    k=7);

/* First row: number of subjects */
data _n;
  set denom;
  length section characteristic $60 value $40;
  ord = 0; section = ''; characteristic = 'Subjects in population'; value = strip(put(n, 8.));
  keep ord section characteristic colno value;
run;
proc append base=long data=_n force; run;

/* --- One column per arm --- */
proc sort data=long; by ord section characteristic colno; run;
proc transpose data=long out=wide(drop=_name_) prefix=c;
  by ord section characteristic;
  id colno;
  var value;
run;

/* Section heading rows (title only, no values) */
data hdr;
  length section characteristic $60;
  do k = 1 to 7;
    ord = k * 10;
    section = symget(cats('sec', k));
    characteristic = '';
    output;
  end;
  keep ord section characteristic;
run;

data final;
  length section characteristic $60 c1 c2 c3 c4 $40;
  set wide hdr;
  section = translate(section, byte(37), '#');
run;
proc sort data=final; by ord; run;

data tfl.t_dm1;
  set final;
  keep ord section characteristic c1-c4;
run;

/* --- CSV (same layout as the Python version) --- */
data _null_;
  file "&DATA_DIR/tfl/t_dm1.csv" lrecl=2000;
  put 'Section,Characteristic,Placebo,Xanomeline Low Dose,Xanomeline High Dose,Total';
run;
data _null_;
  set tfl.t_dm1;
  file "&DATA_DIR/tfl/t_dm1.csv" dsd mod lrecl=2000;
  put section characteristic c1 c2 c3 c4;
run;

/* --- HTML --- */
ods html file="&DATA_DIR/tfl/t_dm1.html" style=minimal;
title "Table 14.1: Summary of Demographic and Baseline Characteristics - Safety Population";
footnote "Percentages use the number of subjects in each arm as the denominator. Source: ADSL.";
proc print data=tfl.t_dm1 noobs;
  var section characteristic c1-c4;
run;
ods html close;
title; footnote;

%put NOTE: Wrote &DATA_DIR/tfl/t_dm1.csv;
