; 尼姆博弈

in r1
loop:
sub r2, r1, 1
and r2, r2, 3
out r2
in r1
jmp loop
