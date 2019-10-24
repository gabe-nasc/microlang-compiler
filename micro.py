import sys

def write(string):
    with open("a.out", "w+") as fhandle:
        print(string, file=fhandle)

if __name__ == "__main__":
    file = sys.argv[1]

    text = ""
    with open(file, "r") as fhandle:
        text = fhandle.read().split("\n")

    write(
        '''
        .DATA
        r DD 33 DUP(?)

        '''
    )

    for line in text:
        args = line.strip().split()

        # Atribuição
        if args[1] == "=":

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

                # ri = const op const
                if args[2].isdecimal() and args[4].isdecimal():
                    write("mov eax {}".format(args[2]))
                    write("{} eax {}".format(op[args[3]], args[4]))
                    write("mov [r+{}] eax".format(args[0][1:]))
                
                # ri = const op rj
                elif args[2].isdecimal():
                    write("mov eax {}".format(args[2]))
                    write("{} eax [r+{}]".format(op[args[3]], args[4][1:]))
                    write("mov [r+{}] eax".format(args[0][1:]))
                
                # ri = rj op const
                elif args[4].isdecimal():
                    write("mov eax {}".format(args[4]))
                    write("{} eax [r+{}]".format(op[args[3]], args[2][1:]))
                    write("mov [r+{}] eax".format(args[0][1:]))
                
                # ri = rj op rk
                elif args[3] in op:
                    write("mov eax [r+{}]".format(args[2][1:]))
                    write("{} eax [r+{}]".format(op[args[3]], args[4][1:]))
                    write("mov [r+{}] eax".format(args[0][1:]))

                # -----> FALTA A DIVISÃO <-------

            # ri = rj
            elif args[2].startswith("r"):
                write("mov eax [r+{}]".format(args[2][1:]))
                write("mov [r+{}] eax".format(args[0][1:]))

            # ri = const
            elif args[2].isdecimal():
                write("mov [r+{}] {}".format(args[0][1:], arg[2]))

            # ri = uop expr;
            else:
                if args[2][0] == '~':
                    write("mov eax [r+{}]".format(args[2][2:]))
                    write("not eax")
                    write("mov [r+{}] eax".format(args[2][2:]))
                else:
                    write("mov eax [r+{}]".format(args[2][2:]))
                    write("neg eax")
                    write("mov [r+{}] eax".format(args[2][2:]))
                    