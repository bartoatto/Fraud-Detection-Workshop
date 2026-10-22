"""Settings shared by the exercises, in one place. Nothing here touches the file system.

Every value can be overridden with an environment variable, so the same code runs against
another volume, snapshot tag or deployment without editing it.
"""
import os

# The NetApp Volume that holds the study data. The flow reads the latest snapshot of it, or the
# snapshot carrying FLOW_SNAPSHOT_TAG when that is set.
VOLUME_NAME = os.environ.get("STUDY_VOLUME_NAME", "cdisc01-study-data")
FLOW_SNAPSHOT_TAG = os.environ.get("FLOW_SNAPSHOT_TAG") or None

# Where Domino mounts NetApp Volumes: DFS projects under /domino, Git-based projects under /mnt.
MOUNT_ROOTS = ("/domino/netapp-volumes", "/mnt/netapp-volumes")
