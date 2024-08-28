###############################################################################################################
# Prepare an initial image later used by intermediate images as well as during the released image build.
###############################################################################################################
FROM armdocker.rnd.ericsson.se/proj-adp-cicd-drop/spin:3.2.0 as release
RUN zypper ar -C -G -f https://arm.sero.gic.ericsson.se/artifactory/proj-ldc-repo-rpm-local/common_base_os/sles/3.45.0-15 LDC-CBO-SLES \
 && zypper ref -f -r LDC-CBO-SLES \
 && zypper install -y python39 \
 && zypper clean --all \
 && find /usr -type d -name  "__pycache__" -exec rm -r {} +

# A locale needs to be installed and set for later use by some python packages like click
ENV LC_ALL=en_US.utf-8
ENV LANG=en_US.utf-8

RUN zypper install -y python39-pip curl unzip apache2-utils
RUN ln -sf /usr/bin/python3.9 /usr/bin/python3

WORKDIR /pipeline-mgt-scripts/

RUN mkdir output-files

COPY requirements.txt .
RUN pip3.9 install -r requirements.txt

COPY *.py /pipeline-mgt-scripts/

ARG COMMIT
ARG REPOSITORY

LABEL \
    eric-oss-pipeline-mgt-scripts.commit=$COMMIT \
    eric-oss-pipeline-mgt-scripts.repository=$REPOSITORY

ENTRYPOINT ["/usr/bin/python3.9", "/pipeline-mgt-scripts"]

###############################################################################################################
# An image that runs various tests on the python code.
###############################################################################################################
FROM release as test

ARG LINT_DIR=/pipeline-mgt-scripts
WORKDIR /pipeline-mgt-scripts/

RUN mkdir /test_results

COPY requirements-test.txt .
RUN true
RUN pip3.9 install -r requirements-test.txt

# Copy rules for the various linters
COPY pylintrc pylintrc
RUN true
COPY .flake8 .flake8
RUN true
COPY .pydocstyle .pydocstyle
RUN true

# Run the various linters from within the context of the ci-scripts directory
# Fail immediately with linters fail.
RUN pylint ${LINT_DIR}
RUN flake8 ${LINT_DIR}
RUN pep257 ${LINT_DIR}
RUN pydocstyle ${LINT_DIR}
