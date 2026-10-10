; 千变万化
; 初始化：从标准输入读取随机种子 (seed) 到寄存器 r4
in r4 ; r4 = seed (直接用 r4 保存种子)

; 循环标签
loop:
    ; 步骤 1: temp1 = seed xor (seed lsr 13)
    lsr r2, r4, 13      ; r2 = seed 逻辑右移 13 位
    xor r2, r4, r2      ; r2 = seed 异或 r2 (结果存回 r2，即 temp1)
	; r2 = temp1
	
    ; 步骤 2: temp2 = temp1 xor (temp1 lsl 17)
    lsl r3, r2, 17      ; r3 = temp1 逻辑左移 17 位
    xor r3, r2, r3      ; r3 = temp1 异或 r3 (结果存回 r3，即 temp2)
	; r3 = temp2
	
    ; 步骤 3: result = temp2 xor (temp2 lsr 5)
    lsr r1, r3, 5       ; r1 = temp2 逻辑右移 5 位
    xor r4, r3, r1      ; r4 = temp2 异或 r1 (直接将 result 存入 r4)
    ; r4 = result
    
    ; 此时 r4 既是 result，也是下一次循环的 seed
    ; 更新种子这一步被自然地融合在了上一步中，无需 mov
    
    ; 输出生成的随机数
    out r4              ; 将寄存器 r4 的值发送到标准输出
    ; 无限循环，生成下一个伪随机数
    jmp loop