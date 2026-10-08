# =============================================================================
# single.py —— 单线程策略库(TFWR / 编程农场)
#
# 是什么:
#   一架无人机怎么干:整田混种 main()、6x6 巨型南瓜、16x16 仙人掌排序、
#   造迷宫 + 深搜寻宝、恐龙摘苹果的最小验证。
#   工具(goto/plant_*)在 lib.py,这里只写策略。
#
# 依赖:single.py -> lib.py(不认识 multi.py / old_codes.py)
#
# 来源:原 f0.py 的策略部分
#
# 坑 / 警告:
#   - main() 在 can_harvest() 为假时既不 else 也不 move,而 plant_* 内部会 move,
#     实际是隔格处理,约一半格子被跳过(原样保留,未改逻辑)
#
# 作者:miko   整理日期:2026-10-08
# =============================================================================
from lib import *


def main():
    # 新版单机主线:整田混种 -> 4 块 6x6 巨型南瓜 -> 整田仙人掌排序 -> 造迷宫寻宝
    # 分区:x>=24 胡萝卜,x>=8 向日葵,x<8 的棋盘格一半种树一半留干草
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
        if dfs(West) == False:
            dfs(East)


def plant_pumpkin_big(tx, ty):
    # 在 (tx,ty) 起铺一块 6x6 南瓜并等它合成巨型南瓜
    # 为什么是 6x6:产量 n^3(n<=5)/ 6n^2(n>=6),每格收益在 n=6 达到饱和,块再大不划算
    # 为什么能等:南瓜成熟后每格有 1/5 概率死掉(can_harvest() 恒 False);
    #            在死格重新 plant 一次即可清除死瓜重新长;bad 记录还没长好的格子;
    #            do_a_flip() 固定 1 秒,正好当轮询节拍器
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
    # 铺 16x16 仙人掌并排好序,然后收获一次触发全田连锁
    # 为什么这么排:仙人掌要求"北/东邻居 >= 自己,南/西邻居 <= 自己",
    #              全田满足时 harvest 一次会递归收掉整片,收益 = 收获数量^2
    # 为什么先排每列再排每行:官方提示——行已排好时再排列不会破坏行序
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
    # 在 (0,15) 用灌木 + 杂草物质造一整块 32x32 迷宫
    # 为什么是这个量:满级迷宫需要 world_size * 2^(等级-1) 份杂草物质
    goto(0, 15)
    harvest()
    water()
    set_ground(Grounds.Grassland)
    plant(Entities.Bush)
    use_item(
        Items.Weird_Substance, get_world_size() * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
    )


def dfs(before):
    # 迷宫深搜:before 是"进入当前格之前所在的方向",用来避免原路返回
    # 为什么能直接用 measure():迷宫内任意位置 measure() 都返回宝藏坐标
    # 为什么找到就直接 return:宝藏已 harvest,逐层 return 即可退出,不用走回起点
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
    # 新版恐龙:只做"摘 10 个苹果就摘帽"的最小验证,不是完整养龙
    # 注意:真实规则是尾巴占格且会阻挡移动(只有最后一节会让开),
    #      这里用 goto 直冲苹果,没做绕尾路径规划,尾巴长了会卡住
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
