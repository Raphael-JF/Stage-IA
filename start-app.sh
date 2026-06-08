#!/bin/bash
cd /data1/Stage-IA/server 
source venv/bin/activate
uvicorn api.main:app --host 0.0.0.0 --port 8000
