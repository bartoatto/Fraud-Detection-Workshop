# Domino Compute Environment Setup
Make the below changes to the Domino compute environment for the workshop.
Leave all other entries as Default

### Name:
```
Fraud-Detection-Workshop
```
(The name is kept so existing projects and templates still find it; rename it if you build a new one.)

### Base Environment / Image:

Select:
```
Start from an existing environment
```
From:
```
Domino Standard Environment Py3.10 R4.5   (or the Py3.12 equivalent)
```

Pick the platform's own environment (the Global, Default one) rather than typing a
custom image tag. The original version of this doc pinned a specific registry tag
(`quay.io/domino/domino-standard-environment:ubuntu22-py3.10-r4.5-domino6.1-standard`
— note the `domino6.1` in the tag). If you're deploying on a different Domino version,
that tag may not match what's actually running there. Starting from the platform's own
already-provisioned Standard Environment sidesteps that mismatch entirely.

Use a **Python 3.12** base. If your organisation maintains its own Standard Environment (for
example one carrying internal package-repository settings), start from that.

### Description
```
Life Sciences Workshop (CDISC pilot study)
Based on a Domino Standard Environment (Py3.12) plus Streamlit
Jupyter, Jupyterlab, VSCode
```

### Visibility
```
Globally Accessible
```

### Additional Docker File Instructions:
```
# The Standard Environment already has pandas, numpy, matplotlib, seaborn, JupyterLab,
# python-domino and Flyte with the Domino flows plugin. This adds Streamlit, which runs
# the Study Review Desk app (Exercise C).

# Lets the exercises import the shared code in common/ from any folder
ENV PYTHONPATH="${PYTHONPATH}:/mnt/code:/mnt"

USER root
RUN pip install --no-cache-dir streamlit

# Switch back to the standard non-root user
USER ubuntu
```

### Plugable Workspace Tools
```
jupyter:
  title: "Jupyter (Python, R, Julia)"
  iconUrl: "/assets/images/workspace-logos/Jupyter.svg"
  start: [ "/opt/domino/workspaces/jupyter/start" ]
  supportedFileExtensions: [ ".ipynb" ]
  httpProxy:
    port: 8888
    rewrite: false
    internalPath: "/{{ownerUsername}}/{{projectName}}/{{sessionPathComponent}}/{{runId}}/{{#if pathToOpen}}tree/{{pathToOpen}}{{/if}}"
    requireSubdomain: false
jupyterlab:
  title: "JupyterLab"
  iconUrl: "/assets/images/workspace-logos/jupyterlab.svg"
  start: [  "/opt/domino/workspaces/jupyterlab/start" ]
  httpProxy:
    internalPath: "/{{ownerUsername}}/{{projectName}}/{{sessionPathComponent}}/{{runId}}/{{#if pathToOpen}}tree/{{pathToOpen}}{{/if}}"
    port: 8888
    rewrite: false
    requireSubdomain: false
vscode:
  title: "vscode"
  iconUrl: "/assets/images/workspace-logos/vscode.svg"
  start: [ "/opt/domino/workspaces/vscode/start" ]
  httpProxy:
    port: 8888
    requireSubdomain: false
rstudio:
  title: "RStudio"
  iconUrl: "/assets/images/workspace-logos/Rstudio.svg"
  start: [ "/opt/domino/workspaces/rstudio/start" ]
  httpProxy:
    port: 8888
    requireSubdomain: false
```
Build It
