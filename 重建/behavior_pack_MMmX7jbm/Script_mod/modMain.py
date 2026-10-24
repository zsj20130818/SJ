# -*- coding: utf-8 -*-
import mod.server.extraServerApi as serverApi
from mod.common.mod import Mod

MOD_NAME = "GhjdsMod"
MOD_VERSION = "1.0.0"
SERVER_SYSTEM_NAME = "GhjdsServerSystem"
SERVER_SYSTEM_CLS = "Script_mod.GhjdsServerSystem.GhjdsServerSystem"


@Mod.Binding(name=MOD_NAME, version=MOD_VERSION)
class GhjdsMod(object):

    @Mod.InitServer()
    def InitServer(self):
        serverApi.RegisterSystem(MOD_NAME, SERVER_SYSTEM_NAME, SERVER_SYSTEM_CLS)
        print "[GhjdsMod] InitServer done, system registered"

    @Mod.DestroyServer()
    def DestroyServer(self):
        print "[GhjdsMod] DestroyServer"


# 兼容旧式显式调用（如果引擎或你的工具链调 register()）
def register():
    serverApi.RegisterSystem(MOD_NAME, SERVER_SYSTEM_NAME, SERVER_SYSTEM_CLS)


def unregister():
    pass