if __name__ == "__main__":
    from argparse import ArgumentParser
    from os import getcwd, makedirs, path
    from time import time

    from src import console
    from src.config import default_xmx
    from src.software import softwares

    start_time = time()

    with open(path.join(path.dirname(__file__), "version.txt"), "r") as f:
        VERSION = f.read()

    parser = ArgumentParser(
        prog="Minecraft Server Launcher",
        description="Create and launch minecraft server."
    )
    parser.add_argument("name")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s " + VERSION)
    parser.add_argument("-s", "--software", required=True)
    parser.add_argument("--path", default=None, help="Default: Current working directory")
    parser.add_argument("--game-version", default=None, help="Default: Latest")
    parser.add_argument("--papermc-build", default=-1, type=int, help="Default: Latest")
    parser.add_argument("--velocity-version", help="Default: Latest")
    parser.add_argument("--fabric-loader-version", help="Default: Latest")
    parser.add_argument("--fabric-installer-version", help="Default: Latest")
    parser.add_argument("--forge-loader-version", help="Default: Recommended (if none, latest).")
    parser.add_argument("--forge-keep-installer", action="store_true")
    parser.add_argument("--xms", type=int)
    parser.add_argument("--xmx", default=default_xmx, type=int)
    parser.add_argument("-e", "--agree-eula", action="store_true", help="https://www.minecraft.net/eula")
    parser.add_argument("-l", "--launch", action="store_true")

    args = parser.parse_args()

    if args.path is None:
        args.path = path.join(getcwd(), args.name)
        makedirs(args.path, exist_ok=True)
    softwares[args.software.lower()].cli(args, args.path)

    console.print(f"It took {time() - start_time:.3f}s!")