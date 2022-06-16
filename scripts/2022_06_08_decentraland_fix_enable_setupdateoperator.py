import click

from brownie import (
    accounts,
    network,
    Rentable,
    history,
)


def main():
    dev = accounts.load("rentable-deployer")
    accounts.default = dev

    # params
    network.gas_price("51 gwei")

    initialDeployerBalance = dev.balance()
    click.echo(
        f"""
        ---- Params ----
     Deployer: {dev.address}
      Balance: {initialDeployerBalance/1e18} ETH
    Gas Price: {network.gas_price()/1e9} gwei
        ----------------
    """
    )

    # PreProd env

    r = Rentable.at("0xd766a11858c57252cC4F9978282B616C3e0bBAC4", dev)
    oLand = "0xcE6AC4D01d18B99BF7926a2cdFa87D03d271d3d8"

    # Enable updateOperator from ORentable
    r.enableProxyCall(oLand, "0x9d40b850", False)  # disable updateOperator signature
    r.enableProxyCall(oLand, "0xb0b02c60", True)  # enable setUpdateOperator signature

    totalGasUsed = 0
    for tx in history:
        totalGasUsed += tx.gas_used

    click.echo(
        f"""
            -------- Stats --------
              TotalGas: {totalGasUsed}
              GasPrice: {network.gas_price()/1e9} gwei
Final Balance Deployer: {dev.balance()/1e18} ETH
           Total Spent: {(initialDeployerBalance - dev.balance())/1e18} ETH
            -----------------------
         """
    )
