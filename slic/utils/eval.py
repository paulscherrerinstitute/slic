import ast
import operator


BIN_OPS = {
    ast.Add:  operator.add,
    ast.Sub:  operator.sub,
    ast.Mult: operator.mul,
    ast.Div:  operator.truediv,
    ast.Mod:  operator.mod
}

UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg
}


def forgiving_eval(value):
    try:
        return arithmetic_eval(value)
    except:
        return value


def arithmetic_eval(s):
    node = ast.parse(s, mode="eval")
    return ast_node_eval(node.body)


def ast_node_eval(node):
    if isinstance(node, ast.Expression):
        return ast_node_eval(node.body)
    elif isinstance(node, ast.Str):
        return node.s
    elif isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.BinOp):
        op_type = type(node.op)
        op = BIN_OPS[op_type]
        left  = ast_node_eval(node.left)
        right = ast_node_eval(node.right)
        return op(left, right)
    elif isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        op = UNARY_OPS[op_type]
        operand = ast_node_eval(node.operand)
        return op(operand)
    else:
        type_name = type(node).__name__
        raise ArithmeticEvalError("Unsupported node type {}".format(type_name))



class ArithmeticEvalError(Exception):
    pass



#TODO:
#print like SyntaxError:
#    "something with an error here"
#                             ^
#this needs full string and offset of current node within full string stored



