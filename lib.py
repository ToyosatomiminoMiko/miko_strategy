# =============================================================================
# lib.py —— 工具库(TFWR / 编程农场)
#
# 是什么:
#   只有"怎么走、怎么种、怎么浇水",不含任何策略(种什么、种哪里不在这里)。
#   single.py 与 multi.py 都从这里取工具,两边互不依赖。
#
# 内容:goto(绕边最短路径)/ moveto / set_ground / plant_bush,carrot,pumpkin,
#       hay,tree,cactus,sunflower / init / water / 单列与单行仙人掌排序
#
# 来源:原 f0.py 的工具与种植部分 + 原 f3.py 的 plant_col_cactus/plant_row_cactus
#
# 坑 / 警告:
#   - plant_xxx() 只在种成功时才 move(North);没钱或格子被占时不推进,循环里要注意
#   - set_ground() 靠 till() 翻转,每次 200 tick,别在循环里反复翻
#
# 作者:miko   整理日期:2026-10-08
# =============================================================================
from __builtins__ import *


def goto(x, y):
    # 走到 (x, y):按环面(世界首尾相连)选更短的一侧绕过去
    ws = get_world_size()
    if (x >= ws) or (y >= ws):
        return None
    if x > get_pos_x():
        if (x - get_pos_x()) >= (ws / 2):
            while get_pos_x() != x:
                move(West)
        else:
            while get_pos_x() != x:
                move(East)
    elif x < get_pos_x():
        if (get_pos_x() - x) >= (ws / 2):
            while get_pos_x() != x:
                move(East)
        else:
            while get_pos_x() != x:
                move(West)
    if y > get_pos_y():
        if (y - get_pos_y()) >= (ws / 2):
            while get_pos_y() != y:
                move(South)
        else:
            while get_pos_y() != y:
                move(North)
    elif y < get_pos_y():
        if (get_pos_y() - y) >= (ws / 2):
            while get_pos_y() != y:
                move(North)
        else:
            while get_pos_y() != y:
                move(South)


def moveto(direction, s):
    # 朝一个方向连续走 s 步
    for i in range(s):
        move(direction)


def set_ground(g):
    # 把脚下换成目标地面:翻一次变 Soil,再翻一次变回 Grassland
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
    # 干草不用种:草地自己会长,这里只保证地面是草地
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
    # 清空整块田并回到 (0,0),慎用
    clear()
    goto(0, 0)


def water():
    # 一次 use_item 只加一槽(0.25 水位),连浇两次才接近满
    use_item(Items.Water)
    use_item(Items.Water)


# ---- 按列/按行排序的单列工具 ----
# 为什么放在工具库而不是单机策略库:多线程的仙人掌作业直接用这两个函数当
# 每架无人机的入口,放这里多线程就只依赖 fw_lib,不必认识单机策略库。


def plant_col_cactus():
    # 把当前这一列(y 方向)种满仙人掌并升序排好
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


def plant_row_cactus():
    # 把当前这一行(x 方向)种满仙人掌并升序排好
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
