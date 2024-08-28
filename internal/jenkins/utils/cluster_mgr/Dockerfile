###############################################################################################################
# Prepare an initial image later used by intermediate images as well as during the released image build.
###############################################################################################################
ARG CBO_TAG=3.45.0-15
ARG PACKAGE_REPO_URL=https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-ldc-repo-rpm-local/common_base_os/sles
FROM armdocker.rnd.ericsson.se/proj-ldc/common_base_os_release/sles:$CBO_TAG as build
ARG CBO_TAG
ARG PACKAGE_REPO_URL
ARG ARM_USER
ARG ARM_PASSWORD

ENV ARM_URL https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-dev-test-generic-local
ENV KIND_VERSION 0.17.0

RUN set -x \
 && zypper ar -C -G -f $PACKAGE_REPO_URL/$CBO_TAG?ssl_verify=no LDC-CBO-SLES \
 && zypper ref -f -r LDC-CBO-SLES \
 && zypper -q install -r LDC-CBO-SLES -y --no-recommends ca-certificates-mozilla curl \
 && zypper clean --all

# Download kind binary
RUN mkdir -p /kind && \
    curl -Lo /kind/kind -u ${ARM_USER}:${ARM_PASSWORD} ${ARM_URL}/3pp-tools/kind/kind-${KIND_VERSION}.bin

FROM armdockerhub.rnd.ericsson.se/ubuntu:22.04

RUN apt -y update
RUN apt -y upgrade
RUN apt -y install curl unzip python3-pip

# Download helm 3 binary for later inclusion in final image.
WORKDIR /helm3/
RUN curl -O https://arm1s11-eiffel052.eiffel.gic.ericsson.se:8443/nexus/service/local/repositories/eo-3pp-foss/content/org/cncf/helm/3.7.1/helm-3.7.1.zip
RUN unzip helm-3.7.1.zip

## Make sure helm is executable
RUN mv /helm3/linux-amd64/helm /usr/bin/helm
RUN helm version

# Download kubectl binary for later inclusion in final image.
WORKDIR /usr/bin
RUN curl -sL https://arm1s11-eiffel052.eiffel.gic.ericsson.se:8443/nexus/content/repositories/eo-3pp-foss/org/cncf/kubernetes/kubectl/1.22.0/kubectl-1.22.0.zip -o kubectl.zip
RUN unzip kubectl.zip

COPY --from=build /kind/kind /usr/bin/kind
RUN chmod +x /usr/bin/kind

## Make sure kubectl is executable
RUN kubectl --help

WORKDIR /cluster-mgr/

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY src /cluster-mgr
COPY node_specs /node_specs

ENTRYPOINT ["python3", "./main.py"]
