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
    console.log('✅ A client connected to WebSocket server!');

    let combinedMessage = None;

    // 💬 클라이언트로부터 메시지 수신 처리
    ws.on('message', (message) => {
        try {
            const jsonData = JSON.parse(message.toString());
            const gesture = jsonData.gesture || "None";
            const expression = jsonData.expression || "None";

            const combinedMessage = `${gesture}/${expression}`;
            console.log('📩 Received JSON:', jsonData);
            console.log('🧩 Combined:', combinedMessage);

            // 👉 받은 즉시 Warudo에 전송
            ws.send(combinedMessage, (err) => {
                if (err) {
                    console.log('❌ Error sending message:', err);
                } else {
                    console.log('📤 Sent to Warudo:', combinedMessage);
                }
            });

        } catch (error) {
            console.error('❌ JSON parsing error:', error);
        }
    });

    // 클라이언트와 연결이 끊어
    ws.on('close', () => {
        console.log('❎ Client disconnected.');
    });
});
