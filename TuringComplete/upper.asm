; 将每个单词的首字母改为大写
; r1: 当前读入/输出的字符
; r2: 单词开始标志，1 表示在单词开头，0 表示不在单词开头

    mov r2, 1          ; 初始认为在单词开头

loop:
    in r1              ; 从标准输入读入一个 ASCII 字符
    cmp r1, 0
    je done            ; 读到 0，结束
    cmp r1, 10
    je done            ; 读到换行符，结束
    cmp r1, 32
    je space           ; 读到空格

    ; 非空格字符（只可能是 a-z）
    cmp r2, 0
    je lower           ; 不在单词开头，直接输出

    ; 在单词开头，将小写字母转大写
    sub r1, r1, 32
    mov r2, 0
    out r1
    jmp loop

lower:
    out r1
    jmp loop

space:
    out r1
    mov r2, 1          ; 空格后，下一个字母是单词开头
    jmp loop

done:
    out 10             ; 输出换行
stop:
    jmp stop           ; 停机
