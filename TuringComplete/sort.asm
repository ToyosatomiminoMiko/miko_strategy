; Symphony 汇编：读 16 个数字，冒泡排序后输出
; 数组基址：0x0100，每个元素 32 位

start:
    mov r1, 0x0100      ; r1 = 数组基址
    mov r2, 0           ; r2 = 已读数量

read_loop:
    in r3               ; 从输入读一个数
    store_32 [r1], r3   ; 存入数组
    add r1, r1, 4       ; 下一个元素地址
    add r2, r2, 1
    cmp r2, 16
    jb read_loop        ; 未读满 16 个则继续

    ; 冒泡排序
    mov r1, 0x0100      ; 重新指向数组基址
    mov r10, 16         ; 外层循环 16 轮，简单起见不做提前退出

outer_loop:
    mov r3, 0           ; r3 = j，从 0 开始

inner_loop:
    lsl r7, r3, 2       ; r7 = j * 4
    add r7, r1, r7      ; r7 = &arr[j]
    add r8, r7, 4       ; r8 = &arr[j + 1]

    load_32 r4, [r7]    ; r4 = arr[j]
    load_32 r5, [r8]    ; r5 = arr[j + 1]

    cmp r4, r5
    jle no_swap         ; 如果 arr[j] <= arr[j+1]，不交换

    ; 交换 arr[j] 和 arr[j+1]
    store_32 [r7], r5
    store_32 [r8], r4

no_swap:
    add r3, r3, 1
    cmp r3, 15
    jb inner_loop       ; j < 15 继续内层循环

    sub r10, r10, 1
    cmp r10, 0
    jne outer_loop      ; 外层未结束则继续

    ; 输出排序后的 16 个数
    mov r1, 0x0100
    mov r2, 0

out_loop:
    load_32 r3, [r1]
    out r3
    add r1, r1, 4
    add r2, r2, 1
    cmp r2, 16
    jb out_loop

end:
    jmp end             ; 程序结束，停在这里
