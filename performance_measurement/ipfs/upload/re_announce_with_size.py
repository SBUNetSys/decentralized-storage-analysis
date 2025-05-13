import argparse
import json
import os
import sys
import time

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", help="upload file size in MB")
    parser.add_argument("--location", help="location")
    args = parser.parse_args()
    if args.size is None:
        print('Please having --size argument')
        exit(-1)
    # size = sys.argv[1]
    size = args.size
    location = ["us-nj", "jp", "de", "cl", "au"]
    if args.location is not None:
        location = [args.location]
    load_dir = "uploaded_files_data"
    save_dir = "announcing_time_data"
    os.makedirs(save_dir, exist_ok=True)
    for loc in location:
        with open(f"{load_dir}/uploaded_files_{size}_{loc}.json", "r") as fin:
            data = json.load(fin)
        announcing_data = []
        for file in data:
            print(f"Announce Location {loc}, CID {file['cid']}")
            star_time = time.time()
            result = os.popen(f"ipfs routing provide {file['cid']}").read()
            end_time = time.time()
            for line in result.split('\n'):
                if "Error" in line:
                    print(line)
            announcing_data.append({
                "cid": file["cid"],
                "start_announce_time": star_time,
                "end_announce_time": end_time
            })
            # file["announcing_time"] = up_time
        with open(f"{save_dir}/announcing_time_{size}_{loc}.json", 'w') as fout:
            json.dump(announcing_data, fout)
    # with open(f"{load_dir}/uploaded_files_{size}_{location}.json", "r") as fin:
    #     data = json.load(fin)
    # announcing_data = []
    # for file in data:
    #     star_time = time.time()
    #     result = os.popen(f"ipfs routing provide {file['cid']}").read()
    #     end_time = time.time()
    #     for line in result.split('\n'):
    #         if "Error" in line:
    #             print(line)
    #     announcing_data.append({
    #         "cid": file["cid"],
    #         "start_announce_time": star_time,
    #         "end_announce_time": end_time
    #     })
    #     # file["announcing_time"] = up_time
    # with open(f"announcing_uploaded_file_{size}MB.json", 'w') as fout:
    #     json.dump(announcing_data, fout)
