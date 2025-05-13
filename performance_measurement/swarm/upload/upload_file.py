import argparse
import json
import os
import time

import pycurl


def upload_to_swarm(file_path, postage_batch_id):
    # Specify the URL for the Bee node's BZZ endpoint
    url = "http://localhost:1633/bzz"

    # Create a new Curl object
    c = pycurl.Curl()

    # Set the URL
    c.setopt(c.URL, url)

    # Set the HTTP method to POST
    c.setopt(c.POST, 1)

    # Set the headers
    c.setopt(c.HTTPHEADER, [
        "swarm-deferred-upload: false",
        "Content-Type: application/x-tar",
        "swarm-postage-batch-id: " + postage_batch_id
    ])

    # Set the data to be uploaded
    c.setopt(c.READDATA, open(file_path, 'rb'))

    # Create a buffer to store the response data
    response_buffer = bytearray()

    # Set the write function to handle the response data
    c.setopt(c.WRITEFUNCTION, response_buffer.extend)

    # Capture the start time
    start_time = time.time()

    # Perform the request
    c.perform()

    # Calculate the total upload time
    total_time = time.time() - start_time

    print("Total upload time:", total_time, "seconds")

    m = {"total_time": c.getinfo(pycurl.TOTAL_TIME), "namelookup_time": c.getinfo(pycurl.NAMELOOKUP_TIME),
         "connect_time": c.getinfo(pycurl.CONNECT_TIME), "pretransfer_time": c.getinfo(pycurl.PRETRANSFER_TIME),
         "redirect_time": c.getinfo(pycurl.REDIRECT_TIME),
         "starttransfer_time": c.getinfo(pycurl.STARTTRANSFER_TIME),
         "length": c.getinfo(pycurl.CONTENT_LENGTH_DOWNLOAD), "upload_time": total_time}
    # Close the Curl object
    c.close()

    # Convert the response buffer to a string
    response_data = response_buffer.decode('utf-8')
    swarm_hash = json.loads(response_data)["reference"]
    print("Swarm hash:", swarm_hash)
    return swarm_hash, m


def main():
    # parse arg for file path and postage batch id
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir_path", help="Path to the file to be uploaded")
    parser.add_argument("--postage_batch_id", help="Postage batch ID")
    args = parser.parse_args()

    dir_path = args.dir_path
    postage_batch_id = args.postage_batch_id
    file_mapping = {}
    # loop through files in the directory and upload them to Swarm
    for root, _, files in os.walk(dir_path):
        for file in files:
            file_path = os.path.join(root, file)
            print("Uploading file:", file_path)

            # upload the file to Swarm
            swarm_hash, upload_measurement = upload_to_swarm(file_path, postage_batch_id)

            # Save the upload measurement to a file
            data_path = "upload_data"
            os.makedirs(data_path, exist_ok=True)
            upload_file_data = {"swarm_hash": swarm_hash, "upload_measurement": upload_measurement}
            file_size = os.path.getsize(file_path) / 1024 / 1024  # in MB
            upload_file_data["file_size"] = file_size
            file_mapping[swarm_hash] = file_size
            print("Uploaded File Data:", upload_file_data)

            with open(os.path.join(data_path, f"{swarm_hash}.json"), "w") as f:
                json.dump(upload_file_data, f)
    with open("uploaded_files.json", "w") as f:
        json.dump(file_mapping, f)


if __name__ == '__main__':
    main()
