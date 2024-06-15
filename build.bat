@echo off
pyinstaller --noconfirm --clean --onefile --console ^
    --specpath .\export ^
    --distpath .\export\dist ^
    --workpath .\export\build ^
    --name "Minecraft Server Launcher" ^
    --icon "NONE" ^
    main.py
pause