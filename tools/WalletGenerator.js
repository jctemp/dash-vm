const Filesystem = require('fs').promises;
const { Wallet } = require('@dashevo/wallet-lib');

async function generateHDPrivateKeys(network, name) {
    const wallet = new Wallet({ name ,network , offlineMode: true });
    const account = await wallet.getAccount();

    const derivedPrivateKey = account.identities.getIdentityHDKeyByIndex(0, 0);
    const hdPrivateKey = wallet.exportWallet('HDPrivateKey');

    await wallet.disconnect();

    return {
        hdPrivateKey,
        derivedPrivateKey,
    };
}

async function main() {

    const network = "devnet";

    const { hdPrivateKey: dpns_HDPrivateKey, derivedPrivateKey: dpns_DerivedPK } = await generateHDPrivateKeys(network, "dpns");
    const { hdPrivateKey: dashpay_HDPrivateKey, derivedPrivateKey: dashpay_DerivedPK } = await generateHDPrivateKeys(network, "dashpay");
    const { hdPrivateKey: feature_flags_HDPrivateKey, derivedPrivateKey: feature_flags_DerivedPK } = await generateHDPrivateKeys(network, "featureFlags");
    const { hdPrivateKey: mn_reward_shares_HDPrivateKey, derivedPrivateKey: mn_reward_shares_DerivedPK } = await generateHDPrivateKeys(network, "mnRewardShares");

    objectJson = {
        "dpns": {
            "public": dpns_DerivedPK.privateKey.toPublicKey().toString(),
            "private": dpns_HDPrivateKey.toString()
        },
        "dashpay": {
            "public": dashpay_DerivedPK.privateKey.toPublicKey().toString(),
            "private": dashpay_HDPrivateKey.toString()
        },
        "featureFlags": {
            "public": feature_flags_DerivedPK.privateKey.toPublicKey().toString(),
            "private": feature_flags_HDPrivateKey.toString()
        },
        "mnRewardShares": {
            "public": mn_reward_shares_DerivedPK.privateKey.toPublicKey().toString(),
            "private": mn_reward_shares_HDPrivateKey.toString()
        }
    };

    Filesystem.writeFile("./Keys.json", JSON.stringify(objectJson));
}

main().catch(console.error);

