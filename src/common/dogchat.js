module.exports = async (message) => {
    var spawn = require('child_process').spawn;
    var result;
    var process = spawn('python', [
        `./dogchat.py`,
        message
    ]);
    await process.stdout.on('data', function(data) {
        result +=data.toString();
        console.log(data.toString());
    });

    await process.on('close', function(code) {
        console.log(result);
    });
    
    return result;
}

