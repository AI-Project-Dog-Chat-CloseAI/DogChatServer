require('dotenv').config();
module.exports = {
    app : require('./app'),
    filedb : require('./db'),
    email : require('./email'),
}