const fs = require('fs');
const WebSocket = require('ws');
const server = new WebSocket.Server({ port: 8080 });

const DATA_FILE = '/tmp/openagi_data.json';
const UPDATE_INTERVAL = 1000; // Time in milliseconds between updates.

let fileData = null;

const updateFileData = () => {
  fs.readFile(DATA_FILE, 'utf-8', (err, data) => {
    if (err) {
      console.error(`Error reading file: ${err}`);
    } else {
      try {
        const parsedData = JSON.parse(data);
        fileData = parsedData;
      } catch (error) {
        console.error(`Error parsing JSON: ${error}`);
      }
    }
  });
};

const sendUpdates = () => {
  if (fileData !== null) {
    server.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(JSON.stringify(fileData));
      }
    });
  }
};

server.on('connection', (socket) => {
  console.log('Client connected.');

  socket.on('close', () => {
    console.log('Client disconnected.');
  });
});

updateFileData();
setInterval(() => {
  updateFileData();
  sendUpdates();
}, UPDATE_INTERVAL);

console.log(`WebSocket server started at ws://localhost:8080`);
