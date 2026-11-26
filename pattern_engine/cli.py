import argparse
import json
from pathlib import Path
from .engine import build, PatternError

def main():
    parser=argparse.ArgumentParser(description="Build a parametric pattern from DSL JSON")
    parser.add_argument("pattern",type=Path)
    parser.add_argument("measurements",type=Path)
    parser.add_argument("-o","--output",type=Path,default=Path("build.json"))
    args=parser.parse_args()
    try:
        doc=json.loads(args.pattern.read_text(encoding="utf-8"))
        measures=json.loads(args.measurements.read_text(encoding="utf-8"))
        result=build(doc,measures)
        args.output.write_text(json.dumps(result.as_dict(),ensure_ascii=False,indent=2),encoding="utf-8")
        print(f"Built {len(result.pieces)} piece(s), {len(result.points)} points -> {args.output}")
        for warning in result.diagnostics: print(f"WARNING: {warning}")
    except (OSError,ValueError,PatternError) as exc:
        parser.exit(1,f"ERROR: {exc}\n")

if __name__=="__main__": main()
