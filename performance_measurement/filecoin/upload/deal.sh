#!/bin/bash
PROVIDER=$1
URL=$2
COMMP=$3
CAR_SIZE=$4
PIECE_SIZE=$5
PAYLOAD_CID=$6
VERIFIED=$7
PRICE=$8
DURATION=$9

#echo $PROVIDER
#echo $URL
#echo $COMMP
#echo $CAR_SIZE
#echo $PIECE_SIZE
#echo $PAYLOAD_CID
#echo "$VERIFIED"
#echo $PRICE
#echo $DURATION
#echo "sent deal proposal
#      deal uuid: df0b7018-ccea-4f56-8ec7-7d37f4d6c152
#      storage provider: f0187709
#      client wallet: f1cn24omlkozds4jr4zxgm2lxlyr3ktki47toq56a
#      payload cid: bafybeiafssuu6pn5b2nabwatjy5jxhoc5txphkjbtdn2eimsay6whxio4u
#      url: http://xxx
#      commp: baga6ea4seaqbmxph7lwt435fnhfgrfmh5xrzcnrfw52pp7zzfwxnonp6xwhs4ey
#      start epoch: 3433884
#      end epoch: 3952284
#      provider collateral: 267.293 μFIL"
#echo "Error: deal proposal rejected: failed validation: storage price per epoch less than asking price: 1 < 9700000000
#"
export FULLNODE_API_INFO=https://api.node.glif.io
boost -vv deal --provider=$PROVIDER \
           --http-url=$URL \
           --commp=$COMMP \
           --car-size=$CAR_SIZE \
           --piece-size=$PIECE_SIZE \
           --payload-cid=$PAYLOAD_CID \
           --verified=$VERIFIED \
           --storage-price=$PRICE \
           --duration=$DURATION
