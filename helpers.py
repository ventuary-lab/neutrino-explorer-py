import pywaves as pw
import requests

# Helpers
def convert_to_waves(x):
    return x / 10 ** 8

def get_data_by_key(address, key, node_url=pw.NODE):
    return requests.get(f'{node_url}/addresses/data/{address}/{key}').json()

def get_asset_quantity(asset_id, node_url=pw.NODE):
    return requests.get(f'{node_url}/assets/details/{asset_id}').json().get('quantity')

def get_account_data(address, node_url=pw.NODE):
    return requests.get(f'{node_url}/addresses/data/{address}').json()

def get_waves_balance(address, node_url=pw.NODE):
    return requests.get(f'{node_url}/addresses/balance/{address}').json().get('balance')

def get_asset_balance(address, asset_id, node_url=pw.NODE):
    return requests.get(f'{node_url}/assets/balance/{address}/{asset_id}').json().get('balance')

def get_waves_locked_balance(auction_contract_address):
    auction_account_data = get_account_data(auction_contract_address)
    waves_locked_balance = auction_account_data.get('balance_lock_waves').value/100
    return waves_locked_balance

def get_decimals(asset_id, node_url=pw.NODE):
    return requests.get(f'{node_url}/assets/details/{asset_id}').json().get('decimals')

def filter_dict_by_key(key, account_data):
    try:
        filtered_array = [obj for obj in account_data if obj.get('key')==str(key)]
        if filtered_array:
            return filtered_array[0]["value"]
    except Exception as e:
        print("Exception occurred in filter_dict(): %s", e)
        return {}

def get_json(url):
    return requests.get(url).json()
