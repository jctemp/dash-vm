const Filesystem = require('fs').promises;
const BlsSignatures = require('bls-signatures');

const { PrivateKey } = require('@dashevo/dashcore-lib');
const { Wallet } = require('@dashevo/wallet-lib');

const networkType = {
    devnet: "devnet",
    testnet: "testnet"
};

const llmqType = {
    devnet: 101,
    testnet: 4,
    mainnet: 4,
    regtest: 100,
}

/**
 * @param {string} name
 * @param {networkType} network 
 */
async function generateHDPrivateKeys(network, name) {
    const wallet = new Wallet({ name, network, offlineMode: true });
    const account = await wallet.getAccount();

    const derivedPrivateKey = account.identities.getIdentityHDKeyByIndex(0, 0);
    const hdPrivateKey = wallet.exportWallet('HDPrivateKey');

    await wallet.disconnect();

    return {
        hdPrivateKey,
        derivedPrivateKey,
    };
}

/**
 * @param {networkType} network 
 */
function generateFaucet(network) {
    const faucetPrivateKey = new PrivateKey(undefined, network);

    faucetJson = {
        address: faucetPrivateKey.toAddress(network).toString(),
        privateKey: faucetPrivateKey.toWIF()
    };

    Filesystem.writeFile("./faucet.json", JSON.stringify(faucetJson));
}

/**
 * @param {networkType} network 
 */
function generateSporks(network) {
    const sporkPrivateKey = new PrivateKey(undefined, network);

    sporkJson = {
        address: sporkPrivateKey.toAddress(network).toString(),
        privateKey: sporkPrivateKey.toWIF()
    };

    Filesystem.writeFile("./spork.json", JSON.stringify(sporkJson));
}

/**
 * @param {networkType} network 
 */
async function generateHDWallets(network) {
    const { hdPrivateKey: dpns_HDPrivateKey, derivedPrivateKey: dpns_DerivedPK } = await generateHDPrivateKeys(network, "dpns");
    const { hdPrivateKey: dashpay_HDPrivateKey, derivedPrivateKey: dashpay_DerivedPK } = await generateHDPrivateKeys(network, "dashpay");
    const { hdPrivateKey: feature_flags_HDPrivateKey, derivedPrivateKey: feature_flags_DerivedPK } = await generateHDPrivateKeys(network, "featureFlags");
    const { hdPrivateKey: mn_reward_shares_HDPrivateKey, derivedPrivateKey: mn_reward_shares_DerivedPK } = await generateHDPrivateKeys(network, "mnRewardShares");

    hdWalletsJson = {
        "dpns": {
            "publicKey": dpns_DerivedPK.privateKey.toPublicKey().toString(),
            "privateKey": dpns_HDPrivateKey.toString()
        },
        "dashpay": {
            "publicKey": dashpay_DerivedPK.privateKey.toPublicKey().toString(),
            "privateKey": dashpay_HDPrivateKey.toString()
        },
        "featureFlags": {
            "publicKey": feature_flags_DerivedPK.privateKey.toPublicKey().toString(),
            "privateKey": feature_flags_HDPrivateKey.toString()
        },
        "mnRewardShares": {
            "publicKey": mn_reward_shares_DerivedPK.privateKey.toPublicKey().toString(),
            "privateKey": mn_reward_shares_HDPrivateKey.toString()
        }
    };

    Filesystem.writeFile("./hdWallets.json", JSON.stringify(hdWalletsJson));
}

/**
 * 
 */
async function generateBLSKeys() {
    const blsSignatures = await BlsSignatures();
    const { PrivateKey: BlsPrivateKey } = blsSignatures;

    const operator = {
        publicKey: Buffer.from(operatorPublicKey.serialize()).toString('hex'),
        privateKey: Buffer.from(operatorPrivateKey.serialize()).toString('hex')
    };
}

/**
 * @param {networkType} network 
 */
function generateAddress(network) {
    const addressPrivateKey = new PrivateKey(undefined, network);
    const addressKeyPair = {
        address: collateralPrivateKey.toAddress(network).toString(),
        privateKey: ollateralPrivateKey.toWIF()
    };
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

const currentNetwork = networkType.devnet;


generateFaucet(currentNetwork);

// generate
// generateToAddress
// getBestBlockHash
// getBestChainLock


console.log(currentNetwork);


