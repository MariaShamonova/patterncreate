# Pattern DSL v0.1 — executable prototype

A **small, safe, deterministic** geometry kernel for AI-authored parametric 2D pattern specifications. Python 3.10+, no runtime dependencies.

## Quick start

```bash
python -m unittest discover -s tests -v
python -m pattern_engine.cli examples/demo_pattern.json examples/measurements.json -o build.json
```

Or install locally with `pip install -e .` and run `pattern-dsl ...`.

## DSL v0.1

The document has `dsl_version: "0.1"`, `units: "cm"`, a `measurements` array, optional ordered `parameters`, and ordered `operations`.

Supported operations:
- `point`: `id`, numeric-expression `x`, `y`
- `offset`: `id`, `from`, expressions `dx`, `dy`
- `polar`: `id`, `from`, `angle` (degrees), `length`
- `midpoint`: `id`, `a`, `b`
- `line_intersection`: `id`, `a`, `b`, `c`, `d` (infinite lines)
- `cubic_bezier`: `id`, `start`, `control1`, `control2`, `end`, optional `samples` (4..200)
- `piece`: `id`, `path`: ordered point IDs and/or cubic curve IDs. Prefix a curve ID with `-` to traverse backwards. The engine closes the last edge implicitly.

All IDs are unique. Point references and parameter references must already be defined. Expressions support `+ - * / **`, parentheses, `min`, `max`, `abs`, `sqrt`, `sin`, `cos`, `tan` (trig in degrees). No arbitrary Python execution. Geometric values are in centimeters.

## Current validation

- Required measurements present and positive; non-finite expressions rejected.
- Unknown and duplicate identifiers rejected; parallel intersections rejected.
- Piece polygons must have nonzero area and no self-intersections.
- This is **not** a fit validator, seam-matching validator, industrial pattern-making method, or production-ready sandbox for adversarial inputs. It also does not yet check whether consecutive path segments are connected (a missing connection can form an unintended straight edge).

## Intentionally out of scope for v0.1

- Valentina `.val` export and `.vit` parsing (next milestone)
- Arbitrary point-on-curve, true spline splitting, seam allowance and notch semantics
- Seam pairs, material stretch behavior, grading, sewing ease, fit assessment
- Image interpretation, AI agent loop, Telegram bot, PDF

The demo is a **rectangular parametric test panel**, not a lingerie construction. Do not interpret its formulas as an approved garment drafting method.

## Proposed next milestones

1. Define semantic seam edges and stitch-line pairs; validate length/tolerance and curve endpoint continuity.
2. Implement the subset of Valentina operations needed for point, offset, line, and cubic constructions, with round-trip compatibility tests against actual `.val` files.
3. Build an AI-to-DSL JSON generation/repair loop with schema validation and limited iterations.
4. Add image-to-design specification after the text-based workflow is stable.
