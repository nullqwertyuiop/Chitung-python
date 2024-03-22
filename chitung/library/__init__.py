import kayaku
from creart import it
from launart import Launart


def launch():
    kayaku.initialize({"{**}": "./config/{**}"})

    from chitung.library.model.config import ChitungConfig
    from chitung.library.service import (
        ConfigService,
        ChitungService,
        MessageCacheService,
        ModuleService,
        ProtocolService,
        SessionService,
    )

    kayaku.create(ChitungConfig)

    mgr = it(Launart)
    mgr.add_component(MessageCacheService())
    mgr.add_component(ConfigService())
    mgr.add_component(ModuleService())
    mgr.add_component(ProtocolService())
    mgr.add_component(SessionService())
    mgr.add_component(ChitungService())
    mgr.launch_blocking()
