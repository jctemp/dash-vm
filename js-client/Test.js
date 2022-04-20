const Dash = require('dash');

const clientOpts = {
    network: "devnet",
    wallet: {
        mnemonic: "wear achieve pledge eager uncover risk ozone shrug pulse prevent hurry carry ostrich jelly damage cat act cradle dismiss forward puppy vacant yellow skin", // this indicates that we want a new wallet to be generated
    },
};

const client = new Dash.Client(clientOpts);

const createWallet = async () => {
    const account = await client.getWalletAccount();

    const mnemonic = client.wallet.exportWallet();
    const address = account.getUnusedAddress();
    console.log('Mnemonic:', mnemonic);
    console.log('Unused address:', address.address);
};

createWallet()
    .catch((e) => console.error('Something went wrong:\n', e))
    .finally(() => client.disconnect());

// Handle wallet async errors
client.on('error', (error, context) => {
    console.error(`Client error: ${error.name}`);
    console.error(context);
});