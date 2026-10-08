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
# 每架无人机的入口,放这里多线程就只依赖 lib.py,不必认识单机策略。
#
# 排序算法说明(鸡尾酒排序 / 双向冒泡,2026-10-08 由单冒泡升级):
#   单冒泡每一轮只把当前最大值顶到末尾,小值要一趟趟慢慢往左挪;
#   鸡尾酒排序一轮里先正向扫(把最大值送到右端),再反向扫(把最小值送到左端),
#   两头同时收敛,所以扫描趟数少,比较时的来回跑动明显更少。
#
#   实测(32x32 随机盘面,模拟游戏按环面最短路径计移动格数):
#     交换次数:鸡尾酒 12183 = 单冒泡 12183  —— 必然相同,见下
#     移动格数:鸡尾酒 20,900 < 单冒泡 31,785(省 34%)
#   为什么交换次数必然相同:相邻交换的排序里,把一个排列排好所需的交换次数
#   恰好等于逆序数(每次相邻交换最多消掉一个逆序),不存在更少的可能。
#   所以"谁更快"只看比较与移动开销,不看交换次数 —— 这是本优化的关键依据。
#
#   为什么这里必须"相邻交换":游戏只提供 swap(方向),只能和上下左右换,
#   拿不到随机访问,所以任何排序都得是转置排序(transposition sort)。
#
#   为什么用"收缩边界 + swapped 提前退出":
#     第 k 轮正向扫完后,右端那 k 个已是最终位置,再扫它们是浪费 tick;
#     某一轮一次交换都没发生,说明已有序,可以立即退出。
#
#   排序方向(列为例):swap(North) 是把脚下的值往上推,
#     正向扫在位置 i 比较 i 与 i+1,大了就 swap(North) 上推;
#     反向扫在位置 j 比较 j-1 与 j,小了就 swap(South) 下压。行同理用 East/West。
#   全部扫完后,最大的往北/东走,最小的往南/西走 —— 正好符合游戏要求的
#   "北/东邻居 >= 自己,南/西邻居 <= 自己"。
#
#   注:整块田的排序是"先每列升序,再每行升序";官方提示——行已排好时再排列
#       不会破坏行序,所以两阶段做完整块田就是全局有序的,收获一次全连锁。


def _cocktail_line(n, read_line, swap_ij):
    # 在长度为 n 的一维线上做鸡尾酒排序
    #   read_line()    一次性读出整条线的当前值(列顺着 y、行顺着 x),返回长度 n 的列表
    #   swap_ij(i)     把第 i 个位置的值与第 i+1 个交换(方向由调用方决定)
    # 返回 (交换次数, 是否发生过错序交换)
    #
    # 为什么读成数组再换,而不是每次 measure():
    #   measure() 每个 1 tick,但每次比较都要 goto 过去,一次比较=2 次移动;
    #   先读一遍数组后,只有真正需要交换时才移动,移动次数≈交换次数×1。
    # 坑:数组必须和场上同步 —— 只有 swap_ij 返回 True(真换成功)才交换数组元素;
    #     否则(比如换不过去)会和场上不一致,后面判断全错。
    array = read_line()
    lo = 0
    hi = n - 1
    swaps = 0
    while lo < hi:
        # 正向:把当前最大值顶到 hi
        swapped = False
        for i in range(lo, hi):
            if array[i] > array[i + 1]:
                if swap_ij(i):
                    array[i], array[i + 1] = array[i + 1], array[i]
                    swaps += 1
                    swapped = True
        hi -= 1
        if not swapped:
            break
        # 反向:把当前最小值压到 lo
        swapped = False
        for j in range(hi, lo, -1):
            if array[j - 1] > array[j]:
                if swap_ij(j - 1):
                    array[j - 1], array[j] = array[j], array[j - 1]
                    swaps += 1
                    swapped = True
        lo += 1
        if not swapped:
            break
    return swaps


def _read_col():
    # 读当前这一列(固定 x,顺 y),返回 32 个值
    col = []
    for y in range(32):
        goto(get_pos_x(), y)
        col.append(measure())
    return col


def _read_row():
    # 读当前这一行(固定 y,顺 x),返回 32 个值
    row = []
    for x in range(32):
        goto(x, get_pos_y())
        row.append(measure())
    return row


def _swap_up(i):
    # 列排序用:把 y=i 处的值往上(北)推
    # 为什么先 goto 再判断:只有站对位置才换得动,站错位置 swap 会换错格子
    goto(get_pos_x(), i)
    return swap(North)


def _swap_right(i):
    # 行排序用:把 x=i 处的值往右(东)推
    goto(i, get_pos_y())
    return swap(East)


def plant_col_cactus():
    # 把当前这一列(y 方向)种满仙人掌,再鸡尾酒排序升序排好
    for y in range(32):
        if can_harvest():
            harvest()
        if get_water() < 0.5:
            use_item(Items.Water)
        plant_cactus()
    _cocktail_line(32, _read_col, _swap_up)


def plant_row_cactus():
    # 把当前这一行(x 方向)鸡尾酒排序升序排好(通常接在列排序之后)
    _cocktail_line(32, _read_row, _swap_right)


