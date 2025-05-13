#!/bin/bash
TIMEFORMAT=%R
rm -rf temp_data
mkdir -p temp_data
for i in {1..3}
do
  for j in {5,50,512}
  do
    dd if=/dev/urandom of=./temp_data/"${j}M_${i}.bin" bs=1M count=$j
    (time ./uplink cp ./temp_data/"${j}M_${i}.bin" sj://upload-measurement) 2> "${j}M_${i}".txt
  done
done