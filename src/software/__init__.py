from typing import Any

from . import fabric, forge, paper_mc, vanilla

softwares: dict[str, Any] = {
    "vanilla": vanilla,
    "fabric": fabric,
    "forge": forge
}

paper_mc_connection = paper_mc.connect()
for project in paper_mc.get_projects(paper_mc_connection):
    softwares[project] = paper_mc
paper_mc_connection.close()