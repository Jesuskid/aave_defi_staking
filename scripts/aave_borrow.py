from scripts.helpful_scripts import get_account
from scripts.getWeth import get_weth
from brownie import config, network, interface
from web3 import Web3

AMOUNT = Web3.toWei(0.1, "ether")


def borrow():
    pass


def get_lending_pool():
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    # Address
    address = lending_pool_addresses_provider.gbrownetLendingPool()
    # ABI
    lending_pool = interface.ILendingPool(address)
    print(lending_pool)
    return lending_pool


def approveErc20(amount, spender_address, erc_token_add, account):
    print("Apprvoing Erc20 token")
    erc20 = interface.IERC20(erc_token_add)
    tx = erc20.approve(spender_address, amount, {"from": account})
    tx.wait(1)
    print("approved")
    return tx
    # abi
    # address


def get_borrowable_data(lending_pool, account):
    (
        total_col_eth,
        total_debt_eth,
        availbale_b_eth,
        current_liquidation_load,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)

    availbale_b_eth = Web3.fromWei(availbale_b_eth, "ether")
    total_col_eth = Web3.fromWei(total_col_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")

    print(f"You have {total_debt_eth} debt eth")
    print(f"You have total col eth {total_col_eth}")
    print(f"You can borrow {availbale_b_eth}")
    return (float(availbale_b_eth), float(total_debt_eth))


def main():
    account = get_account()
    er20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    lending_pool = get_lending_pool()

    approveErc20(AMOUNT, lending_pool.address, er20_address, account)
    print("Depositing")
    tx = lending_pool.deposit(
        er20_address, AMOUNT, account, 0, {"from": account, "gas_limit": 300000}
    )
    tx.wait(1)
    print("Deposited")

    # ...how much
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    print("Let's Borrow")
    #  Dai in terms of eth

    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
    amount_of_dai_to_borrow = (1 / dai_eth_price) * (borrowable_eth * 0.95)
    print(f"We are going to to borrow {amount_of_dai_to_borrow} ")
    dai_address = config["networks"][network.show_active()]["dai_token_address"]
    borrow_tx = lending_pool.borrow(
        dai_address,
        Web3.toWei(amount_of_dai_to_borrow, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )

    borrow_tx.wait(1)
    print(f"We borrowed some Dai")
    get_borrowable_data(lending_pool, account)
    # repay_all(AMOUNT, lending_pool, account)
    print("You just deposited, borrowed an repaid with this contract")


def get_asset_price(price_feed_address):
    # ABI
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    converted_latest_price = Web3.fromWei(latest_price, "ether")
    print(f"Dai eth price is {converted_latest_price}")
    return float(converted_latest_price)
    # Address


def repay_all(amount, lending_pool, account):
    approveErc20(
        Web3.toWei(amount, "ether"),
        lending_pool,
        config["networks"][network.show_active()]["dai_token_address"],
        account,
    )
    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["dai_token_address"],
        amount,
        1,
        account.address,
        {"from": account},
    )
    repay_tx.wait(1)
    print("repaid")
