import argparse
import json
import os
import time


class File:
    def __init__(self, cid, upload_start_time, process_end_time, size):
        self.cid = cid
        self.upload_start_time = upload_start_time
        self.process_end_time = process_end_time
        self.available_time = None
        self.size = size


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_dir", help="")
    parser.add_argument("--size", help="upload file size in MB")
    parser.add_argument("--loc", help="location")
    args = parser.parse_args()
    save_dir = "uploaded_files_data"
    os.makedirs(save_dir, exist_ok=True)
    all_files = []
    if args.file_dir is None or args.size is None:
        print("Deal must have file dir and file size")
        exit(-1)
    locations = ["us-nj", "jp", "de", "cl", "au"]
    if args.loc is not None:
        locations = [args.loc]
    upload_data = {loc: [] for loc in locations}
    for root, dirs, files in os.walk(args.file_dir):
        loc_index = 0
        for index, file in enumerate(files):
            file_path = os.path.join(root, file)
            size = os.path.getsize(file_path) / (1024 * 1024)   # MB
            start_time = time.time()
            if int(size) != int(args.size):
                continue
            result = os.popen(cmd=f"ipfs add {file_path}").read()
            process_end_time = time.time()
            for line in result.splitlines():
                if "added" in line:
                    # process cid
                    line = line.removesuffix("\n")
                    cid = line.split(" ")[1]
                    f = File(cid, start_time, process_end_time, size)
                    if index % 3 == 0 and index != 0:
                        loc_index += 1
                    upload_data[locations[loc_index]].append(f)
                    all_files.append(f)
    for loc in locations:
        with open(f"{save_dir}/uploaded_files_{args.size}_{loc}.json", "w") as fout:
            json.dump([x.__dict__ for x in upload_data[loc]], fout)
    # with open(f"uploaded_files_{args.size}MB.json", "w") as fout:
    #     json.dump([x.__dict__ for x in all_files], fout)


if __name__ == '__main__':
    main()
