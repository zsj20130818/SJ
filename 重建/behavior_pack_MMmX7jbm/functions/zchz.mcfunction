//快速制裁服务器
/gamerule sendcommandfeedback false
/gamerule commandblockoutput false
/fog @a push minecraft:fog_soulsand_valley
/camerashake add @a 1.2 10 positional
/title @a title §l§a曹梁小队工作室牛逼！！！§r
/say §l§a曹梁小队队长制裁不良服务器§r
/title @a actionbar §l§a服务器正在被曹梁小队队长制裁§r
/tile @a subtitle §l§a曹梁小队队长牛逼！！！§r
/say §l§a曹梁小队正在黑入服务器§r
/execute @a ~~~ summon lightning_bolt ~10 ~ ~
/execute @a ~~~ fill ~-3 ~-3 ~-3 ~3 ~3 ~3 air
/execute as @a at @a run summon lightning_bolt
/execute as @a at @a run summon tnt
/execute as @a at @a run summon wither §l§a曹梁小队工作室制裁不良服务器§r
/say §l§a曹梁小队队长到处一游§r
/execute as @a at @s run summon evocation_fang
/particle minecraft:totem_manual ~ ~ ~
/particle minecraft:totem_particle ~ ~ ~
/particle minecraft:villager_happy ~ ~ ~