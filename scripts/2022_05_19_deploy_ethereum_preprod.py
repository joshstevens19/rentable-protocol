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
    governance = dev
    operator = dev
    feeCollector = dev
    network.gas_price("10 gwei")

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

    # deploy logic
    landAddress = "0xF87E31492Faf9A91B02Ee0dEAAd50d51d56D5d4d"
    eth = "0x0000000000000000000000000000000000000000"

    proxyAdmin = ProxyAdmin.deploy()
    rLogic = Rentable.deploy(governance, operator)
    rLogic.SCRAM()

    proxy = ImmutableAdminTransparentUpgradeableProxy.deploy(
        rLogic, proxyAdmin, rLogic.initialize.encode_input(governance, operator)
    )

    r = proxy.address
    ImmutableAdminTransparentUpgradeableProxy.remove(proxy)

    r = Rentable.at(r, dev)

    assert proxyAdmin.getProxyImplementation(r) == rLogic.address

    orentableLogic = ORentable.deploy(landAddress, eth, eth)
    obeacon = UpgradeableBeacon.deploy(orentableLogic)

    wrentableLogic = WRentable.deploy(
        landAddress,
        eth,
        eth,
    )
    wbeacon = UpgradeableBeacon.deploy(wrentableLogic)

    simpleWalletLogic = SimpleWallet.deploy(
        r,
        eth,
    )
    simpleWalletBeacon = UpgradeableBeacon.deploy(
        simpleWalletLogic,
    )
    walletFactory = WalletFactory.deploy(simpleWalletBeacon)

    r.setWalletFactory(walletFactory)

    r.enablePaymentToken(eth)
    r.setFeeCollector(feeCollector)

    click.echo(
        f"""
    Rentable Deployment Parameters
                --- Roles ---
              Deployer: {dev.address}
            Governance: {governance}
              Operator: {operator}
          FeeCollector: {feeCollector}
            ProxyAdmin: {proxyAdmin.address}
                -------------
             --- Tokenization ---
                OLogic: {orentableLogic.address}
               OBeacon: {obeacon.address}
                WLogic: {wrentableLogic.address}
               WBeacon: {wbeacon.address}
             --------------------
             --- Wallet Logic ---   
     SimpleWalletLogic: {simpleWalletLogic.address}
    SimpleWalletBeacon: {simpleWalletBeacon.address}
         WalletFactory: {walletFactory.address}
             --------------------
                 --- Core ---
              Rentable: {r.address}
         RentableLogic: {rLogic.address}
                 ------------
    """
    )

    # Setup LAND

    # OToken
    oproxy = ImmutableAdminUpgradeableBeaconProxy.deploy(
        obeacon,
        proxyAdmin,
        orentableLogic.initialize.encode_input(landAddress, governance, r),
    )

    o = oproxy.address
    ImmutableAdminUpgradeableBeaconProxy.remove(oproxy)  # otw direct cast not work

    orentable = ORentable.at(o, dev)

    r.setORentable(landAddress, orentable)

    # WToken
    wproxy = ImmutableAdminUpgradeableBeaconProxy.deploy(
        wbeacon,
        proxyAdmin,
        wrentableLogic.initialize.encode_input(landAddress, governance, r),
    )

    w = wproxy.address
    ImmutableAdminUpgradeableBeaconProxy.remove(wproxy)  # otw direct cast not work

    wrentable = WRentable.at(w, dev)

    r.setWRentable(landAddress, wrentable)

    # Library
    dcllib = DecentralandCollectionLibrary.deploy()
    r.setLibrary(landAddress, dcllib)

    click.echo(
        f"""
             ---- Decentraland ---- 
   Decentraland (LAND): {landAddress}
                 OLand: {orentable.address}
                 WLand: {wrentable.address}
               Library: {dcllib.address}
             ----------------------
         """
    )

    # Enable MANA, USDC payment
    usdc = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    r.enablePaymentToken(usdc)

    mana = "0x0F5D2fB29fb7d3CFeE444a200298f468908cC942"
    r.enablePaymentToken(mana)

    # Setup Meebits

    meebits = "0x7Bd29408f11D2bFC23c34f18275bBf23bB716Bc7"

    # OToken
    oproxy = ImmutableAdminUpgradeableBeaconProxy.deploy(
        obeacon,
        proxyAdmin,
        orentableLogic.initialize.encode_input(meebits, governance, r),
    )

    o = oproxy.address
    ImmutableAdminUpgradeableBeaconProxy.remove(oproxy)  # otw direct cast not work

    orentable = ORentable.at(o, dev)

    r.setORentable(meebits, orentable)

    # WToken
    wproxy = ImmutableAdminUpgradeableBeaconProxy.deploy(
        wbeacon,
        proxyAdmin,
        wrentableLogic.initialize.encode_input(meebits, governance, r),
    )

    w = wproxy.address
    ImmutableAdminUpgradeableBeaconProxy.remove(wproxy)  # otw direct cast not work

    wrentable = WRentable.at(w, dev)

    r.setWRentable(meebits, wrentable)

    click.echo(
        f"""
                ---- Meebits ---- 
               Meebits: {meebits}
              OMeebits: {orentable.address}
              WMeebits: {wrentable.address}
                -----------------
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
