###############################################################################################################
# Prepare an initial image later used by intermediate images as well as during the released image build.
###############################################################################################################
FROM armdocker.rnd.ericsson.se/proj-ldc/common_base_os/sles:5.12.0-13 as release
RUN zypper ar -C -G -f https://arm.sero.gic.ericsson.se/artifactory/proj-ldc-repo-rpm-local/common_base_os/sles/5.12.0-13 LDC-CBO-SLES \
 && zypper ref -f -r LDC-CBO-SLES \
 && zypper install -y python310 \
 && zypper clean --all \
 && find /usr -type d -name  "__pycache__" -exec rm -r {} +

# A locale needs to be installed and set for later use by some python packages like click
ENV LC_ALL=en_US.utf-8
ENV LANG=en_US.utf-8

RUN zypper install -y python310-pip curl unzip apache2-utils xz
# Add for ci-helm package
RUN ln -sf /usr/bin/python3.10 /usr/bin/python3

# Download helm 3 binary for later inclusion in final image.
WORKDIR /helm3/
RUN curl -O https://arm1s11-eiffel052.eiffel.gic.ericsson.se:8443/nexus/service/local/repositories/eo-3pp-foss/content/org/cncf/helm/3.13.2/helm-3.13.2.gz
RUN tar xfz helm-3.13.2.gz

## Make sure helm is executable
RUN mv /helm3/linux-amd64/helm /usr/bin/helm
RUN helm version

# Download helmfile binary for later inclusion in final image.
WORKDIR /helmfile/
RUN curl -O https://arm1s11-eiffel052.eiffel.gic.ericsson.se:8443/nexus/service/local/repositories/eo-3pp-tools/content/com/helm/helmfile/0.156.0/helmfile-0.156.0.gz
RUN tar xfz helmfile-0.156.0.gz

## Make sure helmfile is executable
RUN mv /helmfile/helmfile /usr/bin/helmfile
RUN helmfile version

# Download kubectl binary for later inclusion in final image.
WORKDIR /usr/bin
RUN curl -O https://arm1s11-eiffel052.eiffel.gic.ericsson.se:8443/nexus/service/local/repositories/eo-3pp-foss/content/org/cncf/kubernetes/kubectl/1.27.4/kubectl-1.27.4.zip
RUN unzip kubectl-1.27.4.zip

# Download ShellCheck
RUN curl --remote-name --location https://github.com/koalaman/shellcheck/releases/download/v0.9.0/shellcheck-v0.9.0.linux.x86_64.tar.xz
RUN tar xf shellcheck-v0.9.0.linux.x86_64.tar.xz
RUN install shellcheck-v0.9.0/shellcheck /usr/local/bin/
RUN rm -rf shellcheck-v0.9.0
RUN rm -f shellcheck-v0.9.0.linux.x86_64.tar.xz

# Add the ci-helm content that was built from the ci-helm docker image
ADD ci/jenkins/scripts/python-ci-scripts/cihelm/python3/lib/cihelm /usr/lib64/python3.10/cihelm
ADD ci/jenkins/scripts/python-ci-scripts/cihelm/python3/bin/* /usr/local/bin/
ADD ci/jenkins/scripts/python-ci-scripts/cihelm/bin/parse_index /usr/lib/cihelm/

## Make sure kubectl is executable
RUN kubectl --help

WORKDIR /ci-scripts/

RUN mkdir output-files
RUN chmod -R 777 output-files
RUN mkdir /test-files
RUN chmod -R 777 /test-files

COPY ci/jenkins/scripts/python-ci-scripts/requirements.txt .
RUN pip3.10 install -r requirements.txt

COPY ci/jenkins/scripts/python-ci-scripts/src /ci-scripts
COPY ci/jenkins/scripts/python-ci-scripts/setup.cfg /ci-scripts
COPY testsuite/helm-chart-validator/helm_file_plugin/file/ /helm_data/helm/plugins/file/

RUN /usr/bin/python3.10 --help

RUN cihelm --help

ARG COMMIT
ARG REPOSITORY
ARG APP_VERSION

LABEL \
    eric-oss-ci-scripts.commit=$COMMIT \
    eric-oss-ci-scripts.repository=$REPOSITORY \
    eric-oss-ci-scripts.app.version=$APP_VERSION

ENTRYPOINT ["/usr/bin/python3.10", "/ci-scripts"]

###############################################################################################################
# An image that runs various tests on the python code.
###############################################################################################################
FROM release as test

ARG LINT_DIR=/ci-scripts
WORKDIR /ci-scripts/

RUN mkdir /test_results

COPY ci/jenkins/scripts/python-ci-scripts/requirements-test.txt .
RUN true
RUN pip3.10 install -r requirements-test.txt

#COPY ci/jenkins/scripts/python-ci-scripts/src /ci-scripts
COPY ci/jenkins/scripts/python-ci-scripts/src/tests /ci-scripts/tests
RUN true
COPY ci/jenkins/scripts/python-ci-scripts/pytest.ini .
RUN true

# Copy rules for the various linters
COPY ci/jenkins/scripts/python-ci-scripts/pylintrc pylintrc
RUN true
COPY ci/jenkins/scripts/python-ci-scripts/.flake8 .flake8
RUN true
COPY ci/jenkins/scripts/python-ci-scripts/.pydocstyle .pydocstyle
RUN true

# Run the various linters from within the context of the ci-scripts directory
# Fail immediately with linters fail.
RUN pylint ${LINT_DIR}
RUN flake8 ${LINT_DIR}
RUN pydocstyle ${LINT_DIR}

# Run pytest but don't fail docker build on failed tests.
# we want Jenkins to publish the results so docker build must succeeed.
RUN coverage run --source ${LINT_DIR} -m pytest --junit-xml=/test_results/tests.xml --html=/test_results/report.html tests/. -vv || true

# Run the code coverage html report
RUN coverage html -d /test_results/unit_coverage/

# # Run the code coverage report to standard out, and fail if under the target percentage
RUN coverage report --fail-under 96 || echo "Coverage Failed" > /test_results/coverage_failed.txt
