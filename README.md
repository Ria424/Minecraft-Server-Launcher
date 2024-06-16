# Minecraft Server Launcher
It allows you to open Minecraft servers easily and quickly.

## Supported Servers
- [Vanilla](https://www.minecraft.net)
- All PaperMC projects ([Paper](https://papermc.io/software/paper), [Velocity](https://papermc.io/software/velocity), [Waterfall](https://papermc.io/software/waterfall), [Folia](https://papermc.io/software/folia) etc.)
- [Fabric](https://fabricmc.net)
- [Forge](https://files.minecraftforge.net/net/minecraftforge/forge)

### To Be Supported
- Spigot
- Purpur

## How To Run Using Python
### From Source
1. Install [Python](https://www.python.org/downloads)
2. Install latest version of [Beautiful Soup](https://pypi.org/project/beautifulsoup4) (html parser)
3. Install latest version of [orjson](https://pypi.org/project/orjson) (basically fast json parser)
4. Download source code
5. Run `main.py` from source code

## How To Compile
1. Install [Python](https://www.python.org/downloads)
2. Install latest version of [Pyinstaller](https://pypi.org/project/pyinstaller)
3. Install latest version of [Beautiful Soup](https://pypi.org/project/beautifulsoup4) (html parser)
4. Install latest version of [orjson](https://pypi.org/project/orjson) (basically fast json parser)
5. Download source code
6. Run `build.bat` from source code
7. Done! Compiled to file `export/dist/minecraft_server_launcher.exe`

## TODO
- JDK가 설치되었는지 확인하고 없으면 다운로드
- GUI