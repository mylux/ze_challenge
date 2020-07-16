#!/bin/bash
mkdir -p lambda_package
cd lambda_package || exit
rm -rf ./*
[ -f ../requirements.txt ] && pip install -t . -r ../requirements.txt
cp ../*.py .
rm -rf bin lib
parent_dir=$(basename "$(realpath ..)")
rm -f "../$parent_dir.zip"; zip -r "../$parent_dir.zip" ./*