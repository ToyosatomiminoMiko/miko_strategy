# strategy 游戏攻略

## TheFarmerWasReplaced 编程农场

### 一共就 5 个 .py

```
main.py   入口   只做一件事:选一行调用(控制台)
  │
  ├─ single.py   单线程策略 ─┐
  ├─ multi.py    多线程策略 ─┼→ lib.py   工具:goto / plant_* / 水 / 地面
  └─ old_codes.py 旧版归档,自包含(不参与新流程)
```

规则:**策略和工具分家,单线程与多线程不互相 import。**

| 文件 | 是什么 | 里面有什么 |
| --- | --- | --- |
| [main.py](main.py) | 入口/控制台 | 改一行 import + 取消一行注释就能跑 |
| [lib.py](lib.py) | 工具库 | `goto`(走环面最短路径)、`moveto`、`set_ground`、`plant_bush/carrot/pumpkin/hay/tree/cactus/sunflower`、`init`、`water`、单列与单行仙人掌排序 |
| [single.py](single.py) | 单线程策略 | `main()`(整田混种+4 块 6x6 巨型南瓜+仙人掌排序+迷宫)、`plant_pumpkin_big`、`plant_cactus_sort`、`get_mazes`、`dfs`、`dino` |
| [multi.py](multi.py) | 多线程策略 + 入口 | 每列一架无人机的作业 `plant_col_*`,调度 `main_plant_cactus` / `main_plant_pumpkin_32x32` / `mian_plant_sunflower` / `mian_plant_carrot`;文件末尾自带 `__main__` |
| [old_codes.py](old_codes.py) | 旧版归档 | 旧工具(不绕边的 `goto`)、旧单机策略(`ptree`/`pbch`/`phay`/`pbchf`/旧 `main`/16x16 仙人掌/旧 `dino`)、旧多机作业(名字统一 `old_` 前缀);自包含,可单独跑 |
| [__builtins__.py](__builtins__.py) | 资料 | 游戏 API 类型定义(社区维护),不要改 |

`backup/` 是重组前的原始快照(`f0~f3`、`main*` 等),已 ignore,只用来回溯。

### 怎么跑

1. 游戏内打开 `main.py`;
2. **单线程**:保持 `from single import *`,取消注释 `main()` 之类;
3. **多线程**:改成 `from multi import *`,取消注释 `main_plant_cactus()` 之类;
4. **旧版**:改成 `from old_codes import *`。

`main.py` 里已经按"单线程 / 多线程 / 旧版"分好注释,照着取消注释即可。

### 已知问题(只标注,没改逻辑)

- `single.py` 的 `main()` 在 `can_harvest()` 为假时既不 `else` 也不 `move`,而 `plant_*` 内部会 `move`,实际是隔格处理,田里约一半格子被跳过;
- `multi.py` 的 `plant_col_*` 在种子或水耗尽时不推进位置,会原地空转;
- 单机仙人掌只利用 16x16,满级整田是 32x32(`multi.py` 才是走满 32 列 + 32 行);
- 化肥会让植物感染,收获时一半产物变成杂草物质,不是纯赚;
- 数值以 `__builtins__.py` 注释为准(社区近似版,部分数值滞后于当前游戏版本)。

## TuringComplete

Symphony 架构汇编,见 [Symphony.asm](TuringComplete/Symphony.asm);包含 `mov`, `neg`, `not`。
游戏里 Stack / Functions / Aliases 三关补齐的 `push`/`pop`/`call`/`ret`/`const` 同样可用。

各关卡程序直接粘进游戏内汇编器运行:[sort.asm](TuringComplete/sort.asm)(排序)、
[upper.asm](TuringComplete/upper.asm)(首字母大写)、[random.asm](TuringComplete/random.asm)(千变万化)、
[card.asm](TuringComplete/card.asm)(尼姆博弈)、[hanoi.asm](TuringComplete/hanoi.asm)(汉诺塔,无 push/pop/call/ret 的迭代解法)。

[hanoi_check.py](TuringComplete/hanoi_check.py) 是离线校验器:Symphony 子集解释器 + 汉诺塔关卡判定脚本,
`python3 TuringComplete/hanoi_check.py` 会先核对助记符是否全在 Symphony.asm 里,再跑完 18 种盘数/方向组合,
并顺带自检解释器本身。
