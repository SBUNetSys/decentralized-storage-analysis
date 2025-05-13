# Decentralized Storage Analysis

This repository contains tools, scripts, and analysis for measuring performance and network characteristics of different decentralized storage platforms compared to traditional centralized solutions.

This code accompanies the paper "Degrees of Decentralized Freedom: Comparing Modern Decentralized Storage Platforms" submitted to TMA 2025 (IFIP Network Traffic Measurement and Analysis Conference).

## Repository Structure

The repository is organized into three main directories:

- **[performance_measurement/](performance_measurement/)**: Tools for measuring upload time, Time-To-First-Byte, and download performance across different decentralized storage systems.
- **[blockchain_measurement/](blockchain_measurement/)**: Scripts for gathering blockchain transaction data related to storage platforms using Etherscan and Ethplorer APIs.
- **[network_measurement/](network_measurement/)**: Scripts for collecting network data from various storage platforms.

## Performance Measurement

The performance measurement tools analyze the following storage systems:

- IPFS
- Filecoin
- Swarm
- Storj
- Google Drive (as a centralized comparison)

The tools measure metrics such as:
- Upload times for different file sizes
- Download performance across geographic locations
- Time-To-First-Byte (TTFB)
- Network characteristics and availability

See the [performance_measurement README](performance_measurement/README.md) for detailed instructions on how to use these tools.

## Blockchain Measurement

The blockchain measurement scripts gather transaction data related to storage tokens from blockchain explorers, allowing analysis of:

- Token price history
- Network participation metrics
- Token distribution patterns

See the [blockchain_measurement README](blockchain_measurement/README.md) for instructions on setting up and running these scripts.

## Network Measurement

The network measurement scripts collect data on network characteristics of various storage platforms, including:

- Peer information
- Network connectivity
- Geographic distribution
- Node availability

See the [network_measurement README](network_measurement/README.md) for more information.

## License

[MIT License](LICENSE)
