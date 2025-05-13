# Storage Systems Performance Measurement

This repository contains tools for measuring various performance metrics (upload time, Time-To-First-Byte, download time) across different decentralized storage systems:

- IPFS
- Filecoin
- Swarm
- Storj
- Google Drive

## Overview

Each storage system has separate directories for upload and download operations with specific scripts to run the measurements. The testing methodology generally follows these steps:

1. Generate test files of various sizes (typically 5MB, 50MB, 512MB)
2. Upload files to the storage system
3. Download files from the storage system and measure performance metrics
4. Collect and analyze the timing data

## Prerequisites

### General Requirements

- Python 3.7+
- pycurl library (`pip install pycurl`)
- Git (for some operations)

### System-Specific Requirements

#### IPFS
- IPFS daemon installed: https://docs.ipfs.tech/install/
- Run `ipfs init` to initialize your node

#### Filecoin
- Boost client installed: https://boost.filecoin.io/
- Lassie installed for downloads: https://github.com/filecoin-project/lassie
- Filecoin wallet with available funds
- Valid storage provider ID

#### Swarm
- Bee client installed: https://docs.ethswarm.org/docs/bee/installation/getting-started
- Purchased postage stamp with valid batch ID

#### Storj
- Uplink CLI client installed: https://storj.dev/dcs/api/uplink-cli/installation
- Configured authentication with access grant

#### Google Drive
- Google API credentials
- Set up OAuth authentication

## Directory Structure

```
.
├── filecoin/
│   ├── download/
│   │   ├── measure_ttbf_time.py
│   │   └── start_lassie_daemon.sh
│   └── upload/
│       ├── check-new.sh
│       ├── deal.sh
│       ├── lookup.py
│       ├── lookup.sh
│       └── upload.py
├── google_drive/
│   ├── download/
│   │   └── download.py
│   └── upload/
│       └── uoload_file.py
├── ipfs/
│   ├── download/
│   │   └── measure_ttfb.py
│   └── upload/
│       ├── announce_with_loc.sh
│       ├── auto_upload_with_loc.sh
│       ├── cleanup.sh
│       ├── gen_upload_file_with_size.py
│       ├── re_announce_with_size.py
│       └── upload_with_size.py
├── storj/
│   ├── download/
│   │   └── measure_ttfb.py
│   └── upload/
│       └── upload.sh
└── swarm/
    ├── download/
    │   └── measure_ttfb.py
    └── upload/
        └── upload_file.py
```

## Usage Instructions

### IPFS

#### Upload
1. Generate test files:
   ```
   python ipfs/upload/gen_upload_file_with_size.py --size <size_in_MB> --count <number_of_files>
   ```

2. Upload files to IPFS:
   ```
   ./ipfs/upload/auto_upload_with_loc.sh <size> <number_of_files> <location>
   ```
   Example: `./ipfs/upload/auto_upload_with_loc.sh 5M 3 us-nj`

3. Announce files to the IPFS network:
   ```
   ./ipfs/upload/announce_with_loc.sh <size> <loc>
   ```
   Example: `./ipfs/upload/announce_with_loc.sh 5M us-nj`

#### Download
1. Measure TTFB (Time To First Byte):
   ```
   python ipfs/download/measure_ttfb.py <location>
   ```

### Filecoin

#### Upload
1. Make sure Boost client is installed and configured.

2. Run the upload script:
   ```
   python filecoin/upload/upload.py --provider <provider_id> --file <file_path> --duration <duration> --verified <true/false> --price <price>
   ```

3. Check deal status:
   ```
   ./filecoin/upload/check-new.sh
   ```

#### Download
1. Start the Lassie daemon:
   ```
   ./filecoin/download/start_lassie_daemon.sh
   ```

2. Measure download performance:
   ```
   python filecoin/download/measure_ttbf_time.py <location>
   ```

### Swarm

#### Upload
1. Ensure you have a valid postage batch ID.

2. Upload files:
   ```
   python swarm/upload/upload_file.py --dir_path <directory_path> --postage_batch_id <batch_id>
   ```

#### Download
1. Measure download performance:
   ```
   python swarm/download/measure_ttfb.py <location>
   ```

### Storj

#### Upload
1. Make sure you have configured Uplink with a valid access grant.

2. Upload files:
   ```
   ./storj/upload/upload.sh <location>
   ```

#### Download
1. Measure TTFB:
   ```
   python storj/download/measure_ttfb.py <location>
   ```

### Google Drive

#### Upload
1. Configure Google API credentials.

2. Upload files:
   ```
   python google_drive/upload/uoload_file.py
   ```

#### Download
1. Measure download performance:
   ```
   python google_drive/downlaod/download.py <location>
   ```

## Additional Notes

### IPFS
- The upload process includes an announcement phase to ensure files are properly distributed in the network
- Location parameters help measure performance from different geographic regions

### Filecoin
- Filecoin operates with storage deals that need to be accepted by storage providers
- You must have a wallet with sufficient funds to pay for storage
- Check that your provider ID is valid and the provider is accepting deals
- Lassie is required for retrieving content from the Filecoin network

### Swarm
- Postage stamps are required to upload content to Swarm
- You need to purchase stamps through the Bee client before uploading
- The postage batch ID is required for all uploads

### Storj
- Authentication setup is required before using Storj
- Files need to be shared using the uplink client to be accessible for download

## Troubleshooting

### IPFS
- If uploads fail, ensure the IPFS daemon is running with `ipfs daemon`
- Use `./ipfs/upload/cleanup.sh` to reset your IPFS environment

### Filecoin
- Deal rejections might occur due to insufficient funds or provider requirements
- Check logs in `./deals/` directory for error messages

### Swarm
- Connection issues may indicate that your Bee node is not properly connected
- Verify stamp balance and validity

### Storj
- Authentication errors are common - check your access grant
- Ensure buckets are properly created and accessible

### Google Drive
- API rate limits may be encountered with frequent requests
- Verify OAuth tokens are not expired
