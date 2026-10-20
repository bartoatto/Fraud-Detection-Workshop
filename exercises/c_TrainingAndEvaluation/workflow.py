# workflow.py
from flytekit import workflow
from flytekitplugins.domino.task import DatasetSnapshot, DominoJobConfig, DominoJobTask

TRAINER_DIR = "exercises/c_TrainingAndEvaluation"


# Flow jobs do not get the project's read-write Dataset, so mount a snapshot of it that
# holds transformed_cc_transactions.csv (snapshot 1, taken after Exercise B).
DATASET_SNAPSHOTS = [DatasetSnapshot(Id="6ab214b5e13dce03e8d45ac0", Name="Fraud-Detection-Workshop", Version=1)]


def _command(script: str) -> str:
    return f"bash -c 'PYTHONPATH=/mnt/code python /mnt/code/{TRAINER_DIR}/{script}'"


ada_training_task = DominoJobTask(
    name='Train AdaBoost classifier',
    domino_job_config=DominoJobConfig(Command=_command("trainer_ada.py"), DatasetSnapshots=DATASET_SNAPSHOTS),
    inputs={'transformed_filename': str},
    outputs={'results': str},
    use_latest=True,
)

gnb_training_task = DominoJobTask(
    name='Train GaussianNB classifier',
    domino_job_config=DominoJobConfig(Command=_command("trainer_gnb.py"), DatasetSnapshots=DATASET_SNAPSHOTS),
    inputs={'transformed_filename': str},
    outputs={'results': str},
    use_latest=True,
)

xgb_training_task = DominoJobTask(
    name='Train XGBoost classifier',
    domino_job_config=DominoJobConfig(Command=_command("trainer_xgb.py"), DatasetSnapshots=DATASET_SNAPSHOTS),
    inputs={'transformed_filename': str},
    outputs={'results': str},
    use_latest=True,
)

compare_task = DominoJobTask(
    name='Compare training results',
    domino_job_config=DominoJobConfig(Command=_command("compare.py")),
    inputs={'ada_results': str, 'gnb_results': str, 'xgb_results': str},
    outputs={'consolidated': str},
    use_latest=True,
)


@workflow
def credit_card_fraud_detection_workflow(transformed_filename: str = 'transformed_cc_transactions.csv') -> str:
    ada_results = ada_training_task(transformed_filename=transformed_filename)
    gnb_results = gnb_training_task(transformed_filename=transformed_filename)
    xgb_results = xgb_training_task(transformed_filename=transformed_filename)

    return compare_task(ada_results=ada_results, gnb_results=gnb_results, xgb_results=xgb_results)
