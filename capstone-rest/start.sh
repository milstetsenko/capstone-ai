#! usr/bin/bash

conda deactivate
. venv/bin/activate
uvicorn main:app --reload
