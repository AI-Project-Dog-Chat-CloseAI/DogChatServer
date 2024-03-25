const fs = require('fs');
const filename = "sentences.txt";

class LString {
    constructor() {
        this.total = 0;
        this.successors = {};
    }

    put(word) {
        this.successors[word] = (this.successors[word] || 0) + 1;
        this.total++;
    }

    getRandom() {
        let ran = Math.floor(Math.random() * this.total);
        for (let key in this.successors) {
            if (ran < this.successors[key]) {
                return key;
            } else {
                ran -= this.successors[key];
            }
        }
    }
}

let coupleWords = {};

function load(phrases) {
    const data = fs.readFileSync(phrases, 'utf8').split('\n');
    for (let line of data) {
        addMessage(line);
    }
}

function addMessage(message) {
    message = message.replace(/[^\p{L}\p{N}\s']/gu, '').toLowerCase().trim();
    const words = message.split(' ');
    for (let i = 2; i < words.length; i++) {
        const key = words[i - 2] + ' ' + words[i - 1];
        if (!coupleWords[key]) {
            coupleWords[key] = new LString();
        }
        coupleWords[key].put(words[i]);
    }
    const lastKey = words[words.length - 2] + ' ' + words[words.length - 1];
    if (!coupleWords[lastKey]) {
        coupleWords[lastKey] = new LString();
    }
    coupleWords[lastKey].put('');
}

function generate(message) {
    let result = [];
    while (result.length < message.length || result.length > 100) {
        result = [];
        const keys = Object.keys(coupleWords);
        const key = keys[Math.floor(Math.random() * keys.length)];
        result.push(...key.split(' '));
        let lastWord = result[result.length - 1];
        while (lastWord) {
            lastWord = coupleWords[result[result.length - 2] + ' ' + lastWord].getRandom();
            result.push(lastWord);
        }
    }
    return result.join(' ');
}

module.exports = (message) => {
    load(filename);
    fs.appendFileSync(filename,'\n'+ message, 'utf8');
    var result = generate(message);
    return result;
}

