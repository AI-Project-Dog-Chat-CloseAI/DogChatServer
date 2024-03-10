const express = require('express');
const app = express();
const path = require('path');
const ejs = require('ejs');
const transporter = require('../common/transporter');
const config = require('config');

const http = require('http');
const server = http.createServer(app);
const { Server } = require('socket.io');
const io = new Server(server);
const db = require('../common/database');
const jwt = require('jsonwebtoken');

app.set("views", config.get("app.view_folder"));
app.set("view engine", config.get("app.view_engine"));

io.on('connection', (socket) => {
    console.log(`Client ${socket.id} connected from ${socket.handshake.address}`);
    socket.on('disconnect', () => {
        console.log(`Client ${socket.id} disconnected from ${socket.handshake.address}`);
    });

    socket.on('login', (data) => {
        var users = JSON.parse(db.readDb());
        var existing = false;
        users.map((item) => {
            if (item.email === data.email && item.active) existing = true;
        });
        if (existing) socket.emit('login', { status: true, message: "Login successfully" });
        else socket.emit('login', { status: false, message: "Email or password is incorrect" });
    })

    socket.on('register', async (data) => {
        var users = JSON.parse(db.readDb());
        var existing = false;
        users.map((item) => {
            if (item.email === data.email) existing = true;
        });
        if (existing) socket.emit('register', { status: false, message: "Email is existing" });
        else {
            const viewPath = app.get("views");
            const token = jwt.sign({ email: data.email }, config.get('app.key'));
            const html = await ejs.renderFile(path.join(viewPath, "verify.ejs"), { email: data.email, token });
            await transporter(html, data.email);
            users.push({ ...data, active: false });
            db.writeDb(users);
            socket.emit('register', { status: true, message: "Create account successfully" });
        }
    })

    socket.on('message', (data) => {
        setTimeout(() => {
            socket.emit('message', { status: true, message: "天気がいいから、散歩しましょう！！！！" });
        }, 5000);
    })

    socket.on('active', (data) => {
        jwt.verify(data.token, config.get('app.key'), (err, data) => {
            if (err) {
                socket.emit('active', { status: false, message: "Can't active your account." });
            } else {
                var users = JSON.parse(db.readDb());
                const email = data.email;
                users.map((item) => {
                    if (item.email === email) item.active = true;
                    return item;
                });
                db.writeDb(users);
                socket.emit('active', { status: true, message: "Active your account successfully." });
            }
        })
    })
});

module.exports = server;