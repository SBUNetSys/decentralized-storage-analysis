import json
import os
import sys
from io import BytesIO

import pycurl


def measure_download_time(cid):
    url = f"http://127.0.0.1:8080/ipfs/{cid}"
    print(f"Requesting {url}")
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
    c.close()
    return m


def main():
    if len(sys.argv) != 2:
        print("Please provide download location")
        exit(-1)
    location = sys.argv[1]
    os.makedirs(f"ipfs_download_ttfb_{location}", exist_ok=True)
    with open("uploaded_files_cid.json", "r") as fin:
        uploaded_files = json.load(fin)
    # all_download_time = {}
    for cid in uploaded_files.keys():
        m = measure_download_time(cid)
        # all_download_time[cid] = m
        with open(f"ipfs_download_ttfb_{location}/{cid}.json", "w") as fout:
            json.dump(m, fout)
    print("Download time measurement completed")


if __name__ == '__main__':
    main()
