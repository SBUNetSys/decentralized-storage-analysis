import json
import os
import sys
from io import BytesIO

import pycurl


def measure_download_time(file_name):
    url = f"https://link.storjshare.io/raw/jwufg2fvoijvnzbychrzdwsfjgka/upload-measurement/{file_name}"
    print(f"Requesting {url}")
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(pycurl.CAINFO, "/etc/ssl/certs/ca-certificates.crt")
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
    os.makedirs(f"storj_download_ttfb_{location}", exist_ok=True)
    # "https://link.storjshare.io/raw/jwufg2fvoijvnzbychrzdwsfjgka/upload-measurement/"
    for size in [5, 50, 512]:
        for i in range(1, 4):
            file_name = f"{size}M_{i}"
            print(f"Measuring TTFB for {file_name}")
            m = measure_download_time(f"{file_name}.bin")
            with open(f"storj_download_ttfb_{location}/{file_name}.json", "w") as fout:
                json.dump(m, fout)

if __name__ == '__main__':
    main()