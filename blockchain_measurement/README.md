# Blockchain Measurement

This directory contains scripts for gathering blockchain transaction data using Etherscan and Ethplorer APIs.

## Files

- `get_stroj_info.py` - Script to collect transactions related to Storj token
- `get_swarm_info.py` - Script to collect transactions related to Swarm token

## Prerequisites

- Python 3.7+
- `requests` library

## Installation

1. Install the required Python packages:

```bash
pip install requests
```

2. Set up your Etherscan API key:
   - Register for an API key at [Etherscan](https://etherscan.io/apis)
   - Edit the scripts to include your API key (see Usage section)

## Usage

### Setting up API Keys

Open each Python file and replace the empty API key value with your actual Etherscan API key:

For `get_stroj_info.py`:
```python
if __name__ == '__main__':
    os.makedirs("storj_info", exist_ok=True)
    os.makedirs("storj_info_etherscan", exist_ok=True)
    main(api_key='YOUR_ETHERSCAN_API_KEY_HERE', start_timestamp="1680248375")
```

For `get_swarm_info.py`:
```python
if __name__ == '__main__':
    main(api_key='YOUR_ETHERSCAN_API_KEY_HERE')
```

### Running the Scripts

#### To collect Storj token transaction data:

```bash
python get_stroj_info.py
```

This script will:
1. Create directories `storj_info` and `storj_info_etherscan` if they don't exist
2. Query the Ethplorer API for Storj token history
3. Save the data in JSON format in the created directories
4. Query Etherscan for ETH transactions of the Storj wallet

#### To collect Swarm token transaction data:

```bash
python get_swarm_info.py
```

This script will:
1. Query the Etherscan API for Swarm token transactions
2. Save the transaction data in JSON format
3. Check for rate limits and implement exponential backoff if necessary

## Output

The scripts will create JSON files containing the transaction data:

- `storj_info/[timestamp].json` - Storj token transaction data from Ethplorer
- `storj_info_etherscan/[block_number].json` - Storj ETH transaction data from Etherscan
- `swarm_eth_info_etherscan_token/[block_number].json` - Swarm token transaction data from Etherscan

## Notes

- The scripts handle rate limiting by implementing sleep intervals when API limits are reached
- Default starting block for queries is 0 (beginning of the blockchain)
- The scripts will automatically query for additional transactions if more than 10,000 are found (API limit per request)
