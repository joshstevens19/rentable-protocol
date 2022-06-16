import click

from brownie import (
    accounts,
    network,
    Rentable,
    ORentable,
    WRentable,
    SimpleWallet,
    WalletFactory,
    ImmutableAdminTransparentUpgradeableProxy,
    ImmutableAdminUpgradeableBeaconProxy,
    DecentralandCollectionLibrary,
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
    network.gas_price("25 gwei")

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

    governance = "0xf6798a60B576658461eeFebf583C2AaECD732334"
    proxyAdmin = "0xdb246e57c401792Fd272314ce666f5dB07E89e67"
    r = Rentable.at("0xd766a11858c57252cC4F9978282B616C3e0bBAC4", dev)
    orentableLogic = ORentable.at("0xe1ac13c21e3F1EeBF71CC0F9e74D6059AbAc7970")
    obeacon = "0x31c82151B1fDD035C64EB8b4c896AFF799ca63b1"
    wrentableLogic = WRentable.at("0x160AC61AFb9323B372FEeB157471F23984544dFb")
    wbeacon = "0x3Ec6fd32bb71fc288f18DCc1F2EBd6Bb00BAB25f"

    # Setup LobsterDAO

    lobsterDAO = "0x026224A2940bFE258D0dbE947919B62fE321F042"

    # OToken
    oproxy = ImmutableAdminUpgradeableBeaconProxy.deploy(
        obeacon,
        proxyAdmin,
        orentableLogic.initialize.encode_input(lobsterDAO, governance, r),
    )

    o = oproxy.address
    ImmutableAdminUpgradeableBeaconProxy.remove(oproxy)  # otw direct cast not work

    orentable = ORentable.at(o, dev)

    r.setORentable(lobsterDAO, orentable)

    # WToken
    wproxy = ImmutableAdminUpgradeableBeaconProxy.deploy(
        wbeacon,
        proxyAdmin,
        wrentableLogic.initialize.encode_input(lobsterDAO, governance, r),
    )

    w = wproxy.address
    ImmutableAdminUpgradeableBeaconProxy.remove(wproxy)  # otw direct cast not work

    wrentable = WRentable.at(w, dev)

    r.setWRentable(lobsterDAO, wrentable)

    click.echo(
        f"""
             ---- LobsterDAO ---- 
     LobsterDAO (LOBS): {lobsterDAO}
                 OLOBS: {orentable.address}
                 WLOBS: {wrentable.address}
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
