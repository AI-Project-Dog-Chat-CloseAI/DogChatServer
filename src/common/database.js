const config = require('config');
const fs = require('fs');

const readDb = () => {
    return fs.readFileSync(config.get('filedb.db'), 'utf-8');
}

const writeDb = (data) => {
    fs.writeFileSync(config.get('filedb.db'), JSON.stringify(data));
}

module.exports = {
    readDb,
    writeDb
}