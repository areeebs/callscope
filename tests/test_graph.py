import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from callscope.graph import build_from_source, build_from_paths

SAMPLE = ROOT / "examples/sample_pkg"


class FromSource(unittest.TestCase):
    def test_callees_and_callers(self):
        g = build_from_source(
            "def a():\n    b()\n    c()\n\ndef b():\n    c()\n\ndef c():\n    pass\n"
        )
        self.assertEqual(g.callees("a"), {"b", "c"})
        self.assertEqual(g.callees("b"), {"c"})
        self.assertEqual(g.callers("c"), {"a", "b"})
        self.assertEqual(g.callers("a"), set())

    def test_method_calls_by_attr(self):
        g = build_from_source("def f(x):\n    x.save()\n\ndef save():\n    pass\n")
        self.assertIn("save", g.callees("f"))

    def test_unknown_callee_filtered(self):
        g = build_from_source("def f():\n    nonexistent()\n")
        self.assertEqual(g.callees("f"), set())  # callee not defined in graph


class FromPaths(unittest.TestCase):
    def setUp(self):
        self.g = build_from_paths([str(SAMPLE)])

    def test_discovers_functions(self):
        for fn in ("start", "handle_request", "load_config", "run_job"):
            self.assertIn(fn, self.g.names)

    def test_cross_file_callers(self):
        # load_config is called by start (app.py) and run_job (worker.py)
        self.assertEqual(self.g.callers("load_config"), {"start", "run_job"})

    def test_dot_export(self):
        dot = self.g.to_dot()
        self.assertIn("digraph callgraph", dot)
        self.assertIn('"start" -> "load_config"', dot)


if __name__ == "__main__":
    unittest.main()
