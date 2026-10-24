# -*- coding: utf-8 -*-
import mod.server.extraServerApi as serverApi
import random

ServerSystem = serverApi.GetServerSystemCls()


class GhjdsServerSystem(ServerSystem):

    def __init__(self, namespace, systemName):
        super(GhjdsServerSystem, self).__init__(namespace, systemName)

        # 引擎事件
        engineNs = serverApi.GetEngineNamespace()
        engineSys = serverApi.GetEngineSystemName()

        # 放置方块：正确事件是 ServerEntityTryPlaceBlockEvent
        self.ListenForEvent(engineNs, engineSys,
                            "ServerEntityTryPlaceBlockEvent", self, self.OnTryPlaceBlock)
        # 物品使用
        self.ListenForEvent(engineNs, engineSys,
                            "ServerItemUseOnEvent", self, self.OnItemUse)

        self.levelId = serverApi.GetLevelId()
        self.factory = serverApi.GetEngineCompFactory()
        self.itemComp = self.factory.CreateItem(self.levelId)
        self.blockComp = self.factory.CreateBlockInfo(self.levelId)
        self.playerComp = self.factory.CreatePlayer(self.levelId)
        self.gameComp = self.factory.CreateGame(self.levelId)

        self.is_sanctioned = False
        self.trigger_player_name = ""
        self.sanction_timer = None

        print "[GhjdsMod] GhjdsServerSystem __init__"

    # ---------- 放置方块 ----------
    def OnTryPlaceBlock(self, args):
        # 参数：entityId, fullName, x, y, z, dimensionId, face, ...
        blockName = args.get("fullName", "")
        if blockName != "ghjds:magic_dirt":
            return

        playerId = args.get("entityId", "")
        dimId = args.get("dimensionId", 0)
        x = args.get("x", 0)
        y = args.get("y", 0)
        z = args.get("z", 0)

        print "[GhjdsMod] place magic_dirt at", (x, y, z), "dim", dimId

        # 把土块替换成制裁盒子
        self.blockComp.SetBlockNew((x, y, z), {"name": "ghjds:sanction_box", "aux": 0},
                                   False, dimId)

        # 生成岩浆桶 + 32K 剑
        lava_dict = {"newItemName": "minecraft:lava_bucket", "count": 1}
        self.itemComp.SpawnItemToLevel(lava_dict, dimId, (x + 0.5, y + 1, z + 0.5))

        sword_dict = {
            "newItemName": "minecraft:diamond_sword",
            "count": 1,
            "customTips": u"§c§l制裁之刃",
            "extraData": {
                "ench": [
                    {"id": 9, "lvl": 32767},
                    {"id": 1, "lvl": 32767},
                ]
            },
        }
        self.itemComp.SpawnItemToLevel(sword_dict, dimId, (x + 0.5, y + 1, z + 0.5))

    # ---------- 物品使用 ----------
    def OnItemUse(self, args):
        itemDict = args.get("itemDict", {})
        playerId = args.get("entityId", "")
        if itemDict.get("newItemName") == "minecraft:lava_bucket":
            if not self.is_sanctioned:
                self.is_sanctioned = True
                self.ExecuteSanction(playerId)

    # ---------- 制裁启动 ----------
    def ExecuteSanction(self, triggerPlayerId):
        nameComp = self.factory.CreateName(triggerPlayerId)
        self.trigger_player_name = nameComp.GetName()

        self.gameComp.SetPlayerGameType(1, triggerPlayerId)
        allPlayers = self.playerComp.GetAllPlayers()
        for pid in allPlayers:
            if pid != triggerPlayerId:
                self.gameComp.SetPlayerGameType(0, pid)

        msg = u"§l§a{} 制裁不良服务器！！！§r".format(self.trigger_player_name)
        self.gameComp.SetNotifyMsg(msg, serverApi.GetMinecraftEnum().NotifyType.Tip)
        # 直接给所有玩家发聊天（避免依赖 ClientSystem）
        for pid in allPlayers:
            self.NotifyToClient(pid, "chat", {"msg": msg})

        # 启动每秒 tick
        if self.sanction_timer is None:
            self.sanction_timer = self.gameComp.AddRepeatedTimer(1.0, self.OnSanctionTick)

    # ---------- 每秒 tick ----------
    def OnSanctionTick(self):
        allPlayers = self.playerComp.GetAllPlayers()

        for targetId in allPlayers:
            posComp = self.factory.CreatePos(targetId)
            pos = posComp.GetFootPos()
            if not pos:
                continue
            x, y, z = pos

            # 脚下 3x3x1 清空（缩小范围，降频）
            for dx in range(-1, 2):
                for dz in range(-1, 2):
                    self.blockComp.SetBlockNew(
                        (int(x) + dx, int(y) - 1, int(z) + dz),
                        {"name": "minecraft:air", "aux": 0}, False, 0)

            # 随机 10 道雷
            for _ in range(10):
                rx = x + random.uniform(-10, 10)
                rz = z + random.uniform(-10, 10)
                self.CreateEngineEntityByTypeStr("minecraft:lightning_bolt",
                                                 (rx, y, rz), (0, 0), 0)

            # TNT（需要点燃才炸）
            tntId = self.CreateEngineEntityByTypeStr("minecraft:tnt",
                                                     (x + 2, y, z), (0, 0), 0)
            if tntId:
                fuseComp = self.factory.CreateEntityEvent(tntId)
                if fuseComp:
                    fuseComp.TriggerCustomEvent(tntId, "minecraft:start_fuse")

            # 凋零
            witherId = self.CreateEngineEntityByTypeStr("minecraft:wither",
                                                        (x, y + 3, z), (0, 0), 0)
            if witherId:
                entityNameComp = self.factory.CreateName(witherId)
                entityNameComp.SetName(u"§l§a{} 的制裁者".format(self.trigger_player_name))

        for pid in allPlayers:
            self.NotifyToClient(pid, "chat",
                                {"msg": u"§l§a{} 正在持续制裁中...§r".format(self.trigger_player_name)})

    # ---------- 停止制裁（供 mcfunction 或调试调用） ----------
    def StopSanction(self):
        if self.sanction_timer is not None:
            self.gameComp.CancelTimer(self.sanction_timer)
            self.sanction_timer = None
        self.is_sanctioned = False
        print "[GhjdsMod] sanction stopped"