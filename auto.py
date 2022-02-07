import string

states = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
start = 0
finals = [4, 5, 6, 9, 10]
buffer = 0
operands = []
operators = []
table_names = []
table_type = []
result = []
temp_var = 1
alphabet = [" ",    # 0
            "_" + string.ascii_uppercase.replace("E", "") + string.ascii_lowercase.replace("e", ""),  # 1
            string.digits,  # 2
            "=",    # 3
            "*",    # 4
            "+",    # 5
            "-",    # 6
            ".",    # 7
            "(",    # 8
            ")",    # 9
            "Ee"]   # 10

operators_rang = ["=", "(", "+", "*"]

delta = [   # _   a   0   =   *   +   -   .   (   )   E
            [ 0,  1, -1, -1, -1, -1, -1, -1, -1, -1,  1],  # 0
            [ 3,  1,  1,  2, -1, -1, -1, -1, -1, -1,  1],  # 1
            [ 2,  4,  5, -1, -1, -1, -1, -1,  2, -1,  4],  # 2
            [ 3, -1, -1,  2, -1, -1, -1, -1, -1, -1, -1],  # 3
            [10,  4,  4, -1,  2,  2, -1, -1, -1, 10,  4],  # 4
            [10, -1,  5, -1,  2,  2, -1,  6, -1, 10,  7],  # 5
            [10, -1,  6, -1,  2,  2, -1, -1, -1, 10,  7],  # 6
            [-1, -1,  9, -1, -1,  8,  8, -1, -1, -1, -1],  # 7
            [-1, -1,  9, -1, -1, -1, -1, -1, -1, -1, -1],  # 8
            [10, -1,  9, -1,  2,  2, -1, -1, -1, 10, -1],  # 9
            [10, -1, -1, -1,  2,  2, -1, -1, -1, 10, -1]   # 10
]

actions = [# _  a  0  =  *  +  -  .  (  )  E
            [0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 3],  # 0
            [0, 5, 5, 7, 0, 0, 0, 0, 0, 0, 5],  # 1
            [0, 3, 4, 0, 0, 0, 0, 0, 1, 0, 3],  # 2
            [0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0],  # 3
            [0, 5, 5, 0, 6, 6, 0, 0, 0, 2, 5],  # 4
            [0, 0, 5, 0, 6, 6, 0, 5, 0, 2, 5],  # 5
            [0, 0, 5, 0, 6, 6, 0, 0, 0, 2, 5],  # 6
            [0, 0, 5, 0, 0, 5, 5, 0, 0, 0, 0],  # 7
            [0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0],  # 8
            [0, 0, 5, 0, 6, 6, 0, 0, 0, 2, 0],  # 9
            [0, 0, 0, 0, 6, 6, 0, 0, 0, 2, 0]   # 10
]


def get_expression():
    try:
        fail_input = open('input.txt', 'r')
    except IOError as e:
        print("ERROR, NOT FILE")
        return ""
    else:
        with fail_input:
            expression = fail_input.read()
            fail_input.close()

    return expression


def create_code():
    global temp_var, result, table_names

    operand_1 = operands.pop()
    operand_2 = operands.pop()
    op = operators.pop()

    if op == operators_rang[3]:
        operator = "MPY"
    elif op == operators_rang[2]:
        operator = "ADD"
    else:
        if result:  # запись перед "="
            result[-1][1] = operand_2
        else:   # если после "=" один элемент
            result.append(["LOAD", operand_1])
            result.append(["STORE", operand_2])
        return

    if operand_1 in table_names and operand_2 in table_names:
        result.append(["LOAD", operand_1])
        result.append([operator, operand_2])
    else:
        # избавиться от лишних временных переменных
        if result[-1][0] == "STORE":
            result.pop()
            temp_var -= 1

        if operand_1 in table_names:
            result.append([operator, operand_1])
        else:
            result.append([operator, operand_2])

    result.append(["STORE", "$" + str(temp_var)])
    operands.append("$" + str(temp_var))
    temp_var += 1


def action(actionId, symbol):
    global buffer, table_names, operands, operators

    if actionId == 1:
        buffer += 1
        operators.append(symbol)

    if actionId == 2:
        buffer -= 1
        if buffer < 0:
            return -1

        if operators_rang[1] in operators:
            operators.reverse()
            operators.remove(operators_rang[1])
            operators.reverse()
            create_code()

    if actionId == 3:
        operands.append(symbol)
        table_names.append(symbol)
        table_type.append("VAR")

    if actionId == 4:
        operands.append(symbol)
        table_names.append(symbol)
        table_type.append("CONST")

    if actionId == 5:
        table_names[-1] += symbol
        operands[-1] += symbol

    if actionId == 6:
        while operators_rang.index(operators[-1]) >= operators_rang.index(symbol):
            create_code()

        operators.append(symbol)

    if actionId == 7:
        operators.append(symbol)

    if actionId == -1:
        while operators and operands:
            create_code()

    return 0


def search_index_alphabet(symbol):
    for i in range(len(alphabet)):
        if symbol in alphabet[i]:
            return i
    return -1


def auto(expression):
    global buffer, actions, delta, alphabet, finals

    if start not in states:
        print("ERROR START TATE \"" + str(start) + "\"")
        return 0

    state = start

    for symbol in expression:
        indexAlphabet = search_index_alphabet(symbol)

        if indexAlphabet == -1:
            print("ERROR, NOT SYMBOL \"" + symbol + "\" IN ALPHABET")
            return

        actionId = action(actions[state][indexAlphabet], symbol)

        if actionId == -1:
            print("ERROR ACTION")
            return

        if delta[state][indexAlphabet] not in states:
            print("ERROR STATE \"" + str(state) + "\"")
            return

        state = delta[state][indexAlphabet]

        # print(symbol + "[" + str(state) + "][" + str(indexAlphabet) + "]")
    print("EXPRESSION: \"" + expression + "\"")
    if state in finals and not buffer:
        action(-1, "")
        print("GOOD FINAL")

        print("TABLE NAMES:")
        for i in range(len(table_names)):
            print("[" + table_type[i], table_names[i], end="]\n")

        print("\nRESULT:")
        for i in result:
            print(i)
    else:
        print("ERROR FINAL")


auto(get_expression())
