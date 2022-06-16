import click

from brownie import (
    accounts,
    network,
    Rentable,
    WalletFactory,
    history,
)


def main():
    dev = accounts.load("rentable-deployer")
    accounts.default = dev

    # params
    network.gas_price("54 gwei")

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
    simpleWalletBeacon = "0x268bC6FC0aB22847d9DE037DcEEb8F656826EF44"

    # Deploy and setup wallet factory

    walletFactory = WalletFactory.deploy(simpleWalletBeacon)
    r.setWalletFactory(walletFactory)

    click.echo(
        f"""
             ---- WalletFactory ---- 
         WalletFactory: {walletFactory.address}
             ----------------------
         """
    )

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
