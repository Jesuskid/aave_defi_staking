from scripts.helpful_scripts import get_account
from brownie import interface, config, network


def get_weth():
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from": account, "value": 0.1 * 10 ** 18, "gas_limit": 300000})
    tx.wait(1)
    print(f"sent 0.1 weht")
    return tx


def main():
    """Mints weth by depositing eth"""

    # Abi
    # address

    get_weth()
