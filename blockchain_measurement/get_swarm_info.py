import json
import logging
import os
import time

import requests


def get_token_history(api_key, start_timestamp=None):
    # download the blockchain history from ethplorer.io
    # and save it to the file
    # Define the URL
    url = f'https://api.ethplorer.io/getTokenHistory/0xB64ef51C888972c908CFacf59B47C1AfBC0Ab8aC'
    params = {
        'apiKey': api_key,
        'limit': 1000
    }
    if start_timestamp:
        params['timestamp'] = start_timestamp
    # Send the GET request
    try:
        print(f"Downloading data from {url} with params {params}, start_timestamp={start_timestamp}")
        response = requests.get(url, params=params)
        data = response.json()
        if response.status_code != 200:
            print(f'Error: {response.status_code}')
            return data
        else:
            return data
    except requests.exceptions.RequestException as e:
        print(e)
        return None


def get_tx_token_history(acct, from_block):
    """
        get all normal transaction from etherscan NOTE: max of 10k due to API limitation
        :param from_block: starting blocks to check
        :param acct: account address
        :return: status:bool : True for ok, False for failed
        :return: data: json result from the api call
        """
    headers = {
        'accept': 'application/json',
        'user-agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }
    print(f"Querying transactions for {acct}, block {from_block}")
    logging.info(f"Querying transactions for {acct}, block {from_block}")
    url = f'https://api.etherscan.io/api' \
          f'?module=account' \
          f'&action=tokentx' \
          f'&address={acct}' \
          f'&startblock={from_block}' \
          f'&endblock=99999999' \
          f'&sort=asc' \
          f'&apikey='
    # f'&page=1&offset=10' \
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        logging.info(f"Failed queried {acct}, status code {r.status_code}")
        print(f"Failed queried {acct}, {r.status_code}")
        return False, {'result': "Max rate limit"}
    try:
        data = r.json()
        status = False
        if data["status"] == "1":
            status = True
            # logging.info(f"Successfully queried {acct}, totalling {len(data['result'])} transaction")
            # print(f"Successfully queried {acct}, totalling {len(data['result'])} transaction")
            return status, data
        else:
            return status, data
    except Exception as e:
        logging.info(f"Failed queried {acct}, {e}")
        print(f"Failed queried {acct}, {e}")
        exit(-1)


def get_tx(acct, from_block):
    """
    get all normal transaction from etherscan NOTE: max of 10k due to API limitation
    :param from_block: starting blocks to check
    :param acct: account address
    :return: status:bool : True for ok, False for failed
    :return: data: json result from the api call
    """
    headers = {
        'accept': 'application/json',
        'user-agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }
    print(f"Querying transactions for {acct}, block {from_block}")
    logging.info(f"Querying transactions for {acct}, block {from_block}")
    url = f'https://api.etherscan.io/api' \
          f'?module=account' \
          f'&action=txlist' \
          f'&address={acct}' \
          f'&startblock={from_block}' \
          f'&endblock=99999999' \
          f'&sort=asc' \
          f'&apikey='
    # f'&page=1&offset=10' \
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        logging.info(f"Failed queried {acct}, status code {r.status_code}")
        print(f"Failed queried {acct}, {r.status_code}")
        return False, {'result': "Max rate limit"}
    try:
        data = r.json()
        status = False
        if data["status"] == "1":
            status = True
            # logging.info(f"Successfully queried {acct}, totalling {len(data['result'])} transaction")
            # print(f"Successfully queried {acct}, totalling {len(data['result'])} transaction")
            return status, data
        else:
            return status, data
    except Exception as e:
        logging.info(f"Failed queried {acct}, {e}")
        print(f"Failed queried {acct}, {e}")
        exit(-1)


def get_tx_gnosis(acct, from_block):
    """
    get all normal transaction from gnosis NOTE: max of 10k due to API limitation
    :param from_block: starting blocks to check
    :param acct: account address
    :return: status:bool : True for ok, False for failed
    :return: data: json result from the api call
    """
    headers = {
        'accept': 'application/json',
        'user-agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }
    print(f"Querying transactions for {acct}, block {from_block}")
    logging.info(f"Querying transactions for {acct}, block {from_block}")
    url = f'https://api.gnosisscan.io/api' \
          f'?module=account' \
          f'&action=txlist' \
          f'&address={acct}' \
          f'&startblock={from_block}' \
          f'&endblock=99999999' \
          f'&sort=asc' \
          f'&apikey='
    # f'&page=1&offset=10' \
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        logging.info(f"Failed queried {acct}, status code {r.status_code}")
        print(f"Failed queried {acct}, {r.status_code}")
        return False, {'result': "Max rate limit"}
    try:
        data = r.json()
        status = False
        if data["status"] == "1":
            status = True
            # logging.info(f"Successfully queried {acct}, totalling {len(data['result'])} transaction")
            # print(f"Successfully queried {acct}, totalling {len(data['result'])} transaction")
            return status, data
        else:
            return status, data
    except Exception as e:
        logging.info(f"Failed queried {acct}, {e}")
        print(f"Failed queried {acct}, {e}")
        exit(-1)


def get_more_tx(wallet_addr, start_block=None, data=None, gnosis=False, save_dir="./"):
    """
    try to get all tx from etherscan for a wallet address
    """
    crawled_all = False
    time_sleep = 5
    count = 0
    while not crawled_all:
        # start_block = current latest block + 1
        if start_block is None:
            # default start block for storj
            start_block = 0
        else:
            if data is not None:
                start_block = int(data["result"][-1]["blockNumber"]) + 1

        if gnosis:
            status, data = get_tx_gnosis(wallet_addr, start_block)
        else:
            status, data = get_tx(wallet_addr, start_block)
        if status is False:
            reason = data["result"]
            print(f"Failed Querying {wallet_addr}, {data}")
            logging.info(f"Failed Querying {wallet_addr}, {data}")
            if "Max rate limit" in reason:
                logging.info(f"Max rate limited, now sleeping {time_sleep}s")
                print(f"Max rate limited, now sleeping {time_sleep}s")
                time.sleep(time_sleep)
                time_sleep = time_sleep * 2
            elif "No transactions found" in data["message"]:
                with open(f"./storj_info_etherscan/{wallet_addr}.json", "w") as fout:
                    json.dump(data, fout)
                logging.info(f"Warning {wallet_addr} no transaction found.")
                print(f"Warning {wallet_addr} no transaction found.")
                crawled_all = True
            else:
                print(f"{wallet_addr}: Non-limit error encountered, exiting")
                exit(-1)
        else:
            time_sleep = 5
            new_tx_amt = len(data["result"])
            logging.info(f"Add {new_tx_amt} tx to {wallet_addr}, "
                         f"totalling {count + new_tx_amt} transaction")
            print(f"Add {new_tx_amt} tx to {wallet_addr}, "
                  f"totalling {count + new_tx_amt} transaction")
            with open(f"./{save_dir}/{start_block}.json", "w") as fout:
                json.dump(data, fout)
            count += new_tx_amt
            if new_tx_amt < 10000:
                logging.info(f"Finished crawling {wallet_addr}, tx {len(data['result']) + count} ")
                print(f"Finished crawling {wallet_addr}, tx {len(data['result']) + count}")
                crawled_all = True


def query_with_etherscan(wallet_addr):
    os.makedirs("swarm_eth_info_etherscan_token", exist_ok=True)
    get_more_tx(wallet_addr, None, None, save_dir="swarm_eth_info_etherscan_token")


def query_with_gnosis(wallet_addr):
    os.makedirs("swarm_eth_info_gnosis", exist_ok=True)
    get_more_tx(wallet_addr, None, None, gnosis=True, save_dir="swarm_eth_info_gnosis")


def query_with_ethplorer(api_key, start_timestamp=None):
    sleep_time = 60
    while True:
        data = get_token_history(api_key, start_timestamp)
        if data:
            if "error" in data:
                print(data)
                time.sleep(sleep_time)
                sleep_time += 60
                continue
            if len(data["operations"]) == 0:
                # finished crawling
                break
            print(f"Downloaded {len(data['operations'])} operations, start_timestamp={start_timestamp}")
            if start_timestamp is None:
                # newest data / first time crawling
                save_timestamp = data["operations"][0]["timestamp"]
                # update the start_timestamp to the newest timestamp
                start_timestamp = data["operations"][-1]["timestamp"]
            else:
                # save the data to the file with start_timestamp
                save_timestamp = start_timestamp
                # update the start_timestamp to the newest timestamp
                start_timestamp = data["operations"][-1]["timestamp"]
            print(f"Updated start_timestamp from {save_timestamp} to {start_timestamp}")
            # Save the data to the file
            with open(f"storj_info/{save_timestamp}.json", "w") as f:
                json.dump(data, f)
        else:
            # Wait for 1 minute
            time.sleep(60)


def main(api_key, start_timestamp=None):
    """
       This function will try to get all the transactions that is over 10k
       Query next 10k by specifying block starting point
    """
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                        level=logging.INFO,
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename="get-all-transactions.log")
    # get ETH chains
    query_with_etherscan("0x19062190B1925b5b6689D7073fDfC8c2976EF8Cb")
    # get transactions from gnosis
    # query_with_gnosis("0xdbf3ea6f5bee45c02255b2c26a16f300502f68da")


if __name__ == '__main__':
    main(api_key='freekey')
