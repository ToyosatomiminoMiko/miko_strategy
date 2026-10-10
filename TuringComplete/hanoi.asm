; =============================================================================
; 汉诺塔 / Tower of Hanoi —— Turing Complete,Symphony 架构汇编
;
; 是什么:
;   输入 4 个数(顺序固定):
;     in r4 = disk_nr     最大盘号(2~4,盘号从 0 开始,共 N = disk_nr+1 个盘子)
;     in r5 = source      起始金属针
;     in r6 = destination 目标金属针
;     in r7 = spare       第三根金属针
;   输出:0/1/2 = 电磁铁移到 0/1/2 号针;5 = 切换电磁铁(吸住 / 放下)。
;   一次搬运 = out 源针 / out 5 / out 目标针 / out 5。
;   盘号不用自己记:磁铁在哪根针上,关卡脚本就吸走该针最上面(最小)的盘。
;
; 为什么不用 push/pop/call/ret:
;   本架构(spec.isa / Symphony.asm)里没有这几条,它们要等 Stack、Functions 关
;   才会作为"同义指令"补进来;const 也没有。所以本程序只用列在 Symphony.asm 里的
;   指令:in/out/mov/add/sub/and/lsl/lsr/cmp/je/jne/jb/jbe/jmp。
;   既不用栈,也不碰内存,因此与 RAM 大小、sp 初值都无关。
;
; 为什么这样算(无递归的闭式公式,推导):
;   把三根针按"位置"编号:position 0 = source,1 = destination,2 = spare。
;   经典结论:第 m 次搬运(1 基)动的是 d = ctz(m) 号盘(最低位 1 的下标),
;   而 d 号盘在它第 j 次搬运后位于 position (s_d * j) mod 3:
;     - 最小的 0 号盘每 2 步动一次,方向 s_0 = +1(N 为奇数)或 -1(N 为偶数);
;     - 每大一档,方向取反:s_d = s_0 * (-1)^d。
;   设 q = m >> (d+1)(d 号盘此前已搬过的次数),于是
;     起点 position = (s_d * q) mod 3,终点 position = (起点 + s_d) mod 3,
;   再各自映射回针号即可。所以整段程序是"由 m 直接算出动作"的无状态循环。
;   校验例子(N=3, source=0, destination=1, spare=2):m=1..7 得到
;   0→1, 0→2, 1→2, 0→1, 2→0, 2→1, 0→1,与递归解完全一致。
;   取模用减法循环完成:q <= 2^5/2 = 15,最多减 5 次,不需要除法指令。
;
; 寄存器分配:
;   r4 = N(盘数)        r5/r6/r7 = source/destination/spare
;   r8 = m(当前第几次)  r9 = 2^N-1(总次数)   r10 = s_0
;   r1 = d   r2 = q   r3 = s_d(之后临时存"目标针")
;   r11 = 起点 position  r12 = 终点 position  r13 = 临时/"源针"
;
; 元信息:由 DSH 依据 Symphony.asm(spec.isa)与关卡脚本 tower/test.si 编写。
; =============================================================================

start:
    in r4                       ; disk_nr
    in r5                       ; source
    in r6                       ; destination
    in r7                       ; spare
    add r4, r4, 1               ; N = disk_nr + 1

    ; s_0 = +1(等价 1)当 N 为奇数, -1 当 N 为偶数;取模 3 意义下 -1 记作 2
    and r13, r4, 1
    mov r10, 2                  ; 先按"N 偶"填 2
    cmp r13, 0
    je base_sign_ready
    mov r10, 1                  ; N 奇 -> 1
base_sign_ready:

    ; r9 = 2^N - 1,即总搬运次数
    mov r9, 1
    mov r13, r4
limit_shift:
    lsl r9, r9, 1
    sub r13, r13, 1
    cmp r13, 0
    jne limit_shift
    sub r9, r9, 1

    mov r8, 1                   ; m = 1
move_loop:
    ; --- d = ctz(m):右移直到最低位是 1 ---
    mov r1, 0
    mov r2, r8
ctz_loop:
    and r13, r2, 1
    cmp r13, 0
    jne ctz_done
    lsr r2, r2, 1
    add r1, r1, 1
    jmp ctz_loop
ctz_done:
    lsr r2, r2, 1               ; 去掉那个 1 位 -> q = m >> (d+1)

    ; --- s_d = s_0(d 偶)或 3 - s_0(d 奇) ---
    and r13, r1, 1
    mov r3, r10
    cmp r13, 0
    je sign_ready
    mov r3, 3
    sub r3, r3, r10
sign_ready:

    ; --- 起点 position = (s_d * q) mod 3 ---
    mov r13, r2                 ; r13 = q
mod3_loop:
    cmp r13, 3
    jb mod3_done
    sub r13, r13, 3
    jmp mod3_loop
mod3_done:                      ; r13 = q mod 3
    cmp r3, 1
    je pos_forward
    mov r11, 3                  ; s_d = 2 即 -1:pos = (3 - q mod 3) mod 3
    sub r11, r11, r13
    cmp r11, 3
    jne pos_ready
    mov r11, 0
    jmp pos_ready
pos_forward:
    mov r11, r13
pos_ready:

    ; --- 终点 position = (起点 + s_d) mod 3 ---
    add r12, r11, r3
    cmp r12, 3
    jb pos_out_ready
    sub r12, r12, 3
pos_out_ready:

    ; --- position -> 针号:order = [source, destination, spare] ---
    mov r13, r5                 ; 起点 position 0 -> source
    cmp r11, 0
    je from_ready
    mov r13, r6                 ; position 1 -> destination
    cmp r11, 1
    je from_ready
    mov r13, r7                 ; position 2 -> spare
from_ready:

    mov r3, r5                  ; 终点 position 0 -> source
    cmp r12, 0
    je to_ready
    mov r3, r6                  ; position 1 -> destination
    cmp r12, 1
    je to_ready
    mov r3, r7                  ; position 2 -> spare
to_ready:

    out r13                     ; 电磁铁移到源针
    out 5                       ; 开磁铁,吸住最上面的盘
    out r3                      ; 电磁铁移到目标针
    out 5                       ; 关磁铁,放下盘

    add r8, r8, 1
    cmp r8, r9
    jbe move_loop               ; 还有搬运次数就继续

halt:
    jmp halt
