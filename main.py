if __name__ == "__main__":
    from src import config, console
    from src.software import softwares

    console.print(f"Server Software (Default: {config.default_software}):\n")
    console.get_response_dict(softwares, tuple(softwares.keys()).index(config.default_software) + 1).cli()