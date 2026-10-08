# =============================================================================
# multi.py —— 多线程策略库 + 入口(TFWR / 编程农场)
#
# 是什么:
#   满级 Megafarm 上限 32 架无人机(含主控那架),这里按 32 列分配:
#   31 列各派一架,最后一列主控自己干。每架无人机跑一个 plant_col_* 作业。
#
# 依赖:multi.py -> lib.py(不认识 single.py)
#
# 内容:
#   新版:plant_col_tree0/1, plant_col_hay, plant_col_carrot, plant_col_pumpkin,
#         plant_col_sunflower + main_plant_cactus / main_plant_pumpkin_32x32 /
#         mian_plant_sunflower / mian_plant_carrot
#   旧版(原名加 old_ 前缀,不会被调用,留作对照):old_main1 /
#         old_main_plant_pumpkin_32x32 / old_mian_plant_sunflower /
#         old_mian_plant_cactus / old_plant_col_cactus / old_plant_row_cactus 等
#
# 坑 / 警告:
#   - plant_col_* 里 plant_xxx() 只在种成功时 move,水或种子耗尽会原地空转
#   - 每架无人机独立解释器、独立全局变量,不能靠共享变量通信
#   - 32 是满级世界尺寸的硬编码
#
# 来源:原 f3.py(新版)+ 原 main_multi-thread.py(旧版,存于 old_codes.py 之外这里)
#
# 作者:miko   整理日期:2026-10-08
# =============================================================================
from lib import *

# ==================== 新版作业 ====================

def plant_col_tree0():
    # 偶数列的树/干草:偶数 y 种树,奇数 y 留干草
    while True:
        if get_water() < 0.5:
            use_item(Items.Water)
        if can_harvest():
            harvest()
        if get_pos_y() % 2 == 0:
            plant_tree()
        else:
            plant_hay()


def plant_col_tree1():
    # 奇数列的树/胡萝卜:奇数 y 种树,偶数 y 种胡萝卜
    while True:
        if get_water() < 0.5:
            use_item(Items.Water)
        if can_harvest():
            harvest()
        if get_pos_y() % 2 != 0:
            plant_tree()
        else:
            plant_carrot()


def plant_col_hay():
    # 只收干草的一列:上下各扫一遍,顺便保证地面是草地
    # 为什么走两遍:第一遍从南到北收完,再走回来复位,方便下一轮/下架无人机起步
    for y in range(33):
        harvest()
        set_ground(Grounds.Grassland)
        move(North)
    for y in range(33):
        harvest()
        set_ground(Grounds.Grassland)
        move(South)


def plant_col_carrot():
    # 只种胡萝卜的一列
    for y in range(get_world_size()):
        if can_harvest():
            harvest()
        if get_water() < 0.5:
            use_item(Items.Water)
        plant_carrot()


def plant_col_pumpkin():
    # 整列南瓜并等合成巨型南瓜(1 x 32 的长条)
    # 坑:这里 y==31 分支只补种最后一格就跳到 0,和下面的补种循环是两套逻辑,
    #     原样保留自旧实现,改动风险高
    while True:
        if get_pos_y() == 31:
            # if can_harvest():
            #     harvest()
            plant_pumpkin()
            goto(get_pos_x(), 0)
            break
        # if can_harvest():
        #     harvest()
        if get_water() < 0.5:
            use_item(Items.Water)
        plant_pumpkin()
    bad = []
    while True:
        for y in range(32):
            goto(get_pos_x(), y)
            if can_harvest():
                if y in bad:
                    bad.remove(y)
            else:
                plant_pumpkin()
                if y not in bad:
                    bad.append(y)
        if len(bad) == 0:
            break


def plant_col_sunflower():
    # 整列向日葵:一直收、一直浇、一直种
    while True:
        for y in range(32):
            # if can_harvest():
            harvest()
            if get_water() < 0.5:
                use_item(Items.Water)
            plant_sunflower()


def main_plant_cactus():
    # 多线程满田仙人掌:先 32 列并行各排好自己那一列,再 32 行并行各排好自己那一行
    # 为什么够了:行已排好后再排列不会破坏行序,全部排好后 harvest 一次连锁收整田
    goto(0, 0)
    for x in range(31):
        goto(x, 0)
        spawn_drone(plant_col_cactus)
    goto(31, 0)
    plant_col_cactus()
    while True:
        if num_drones() == 1:
            break
    for y in range(31):
        goto(0, y)
        spawn_drone(plant_row_cactus)
    goto(0, 31)
    plant_row_cactus()
    while True:
        if num_drones() == 1:
            break
    goto(0, 0)
    harvest()


def main_plant_pumpkin_32x32():
    # 多线程南瓜:32 列并行,每列自己等自己那一条合成
    goto(0, 0)
    for x in range(31):
        goto(x, 0)
        spawn_drone(plant_col_pumpkin)
    goto(31, 0)
    plant_col_pumpkin()
    while True:
        if num_drones() == 1:
            break
    goto(0, 0)
    harvest()


def mian_plant_sunflower():
    # 多线程向日葵(函数名的 mian 是原文件里的拼写错误,保留以免改调用点)
    goto(0, 0)
    for x in range(31):
        goto(x, 0)
        spawn_drone(plant_col_sunflower)
    goto(31, 0)
    plant_col_sunflower()


def mian_plant_carrot():
    # 多线程胡萝卜(同样是原文件的拼写错误,保留)
    goto(0, 0)
    for x in range(31):
        goto(x, 0)
        spawn_drone(plant_col_carrot)
    goto(31, 0)
    plant_col_carrot()
# ==================== 旧版作业(加 old_ 前缀,不被调用,仅供对照) ====================

def old_plant_col_tree0():
    # 偶数列:偶数 y 种树,奇数 y 留干草
    while True:
        if get_water() < 0.5:
            use_item(Items.Water)
        if can_harvest():
            harvest()
        if get_pos_y() % 2 == 0:
            plant_tree()
        else:
            plant_hay()


def old_plant_col_tree1():
    # 奇数列:奇数 y 种树,偶数 y 种胡萝卜
    while True:
        if get_water() < 0.5:
            use_item(Items.Water)
        if can_harvest():
            harvest()
        if get_pos_y() % 2 != 0:
            plant_tree()
        else:
            plant_carrot()


def old_plant_col_sunflower():
    # 向日葵列
    while True:
        for y in range(32):
            if can_harvest():
                harvest()
            if get_water() < 0.5:
                use_item(Items.Water)
            plant_sunflower()


def old_plant_col_sunflower_b():
    # 与 old_plant_col_sunflower 同义的另一份实现,保留原样
    while True:
        for y in range(32):
            if can_harvest():
                harvest()
            if get_water() < 0.5:
                use_item(Items.Water)
            plant_sunflower()


def old_plant_col_hay():
    # 干草列(生效版,32 步):上下各扫一遍
    for y in range(32):
        harvest()
        set_ground(Grounds.Grassland)
        move(North)
    for y in range(32):
        harvest()
        set_ground(Grounds.Grassland)
        move(South)


def old_plant_col_hay_long():
    # 原文件里被上一个同名函数覆盖的那份(33 步),改名保留
    for y in range(33):
        harvest()
        set_ground(Grounds.Grassland)
        move(North)
    for y in range(33):
        harvest()
        set_ground(Grounds.Grassland)
        move(South)


def old_plant_col_carrot():
    # 胡萝卜列(生效版,31 步)
    for y in range(31):
        if can_harvest():
            harvest()
        if get_water() < 0.5:
            use_item(Items.Water)
        plant_carrot()


def old_plant_col_carrot_31():
    # 原文件里被覆盖的那份同名实现(内容同样是 31 步),改名保留
    for y in range(31):
        if can_harvest():
            harvest()
        if get_water() < 0.5:
            use_item(Items.Water)
        plant_carrot()


def old_plant_col_pumpkin():
    # 旧版南瓜列:先铺,再轮询补种死格,直到整列长好
    while True:
        if get_pos_y() == 31:
            if can_harvest():
                harvest()
                plant_pumpkin()
            goto(get_pos_x(), 0)
            break
        if can_harvest():
            harvest()
        if get_water() < 0.5:
            use_item(Items.Water)
        plant_pumpkin()
    bad = []
    while True:
        for y in range(32):
            goto(get_pos_x(), y)
            if can_harvest():
                if y in bad:
                    bad.remove(y)
            else:
                plant_pumpkin()
                if y not in bad:
                    bad.append(y)
        if len(bad) == 0:
            break


def old_plant_col_cactus():
    # 仙人掌列:先种满再升序排好(旧版多机两阶段排序的第一阶段)
    # 原 main_multi-thread.py 是借用 f0 里的同名函数,这里自带一份,
    # 这样旧多机库不再依赖单机库
    for y in range(32):
        if can_harvest():
            harvest()
        if get_water() < 0.5:
            use_item(Items.Water)
        plant_cactus()
    goto(get_pos_x(), 0)
    array = []
    for y in range(32):
        goto(get_pos_x(), y)
        array.append(measure())
    for y in range(32):
        swapped = False
        for yi in range(0, 32 - y - 1):
            if array[yi] > array[yi + 1]:
                array[yi], array[yi + 1] = array[yi + 1], array[yi]
                goto(get_pos_x(), yi)
                swap(North)
                swapped = True
        if not swapped:
            break


def old_plant_row_cactus():
    # 仙人掌行:第二阶段,把每一行升序排好
    array = []
    for x in range(32):
        goto(x, get_pos_y())
        array.append(measure())
    for x in range(32):
        swapped = False
        for xi in range(0, 32 - x - 1):
            if array[xi] > array[xi + 1]:
                array[xi], array[xi + 1] = array[xi + 1], array[xi]
                goto(xi, get_pos_y())
                swap(East)
                swapped = True
        if not swapped:
            break


# ---- 调度 ----


def old_main1():
    # 旧版树/干草调度:偶数/奇数列分配不同作业,最后一列主控自己干
    change_hat(Hats.Brown_Hat)
    while True:
        goto(0, 0)
        for x in range(31):
            goto(x, 0)
            # spawn_drone(old_plant_col_hay)
            if x % 2 == 0:
                spawn_drone(old_plant_col_tree0)
            else:
                spawn_drone(old_plant_col_tree1)
        goto(31, 0)
        old_plant_col_tree1()


def old_main_plant_pumpkin_32x32():
    # 旧版南瓜调度:32 列并行,等全部收工后回起点收获
    change_hat(Hats.Brown_Hat)
    while True:
        goto(0, 0)
        for x in range(31):
            goto(x, 0)
            spawn_drone(old_plant_col_pumpkin)
        goto(31, 0)
        old_plant_col_pumpkin()
        while True:
            if num_drones() == 1:
                move(North)
                move(East)
                goto(0, 0)
                harvest()
                break


def old_mian_plant_sunflower():
    # 旧版向日葵调度(mian 拼写保留)
    change_hat(Hats.Brown_Hat)
    while True:
        goto(0, 0)
        for x in range(31):
            goto(x, 0)
            spawn_drone(old_plant_col_sunflower)
        goto(31, 0)
        old_plant_col_sunflower()


def old_mian_plant_cactus():
    # 旧版仙人掌调度:32 列并行排序 -> 32 行并行排序 -> 收获
    change_hat(Hats.Brown_Hat)
    while True:
        goto(0, 0)
        for x in range(31):
            goto(x, 0)
            spawn_drone(old_plant_col_cactus)
        goto(31, 0)
        old_plant_col_cactus()
        while True:
            if num_drones() == 1:
                break
        for y in range(31):
            goto(0, y)
            spawn_drone(old_plant_row_cactus)
        goto(0, 31)
        old_plant_row_cactus()
        while True:
            if num_drones() == 1:
                break
        goto(0, 0)
        harvest()
# ==================== 入口 ====================
if __name__ == "__main__":
    change_hat(Hats.Brown_Hat)
    goto(0, 0)

    # ---- 选一个开跑 ----
    main_plant_cactus()             # 满田仙人掌:32 列并行排列 -> 32 行并行排行 -> 收获
    # main_plant_pumpkin_32x32()    # 32 列并行南瓜
    # mian_plant_sunflower()        # 32 列并行向日葵
    # mian_plant_carrot()           # 32 列并行胡萝卜
    # old_main1()                   # 旧版树/干草调度(对照用)

