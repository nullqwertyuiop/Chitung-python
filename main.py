from graia.ariadne.app import Ariadne
from graia.ariadne.model import MiraiSession
from graia.saya import Saya
from graia.saya.builtins.broadcast import BroadcastBehaviour
from graia.scheduler import GraiaScheduler
from graia.scheduler.saya import GraiaSchedulerBehaviour

app = Ariadne(
    MiraiSession(
        host="http://localhost:8080",
        verify_key="verifyKey",
        account=1234567890,
    )
)

saya = app.create(Saya)
app.create(GraiaScheduler)
saya.install_behaviours(
    app.create(BroadcastBehaviour), app.create(GraiaSchedulerBehaviour)
)

with saya.module_context():
    saya.require("chitung")

app.launch_blocking()
