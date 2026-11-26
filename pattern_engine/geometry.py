from dataclasses import dataclass
from math import hypot

EPS = 1e-8

@dataclass(frozen=True)
class Point:
    x: float
    y: float


def distance(a: Point, b: Point) -> float:
    return hypot(a.x-b.x, a.y-b.y)


def cross(ax, ay, bx, by):
    return ax*by-ay*bx


def intersection(a: Point, b: Point, c: Point, d: Point) -> Point:
    """Infinite line intersection; parallel lines are rejected."""
    rx, ry = b.x-a.x, b.y-a.y
    sx, sy = d.x-c.x, d.y-c.y
    det = cross(rx, ry, sx, sy)
    if abs(det) < EPS:
        raise ValueError("Parallel or coincident lines")
    t = cross(c.x-a.x, c.y-a.y, sx, sy)/det
    return Point(a.x+t*rx, a.y+t*ry)


def cubic(a: Point, b: Point, c: Point, d: Point, t: float) -> Point:
    u = 1-t
    return Point(u**3*a.x+3*u*u*t*b.x+3*u*t*t*c.x+t**3*d.x,
                 u**3*a.y+3*u*u*t*b.y+3*u*t*t*c.y+t**3*d.y)


def signed_area(vertices: list[Point]) -> float:
    return sum(p.x*q.y-q.x*p.y for p,q in zip(vertices, vertices[1:]+vertices[:1]))/2


def on_segment(a, b, p):
    return (min(a.x,b.x)-EPS <= p.x <= max(a.x,b.x)+EPS and
            min(a.y,b.y)-EPS <= p.y <= max(a.y,b.y)+EPS and
            abs(cross(b.x-a.x,b.y-a.y,p.x-a.x,p.y-a.y)) < EPS)


def segments_intersect(a,b,c,d):
    def orient(p,q,r):
        return cross(q.x-p.x,q.y-p.y,r.x-p.x,r.y-p.y)
    o1,o2,o3,o4 = orient(a,b,c),orient(a,b,d),orient(c,d,a),orient(c,d,b)
    if (o1 > EPS and o2 < -EPS or o1 < -EPS and o2 > EPS) and (o3 > EPS and o4 < -EPS or o3 < -EPS and o4 > EPS):
        return True
    return any((abs(o)<EPS and on_segment(x,y,z)) for o,x,y,z in
               [(o1,a,b,c),(o2,a,b,d),(o3,c,d,a),(o4,c,d,b)])


def self_intersects(poly: list[Point]) -> bool:
    n=len(poly)
    for i in range(n):
        for j in range(i+1,n):
            if j==i+1 or (i==0 and j==n-1):
                continue
            if segments_intersect(poly[i],poly[(i+1)%n],poly[j],poly[(j+1)%n]):
                return True
    return False
