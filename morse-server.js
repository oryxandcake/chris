const WebSocket = require('ws');

const PORT = process.env.PORT || 8080;
const server = new WebSocket.Server({ port: PORT });

const clients = new Map(); // Map of userId -> WebSocket

console.log(`Morse Code WebSocket Server running on port ${PORT}`);

server.on('connection', (ws) => {
    let userId = null;

    ws.on('message', (message) => {
        try {
            const data = JSON.parse(message);

            switch (data.type) {
                case 'join':
                    userId = data.userId;
                    clients.set(userId, ws);
                    console.log(`User joined: ${userId} (Total: ${clients.size})`);

                    // Send current user list to the new user
                    ws.send(JSON.stringify({
                        type: 'userList',
                        users: Array.from(clients.keys())
                    }));

                    // Notify all other users about the new user
                    broadcast({
                        type: 'userJoined',
                        userId: userId
                    }, userId);
                    break;

                case 'transmitStart':
                    console.log(`${userId} started transmitting`);
                    broadcast({
                        type: 'transmitStart',
                        userId: userId
                    }, userId);
                    break;

                case 'transmitEnd':
                    console.log(`${userId} stopped transmitting`);
                    broadcast({
                        type: 'transmitEnd',
                        userId: userId
                    }, userId);
                    break;

                case 'ping':
                    // Heartbeat - just acknowledge
                    ws.send(JSON.stringify({ type: 'pong' }));
                    break;
            }
        } catch (error) {
            console.error('Error processing message:', error);
        }
    });

    ws.on('close', () => {
        if (userId) {
            clients.delete(userId);
            console.log(`User left: ${userId} (Total: ${clients.size})`);

            // Notify all users about the disconnection
            broadcast({
                type: 'userLeft',
                userId: userId
            });
        }
    });

    ws.on('error', (error) => {
        console.error('WebSocket error:', error);
    });
});

function broadcast(message, excludeUserId = null) {
    const messageStr = JSON.stringify(message);
    clients.forEach((client, id) => {
        if (id !== excludeUserId && client.readyState === WebSocket.OPEN) {
            client.send(messageStr);
        }
    });
}

// Handle server shutdown gracefully
process.on('SIGINT', () => {
    console.log('\nShutting down server...');
    server.close(() => {
        console.log('Server closed');
        process.exit(0);
    });
});
