#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

mkdir -p home/models/final_model
if [ ! -f home/models/final_model/model.safetensors ]; then
  curl -L -o home/models/final_model/model.safetensors \
    "https://huggingface.co/Narayanan2004/jarvis-final-model/resolve/main/model.safetensors"
fi

python manage.py collectstatic --no-input
python manage.py migrate