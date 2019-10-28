import sys

def write(string):
    with open("a.out", "a") as fhandle:
        print(string, file=fhandle)

if __name__ == "__main__":
    file = sys.argv[1]
    
    with open("a.out", "w") as f:
        pass

    text = ""
    with open(file, "r") as fhandle:
        text = fhandle.read().split("\n")

    write(".section data")
    for i in range(1, 33):
        write("r{} DD ?".format(i))
    write("")

    label = 0
    tem_else = False
    x, y, z = None, None, None
    for line in text:
        args = line.strip().split()

        # ----- Desvio ------
        if args[0] == "if":
            cmp = {
                "==":"je",
                "!=":"jne",
                ">":"jg",
                ">=":"jge",
                "<":"jl",
                "<=":"jle"
            }

            anti_op = {
                "je":"jne",
                "jne":"je",
                "jg":"jle",
                "jle":"jg",
                "jl":"jge",
                "jge":"jl"
            }

            op = cmp[args[2]]
            x, y, z = args[1], args[3], anti_op[op]

            if x.isdecimal():
                write("mov eax {}".format(x))
            else:
                write("mov eax [{}]".format(x))
            
            if y.isdecimal():
                write("mov ebx {}".format(y))
            else:
                write("mov ebx [{}]".format(y))

            write("cmp eax ebx")
            write("{} #if{}".format(op, label))
            write("jmp #endif{}".format(label))
            write("#if{}".format(label))

        # ----- Desvio Cont. -----
        elif args[0] == "else":
            write("#else{}".format(label))
            tem_else = True
        
        # ----- Fim Desvio -----
        elif args[0] == "endif":
            write("#endif{}".format(label))
            if tem_else:
                tem_else = False

                if x.isdecimal():
                    write("mov eax {}".format(x))
                else:
                    write("mov eax [{}]".format(x))
                
                if y.isdecimal():
                    write("mov ebx {}".format(y))
                else:
                    write("mov ebx [{}]".format(y))

                write("cmp eax ebx")
                write("{} #else{}".format(z, label))
            
            label += 1

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
                        write("mov eax {}".format(args[2]))
                        write("{} eax {}".format(op[args[3]], args[4]))
                        write("mov [{}] eax".format(args[0]))

                    # ri = const op rj
                    elif args[2].isdecimal():
                        write("mov eax {}".format(args[2]))
                        write("mov cl [{}]".format(args[4]))
                        write("{} eax cl".format(op[args[3]], args[4]))
                        write("mov [{}] eax".format(args[0]))

                    # ri = rj op const
                    elif args[4].isdecimal():
                        write("mov eax [{}]".format(args[2]))
                        write("{} eax {}".format(op[args[3]], args[2]))
                        write("mov [{}] eax".format(args[0]))

                    # ri = rj op rk
                    elif args[3] in op:
                        write("mov eax [{}]".format(args[2]))
                        write("mov cl [{}]".format(args[4]))
                        write("{} eax cl".format(op[args[3]], args[4]))
                        write("mov [{}] eax".format(args[0]))

                # DIV & MOD
                elif args[3] == "/" or args[3] == "%":
                    write("mov ebx 0")

                    if args[3] == "/":
                        op = "eax"
                    else:
                        op = "ebx"

                    # ri = const op const
                    if args[2].isdecimal() and args[4].isdecimal():
                        write("mov eax {}".format(args[2]))
                        write("mov edx {}".format(args[4]))
                        write("idiv edx".format(args[4]))
                        write("mov [{}] {}".format(args[0], op))

                    # ri = const op rj
                    elif args[2].isdecimal():
                        write("mov eax {}".format(args[2]))
                        write("mov edx [{}]".format(args[4]))
                        write("idiv edx".format(args[4]))                        
                        write("mov [{}] eax".format(args[0]))

                    # ri = rj op const
                    elif args[4].isdecimal():
                        write("mov eax [{}]".format(args[2]))
                        write("mov edx {}".format(args[4]))
                        write("idiv edx".format(args[4]))                        
                        write("mov [{}] eax".format(args[0]))

                    # ri = rj op rk
                    write("mov eax [{}]".format(args[2]))
                    write("mov edx [{}]".format(args[4]))
                    write("idiv edx".format(args[4]))                        
                    write("mov [{}] eax".format(args[0]))

                # OUTROS
                # ri = const op const
                elif args[2].isdecimal() and args[4].isdecimal():
                    write("mov eax {}".format(args[2]))
                    write("{} eax {}".format(op[args[3]], args[4]))
                    write("mov [{}] eax".format(args[0]))

                # ri = const op rj
                elif args[2].isdecimal():
                    write("mov eax {}".format(args[2]))
                    write("{} eax [{}]".format(op[args[3]], args[4]))
                    write("mov [{}] eax".format(args[0]))

                # ri = rj op const
                elif args[4].isdecimal():
                    write("mov eax {}".format(args[4]))
                    write("{} eax [{}]".format(op[args[3]], args[2]))
                    write("mov [{}] eax".format(args[0]))

                # ri = rj op rk
                elif args[3] in op:
                    write("mov eax [{}]".format(args[2]))
                    write("{} eax [{}]".format(op[args[3]], args[4]))
                    write("mov [{}] eax".format(args[0]))

            # ri = rj
            elif args[2].startswith("r"):
                write("mov eax [{}]".format(args[2]))
                write("mov [{}] eax".format(args[0]))

            # ri = const
            elif args[2].isdecimal():
                write("mov [{}] {}".format(args[0], args[2]))

            # ri = uop expr;
            else:
                if args[2][0] == '~':
                    write("mov eax [{}]".format(args[2][2:]))
                    write("not eax")
                    write("mov [{}] eax".format(args[2][2:]))
                else:
                    write("mov eax [{}]".format(args[2][2:]))
                    write("neg eax")
                    write("mov [{}] eax".format(args[2][2:]))
