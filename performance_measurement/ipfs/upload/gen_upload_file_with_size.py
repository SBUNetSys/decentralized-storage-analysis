import argparse
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--size')
    parser.add_argument('--count')
    args = parser.parse_args()
    if args.size is None or args.count is None:
        print('Please having --size and --count arguments')
        exit(-1)

    os.makedirs("upload_files", exist_ok=True)
    for i in range(0, int(args.count)):
        file_name = os.path.join("upload_files", f"{args.size}m-test-{i + 1}" + ".bin")
        os.system(command=f"dd if=/dev/urandom of={file_name} bs=1M count={args.size}")
