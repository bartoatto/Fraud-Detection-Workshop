/*****************************************************************************
* domino_setup.sas - shared setup for the SAS exercises
* ----------------------------------------------------------------------------
* Finds the NetApp Volume and creates the libraries every program uses.
*
*   ADAM   (read-only)  adam/ on the volume, or a snapshot tag of it
*   TFL                 tfl/        production tables
*   TFLQC               qc/tfl/     QC tables
*
* Macro variables set: DATA_DIR ADSL_DIR ART_DIR WORK_DIR
*
* Optional environment variable:
*   ADSL_SNAPSHOT_TAG  read ADSL from that snapshot tag of the volume, so a run is
*                      reproducible even if the live data changes
*****************************************************************************/

%macro domino_setup;
  %global DATA_DIR ADSL_DIR ART_DIR WORK_DIR;
  %local vol root p1 p2 tag gitbased artdir;

  %let vol = cdisc01-study-data;
  %let WORK_DIR = %sysget(DOMINO_WORKING_DIR);

  /* DFS projects mount volumes under /domino, Git-based projects under /mnt */
  %let root = ;
  %let p1 = /domino/netapp-volumes/&vol;
  %let p2 = /mnt/netapp-volumes/&vol;
  %if %sysfunc(fileexist(&p1)) %then %let root = /domino/netapp-volumes;
  %else %if %sysfunc(fileexist(&p2)) %then %let root = /mnt/netapp-volumes;

  %if %length(&root) = 0 %then %do;
    %put ERROR: NetApp Volume &vol is not mounted. Add it to the project under Data > NetApp Volumes and restart.;
    %abort cancel;
  %end;

  %let DATA_DIR = &root/&vol;
  %let ADSL_DIR = &DATA_DIR/adam;

  %let tag = %sysget(ADSL_SNAPSHOT_TAG);
  %if %length(&tag) > 0 %then %do;
    %let ADSL_DIR = &root/snapshot-tags/&vol/&tag/adam;
    %put NOTE: Reading ADSL from snapshot tag &tag;
  %end;

  /* Git-based projects keep results in /mnt/artifacts, DFS projects in the project folder */
  %let gitbased = %sysget(DOMINO_IS_GIT_BASED);
  %if &gitbased = true %then %do;
    %let artdir = %sysget(DOMINO_ARTIFACTS_DIR);
    %if %length(&artdir) = 0 %then %let artdir = /mnt/artifacts;
    %let ART_DIR = &artdir;
  %end;
  %else %let ART_DIR = &WORK_DIR/artifacts;
%mend domino_setup;

/* Create a sub-folder if it does not exist yet */
%macro ensure_dir(parent, name);
  %local rc;
  %if not %sysfunc(fileexist(&parent/&name)) %then %let rc = %sysfunc(dcreate(&name, &parent));
%mend ensure_dir;

/* Publish headline numbers on the Domino Jobs screen (dominostats.json).
   Git-based projects read it from the artifacts folder, DFS projects from the project root. */
%macro write_dominostats(table=, status=, cells=, diffs=);
  %local target gitbased;
  %let gitbased = %sysget(DOMINO_IS_GIT_BASED);
  %if &gitbased = true %then %let target = &ART_DIR/dominostats.json;
  %else %let target = &WORK_DIR/dominostats.json;

  data _null_;
    file "&target";
    put '{';
    line = cats('  "Table": "', "&table", '",');           put line;
    line = cats('  "Status": "', "&status", '",');         put line;
    line = cats('  "Cells compared": ', "&cells", ',');    put line;
    line = cats('  "Cell differences": ', "&diffs");       put line;
    put '}';
  run;
%mend write_dominostats;

%domino_setup;

libname adam   "&ADSL_DIR" access=readonly;
%ensure_dir(&DATA_DIR, tfl);
%ensure_dir(&DATA_DIR, qc);
%ensure_dir(&DATA_DIR/qc, tfl);
%ensure_dir(&DATA_DIR, compare);
libname tfl    "&DATA_DIR/tfl";
libname tflqc  "&DATA_DIR/qc/tfl";

%put NOTE: DATA_DIR=&DATA_DIR ADSL_DIR=&ADSL_DIR ART_DIR=&ART_DIR;
