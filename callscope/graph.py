"""
Build a call graph from Python source using the stdlib `ast` module.

MVP: nodes are functions/methods identified by their short name. For each
function we record where it's defined and which names it calls. That's enough to
answer "who calls X?" and "what does X call?" and to export a graph — the core
of navigating unfamiliar code. Cross-module resolution by full qualified path is
a planned refinement; see the roadmap in the README.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Func:
    name: str
    file: str
    line: int
    calls: set[str] = field(default_factory=set)


class CallGraph:
    def __init__(self) -> None:
        self.funcs: dict[str, list[Func]] = {}  # name -> definitions (may be >1)

    def add(self, func: Func) -> None:
        self.funcs.setdefault(func.name, []).append(func)

    @property
    def names(self) -> list[str]:
        return sorted(self.funcs)

    def callees(self, name: str) -> set[str]:
        out: set[str] = set()
        for f in self.funcs.get(name, []):
            out |= {c for c in f.calls if c in self.funcs}
        return out

    def callers(self, name: str) -> set[str]:
        return {other for other, defs in self.funcs.items()
                for d in defs if name in d.calls}

    def to_dot(self) -> str:
        lines = ["digraph callgraph {", '  rankdir=LR; node [shape=box];']
        for name, defs in self.funcs.items():
            for d in defs:
                for callee in sorted(c for c in d.calls if c in self.funcs):
                    lines.append(f'  "{name}" -> "{callee}";')
        lines.append("}")
        return "\n".join(lines)


class _Visitor(ast.NodeVisitor):
    def __init__(self, graph: CallGraph, file: str) -> None:
        self.graph = graph
        self.file = file
        self._stack: list[Func] = []

    def _enter(self, node) -> None:
        func = Func(name=node.name, file=self.file, line=node.lineno)
        self.graph.add(func)
        self._stack.append(func)
        self.generic_visit(node)
        self._stack.pop()

    visit_FunctionDef = _enter
    visit_AsyncFunctionDef = _enter

    def visit_Call(self, node: ast.Call) -> None:
        if self._stack:
            name = _call_name(node.func)
            if name:
                self._stack[-1].calls.add(name)
        self.generic_visit(node)


def _call_name(func_node) -> str | None:
    if isinstance(func_node, ast.Name):
        return func_node.id
    if isinstance(func_node, ast.Attribute):
        return func_node.attr
    return None


def build_from_source(source: str, file: str = "<string>") -> CallGraph:
    graph = CallGraph()
    _Visitor(graph, file).visit(ast.parse(source))
    return graph


def build_from_paths(paths: list[str]) -> CallGraph:
    graph = CallGraph()
    files: list[Path] = []
    for p in paths:
        pp = Path(p)
        files.extend(pp.rglob("*.py") if pp.is_dir() else [pp])
    for f in sorted(files):
        try:
            tree = ast.parse(f.read_text(), filename=str(f))
        except (SyntaxError, UnicodeDecodeError):
            continue
        _Visitor(graph, str(f)).visit(tree)
    return graph
