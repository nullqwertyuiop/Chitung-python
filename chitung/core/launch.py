from creart import it
from graia.broadcast import Broadcast

from chitung.core._ctx import launch_manager
from chitung.core.service.bank import ChitungServiceBank
from chitung.core.service.essential import ChitungServiceEssential
from chitung.core.service.mpse import MPSEService
from chitung.core.service.session import ChitungServiceSession


def launch():
    mgr = launch_manager.get()
    mgr.add_launchable(ChitungServiceEssential())
    mgr.add_launchable(ChitungServiceSession())
    mgr.add_launchable(MPSEService())
    mgr.add_launchable(ChitungServiceBank())
    mgr.launch_blocking(loop=it(Broadcast).loop)
