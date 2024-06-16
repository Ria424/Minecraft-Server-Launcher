@echo off
pyinstaller --noconfirm --clean --onefile --console ^
    --specpath=.\export ^
    --distpath=.\export\dist ^
    --workpath=.\export\build ^
    --add-data=..\version.txt:. ^
    --name="minecraft_server_launcher" ^
    --icon="NONE" ^
    main.py
pause