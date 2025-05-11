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

    let combinedMessage = "Confused/Joy";   // 기본값

    // 💬 클라이언트로부터 메시지 수신 처리
    ws.on('message', (message) => {
        try {
            const jsonData = JSON.parse(message.toString());
            const gesture = jsonData.gesture || "None";
            const expression = jsonData.expression || "None";

            combinedMessage = `${gesture}/${expression}`;
            console.log('📩 Received JSON:', jsonData);
            console.log('🧩 Combined:', combinedMessage);
        } catch (error) {
            console.error('❌ JSON parsing error:', error);
        }
    });

    const interval = setInterval(() => {
        // WebSocket을 통해 Warudo로 메시지 전송
        ws.send(combinedMessage, (err) => {
            if (err) {
                console.log('Error sending message:', err);
            } else {
                console.log(combinedMessage, '메시지를 보냈다');
            }
        });
    }, 10000); // 10초마다 반복

    // 클라이언트와 연결이 끊어지면 반복 전송 중단
    ws.on('close', () => {
        clearInterval(interval);
        console.log('Client disconnected, stopped sending messages.');
    });
});
