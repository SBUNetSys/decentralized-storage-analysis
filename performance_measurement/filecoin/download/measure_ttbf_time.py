import json
import os
import sys
from io import BytesIO

import pycurl


def measure_download_time(cid):
    url = f"http://127.0.0.1:34451/ipfs/{cid}?filename=sample.car"

    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    c.perform()

    # ttfb = c.getinfo(pycurl.INFO_STARTTRANSFER_TIME)
    m = {"total_time": c.getinfo(pycurl.TOTAL_TIME), "namelookup_time": c.getinfo(pycurl.NAMELOOKUP_TIME),
         "connect_time": c.getinfo(pycurl.CONNECT_TIME), "pretransfer_time": c.getinfo(pycurl.PRETRANSFER_TIME),
         "redirect_time": c.getinfo(pycurl.REDIRECT_TIME),
         "starttransfer_time": c.getinfo(pycurl.STARTTRANSFER_TIME),
         "length": c.getinfo(pycurl.CONTENT_LENGTH_DOWNLOAD)}

    http_code = c.getinfo(pycurl.RESPONSE_CODE)
    if http_code == 200:
        print(f"Request to {url} was successful")
    else:
        print(f"Request to {url} failed with status code: {http_code}")

    c.close()
    return m


def main():
    if len(sys.argv) != 2:
        print("Usage: need specificfy location")
        exit()
    location = sys.argv[1]
    os.makedirs(f"./filecoin_ttbf_{location}", exist_ok=True)
    for root, dirs, files in os.walk('../deals'):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, "r") as fin:
                data = json.load(fin)
            cid = data["payload_cid"]
            if "Proving" in data["deal_stats"]:
                deal_success = True
            else:
                deal_success = False
            download_info = {"cid": cid,
                             "success": True,
                             "error": False,
                             "deal_status": deal_success}

            if deal_success:
                print(cid, file)
                m = measure_download_time(cid)
                with open(f"./filecoin_ttbf_{location}/{file.split('.')[0]}.json", "w") as fout:
                    json.dump(m, fout)
    print("Download time measurement completed")


if __name__ == '__main__':
    main()
