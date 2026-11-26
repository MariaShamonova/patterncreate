import json
import unittest
from pathlib import Path
from pattern_engine import build, PatternError
from pattern_engine.expressions import evaluate, ExpressionError
from pattern_engine.geometry import Point, intersection

ROOT=Path(__file__).resolve().parents[1]
DOC=json.loads((ROOT/'examples/demo_pattern.json').read_text())

class EngineTests(unittest.TestCase):
    def test_build_and_resize(self):
        small=build(DOC,{'hips':92})
        large=build(DOC,{'hips':104})
        self.assertAlmostEqual(small.points['B'].x,21.16)
        self.assertGreater(large.points['B'].x,small.points['B'].x)
        self.assertEqual(len(small.pieces['panel']),4)
    def test_missing_measurement(self):
        with self.assertRaisesRegex(PatternError,'Missing measurements'): build(DOC,{})
    def test_no_arbitrary_execution(self):
        with self.assertRaises(ExpressionError): evaluate('__import__("os").system("echo bad")',{})
        with self.assertRaises(ExpressionError): evaluate('hips.__class__',{'hips':92})
    def test_intersection(self):
        q=intersection(Point(0,0),Point(2,2),Point(0,2),Point(2,0))
        self.assertAlmostEqual(q.x,1)
        self.assertAlmostEqual(q.y,1)
    def test_self_intersection_rejected(self):
        doc={"dsl_version":"0.1","units":"cm","measurements":[],"operations":[
            {"id":"A","type":"point","x":0,"y":0},
            {"id":"B","type":"point","x":2,"y":2},
            {"id":"C","type":"point","x":0,"y":2},
            {"id":"D","type":"point","x":2,"y":0},
            {"id":"bow","type":"piece","path":["A","B","C","D"]}]}
        with self.assertRaises(PatternError): build(doc,{})
    def test_unknown_op(self):
        doc=dict(DOC,operations=[{"id":"X","type":"execute_python"}])
        with self.assertRaisesRegex(PatternError,'Unsupported'): build(doc,{'hips':92})

if __name__=='__main__': unittest.main()
