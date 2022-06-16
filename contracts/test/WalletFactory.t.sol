// SPDX-License-Identifier: AGPL-3.0-only
pragma solidity >=0.8.7;

import {DSTest} from "ds-test/test.sol";
import {Vm} from "forge-std/Vm.sol";

import {TestHelper} from "./TestHelper.t.sol";

import {SimpleWallet} from "../wallet/SimpleWallet.sol";
import {WalletFactory} from "../wallet/WalletFactory.sol";

import {UpgradeableBeacon} from "@openzeppelin/contracts/proxy/beacon/UpgradeableBeacon.sol";

contract WalletFactoryTest is DSTest, TestHelper {
    Vm public constant vm = Vm(HEVM_ADDRESS);

    address owner;
    address user;

    SimpleWallet simpleWalletLogic;
    UpgradeableBeacon simpleWalletBeacon;
    WalletFactory walletFactory;

    // Events

    event WalletBeaconChanged(
        address indexed previousBeacon,
        address indexed newBeacon
    );

    function setUp() public {
        owner = getNewAddress();
        user = getNewAddress();

        vm.startPrank(owner);

        simpleWalletLogic = new SimpleWallet(owner, user);
        simpleWalletBeacon = new UpgradeableBeacon(address(simpleWalletLogic));
        walletFactory = new WalletFactory(address(simpleWalletBeacon));
    }

    function testTransferOwnership() public {
        // change owner
        // only owner
        assertEq(owner, walletFactory.owner());

        address newOwner = getNewAddress();

        switchUser(getNewAddress());

        vm.expectRevert(bytes("Ownable: caller is not the owner"));
        walletFactory.transferOwnership(newOwner);

        switchUser(owner);

        walletFactory.transferOwnership(newOwner);

        assertEq(newOwner, walletFactory.owner());
    }

    function testSetBeacon() public {
        // change beacon
        // only admin
        assertEq(address(simpleWalletBeacon), walletFactory.getBeacon());

        address newBeacon = getNewAddress();

        switchUser(getNewAddress());

        vm.expectRevert(bytes("Ownable: caller is not the owner"));
        walletFactory.setBeacon(newBeacon);

        switchUser(owner);

        // Test event emitted
        vm.expectEmit(true, true, true, true);
        emit WalletBeaconChanged(walletFactory.getBeacon(), newBeacon);
        walletFactory.setBeacon(newBeacon);

        assertEq(newBeacon, walletFactory.getBeacon());
    }

    function testCreateWallet() public {
        // test proxy props and simplewallet ones

        address walletOwner = getNewAddress();
        address walletUser = getNewAddress();

        address payable newWallet = payable(
            walletFactory.createWallet(walletOwner, walletUser)
        );

        // owner
        assertEq(walletOwner, SimpleWallet(newWallet).owner());

        // user
        assertEq(walletUser, SimpleWallet(newWallet).getUser());

        assertTrue(true);
    }
}
