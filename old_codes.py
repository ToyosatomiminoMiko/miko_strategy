# =============================================================================
# old_codes.py —— 旧版代码归档(TFWR / 编程农场)
#
# 是什么:
#   把拆分前的旧实现全部堆在这一个文件里,自包含:只 import __builtins__,
#   不依赖 lib.py / single.py / multi.py,也不被它们调用。想跑旧代码就单独跑本文件。
#
# 内容(按原文件分三段):
#   1) 旧工具:goto(不绕边)/ plant_* / init / water        ← 原 main.py
#   2) 旧单机策略:ptree / pbch / phay / pbchf / main / plant_pumpkin_big /
#      plant_cactus_sort / get_mazes / dfs / dino            ← 原 main.py + f0.py
#   3) 旧多机列式作业与调度(函数名统一 old_ 前缀,避免与新版重名)
#      ← 原 main_multi-thread.py
#
# 为什么统一 old_ 前缀:
#   旧多机里 plant_col_tree0、plant_col_sumflower 等和新版 multi.py 同名,
#   归档时加前缀以免混淆;重名的那份存为 old_plant_col_sunflower_b。
#
# 来源:原 main.py / main_multi-thread.py / f0.py 的旧策略部分
#
# 作者:miko   整理日期:2026-10-08
# =============================================================================
from __builtins__ import *



# ==================== 1) 旧工具(原 main.py) ====================

def goto(x, y):
    # 旧版走位:先横后纵,不绕边(慢,但直白)
    if x >= get_world_size() or y >= get_world_size():
        return None
    if x > get_pos_x():
        while x - get_pos_x():
            move(East)
    elif x < get_pos_x():
        while x - get_pos_x():
            move(West)
    if y > get_pos_y():
        while y - get_pos_y():
            move(North)
    elif y < get_pos_y():
        while y - get_pos_y():
            move(South)


def moveto(direction, s):
    for i in range(s):
        move(direction)


def set_ground(g):
    if get_ground_type() != g:
        till()


def plant_bush():
    set_ground(Grounds.Grassland)
    if plant(Entities.Bush):
        move(North)


def plant_carrot():
    set_ground(Grounds.Soil)
    if plant(Entities.Carrot):
        move(North)


def plant_pumpkin():
    set_ground(Grounds.Soil)
    if plant(Entities.Pumpkin):
        move(North)


def plant_hay():
    set_ground(Grounds.Grassland)
    move(North)


def plant_tree():
    set_ground(Grounds.Grassland)
    if plant(Entities.Tree):
        move(North)


def plant_cactus():
    set_ground(Grounds.Soil)
    if plant(Entities.Cactus):
        move(North)


def plant_sunflower():
    set_ground(Grounds.Soil)
    if plant(Entities.Sunflower):
        move(North)


def init():
    clear()
    goto(0, 0)


def water():
    use_item(Items.Water)
    use_item(Items.Water)


# ==================== 2) 旧单机策略(原 main.py + f0.py) ====================

def ptree():
    # 纯树田:棋盘格(x%2 与 y%2 同奇偶的位置种树,其余留干草)
    # 为什么要棋盘格:树的正交邻居每有一棵,生长时间翻倍,棋盘格可以做到零惩罚
    while True:
        goto(0, 0)
        for x in range(get_world_size()):
            for y in range(get_world_size()):
                if can_harvest():
                    harvest()
                    if x % 2 == 0:
                        if y % 2 == 0:
                            plant_tree()
                        else:
                            plant_hay()
                    elif x % 2 != 0:
                        if y % 2 != 0:
                            plant_tree()
                        else:
                            plant_hay()
                else:
                    move(North)
            move(East)


def pbch():
    # 树+干草+胡萝卜的三分区旧策略
    while True:
        goto(0, 0)
        for x in range(get_world_size()):
            for y in range(get_world_size()):
                if can_harvest():
                    harvest()
                    if x >= 16:
                        plant_carrot()
                    elif (x >= 0) and (x % 2 == 0):
                        if y % 2 == 0:
                            plant_tree()
                        else:
                            plant_hay()
                    elif (x >= 0) and (x % 2 != 0):
                        if y % 2 != 0:
                            plant_tree()
                        else:
                            plant_hay()
                else:
                    move(North)
            move(East)


def phay():
    # 纯干草田
    while True:
        goto(0, 0)
        for x in range(get_world_size()):
            for y in range(get_world_size()):
                if can_harvest():
                    harvest()
                move(North)
            move(East)


def pbchf():
    # 树+干草+胡萝卜+向日葵,带浇水的旧版混种
    while True:
        goto(0, 0)
        for x in range(get_world_size()):
            for y in range(get_world_size()):
                water()
                if can_harvest():
                    harvest()
                if x >= 24:
                    plant_sunflower()
                elif x >= 12:
                    plant_carrot()
                elif x >= 0 and (x % 2 == 0):
                    if y % 2 == 0:
                        plant_tree()
                    else:
                        plant_hay()
                elif x >= 0 and (x % 2 != 0):
                    if y % 2 != 0:
                        plant_tree()
                    else:
                        plant_hay()
            move(East)


# MAIN ########################################################################


def main():
    # 旧版单机主线:整田混种 -> 4 块 6x6 巨型南瓜 -> 仙人掌排序 -> 收田 -> 迷宫寻宝
    # 分区:x>=24 胡萝卜,x>=8 向日葵,x<8 棋盘格树/干草
    # 已知缺陷:can_harvest() 为假时既没 else 也没 move,而 plant_* 内部会 move,
    #          实际是"隔格处理",一半格子被跳过
    while True:
        goto(0, 0)
        for x in range(get_world_size()):
            for y in range(get_world_size()):
                water()
                if can_harvest():
                    harvest()
                if x >= 24:
                    plant_carrot()
                elif x >= 8:
                    plant_sunflower()
                elif x >= 0 and (x % 2 == 0):
                    if y % 2 == 0:
                        plant_tree()
                        use_item(Items.Fertilizer)
                    else:
                        plant_hay()
                elif x >= 0 and (x % 2 != 0):
                    if y % 2 != 0:
                        plant_tree()
                        use_item(Items.Fertilizer)
                    else:
                        plant_hay()
            move(East)
        # plant 6x6 big pumpkin
        for i in range(4):
            plant_pumpkin_big(26, i * 6 + i * 1)
        plant_cactus_sort()  # plant Cactus
        for x in range(get_world_size()):
            for y in range(get_world_size()):
                harvest()
                move(North)
            move(East)
        get_mazes()  # create maze
        # search Gold
        if dfs(North) == False:
            dfs(South)


def plant_pumpkin_big(tx, ty):
    # 旧版 6x6 巨型南瓜:铺满后轮询补种死掉的格子,直到全部长好再 harvest
    goto(tx, ty)
    for y in range(ty, ty + 6):
        if y % 2:
            for x in range(tx + 5, tx - 1, -1):
                water()
                goto(x, y)
                if can_harvest():
                    harvest()
                plant_pumpkin()
        else:
            for x in range(tx, tx + 6, 1):
                water()
                goto(x, y)
                if can_harvest():
                    harvest()
                plant_pumpkin()
    goto(tx, ty)
    n = 0
    bad = []
    while True:
        for y in range(ty, ty + 6):
            if y % 2:
                for x in range(tx + 5, tx - 1, -1):
                    goto(x, y)
                    if can_harvest():
                        if (x, y) in bad:
                            bad.remove((x, y))
                    else:
                        plant_pumpkin()
                        if (x, y) not in bad:
                            bad.append((x, y))
            else:
                for x in range(tx, tx + 6, 1):
                    goto(x, y)
                    if can_harvest():
                        if (x, y) in bad:
                            bad.remove((x, y))
                    else:
                        plant_pumpkin()
                        if (x, y) not in bad:
                            bad.append((x, y))
        do_a_flip()
        if len(bad) == 0:
            harvest()
            break


def plant_cactus_sort():
    # 旧版仙人掌:只铺 16x16(整田 32x32,等于只利用 1/4),先排列再排行
    # 与原 main.py 一致:补种前先 harvest() 掉旧瓜
    goto(0, 0)
    for x in range(17):
        for y in range(16):
            if can_harvest():
                harvest()
                plant_cactus()
            else:
                plant_cactus()
        goto(x, 0)
    goto(0, 0)
    array2d = []
    for x in range(0, 16):
        array = []
        for y in range(0, 16):
            goto(x, y)
            array.append(measure())
        array2d.append(array)
    for x in range(0, 16):
        for y in range(0, 16):
            swapped = False
            for yi in range(0, 16 - y - 1):
                if array2d[x][yi] > array2d[x][yi + 1]:
                    array2d[x][yi], array2d[x][yi + 1] = (
                        array2d[x][yi + 1],
                        array2d[x][yi],
                    )
                    goto(x, yi)
                    swap(North)
                    swapped = True
            if not swapped:
                break
    for y in range(0, 16):
        for x in range(0, 16):
            swapped = False
            for xi in range(0, 16 - x - 1):
                if array2d[xi][y] > array2d[xi + 1][y]:
                    array2d[xi][y], array2d[xi + 1][y] = (
                        array2d[xi + 1][y],
                        array2d[xi][y],
                    )
                    goto(xi, y)
                    swap(East)
                    swapped = True
            if not swapped:
                break
    goto(0, 0)
    if can_harvest():
        harvest()


def get_mazes():
    # 造 32x32 迷宫:灌木 + 满级所需杂草物质
    goto(0, 15)
    harvest()
    water()
    set_ground(Grounds.Grassland)
    plant(Entities.Bush)
    use_item(
        Items.Weird_Substance, get_world_size() * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
    )


def dfs(before):
    # 迷宫深搜,和 fw_single.dfs 同源;这里被旧 main() 以 dfs(North)/dfs(South) 调用
    opposite = {East: West, West: East, North: South, South: North}
    if (get_pos_x(), get_pos_y()) == measure():
        harvest()
        return True
    dire = [East, South, West, North]
    s = []
    for d in dire:
        if d == opposite[before]:
            continue
        if can_move(d):
            s.append(d)
    for m in s:
        move(m)
        if dfs(m):
            return True
    move(opposite[before])
    return False


def dino():
    # 旧版恐龙:同样是"追 10 个苹果"的最小验证
    goto(0, 0)
    i = 0
    change_hat(Hats.Dinosaur_Hat)
    nx, ny = measure()
    while True:
        if i >= 10:
            break
        nx, ny = measure()
        if (nx == None) or (ny == None):
            return False
        goto(nx, ny)
        i += 1
    change_hat(Hats.Brown_Hat)


# ==================== 3) 旧多机作业与调度(原 main_multi-thread.py,统一 old_ 前缀) ====================

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


def old_plant_col_sunflower_b():
    # 向日葵列
    while True:
        for y in range(32):
            if can_harvest():
                harvest()
            if get_water() < 0.5:
                use_item(Items.Water)
            plant_sunflower()


def old_plant_col_sunflower():
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


# ==================== 入口(要跑旧代码时用) ====================
if __name__ == "__main__":
    change_hat(Hats.Brown_Hat)
    goto(0, 0)

    # ---- 选一个开跑 ----
    # main()                     # 旧版单机主线(整田混种 + 巨型南瓜 + 仙人掌 + 迷宫)
    # pbchf()                    # 旧版混种
    # plant_cactus_sort()        # 旧版仙人掌(只 16x16)
    # old_main1()                # 旧版多机树/干草
    # old_mian_plant_cactus()    # 旧版多机仙人掌
    pass

