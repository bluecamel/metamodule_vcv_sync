#!/usr/bin/env bash

source ${HOME}/metamodule_vcv_sync/venv/bin/activate
python3 ${HOME}/metamodule_vcv_sync/sync/run.py ${@}
