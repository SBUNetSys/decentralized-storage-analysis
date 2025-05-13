import json
import os
import time


def check_deal_status(deal_data):
    """
    look up a deal with uuid and provider
    :param deal_data:
    :return: if new update was found
    """
    """
    boost deal-status --provider=f0187709 --deal-uuid=df0b7018-ccea-4f56-8ec7-7d37f4d6c152
    """
    """
    got deal status response
      deal uuid: df0b7018-ccea-4f56-8ec7-7d37f4d6c152
      deal status: Transfer Queued
      deal label: bafybeiafssuu6pn5b2nabwatjy5jxhoc5txphkjbtdn2eimsay6whxio4u
      publish cid: <nil>
      chain deal id: 0
    """
    result = os.popen(cmd=f"bash lookup.sh {deal_data['provider']} {deal_data['uuid']} 2>&1").read()
    # result = "got deal status response \n" \
    #          "deal uuid: df0b7018-ccea-4f56-8ec7-7d37f4d6c152)\n" \
    #          "deal status: Transfer Queued\n" \
    #          "deal label: bafybeiafssuu6pn5b2nabwatjy5jxhoc5txphkjbtdn2eimsay6whxio4u\n" \
    #          "publish cid: <nil>\n" \
    # "chain deal id: 0\n"
    deal_success = False
    update = False
    for line in result.split("\n"):
        if "got deal status" in line:
            deal_success = True
            continue
        if "Error" in line or "error" in line:
            line = line.replace("\n", "")
            split = line.split(": ")
            error_msg = split[-1]
            # print(f"{deal_data['uuid']} -> Error {line}", flush=True)
            if error_msg not in deal_data["deal_stats"]:
                print(f"New Error {deal_data['uuid']}, {error_msg}")
                deal_data["deal_stats"][error_msg] = line
                return True
            else:
                return False
        if deal_success and "publish" in line and "publish_cid" not in deal_data["deal_stats"]:
            line = line.replace("\n", "")
            split = line.split(": ")
            cid = split[-1]
            deal_data["deal_stats"]["publish_cid"] = cid
            update = True
        if deal_success and "status" in line:
            line = line.replace("\n", "")
            split = line.split(": ")
            status = split[-1]
            if status not in deal_data["deal_stats"]:
                print(f"Update status {deal_data['uuid']}, {status}")
                deal_data["deal_stats"][status] = time.time()
                update = True
    return update


def main():
    """
    read deal json from deals dir and look up each deal's status
    :return:
    """
    if not os.path.exists("./deal"):
        print("Deal directory doesn't exist")
        exit(-1)
    for root, dirs, files in os.walk("./deals"):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, 'r') as fin:
                deal_data = json.load(fin)
            # pass finished deal or error deal
            if "Proving" in deal_data["deal_stats"]:
                continue
            if check_deal_status(deal_data):
                with open(file_path, 'w') as fout:
                    json.dump(deal_data, fout)


if __name__ == '__main__':
    """
    This program lookup the status of a deal on file coin
    """
    main()
