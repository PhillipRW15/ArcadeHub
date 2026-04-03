const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

// Serve the arcade files
app.use(express.static(path.join(__dirname)));

const players = {}; // stores socket.id -> { pId: 1|2, x, y, damage, stocks, isShielding, dir }

let matchActive = false;

io.on('connection', (socket) => {
    console.log('User connected:', socket.id);

    // Assign Player ID (1 or 2)
    let pId = null;
    const connectedPIds = Object.values(players).map(p => p.pId);
    if (!connectedPIds.includes(1)) pId = 1;
    else if (!connectedPIds.includes(2)) pId = 2;

    if (pId) {
        players[socket.id] = { pId, x: pId === 1 ? 400 : 940, y: 600, damage: 0, stocks: 3, isShielding: false, dir: pId === 1 ? 1 : -1, isDead: false };
        socket.emit('player-assigned', { pId, matchActive });
        io.emit('player-update', players); 
    } else {
        socket.emit('full', 'Game is full');
    }

    // Handle state updates from clients
    socket.on('sync', (data) => {
        if (players[socket.id]) {
            players[socket.id] = { ...players[socket.id], ...data };
            socket.broadcast.emit('player-sync', { pId: players[socket.id].pId, ...data });
        }
    });

    // Handle attacks (broadcast to trigger collision on both sides)
    socket.on('attack', (data) => {
        io.emit('attack-event', data);
    });

    // Handle match start
    socket.on('start-match', () => {
        matchActive = true;
        io.emit('match-start');
    });

    // Handle match restart authoritatively
    socket.on('restart-match', () => {
        matchActive = true;
        for (let key in players) {
            players[key].damage = 0;
            players[key].stocks = 3;
            players[key].isDead = false;
        }
        io.emit('match-reset', players);
    });

    // Handle player death
    socket.on('player-died', (data) => {
        if (players[socket.id]) {
            players[socket.id].stocks = data.stocks;
            players[socket.id].damage = 0;
            io.emit('player-update', players);
        }
    });

    socket.on('disconnect', () => {
        console.log('User disconnected:', socket.id);
        delete players[socket.id];
        // If everyone leaves, reset match state
        if (Object.keys(players).length === 0) {
            matchActive = false;
        }
        io.emit('player-update', players);
    });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`\n--------------------------------------------`);
    console.log(`SQUARE SMASH ONLINE SERVER`);
    console.log(`Running on: http://localhost:${PORT}`);
    console.log(`--------------------------------------------\n`);
});
