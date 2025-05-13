# Storga Network Scripts

This repository contains scripts for interacting with different decentralized storage platforms through the Storga network integration.

## Directory Structure

The directory is organized by platform, with each subdirectory containing platform-specific scripts and configurations. Each platform directory contains a `collect.sh` script for data collection.

```
storga-network-scripts/
├── ipfs_filecoin/  # Combined IPFS and Filecoin integration scripts (1 item)
├── storj/          # Storj integration scripts and custom uplink client (3 items)
│   └── upload-hooked/  # Custom uplink client implementation
├── swarm/          # Swarm integration scripts (1 item)
└── README.md       # This documentation file
```

## Platform Requirements

### IPFS and Filecoin

To use the IPFS and Filecoin scripts (combined in the `ipfs_filecoin` directory), you need to install Nebula:

1. Install Nebula from [https://github.com/dennis-tra/nebula](https://github.com/dennis-tra/nebula)
2. Follow the installation instructions in the Nebula repository README
3. Verify installation with:
   ```
   nebula --version
   ```

### Storj

For Storj integration, you need to:

1. Navigate to the `storj/upload-hooked` directory
2. Build the custom uplink client:
   ```
   go build examples/walkthrough
   ```
3. Obtain API keys from Storj:
   - Create an account at [https://www.storj.io/](https://www.storj.io/)
   - Generate access grants in the Storj console
   - Save your keys securely for use with the client

### Swarm

The Swarm scripts can be run as-is without additional installation.

## Usage

Each platform directory contains a `collect.sh` script as the main entry point.

### IPFS and Filecoin

```bash
cd ipfs_filecoin
./collect.sh
```

### Storj

```bash
cd storj
./collect.sh
```

For using the custom uplink client:

```bash
cd storj/upload-hooked
# Build the client
go build examples/walkthrough
# Run the custom uplink client with regional API keys
./walkthrough --na key --eu key --ap key --output ./storj
```

The walkthrough command accepts regional API keys:
- `--na`: North America region key
- `--eu`: Europe region key
- `--ap`: Asia-Pacific region key
- `--output`: Directory where data will be saved

### Swarm

```bash
cd swarm
./collect.sh
```

## Troubleshooting

If you encounter issues:

- Check that all required dependencies are installed
- Verify API keys and access grants are valid
- Ensure network connectivity to the respective platforms
- Review logs for specific error messages
