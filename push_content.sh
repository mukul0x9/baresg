#!/bin/bash
set -e

source .venv/bin/activate

python3 site_generator.py

rsync -av --delete --exclude '.git/' public/ ../mukul0x9.github.io/

cd ../mukul0x9.github.io

# git add .
# git commit -m "pushed content change"
# git push
