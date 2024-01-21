@echo off
pyinstaller --specpath .\export --distpath .\export\dist --workpath .\export\build --name "Minecraft Server Launcher" --onefile --clean main.py
pause