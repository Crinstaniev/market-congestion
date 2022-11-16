import os
from doctest import REPORT_CDIFF

import pandas as pd
from eth_defi.event_reader.json_state import JSONFileScanState
from eth_defi.uniswap_v3.constants import UNISWAP_V3_FACTORY_CREATED_AT_BLOCK
from eth_defi.uniswap_v3.events import fetch_events_to_csv
from eth_defi.uniswap_v3.pool import fetch_pool_details
from web3 import HTTPProvider, Web3

while os.getcwd().split('/')[-1] != 'market-congestion':
    os.chdir('..')


RPC_URL = 'https://mainnet.infura.io/v3/b5502deb425f4629a1c886601e332e56'
web3 = Web3(HTTPProvider(RPC_URL))

start_block = 14650515
end_block = 14713964

state = JSONFileScanState('/tmp/uniswap-v3-price-scan.json')

fetch_events_to_csv(RPC_URL, state, start_block=start_block,
                    end_block=end_block)

swap_df = pd.read_csv('/tmp/uniswap-v3-swap.csv')

print(f"We have total {len(swap_df):,} swaps in the dataset")

pool_address = "0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8"
pool_details = fetch_pool_details(web3, pool_address)

print(pool_details)
print("token0 is", pool_details.token0, "with",
      pool_details.token0.decimals, "decimals")
print("token1 is", pool_details.token1, "with",
      pool_details.token1.decimals, "decimals")

# filter out the pool we are interested in
df = swap_df.loc[swap_df.pool_contract_address == pool_address.lower()]


def convert_price(row):
    # USDC/WETH pool has reverse token order, so let's flip it WETH/USDC
    tick = row["tick"]
    return pool_details.convert_price_to_human(tick, reverse_token_order=True)


def convert_value(row):
    # USDC is token0 and amount0
    price = float(row["price"])
    return abs(float(row["amount0"])) / (10**pool_details.token0.decimals)


df = df.copy(deep=True)  # https://stackoverflow.com/a/60885847/315168
df["price"] = df.apply(convert_price, axis=1)
df["value"] = df.apply(convert_value, axis=1)

print(df[["block_number", "timestamp", "price"]])
df.to_csv('data/price.csv')
