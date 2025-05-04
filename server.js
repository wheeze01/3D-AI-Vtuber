const WebSocket = require('ws');
const http = require('http');
const fs = require('fs');
const path = require('path');

// HTTP 서버 생성 (8080 포트)
const server = http.createServer((req, res) => {
    const filePath = path.join(__dirname, 'index.html');
    fs.readFile(filePath, (err, data) => {
        if (err) {
            res.writeHead(500);
            res.end('Error loading index.html');
            return;
        }
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end(data);
    });
});

server.listen(8080, () => {
    console.log('HTTP server running on http://localhost:8080');
});

// WebSocket 서버 생성 (8081 포트)
const wss = new WebSocket.Server({ port: 19190 });

wss.on('connection', (ws) => {
    console.log('A client connected to WebSocket server!');

    // 1을 반복적으로 보내기 (5초마다 1을 전송)
    const interval = setInterval(() => {
        const message = "Smile/Hello"
        
        // WebSocket을 통해 Warudo로 메시지 전송
        ws.send(message, (err) => {
            if (err) {
                console.log('Error sending message:', err);
            } else {
                console.log('메시지를 보냈다');
            }
        });
    }, 10000); // 5초마다 반복

    // 클라이언트와 연결이 끊어지면 반복 전송 중단
    ws.on('close', () => {
        clearInterval(interval);
        console.log('Client disconnected, stopped sending messages.');
    });
});
