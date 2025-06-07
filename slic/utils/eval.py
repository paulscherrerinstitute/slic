import ast
import operator

from .utils import typename


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


def defaulting_eval(value, default=None):
    try:
        return arithmetic_eval(value)
    except:
        return default


def arithmetic_eval(s):
    node = ast.parse(s, mode="eval")
    return ast_node_eval(node.body)


def ast_node_eval(node):
    if isinstance(node, ast.Expression):
        return ast_node_eval(node.body)
    elif isinstance(node, ast.BinOp):
        op = get_operator(node, BIN_OPS)
        left  = ast_node_eval(node.left)
        right = ast_node_eval(node.right)
        return op(left, right)
    elif isinstance(node, ast.UnaryOp):
        op = get_operator(node, UNARY_OPS)
        operand = ast_node_eval(node.operand)
        return op(operand)
    # from >=3.8, Constant can replace Str/Num
    # from >=3.14, Str/Num are deprecated and removed
    # check Constant first then fall back to Str/Num for <3.8
    elif isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.Str):
        return node.s
    elif isinstance(node, ast.Num):
        return node.n
    else:
        tn = typename(node)
        raise ArithmeticEvalError(f"Unsupported node type {tn}")


def get_operator(node, ops):
    op_type = type(node.op)
    try:
        op = ops[op_type]
    except KeyError as e:
        nn = typename(node)
        on = typename(node.op)
        raise ArithmeticEvalError(f"Unsupported {nn} {on}") from e
    else:
        return op


class ArithmeticEvalError(Exception):
    pass



#TODO:
#print like SyntaxError:
#    "something with an error here"
#                             ^
#this needs full string and offset of current node within full string stored



