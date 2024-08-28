###############################################################################################################
# Prepare an initial image later used by intermediate images as well as during the released image build.
###############################################################################################################
FROM armdockerhub.rnd.ericsson.se/python:3.9-slim-buster

WORKDIR /freeport/

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY src /freeport

ENTRYPOINT ["python3", "./main.py"]
