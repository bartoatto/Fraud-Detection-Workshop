# This is a convenience copy of the instructions in ./environment.md. Domino handles
# the base image itself — in the Domino UI, select "Start from an existing
# environment" and pick "Domino Standard Environment Py3.10 R4.5"

# Install uWSGI pre-requisites
USER root
RUN apt-get update && apt-get install -y --no-install-recommends gcc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Add missing library for uWSGI
ARG LDFLAGS=-fno-lto
ENV LDFLAGS=-fno-lto
ENV PYTHONPATH="${PYTHONPATH}:/mnt/code:/mnt"

# Install Flask & uWSGI
RUN pip install --no-cache-dir "setuptools<81" Flask Flask-Compress Flask-Cors uwsgi six prometheus-client ydata_profiling streamlit st-pages streamlit-extras altair-saver "nbclient>=0.6.7,<0.7" "nbconvert>=6.5.4,<7" "lxml[html_clean]"

# Switch back to the standard non-root user - required for Model API builds, which
# run Domino's own build steps (e.g. creating an mlflow directory under /mnt) as
# whatever user the image ends on. Leaving this as root causes those steps to fail
# with a permission error against the expected non-root mount ownership.
USER ubuntu
