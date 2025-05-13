import json
import os.path
import sys

import pycurl
from io import BytesIO


def download_google_drive_file(file_id, output_file):
    # Construct the direct download link
    # download_url = "https://drive.google.com/uc?export=download&id=" + file_id + "&confirm=xxx"
    download_url = f"https://drive.usercontent.google.com/download?id={file_id}&confirm=xxx"
    # Initialize pycurl
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, download_url)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.FOLLOWLOCATION, True)  # Follow redirects
    c.setopt(pycurl.CAINFO, "/etc/ssl/certs/ca-certificates.crt")  # Specify the path to the CA certificate file
    # Perform the request
    c.perform()
    m = {"total_time": c.getinfo(pycurl.TOTAL_TIME), "namelookup_time": c.getinfo(pycurl.NAMELOOKUP_TIME),
         "connect_time": c.getinfo(pycurl.CONNECT_TIME), "pretransfer_time": c.getinfo(pycurl.PRETRANSFER_TIME),
         "redirect_time": c.getinfo(pycurl.REDIRECT_TIME),
         "starttransfer_time": c.getinfo(pycurl.STARTTRANSFER_TIME),
         "length": c.getinfo(pycurl.CONTENT_LENGTH_DOWNLOAD)}
    # Check if the request was successful (HTTP 200)
    if c.getinfo(pycurl.RESPONSE_CODE) == 200:
        # Save the response content to a file
        with open(output_file, 'wb') as f:
            f.write(buffer.getvalue())
        print("File downloaded successfully.")
    else:
        print("Failed to download file. HTTP status code:", c.getinfo(pycurl.RESPONSE_CODE))

    # Clean up
    c.close()
    return m


def process_shared_link():
    if os.path.exists("upload_file.json"):
        with open("upload_file.json", "r") as f:
            return json.load(f)
    size = ["5", "50", "512"]
    upload_file = {}
    with open("./link", "r") as f:
        link = f.read().strip()
        link = link.split(",")
        size_count = 0
        for index, i in enumerate(link):
            file_id = i.split("/")[-2]
            if index % 3 == 0 and index != 0:
                size_count += 1
            if size[size_count] not in upload_file:
                upload_file[size[size_count]] = []
            upload_file[size[size_count]].append(file_id)
    with open("upload_file.json", "w") as f:
        f.write(json.dumps(upload_file))
    return upload_file


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python download.py <location>")
        exit(1)
    location = sys.argv[1]
    save_path = f"google_drive_ttfb_{location}"
    os.makedirs(save_path, exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    # Example usage
    upload_file = process_shared_link()
    upload_time = {}
    for size, file_ids in upload_file.items():
        for file_id in file_ids:
            output_file = os.path.join("temp", f"downloaded_file_{size}_{file_id}.ext")
            print(f"Downloading file: {file_id}, size: {size}MB")
            upload_data = download_google_drive_file(file_id, output_file)
            print(f"Download time: {upload_data['total_time']} seconds")
            if size not in upload_time:
                upload_time[size] = {}
            upload_time[size][file_id] = upload_data
    with open(os.path.join(save_path, "download_time.json"), "w") as f:
        json.dump(upload_time, f)
    print("Download time measurement completed")
    # clean up
    # os.system("rm -rf temp")
    print("Clean up completed")
    #
    # file_id = "11t7v1ZeIa66Qjy_o68EwyzmE8y23YFu8"  # Replace with the ID of your shared Google Drive file
    # output_file = "downloaded_file.ext"  # Replace with the desired output file name and extension
    # download_google_drive_file(file_id, output_file)
