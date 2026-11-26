"""Ordered, typed construction operations with geometric diagnostics.
All dimensions are centimeters. Operations are evaluated sequentially.
"""
from dataclasses import dataclass, field
from math import cos, sin, radians
from .expressions import evaluate, ExpressionError
from .geometry import Point, distance, intersection, cubic, signed_area, self_intersects, EPS

class PatternError(ValueError):
    pass

@dataclass
class BuildResult:
    points: dict[str, Point]
    curves: dict[str, list[Point]]
    pieces: dict[str, list[Point]]
    diagnostics: list[str] = field(default_factory=list)

    def as_dict(self):
        def coords(p): return [round(p.x, 5), round(p.y, 5)]
        return {"units":"cm", "points":{k:coords(v) for k,v in self.points.items()},
                "curves":{k:[coords(p) for p in v] for k,v in self.curves.items()},
                "pieces":{k:[coords(p) for p in v] for k,v in self.pieces.items()},
                "diagnostics":self.diagnostics}


def build(document: dict, measurements: dict[str, float]) -> BuildResult:
    if not isinstance(document, dict) or document.get("dsl_version") != "0.1":
        raise PatternError("Expected dsl_version '0.1'")
    if document.get("units") != "cm":
        raise PatternError("v0.1 requires units='cm'")
    required = document.get("measurements", [])
    if not isinstance(required, list) or not all(isinstance(n,str) for n in required):
        raise PatternError("measurements must be a list of names")
    missing = [n for n in required if n not in measurements]
    if missing:
        raise PatternError(f"Missing measurements: {missing}")
    params = document.get("parameters", {})
    if not isinstance(params, dict):
        raise PatternError("parameters must be an object")
    vars = {}
    try:
        for name in required:
            value = evaluate(measurements[name], {})
            if value <= 0:
                raise PatternError(f"Measurement {name} must be positive")
            vars[name] = value
        for name, expr in params.items():
            if not isinstance(name,str) or not name.isidentifier() or name in vars or name in ("min","max","sqrt","abs","sin","cos","tan"):
                raise PatternError(f"Invalid parameter name: {name}")
            vars[name] = evaluate(expr, vars)
    except ExpressionError as exc:
        raise PatternError(str(exc)) from exc
    points, curves, pieces, warnings = {}, {}, {}, []
    operations = document.get("operations", [])
    if not isinstance(operations,list) or len(operations)>2000:
        raise PatternError("operations must be a list with <=2000 items")

    def p(name):
        if name not in points:
            raise PatternError(f"Unknown point {name!r}")
        return points[name]
    def number(v): return evaluate(v,vars)
    def put(name,pt):
        if name in points or name in curves or name in pieces:
            raise PatternError(f"Duplicate identifier {name!r}")
        points[name] = pt
    for idx,op in enumerate(operations):
        try:
            if not isinstance(op,dict): raise PatternError("Operation must be an object")
            typ, ident = op.get("type"), op.get("id")
            if not isinstance(ident,str) or not ident.isidentifier():
                raise PatternError("Each operation needs an identifier id")
            if typ == "point":
                put(ident,Point(number(op["x"]),number(op["y"])))
            elif typ == "offset":
                base=p(op["from"])
                put(ident,Point(base.x+number(op["dx"]),base.y+number(op["dy"])))
            elif typ == "polar":
                base=p(op["from"]); angle=radians(number(op["angle"])); length=number(op["length"])
                put(ident,Point(base.x+length*cos(angle),base.y+length*sin(angle)))
            elif typ == "midpoint":
                a,b=p(op["a"]),p(op["b"])
                put(ident,Point((a.x+b.x)/2,(a.y+b.y)/2))
            elif typ == "line_intersection":
                put(ident,intersection(p(op["a"]),p(op["b"]),p(op["c"]),p(op["d"])))
            elif typ == "cubic_bezier":
                if ident in points or ident in curves or ident in pieces: raise PatternError("Duplicate identifier")
                count=int(op.get("samples",24))
                if not 4 <= count <= 200: raise PatternError("samples must be between 4 and 200")
                a,b,c,d=(p(op[k]) for k in ("start","control1","control2","end"))
                curves[ident]=[cubic(a,b,c,d,i/count) for i in range(count+1)]
            elif typ == "piece":
                if ident in points or ident in curves or ident in pieces: raise PatternError("Duplicate identifier")
                refs=op["path"]
                if not isinstance(refs,list) or len(refs)<3: raise PatternError("Piece path needs >=3 entries")
                poly=[]
                for ref in refs:
                    if ref in points: segment=[points[ref]]
                    elif ref in curves: segment=curves[ref]
                    elif isinstance(ref,str) and ref.startswith("-") and ref[1:] in curves: segment=list(reversed(curves[ref[1:]]))
                    else: raise PatternError(f"Unknown path reference {ref!r}")
                    if poly and distance(poly[-1],segment[0])<EPS: segment=segment[1:]
                    poly.extend(segment)
                if len(poly)>1 and distance(poly[0],poly[-1])<EPS: poly.pop()
                if len(poly)<3 or abs(signed_area(poly))<EPS: raise PatternError("Degenerate piece polygon")
                if self_intersects(poly): raise PatternError("Self-intersecting piece polygon")
                pieces[ident]=poly
            else:
                raise PatternError(f"Unsupported operation type {typ!r}")
        except (KeyError,TypeError,ValueError,ExpressionError,PatternError) as exc:
            raise PatternError(f"Operation {idx} ({op.get('id','?') if isinstance(op,dict) else '?'}): {exc}") from exc
    if not pieces: warnings.append("No finished pieces defined")
    return BuildResult(points,curves,pieces,warnings)
