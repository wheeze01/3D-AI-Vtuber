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

    // 💬 클라이언트로부터 메시지 수신 처리
    ws.on('message', (message) => {
        try {
            const jsonData = JSON.parse(message.toString());
            const gesture = jsonData.gesture || "None"; // 제스처
            const expression = jsonData.expression || "None"; // 표정

            const combinedMessage = `${gesture}/${expression}`;
            console.log('📩 Received JSON:', jsonData);
            console.log('🧩 Combined:', combinedMessage);

            // 🔥 연결된 모든 클라이언트(Warudo 포함)에게 전송
            wss.clients.forEach(client => {
                if (client.readyState === WebSocket.OPEN) {
                    client.send(combinedMessage, (err) => {
                        if (err) console.log('❌ Error sending:', err);
                        else console.log('📤 Broadcasted:', combinedMessage);
                    });
                }
            });

        } catch (error) {
            console.error('❌ JSON parsing error:', error);
        }
    });

    // 클라이언트와 연결이 끊어지면 반복 전송 중단
    ws.on('close', () => {
        console.log('Client disconnected, stopped sending messages.');
    });
});