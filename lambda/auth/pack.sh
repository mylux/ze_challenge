#!/bin/bash
mkdir -p lambda_package
cd lambda_package
rm -rf *
pip install -t . -r ../requirements.txt
cp ../main.py .
rm -rf bin lib
parent_dir=$(basename $(realpath ..))
rm -f ../$parent_dir.zip; zip -r ../$parent_dir.zip *
