#!/bin/bash

source /home/cbrazier/venvs/llmserver/bin/activate

export CUDA_VISIBLE_DEVICES=1
export VLLM_USE_V1=0

vllm serve /home/cbrazier/models/Mistral-Nemo-Instruct-2407 \
  --served-model-name mistral-nemo \
  --host 0.0.0.0 \
  --port 8001 \
  --dtype bfloat16 \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.70 \
  --tokenizer-mode mistral
