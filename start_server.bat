@echo off
echo [SERVER] Starting Tibia-like server...
python -m server.server --host 127.0.0.1 --port 8765
pause
