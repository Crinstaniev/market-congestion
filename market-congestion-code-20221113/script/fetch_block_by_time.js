const EthDater = require('ethereum-block-by-date');
const Web3 = require('Web3');
const web3 = new Web3(new Web3.providers.HttpProvider('https://mainnet.infura.io/v3/b5502deb425f4629a1c886601e332e56'));
const fs = require('fs');

const dater = new EthDater(web3);

// console.log(process.cwd());

(async () => {
    let blocks = await dater.getEvery(
        'hours',
        '2022-04-25T00:00:00Z',
        '2022-05-05T00:00:00Z',
        1,
        true,
        false
    );

    let json = JSON.stringify(blocks);
    fs.writeFileSync(
        './data/blocks_timestamp.json',
        json,
        'utf8',
    );
    console.log('complete');
})();