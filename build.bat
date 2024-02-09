@echo off
pyinstaller -F -n "Minecraft Server Launcher" -i "NONE" --specpath .\export --distpath .\export\dist --workpath .\export\build --clean main.py
pause