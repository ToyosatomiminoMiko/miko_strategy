#!/usr/bin/env python3
# 是什么:Symphony 汇编(见 Symphony.asm)的离线汇编器 + 解释器,
#         并把关卡脚本 campaign/tower/test.si(汉诺塔)的判定逻辑逐行翻译进来,
#         用来在没有打开游戏时验证 hanoi.asm。
# 用法:   python3 TuringComplete/hanoi_check.py            # 默认检查同目录的 hanoi.asm
#         python3 TuringComplete/hanoi_check.py 某个.asm
# 覆盖的指令:in/out/mov/neg/not/nop/add/sub/and/or/xor/nand/nor/lsl/lsr/asr/cmp/
#         jmp/je/jne/jb/jae/jbe/ja/jl/jge/jle/jg/push/pop/call/ret/load_*/store_*/const。
# 已知限制:只实现本仓库关卡程序用到的子集,不含 screen/keyboard/time/pload/pstore,
#         也不模拟真实时序,只验证"逻辑上能否过关"。
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

REGS = {'zr': 0, 'r0': 0, **{f'r{i}': i for i in range(1, 14)}, 'sp': 14, 'flags': 15}
ALU3 = {'add', 'sub', 'and', 'or', 'xor', 'nand', 'nor', 'lsl', 'lsr', 'asr'}
JUMPS = {'je', 'jne', 'jb', 'jae', 'jbe', 'ja', 'jl', 'jge', 'jle', 'jg'}


def opnd(tok, aliases):
    tok = aliases.get(tok, tok)          # 展开 const 别名
    m = re.fullmatch(r'\[(.+)\]', tok)
    if m:
        inner = aliases.get(m.group(1).strip(), m.group(1).strip()).lower()
        return ('memreg', REGS[inner]) if inner in REGS else ('memimm', int(m.group(1), 0))
    if tok.lower() in REGS:
        return ('reg', REGS[tok.lower()])
    if re.fullmatch(r'[A-Za-z_]\w*', tok):
        return ('label', tok)
    return ('imm', int(tok, 0))


def assemble(text):
    instrs, labels, aliases = [], {}, {}
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.split(';', 1)[0].strip()
        if line.startswith('const '):
            name, _, value = line[6:].partition('=')
            aliases[name.strip()] = value.strip()
            continue
        while ':' in line:
            head, _, rest = line.partition(':')
            labels[head.strip()] = len(instrs)
            line = rest.strip()
        if line:
            p = line.replace(',', ' ').split()
            instrs.append((p[0].lower(), [opnd(x, aliases) for x in p[1:]], lineno))
    return instrs, labels


def run(instrs, labels, inputs, on_out, sp0=0x3FC, max_steps=2_000_000):
    """返回 (结局, 步数, 已读输入数)。结局 = win / fail / timeout。"""
    regs = [0] * 16
    regs[14] = sp0
    mem, flags, pc, nin, steps = {}, None, 0, 0, 0

    def rd(o):
        return {'reg': lambda: regs[o[1]], 'imm': lambda: o[1],
                'label': lambda: labels[o[1]]}[o[0]]()

    def wr(i, v):
        if i:
            regs[i] = v & 0xFFFFFFFF

    while steps < max_steps:
        steps += 1
        op, ops, line = instrs[pc]
        if op == 'nop':
            pc += 1
        elif op == 'in':
            regs[ops[0][1]] = inputs[nin] if nin < len(inputs) else 0
            nin += 1
            pc += 1
        elif op == 'out':
            r = on_out(rd(ops[0]))
            if r in ('win', 'fail'):
                return r, steps, nin
            pc += 1
        elif op in ('mov', 'neg', 'not'):
            v = rd(ops[1])
            wr(ops[0][1], v if op == 'mov' else (-v if op == 'neg' else ~v))
            flags = None
            pc += 1
        elif op in ALU3:
            a, b = rd(ops[1]), rd(ops[2])
            r = {'add': a + b, 'sub': a - b, 'and': a & b, 'or': a | b, 'xor': a ^ b,
                 'nand': ~(a & b), 'nor': ~(a | b), 'lsl': a << (b & 31),
                 'lsr': (a & 0xFFFFFFFF) >> (b & 31), 'asr': a >> (b & 31)}[op]
            wr(ops[0][1], r)
            flags = None
            pc += 1
        elif op == 'cmp':
            flags = (rd(ops[0]), rd(ops[1]))
            pc += 1
        elif op == 'jmp':
            pc = rd(ops[0])
        elif op in JUMPS:
            assert flags is not None, f'第 {line} 行: flags 已被 call/push/ALU 破坏'
            a, b = flags
            ua, ub = a & 0xFFFFFFFF, b & 0xFFFFFFFF
            sa, sb = (ua - (1 << 32) if ua >> 31 else ua), (ub - (1 << 32) if ub >> 31 else ub)
            taken = {'je': ua == ub, 'jne': ua != ub, 'jb': ua < ub, 'jae': ua >= ub,
                     'jbe': ua <= ub, 'ja': ua > ub, 'jl': sa < sb, 'jge': sa >= sb,
                     'jle': sa <= sb, 'jg': sa > sb}[op]
            if taken:
                pc = rd(ops[0]) if ops[0][0] != 'label' else labels[ops[0][1]]
            else:
                pc += 1
        elif op == 'push':
            regs[14] -= 4
            mem[regs[14]] = rd(ops[0])
            flags = None
            pc += 1
        elif op == 'pop':
            wr(ops[0][1], mem.get(regs[14], 0))
            regs[14] += 4
            flags = None
            pc += 1
        elif op == 'call':
            regs[14] -= 4
            mem[regs[14]] = pc + 1
            flags = None
            pc = labels[ops[0][1]]
        elif op == 'ret':
            pc = mem.get(regs[14], 0)
            regs[14] += 4
            flags = None
        elif op.startswith('load'):
            o = ops[1]
            addr = regs[o[1]] if o[0] == 'memreg' else (o[1] if o[0] == 'memimm' else rd(o))
            wr(ops[0][1], mem.get(addr, 0))
            flags = None
            pc += 1
        elif op.startswith('store'):
            o = ops[0]
            addr = regs[o[1]] if o[0] == 'memreg' else (o[1] if o[0] == 'memimm' else rd(o))
            mem[addr] = rd(ops[1])
            flags = None
            pc += 1
        else:
            raise AssertionError(f'第 {line} 行: 未知指令 {op}')
    return 'timeout', steps, nin


class Crane:
    """campaign/tower/test.si 中 level_input / check_output_switched 的翻译"""

    def __init__(self, height, src, dst):
        self.target = dst
        self.plates = [src] * height + [-1] * (5 - height)
        self.mag_pos, self.mag_lifted, self.failed = 0, -1, False

    def level_input(self, v):
        if v in (0, 1, 2):
            self.mag_pos = v
        elif v == 5:
            if self.mag_lifted == -1:
                for i in range(5):
                    if self.plates[i] == self.mag_pos:
                        self.mag_lifted = i
                        break
            else:
                for i in range(self.mag_lifted):
                    if self.plates[i] == self.mag_pos:
                        self.failed = True
                        break
                self.plates[self.mag_lifted] = self.mag_pos
                self.mag_lifted = -1

    def is_win(self):
        for i in range(5):
            if self.plates[i] == -1:
                return True
            if self.plates[i] != self.target:
                return False
        return True


def ref_moves(n, src, dst, spare, acc):
    if n == 0:
        acc.append((src, dst))
        return
    ref_moves(n - 1, src, spare, dst, acc)
    acc.append((src, dst))
    ref_moves(n - 1, spare, dst, src, acc)


def selftest():
    """用游戏自带的示例程序校验解释器(call/ret/push/pop/循环/内存)。"""
    # 1) campaign/symphony_11_functions/new_program.asm 的等价内容: 2^5 = 32
    funcs = '''
const RES = r1
const ARG_1 = r1
const ARG_2 = r2
in ARG_1
in ARG_2
call power
out RES
multiply:
    push r3
    const LHS = r1
    const RHS = r2
    const ACC = r3
    mov ACC, 0
    jmp mul_condition
    mul_start:
    sub RHS, RHS, 1
    add ACC, ACC, LHS
    mul_condition:
    cmp RHS, 0
    jne mul_start
    mov RES, ACC
    pop r3
    ret
power:
    push r3
    push r4
    const BASE = r3
    const REM_POW = r4
    mov BASE, ARG_1
    sub REM_POW, ARG_2, 1
    pow_start:
    sub REM_POW, REM_POW, 1
    mov ARG_2, BASE
    call multiply
    pow_condition:
    cmp REM_POW, 0
    jne pow_start
    pop r4
    pop r3
    ret
'''
    outs = []
    instrs, labels = assemble(funcs)
    run(instrs, labels, [2, 5], lambda v: outs.append(v))
    assert outs == [32], f'函数示例应输出 32, 实际 {outs}'
    print('自检 1: 游戏自带函数示例输出 32  [通过]')

    # 2) 仓库里已过关的 sort.asm: 16 个数排序
    import random as _r
    data = [_r.getrandbits(20) for _ in range(16)]
    outs2 = []
    instrs, labels = assemble(open(os.path.join(HERE, 'sort.asm'), encoding='utf-8').read())
    run(instrs, labels, data, lambda v: outs2.append(v))
    assert outs2 == sorted(data), 'sort.asm 输出应等于升序'
    print('自检 2: sort.asm 冒泡排序结果正确  [通过]')

    # 3) 仓库里已过关的 random.asm: 输出必须随种子变化(只验证能持续产出)
    outs3 = []
    instrs, labels = assemble(open(os.path.join(HERE, 'random.asm'), encoding='utf-8').read())
    run(instrs, labels, [0x1234], lambda v: outs3.append(v) if len(outs3) < 5 else 'win')
    assert len(set(outs3)) > 1, 'random.asm 应持续产出不同的值'
    print('自检 3: random.asm 伪随机序列正常  [通过]')


def isa_opcodes(isa_path):
    """从 Symphony.asm(spec.isa)的 [instructions] 段取出全部合法助记符。

    用来卡住"用了架构里还没有的指令"这类错误 —— 例如 push/pop/call/ret/const
    要等 Stack、Functions、Aliases 关才会作为同义指令补进来,当前架构里没有。
    """
    ops, section = set(), None
    for raw in open(isa_path, encoding='utf-8').read().splitlines():
        line = raw.strip()
        if line.startswith('['):
            section = line
            continue
        if section != '[instructions]' or not line or line.startswith('#'):
            continue
        head = line.split()[0]
        if re.fullmatch(r'[a-z_][a-z0-9_]*', head):   # 编码行/寄存器行不以助记符开头
            ops.add(head)
    return ops


def check_opcodes(instrs, isa_path):
    allowed = isa_opcodes(isa_path)
    used = {op for op, _, _ in instrs}
    unknown = sorted(used - allowed)
    print(f'用到的助记符: {" ".join(sorted(used))}')
    if unknown:
        print(f'!!! 架构里没有这些指令: {" ".join(unknown)}')
        return False
    print(f'所有助记符都在 {os.path.basename(isa_path)} 里  [通过]')
    return True


def main(path):
    selftest()
    if not check_opcodes(assemble(open(path, encoding='utf-8').read())[0],
                         os.path.join(HERE, 'Symphony.asm')):
        return 1
    instrs, labels = assemble(open(path, encoding='utf-8').read())
    print(f'{path}: {len(instrs)} 条指令, 标签 {sorted(labels)}')
    bad = 0
    for disk_nr in (2, 3, 4):
        for src in range(3):
            for dst in range(3):
                if src == dst:
                    continue
                spare = 3 - src - dst
                crane = Crane(disk_nr + 1, src, dst)
                moves = []

                def on_out(v, crane=crane, moves=moves):
                    lifted = crane.mag_lifted
                    frm = crane.plates[lifted] if lifted != -1 else None
                    crane.level_input(v)
                    if crane.failed:
                        return 'fail'
                    if v == 5 and lifted != -1:
                        moves.append((frm, crane.plates[lifted]))
                    return 'win' if crane.is_win() else None

                outcome, steps, nin = run(instrs, labels,
                                          [disk_nr, src, dst, spare], on_out)
                want = []
                ref_moves(disk_nr, src, dst, spare, want)
                ok = outcome == 'win' and moves == want and nin == 4
                bad += 0 if ok else 1
                print(f'  {"PASS" if ok else "FAIL"} disk_nr={disk_nr} {src}->{dst} '
                      f'spare={spare} 结局={outcome} 步数={steps} 输入数={nin} '
                      f'动作数={len(moves)} 末态={crane.plates}')
    print('全部 18 个用例通过' if not bad else f'{bad} 个用例失败')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'hanoi.asm')))
