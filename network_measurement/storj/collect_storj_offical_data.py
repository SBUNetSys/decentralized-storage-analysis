import datetime
import json
import os.path

import requests


def collect_storj_data(prev_update_time, url):
    # collect storj data from official website

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(response.headers)
            if response.headers["Last-Modified"] == prev_update_time:
                print("No new data available")
                return None
            else:
                # print("New data available")
                return data, response.headers["Last-Modified"]
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def main():
    url_dic = {
        "data": "https://stats.storjshare.io/data.json",
        "nodes": "https://stats.storjshare.io/nodes.json",
        "nodes_geo": "https://stats.storjshare.io/nodes_geo.json",
        "accounts": "https://stats.storjshare.io/accounts.json",
    }
    save_dir = "storj_official_data"
    os.makedirs(save_dir, exist_ok=True)
    if os.path.exists("last_update_time.json"):
        with open("last_update_time.json", "r") as f:
            prev_update_time_dic = json.load(f)
    else:
        prev_update_time_dic = {"data": None, "nodes": None, "nodes_geo": None, "accounts": None}

    date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")

    for key, url in url_dic.items():
        last_update_time = prev_update_time_dic[key]
        data, new_update_time = collect_storj_data(last_update_time, url)
        # save data to file
        if data is not None:
            with open(f"{save_dir}/{date}_{key}.json", "w") as f:
                json.dump(data, f)
        # update last update time
        prev_update_time_dic[key] = new_update_time

    with open("last_update_time.json", "w") as f:
        json.dump(prev_update_time_dic, f)


if __name__ == '__main__':
    main()
