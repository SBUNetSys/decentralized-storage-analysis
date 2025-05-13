import json
import os
import sys

import pycurl


def discard_response(data):
    # This function simply returns the length of the data, effectively discarding it
    return len(data)


def download_from_swarm(swarm_hash):
    # Specify the URL for the Bee node's BZZ endpoint
    url = f"http://localhost:1633/bzz/{swarm_hash}/"
    print(f"Requesting {url}")
    # Create a new Curl object
    c = pycurl.Curl()
    try:
        # Set the URL
        c.setopt(c.URL, url)

        # Set the follow location option to automatically follow redirects
        c.setopt(c.FOLLOWLOCATION, True)

        # Set the header to disable caching
        c.setopt(pycurl.HTTPHEADER, ["swarm-cache: false"])

        # Enable TCP keep-alive
        c.setopt(pycurl.TCP_KEEPALIVE, True)

        # Specify the time (in seconds) the connection can remain idle before sending TCP keepalive probes
        c.setopt(pycurl.TCP_KEEPIDLE, 120)  # Example: 60 seconds

        # Set the option to automatically output to a file with the same name as in the URL
        # c.setopt(c.WRITEDATA, open(os.path.basename(url), 'wb'))

        # Set the option to discard the response data
        c.setopt(c.WRITEFUNCTION, discard_response)

        # Perform the request
        c.perform()

    except pycurl.error as e:
        print(f"Error {e}")
    finally:
        # Calculate the total upload time
        m = {"total_time": c.getinfo(pycurl.TOTAL_TIME), "namelookup_time": c.getinfo(pycurl.NAMELOOKUP_TIME),
             "connect_time": c.getinfo(pycurl.CONNECT_TIME), "pretransfer_time": c.getinfo(pycurl.PRETRANSFER_TIME),
             "redirect_time": c.getinfo(pycurl.REDIRECT_TIME),
             "starttransfer_time": c.getinfo(pycurl.STARTTRANSFER_TIME),
             "length": c.getinfo(pycurl.CONTENT_LENGTH_DOWNLOAD)}

        # Close the Curl object
        c.close()
    return m


def main():
    if len(sys.argv) != 2:
        print("Please provide download location")
        exit(-1)
    location = sys.argv[1]
    os.makedirs(f"swarm_download_ttfb_{location}", exist_ok=True)
    # load uploaded_files.json
    with open("uploaded_files.json", "r") as fin:
        uploaded_files = json.load(fin)
    for swarm_hash in uploaded_files:
        if os.path.exists(f"swarm_download_ttfb_{location}/{swarm_hash}.json"):
            print(f"File {swarm_hash} already downloaded")
            continue
        m = download_from_swarm(swarm_hash)
        print(f"Downloaded {swarm_hash}, \nmeasurement: {m}")
        with open(f"swarm_download_ttfb_{location}/{swarm_hash}.json", "w") as fout:
            json.dump(m, fout)
    print("Download time measurement completed")


if __name__ == '__main__':
    main()
