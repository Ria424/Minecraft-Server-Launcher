from typing import OrderedDict

from . import fabric, forge, paper_mc, vanilla

softwares = OrderedDict(
    Vanilla=vanilla,
    PaperMC=paper_mc,
    Fabric=fabric,
    Forge=forge
)
