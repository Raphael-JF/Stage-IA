#!/bin/bash

source /home/cbrazier/venvs/llmserver/bin/activate

streamlit run /home/cbrazier/atelier_ia/app_qwen.py \
  --server.address 0.0.0.0 \
  --server.port 9000
