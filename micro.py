import sys
import re

def write(string="", pad=4):
    with open("out.asm", "a") as fhandle:
        print(" "*pad + string, file=fhandle)

if __name__ == "__main__":
    file = sys.argv[1]
    
    # Limpa o arquivo
    with open("out.asm", "w") as f:
        pass
    
    # Pega o texto
    text = ""
    with open(file, "r") as fhandle:
        text = fhandle.read()

    # Variaveis "Globais"
    label_if = 0
    label_wh = 0
    tem_else = False
    x, y, z = None, None, None
    q, w, t = None, None, None

    cmp = {
        "==":"je",
        "!=":"jne",
        ">":"jg",
        ">=":"jge",
        "<":"jl",
        "<=":"jle"
    }

    anti_cmp = {
        "je":"jne",
        "jne":"je",
        "jg":"jle",
        "jle":"jg",
        "jl":"jge",
        "jge":"jl"
    }

    nvars = sorted(set(re.findall("[r][0-9]{1,2}", text)))
    write("section .data", 0)
    write("scan:  db  \"%d\", 0")
    write("print:  db  \"%d\", 10, 0")
    for i in nvars:
        write("r{} dd 0".format(i))
    write()
    write("section .text", 0)
    write("global main")
    write("extern scanf")
    write("extern printf\n")
    write("main:", 0)

    for line in text.split("\n"):
        args = [i if re.match("[r][0-9]{1,2}", i) == None else 'r'+i for i in line.strip().split()]
        if len(args) == 0:
            continue

        # ----- Desvio ------
        if args[0] == "if":
            op = cmp[args[2]]
            x, y, z = args[1], args[3], op

            if x.isdecimal():
                write("mov eax, {}".format(x))
            else:
                write("mov eax, [{}]".format(x))
            
            if y.isdecimal():
                write("mov ebx, {}".format(y))
            else:
                write("mov ebx, [{}]".format(y))

            write("cmp eax, ebx")
            write("{} if{}".format(op, label_if))
            write("jmp endif{}".format(label_if))
            write("if{}:".format(label_if))

        # ----- Desvio Cont. -----
        elif args[0] == "else":
            write("jmp resto{}".format(label_if))
            write("else{}:".format(label_if))
            tem_else = True
        
        # ----- Fim Desvio -----
        elif args[0] == "endif":
            if tem_else:
                write("jmp resto{}".format(label_if))
                write("endif{}:".format(label_if))
                tem_else = False

                if x.isdecimal():
                    write("mov eax, {}".format(x))
                else:
                    write("mov eax, [{}]".format(x))
                
                if y.isdecimal():
                    write("mov ebx, {}".format(y))
                else:
                    write("mov ebx, [{}]".format(y))

                write("cmp eax, ebx")
                write("{} else{}".format(anti_cmp[z], label_if))
                write("resto{}:".format(label_if))
            else:
                write("endif{}:".format(label_if))
            
            label_if += 1

        # ----- Loop ------
        elif args[0] == "while":
            q, w, t = args[1], args[2], args[3]
            write("while{}:".format(label_wh))
        
        # ----- Fim Loop -----
        elif args[0] == "endwhile":
            # w = anti_cmp[cmp[w]]
            write("mov eax, [{}]".format(q))
            
            if t.isdecimal():
                write("mov ebx, {}".format(t))
            else:
                write("mov ebx, [{}]".format(t))
            
            write("cmp eax, ebx")
            write("{} while{}".format(cmp[w], label_wh))
            label_wh += 1

        # ----- Impressão ------        
        elif args[0] == "print":
            write("push dword[{}]".format(args[1]))
            write("push print")
            write("call printf")
            write("add esp, 8")

        elif args[0] == "scan":
            write("push dword[{}]".format(args[1]))
            write("push scan")
            write("call scanf")
            write("add esp, 8")

        # ----- Atribuição -----
        elif args[1] == "=":

            # ri = expr op expr
            if len(args) == 5:
                op = {
                    "+":"add",
                    "-":"sub",
                    "*":"imul",
                    "&":"and",
                    "|":"or",
                    "^":"xor"
                }

                # SHIFT
                if args[3] == ">>" or args[3] == "<<":
                    op = {
                        ">>":"shr",
                        "<<":"shl"
                    }

                    # ri = const op const
                    if args[2].isdecimal() and args[4].isdecimal():
                        write("mov eax, {}".format(args[2]))
                        write("{} eax, {}".format(op[args[3]], args[4]))
                        write("mov dword[{}], eax".format(args[0]))

                    # ri = const op rj
                    elif args[2].isdecimal():
                        write("mov eax, {}".format(args[2]))
                        write("mov cl, [{}]".format(args[4]))
                        write("{} eax, cl".format(op[args[3]], args[4]))
                        write("mov dword[{}], eax".format(args[0]))

                    # ri = rj op const
                    elif args[4].isdecimal():
                        write("mov eax, [{}]".format(args[2]))
                        write("{} eax, {}".format(op[args[3]], args[4]))
                        write("mov dword[{}], eax".format(args[0]))

                    # ri = rj op rk
                    elif args[3] in op:
                        write("mov eax, [{}]".format(args[2]))
                        write("mov cl, [{}]".format(args[4]))
                        write("{} eax, cl".format(op[args[3]], args[4]))
                        write("mov dword[{}], eax".format(args[0]))

                # DIV & MOD
                elif args[3] == "/" or args[3] == "%":
                    write("mov edx, 0")

                    if args[3] == "/":
                        opr = "eax"
                    else:
                        opr = "edx"

                    # ri = const op const
                    if args[2].isdecimal() and args[4].isdecimal():
                        write("mov eax, {}".format(args[2]))
                        write("mov ebx, {}".format(args[4]))
                        write("idiv ebx")
                        write("mov dword[{}], {}".format(args[0], opr))

                    # ri = const op rj
                    elif args[2].isdecimal():
                        write("mov eax, {}".format(args[2]))
                        write("mov ebx, [{}]".format(args[4]))
                        write("idiv ebx")                        
                        write("mov dword[{}], {}".format(args[0], opr))

                    # ri = rj op const
                    elif args[4].isdecimal():
                        write("mov eax, [{}]".format(args[2]))
                        write("mov ebx, {}".format(args[4]))
                        write("idiv ebx")                        
                        write("mov dword[{}], {}".format(args[0], opr))

                    # ri = rj op rk
                    else:
                        write("mov eax, [{}]".format(args[2]))
                        write("mov ebx, [{}]".format(args[4]))
                        write("idiv ebx")                        
                        write("mov dword[{}], {}".format(args[0], opr))

                # OUTROS
                # ri = const op const
                elif args[2].isdecimal() and args[4].isdecimal():
                    write("mov eax, {}".format(args[2]))
                    write("{} eax, {}".format(op[args[3]], args[4]))
                    write("mov dword[{}], eax".format(args[0]))

                # ri = const op rj
                elif args[2].isdecimal():
                    write("mov eax, {}".format(args[2]))
                    write("{} eax, [{}]".format(op[args[3]], args[4]))
                    write("mov dword[{}], eax".format(args[0]))

                # ri = rj op const
                elif args[4].isdecimal():
                    write("mov eax, {}".format(args[4]))
                    write("{} eax, [{}]".format(op[args[3]], args[2]))
                    write("mov dword[{}], eax".format(args[0]))

                # ri = rj op rk
                elif args[3] in op:
                    write("mov eax, [{}]".format(args[2]))
                    write("{} eax, [{}]".format(op[args[3]], args[4]))
                    write("mov dword[{}], eax".format(args[0]))

            # ri = rj
            elif args[2].startswith("r"):
                write("mov eax, [{}]".format(args[2]))
                write("mov dword[{}], eax".format(args[0]))

            # ri = const
            elif args[2].isdecimal():
                write("mov dword[{}], {}".format(args[0], args[2]))

            # ri = uop expr;
            else:
                if args[2][0] == '~':
                    write("mov eax, [{}]".format(args[2][2:]))
                    write("not eax")
                    write("mov dword[{}], eax".format(args[2][2:]))
                else:
                    write("mov eax, [{}]".format(args[2][2:]))
                    write("neg eax")
                    write("mov dword[{}], eax".format(args[2][2:]))
