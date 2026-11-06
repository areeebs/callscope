#!/usr/bin/env python3
"""
callscope - explore a Python codebase's call graph.

  python3 -m callscope callers <function> <path> [<path> ...]
  python3 -m callscope callees <function> <path> [<path> ...]
  python3 -m callscope list <path> [<path> ...]
  python3 -m callscope dot  <path> [<path> ...] > graph.dot
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from .graph import build_from_paths
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from callscope.graph import build_from_paths


def _where(graph, name):
    return ", ".join(f"{d.file}:{d.line}" for d in graph.funcs.get(name, []))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="callscope", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for cmd in ("callers", "callees"):
        p = sub.add_parser(cmd)
        p.add_argument("function")
        p.add_argument("paths", nargs="+")
    sub.add_parser("list").add_argument("paths", nargs="+")
    sub.add_parser("dot").add_argument("paths", nargs="+")
    args = ap.parse_args(argv)

    graph = build_from_paths(args.paths)

    if args.cmd == "list":
        for name in graph.names:
            print(f"{name}  ({_where(graph, name)})")
        return 0
    if args.cmd == "dot":
        print(graph.to_dot())
        return 0

    if args.function not in graph.funcs:
        print(f"'{args.function}' not found. Known: {', '.join(graph.names) or '(none)'}",
              file=sys.stderr)
        return 1
    related = graph.callers(args.function) if args.cmd == "callers" else graph.callees(args.function)
    print(f"{args.cmd} of {args.function} ({_where(graph, args.function)}):")
    if not related:
        print("  (none)")
    for name in sorted(related):
        print(f"  {name}  ({_where(graph, name)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
