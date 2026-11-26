"""Restricted numeric expression evaluator; never calls eval/exec."""
import ast
import math
import operator

class ExpressionError(ValueError):
    pass

_BIN = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Pow: operator.pow}
_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_FUNCS = {"min": min, "max": max, "abs": abs, "sqrt": math.sqrt,
          "sin": lambda x: math.sin(math.radians(x)),
          "cos": lambda x: math.cos(math.radians(x)),
          "tan": lambda x: math.tan(math.radians(x))}


def evaluate(expression, variables: dict[str, float]) -> float:
    if isinstance(expression, bool) or not isinstance(expression, (int, float, str)):
        raise ExpressionError("Expression must be a number or a string")
    if isinstance(expression, str) and len(expression) > 256:
        raise ExpressionError("Expression too long")
    try:
        tree = ast.parse(str(expression), mode="eval")
        if sum(1 for _ in ast.walk(tree)) > 80:
            raise ExpressionError("Expression too complex")

        def visit(node):
            if isinstance(node, ast.Expression):
                return visit(node.body)
            if isinstance(node, ast.Constant) and type(node.value) in (int, float):
                return float(node.value)
            if isinstance(node, ast.Name) and node.id in variables:
                return float(variables[node.id])
            if isinstance(node, ast.BinOp) and type(node.op) in _BIN:
                left, right = visit(node.left), visit(node.right)
                if isinstance(node.op, ast.Pow) and (abs(right) > 8 or abs(left) > 1e6):
                    raise ExpressionError("Power exceeds limits")
                return _BIN[type(node.op)](left, right)
            if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY:
                return _UNARY[type(node.op)](visit(node.operand))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and not node.keywords:
                fn = _FUNCS.get(node.func.id)
                if fn is not None and len(node.args) <= 2:
                    return fn(*(visit(a) for a in node.args))
            raise ExpressionError(f"Unsupported expression element: {type(node).__name__}")

        result = float(visit(tree))
        if not math.isfinite(result) or abs(result) > 1e9:
            raise ExpressionError("Non-finite or excessive result")
        return result
    except (SyntaxError, ZeroDivisionError, OverflowError, ValueError, TypeError) as exc:
        if isinstance(exc, ExpressionError):
            raise
        raise ExpressionError(f"Invalid expression {expression!r}: {exc}") from exc
