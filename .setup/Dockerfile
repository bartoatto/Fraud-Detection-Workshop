# This is a convenience copy of the instructions in ./environment.md. Domino handles
# the base image itself - in the Domino UI, select "Start from an existing
# environment" and pick a Python 3.12 Domino Standard Environment. If your organisation
# maintains its own (e.g. one carrying internal package-repository settings), use that.
#
# The Standard Environment already has everything the workshop uses except Streamlit:
# pandas, numpy, matplotlib, seaborn, JupyterLab, python-domino, and Flyte with the Domino
# flows plugin. So this adds one package.

# Lets the exercises import the shared code in common/ from any folder
ENV PYTHONPATH="${PYTHONPATH}:/mnt/code:/mnt"

# Streamlit runs the Study Review Desk app (Exercise C)
USER root
RUN pip install --no-cache-dir streamlit

# Switch back to the standard non-root user
USER ubuntu
