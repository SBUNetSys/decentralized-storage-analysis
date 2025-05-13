#!/bin/bash
# Upload files to IPFS
# Usage: ./auto_upload.sh <size> <number of files to upload>
# Example: ./auto_upload.sh 1M 10
if [ "$#" -ne 3 ]; then
    echo "Usage: ./auto_upload.sh <size> <number of files to upload> <location>"
    echo "Example: ./auto_upload.sh 1M 10 us-nj"
    exit 1
fi
size=$1
num_files=$2
python3 gen_upload_file_with_size.py --size=$size --count=$num_files
python3 upload_with_size.py --file_dir=upload_files --size=$size --loc=$3
git add uploaded_files_data/
git commit -m "Upload $num_files files with size $size"
git push