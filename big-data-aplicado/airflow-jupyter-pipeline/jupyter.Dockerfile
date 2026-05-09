FROM jupyter/base-notebook:python-3.11

USER root

RUN apt-get update && apt-get install -y --no-install-recommends graphviz tzdata pandoc texlive-xetex texlive-fonts-recommended texlive-plain-generic && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    requests \
    papermill \
    ipywidgets \
    graphviz \
    apache-airflow==2.8.3 \
    apache-airflow-providers-postgres==5.10.0

ENV PYDEVD_DISABLE_FILE_VALIDATION=1

USER jovyan

WORKDIR /home/jovyan
