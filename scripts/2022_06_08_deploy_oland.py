import click

from brownie import (
    accounts,
    network,
    Rentable,
    OLandRegistry,
    history,
    project,
)

oz = project.load("./lib/openzeppelin-contracts")
UpgradeableBeacon = oz.UpgradeableBeacon
ProxyAdmin = oz.ProxyAdmin


def main():
    dev = accounts.load("rentable-deployer")
    accounts.default = dev

    # params
    network.gas_price("50 gwei")

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

    r = Rentable.at("0xd766a11858c57252cC4F9978282B616C3e0bBAC4")
    proxyAdmin = ProxyAdmin.at("0xdb246e57c401792Fd272314ce666f5dB07E89e67")
    landAddress = "0xF87E31492Faf9A91B02Ee0dEAAd50d51d56D5d4d"
    eth = "0x0000000000000000000000000000000000000000"
    oLand = "0xcE6AC4D01d18B99BF7926a2cdFa87D03d271d3d8"

    # Deploy OLandRegistry and upgrade proxy contract

    orentableLogic = OLandRegistry.deploy(landAddress, eth, eth)
    obeacon = UpgradeableBeacon.deploy(orentableLogic)
    proxyAdmin.upgrade(oLand, obeacon)

    click.echo(
        f"""
             ---- Decentraland(LAND) ---- 
                OLogic: {orentableLogic.address}
               OBeacon: {obeacon.address}
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
