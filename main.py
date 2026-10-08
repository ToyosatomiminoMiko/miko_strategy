# =============================================================================
# main.py —— 唯一入口(TFWR / 编程农场)
#
# 怎么用:
#   只想跑一种玩法,就把最上面那行 import 改成对应的库,再把下面某一行取消注释。
#   不要一次 import 多个库,不同库里有同名函数,会互相覆盖。
#
#   跑单线程玩法 →   from single import *
#   跑多线程玩法 →   from multi import *
#   跑旧版代码   →   from old_codes import *
#
# 各库能调用什么(细节看库文件头部注释):
#   single.py: main()(整田混种+巨型南瓜+仙人掌+迷宫)/ plant_cactus_sort() /
#              plant_pumpkin_big(x,y) / get_mazes() / dfs(方向) / dino()
#   multi.py:  main_plant_cactus() / main_plant_pumpkin_32x32() /
#              mian_plant_sunflower() / mian_plant_carrot()
#   old_codes.py: main() / pbchf() / ptree() / phay() / pbch() / plant_cactus_sort() /
#              old_main1() / old_mian_plant_cactus() ...
#
# lib.py 是工具库(goto / plant_* / water),single.py 和 multi.py 都自带它,不用单独 import。
#
# 作者:miko   整理日期:2026-10-08
# =============================================================================
from single import *          # 换玩法时改这一行:single / multi / old_codes
# from multi import *
# from old_codes import *

if __name__ == "__main__":
    goto(0, 0)
    # init()          # 清空整块田并回到 (0,0),慎用

    # ---- 选一个开跑(取消注释)----
    # --- 单线程 ---
    # main()                     # 整田混种 -> 4 块 6x6 巨型南瓜 -> 仙人掌排序 -> 迷宫寻宝
    # plant_cactus_sort()        # 只做 16x16 仙人掌排序 + 一次连锁收获
    # get_mazes()
    # dfs(West)                  # 造完迷宫后寻宝(挂机刷金可循环这两行)
    # dino()                     # 恐龙摘 10 个苹果的最小验证

    # --- 多线程(把上面 import 换成 multi)---
    # main_plant_cactus()        # 满田仙人掌:32 列并行排列 -> 32 行并行排行 -> 收获
    # main_plant_pumpkin_32x32() # 32 列并行南瓜
    # mian_plant_sunflower()     # 32 列并行向日葵
    # mian_plant_carrot()        # 32 列并行胡萝卜

    # --- 旧版(把上面 import 换成 old_codes)---
    # main()                     # 旧版单机主线
    # pbchf()                    # 旧版混种
    # old_main1()                # 旧版多机树/干草
