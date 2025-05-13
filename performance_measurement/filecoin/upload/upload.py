import argparse
import json
import os
import random
import secrets
import time


class Deal:
    def __init__(self):
        self.provider = ""
        self.file_path = ""
        self.file_link = ""
        self.car_path = ""
        self.duration = 518400
        self.verified = False
        self.car_size = 0
        self.commp = ""
        self.piece_size = 0
        self.payload_cid = ""
        self.storage_price = 1
        self.uuid = ""
        self.error = None
        self.deal_stats = {}
        self.log = None


def prepare_deal(deal: Deal):
    """
    this function prepares the necessary information to make a filecoin deal
    1. generate car file and upload car file to http server
    2. compute car file CID
    3. commp car file
    4. get piece size
    5. get car size
    :type deal: Deal, The deal for the file
    :return:
    """
    car_name = secrets.token_hex(nbytes=16)
    car_file_path = os.path.join("./simple-http-server/files", f"{car_name}.car")
    deal.car_path = car_file_path
    print(f"Creating car file with path {car_file_path}")
    os.popen(cmd=f"car create -f {car_file_path} --version 1 {deal.file_path}").read()  # need call read to wait
    deal.file_link = f"http://130.245.145.107/{car_name}.car"
    cid = os.popen(cmd=f"car root {car_file_path}").read()
    cid = cid.replace("\n", "")
    print(f"payload cid = {cid}")
    deal.payload_cid = cid
    result = os.popen(cmd=f"boostx commp {car_file_path}").read()
    for line in result.split("\n"):
        line = line.replace(" ", "")
        line = line.replace("\n", "")
        split = line.split(":")
        if "CommP" in line:
            deal.commp = split[-1]
            print(f"commp {split[-1]}")
        if "Piece" in line:
            deal.piece_size = int(split[-1])
            print(f"piece_size {int(split[-1])}")
        if "Car" in line:
            deal.car_size = int(split[-1])
            print(f"car_size {int(split[-1])}")


def make_deal(deal: Deal):
    """
    make deal on fil coin network
    :param deal: the deal of this car file
    :return:
    """
    """
    PROVIDER=$1
    URL=$2
    COMMP=$3
    CAR_SIZE=$4
    PIECE_SIZE=$5
    PAYLOAD_CID=$6
    VERIFIED=$7
    PRICE=$8
    DURATION=$9
    """
    result = os.popen(cmd=f"bash deal.sh "
                          f"{deal.provider} "
                          f"{deal.file_link} "
                          f"{deal.commp} "
                          f"{deal.car_size} "
                          f"{deal.piece_size} "
                          f"{deal.payload_cid} "
                          f"{str(deal.verified).lower()} "
                          f"{deal.storage_price} "
                          f"{deal.duration} 2>&1").read()
    deal_success = False
    deal.log = result
    print(result)
    for line in result.split("\n"):
        line = line.replace("\n", "")
        if "Error" in line:
            deal.error = line
            print(line)
            print(f"file: {deal.file_path}")
            print(f"car file: {deal.car_path}")
            os.system(f"rm {deal.car_path}")
            exit(-1)
        if "sent deal proposal" in line:
            deal.deal_stats["start"] = time.time()
            deal_success = True
            continue
        if deal_success:
            if "uuid" in line:
                split = line.split(" ")
                deal.uuid = split[-1].replace(" ", "")
    if not os.path.exists("./deals"):
        os.makedirs("./deals")
    with open(f"./deals/{deal.uuid}.json", "w") as fout:
        json.dump(deal.__dict__, fout)
    """
    sent deal proposal
      deal uuid: df0b7018-ccea-4f56-8ec7-7d37f4d6c152
      storage provider: f0187709
      client wallet: f1cn24omlkozds4jr4zxgm2lxlyr3ktki47toq56a
      payload cid: bafybeiafssuu6pn5b2nabwatjy5jxhoc5txphkjbtdn2eimsay6whxio4u
      url: http://files-us.hoshiro.moe/test.car
      commp: baga6ea4seaqbmxph7lwt435fnhfgrfmh5xrzcnrfw52pp7zzfwxnonp6xwhs4ey
      start epoch: 3433884
      end epoch: 3952284
      provider collateral: 267.293 μFIL
    """


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", help="deal storage provider")
    parser.add_argument("--file", help="path to file wish to upload")
    # parser.add_argument("--link", help="http link to car file wish to upload")
    parser.add_argument("--duration", help="store duration, default 180 days", default=518400)
    parser.add_argument("--verified", help="verified deal, default false", default=False)
    parser.add_argument("--price", help="storage price for the dealer")
    args = parser.parse_args()
    deal = Deal()
    if args.provider is None or args.file is None:
        print("Deal must have storage provider and file path")
        exit(-1)
    deal.provider = args.provider
    deal.file_path = args.file
    # deal.file_link = args.link
    if args.duration is not None:
        deal.duration = int(args.duration)
    if args.verified is not None:
        deal.verified = bool(args.verified)
    if args.price is not None:
        deal.storage_price = int(args.price)
    prepare_deal(deal)
    make_deal(deal)


if __name__ == '__main__':
    """
    The goal is to upload file to file coin and measure the time it takes to be
    available from the network
    
    Upload flow:
        - Given a storage provider, file, duration submit a propose
        - Record the submit time
        - Check the status every minute, record any update time
        - Stop checking if the status reached 'Sealing: Proving'
    """
    main()
