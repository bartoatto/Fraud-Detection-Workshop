# Training And Evaluation
In this phase, we will train 3 models, evaluate them, and register the best one.  We will run the three training scripts, compare them in the Domino Experiment Manager, and register the winner in the Model Registry.

## Exercise Instructions

In the workspace, open the terminal

Run the three trainer programs:

```
python exercises/c_TrainingAndEvaluation/trainer_ada.py
python exercises/c_TrainingAndEvaluation/trainer_gnb.py
python exercises/c_TrainingAndEvaluation/trainer_xgb.py
```

### Optional: run the three as parallel Jobs

Instead of running them one after another in the terminal, you can submit all three as
Domino Jobs that train at the same time, each in its own container:

```
python exercises/c_TrainingAndEvaluation/job_trainer_ada.py
python exercises/c_TrainingAndEvaluation/job_trainer_gnb.py
python exercises/c_TrainingAndEvaluation/job_trainer_xgb.py
```

Each of these returns immediately - it submits a Job through the Domino API rather than
training in your terminal. Watch them under **Jobs**. Sync your workspace first, because Jobs
run the project's files rather than your unsaved edits, and note the scripts request the
`Medium` hardware tier, so change `hwtier` if your deployment names tiers differently.

The runs land in the same experiment either way, so Compare works the same.

Click "Experiment Manager"  (Main Window, Left-Hand Column)

Select all runs (3) and click "Compare"

Select the one with the best metrics (here is a hint: XGBoost)

Review the complete traceability and all factors.

Click "Register Model From Run" in Upper Right Hand

Create model name

This concludes the "3. MODEL TRAINING and EVALUATION" section of the workshop.

### Other files in this folder

`generic_trainer.py` is the shared training code the three trainers call - open it to see how
the metrics, plots and model are logged. `train_fraud.ipynb` is a notebook that does the same
thing end to end, if you prefer working that way. `workflow.py` and `compare.py` are for Domino
Flows, Domino's orchestration layer, and are not used in this exercise.

## New Domino Concepts

**Experiment Manager:**
> Experiment Manager is a centralized tracking system that automatically captures and compares all experiment runs, including parameters, metrics, code versions, and results in a searchable interface. This accelerates model development by enabling data scientists to quickly identify the best-performing models, understand what changes improved performance, and reproduce any past experiment.

**Model Registry:**
> Model Registry is a centralized repository that catalogs all trained models with their metadata, performance metrics, lineage, and deployment status throughout their lifecycle. This provides governance and collaboration capabilities by enabling teams to discover, compare, promote, and deploy models while maintaining full auditability and compliance documentation.
