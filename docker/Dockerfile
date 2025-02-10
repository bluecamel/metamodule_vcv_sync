FROM ubuntu:24.04

ENV USER="ubuntu"
ENV USER_HOME="/home/${USER}"

SHELL ["/bin/bash", "-c"]

RUN apt-get update && \
    apt-get install -y \
        python3 \
        python3-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER ${USER}

ENV METAMODULE_VCV_SYNC_DIR="${USER_HOME}/metamodule_vcv_sync"
ENV METAMODULE_VCV_SYNC_VENV_DIR="${METAMODULE_VCV_SYNC_DIR}/venv"

RUN mkdir -p ${METAMODULE_VCV_SYNC_DIR} && \
    python3 -m venv ${METAMODULE_VCV_SYNC_VENV_DIR}

COPY --chown=${USER}:${USER} sync ${METAMODULE_VCV_SYNC_DIR}/sync

RUN source ${METAMODULE_VCV_SYNC_VENV_DIR}/bin/activate && \
    python3 -m pip install --upgrade pip && \
    python3 -m pip install -r ${METAMODULE_VCV_SYNC_DIR}/sync/requirements.txt

WORKDIR ${USER_HOME}

ENTRYPOINT ["/home/ubuntu/metamodule_vcv_sync/sync/entrypoint.sh"]
CMD []
