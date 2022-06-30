import json

from brownie import accounts, network, Rentable, history, project, interface

address0 = "0x0000000000000000000000000000000000000000"

oz = project.load("./lib/openzeppelin-contracts")
UpgradeableBeacon = oz.UpgradeableBeacon
ProxyAdmin = oz.ProxyAdmin


def main():
    dev = accounts.load("rentable-deployer")
    accounts.default = dev
    network.gas_price("77 gwei")

    deployment = json.load(open("deployments/ethereum-mainnet.json"))
    print(f"Deployed contracts: {len(deployment)}")

    expectedGovernance = "0xC08618375bb20ac1C4BB806Baa027a4362156fE6"
    expectedAdmin = "0xdb246e57c401792Fd272314ce666f5dB07E89e67"

    # 1. checking governance proxy admin
    proxyAdmin = ProxyAdmin.at(deployment["ProxyAdmin"])

    print(f"ProxyAdmin owner: {proxyAdmin.owner()}")
    print(f"ProxyAdmin expected owner: {expectedGovernance}")

    if proxyAdmin.owner() != expectedGovernance:
        print("NOT OK! Fixing...")
        proxyAdmin.transferOwnership(expectedGovernance)
    else:
        print("OK!")

    # 2. checking ownable contracts
    ownableContractsList = [
        "OBeacon",
        "WBeacon",
        "OLogic",
        "WLogic",
        "OLand",
        "WLand",
        "OMeebits",
        "WMeebits",
        "OLobs",
        "WLobs",
        "SimpleWalletBeacon",
        "WalletFactory",
    ]

    ownableContracts = {k: deployment[k] for k in ownableContractsList}

    print(f"Checking ownable contracts: {len(ownableContracts)}")

    for contractName, contractAddress in ownableContracts.items():
        contract = interface.IOwnable(contractAddress)
        contractOwner = contract.owner()
        print(f"{contractName} owner: {contractOwner}")
        print(f"{contractName} expected owner: {expectedGovernance}")
        if contractOwner != expectedGovernance and contractOwner != address0:
            print("NOT OK! Fixing...")
            contract.transferOwnership(expectedGovernance)
        else:
            print("OK!")

    # 3. check adminables contracts
    adminableContractsList = [
        "OLand",
        "WLand",
        "OMeebits",
        "WMeebits",
        "OLobs",
        "WLobs",
        "Rentable",
    ]

    adminableContracts = {k: deployment[k] for k in adminableContractsList}

    print(f"Checking adminable contracts: {len(adminableContracts)}")

    for contractName, contractAddress in adminableContracts.items():
        contractAdmin = proxyAdmin.getProxyAdmin(
            contractAddress
        )  ## todo use proxyadmin to get the effective admin
        print(f"{contractName} owner: {contractAdmin}")
        print(f"{contractName} expected admin: {expectedAdmin}")
        if contractOwner != expectedAdmin and contractAdmin != address0:
            print("OK!")
        else:
            print("NOT OK!")

    # 4. check rentable governance
    print("Checking Rentable governance")

    rentableContractList = ["Rentable", "RentableLogic"]
    rentableContracts = {k: deployment[k] for k in rentableContractList}

    for contractName, contractAddress in rentableContracts.items():
        contract = Rentable.at(contractAddress)
        contractOwner = contract.getGovernance()
        print(f"{contractName} owner: {contractOwner}")
        print(f"{contractName} expected owner: {expectedGovernance}")
        if contractOwner != expectedGovernance and contractOwner != address0:
            print("NOT OK! Fixing...")
            contract.setGovernance(expectedGovernance)
            print(f"Remember to accept it with {expectedGovernance}")
        else:
            print("OK!")

    totalGasUsed = 0
    for tx in history:
        totalGasUsed += tx.gas_used

    print(f"Total gas used {totalGasUsed}")
