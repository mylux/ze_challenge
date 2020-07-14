#!/bin/bash
current_dir=$(pwd)
pkgdir="lambda_package"
pkgpath="$pkgdir/python/lib/python3.8/site-packages"
parent_dir="$(basename "$current_dir")"

mkdir -p "$pkgpath"
cd "$pkgpath" || exit
rm -rf ./*
pip install -t . -r "$current_dir/requirements.txt"
rm -rf bin lib
find "$current_dir" -maxdepth 1 -type f -name "*.py" -not -name "$parent_dir" -not -name "$pkgdir" -exec cp {} . \;
find "$current_dir" -maxdepth 1 -type d -not -name "." -not -name ".." -not -name "$pkgdir" -not -name "$parent_dir" -exec cp -r {} . \;
rm -f "$current_dir/$parent_dir.zip"; cd "$current_dir/$pkgdir" && zip -r "../$parent_dir.zip" "./python/"
