# 🕹️ Multiplayer Tic Tac Toe (Python + Pygame + Socket)

A networked two-player Tic Tac Toe game built using Python. The game features a server-client architecture that enables real-time gameplay over a local network. The GUI is built with Pygame, and the networking is handled using Python's socket and threading libraries.

## 🔧 Features
- Real-time multiplayer gameplay
- Clean graphical interface using Pygame
- Turn-based system with win/tie detection
- Rematch option after game ends
- JSON-based communication between server and clients

## 📂 Files
- `server.py` — Runs the game server and manages player connections, moves, and rematches.
- `client.py` / `client2.py` — Launch the game interface for players. Connects to the server, sends moves, and renders the board.

## 🚀 How to Run

1. Start the server:

2. Launch two clients (either on different machines in same network or on localhost with different terminals):

3. Enter the server IP when prompted.

## 🛠️ Technologies Used
- Python
- Pygame
- Socket Programming
- Threading
- JSON

## 💡 Learnings
- Client-server communication in Python
- Real-time game development
- Thread-safe data sharing
- GUI rendering with Pygame

## 📘 Future Enhancements
- Chat feature between players
- Add game timer
- Play over the internet (not just local network)
