const express = require('express');
const app = express();

const http = require('http');
const server = http.createServer(app);
const {Server} = require('socket.io');
const io = new Server(server);
const db = require('../common/database');

io.on('connection', (socket) => {
    console.log(`Client ${socket.id} connected from ${socket.handshake.address}`);
    socket.on('disconnect', () => {
        console.log(`Client ${socket.id} disconnected from ${socket.handshake.address}`);
    });

    socket.on('login', (data) => {
        var users = JSON.parse(db.readDb());
        var existing = false;
        users.map((item) => {
            if(item.email === data.email) existing = true;
        });
        if(existing) socket.emit('login', {status: true, message: "Login successfully"});
        else socket.emit('login', {status: false, message: "Email or password is incorrect"});
    })

    socket.on('register',(data) => {
        var users = JSON.parse(db.readDb());
        var existing = false;
        users.map((item) => {
            if(item.email === data.email) existing = true;
        });
        if(existing) socket.emit('register', {status: false, message: "Email is existing"});
        else {
            users.push(data);
            db.writeDb(users);
            socket.emit('register', {status: true, message: "Create account successfully"});
        }
    })

    socket.on('message',(data) => {
        setTimeout(()=>{
            socket.emit('message',{status: true, message:"天気がいいから、散歩しましょう！！！！"});
        },5000);
    })
});

module.exports = server;