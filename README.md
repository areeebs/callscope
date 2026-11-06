# callscope

Explore an unfamiliar Python codebase by its **call graph**: ask "who calls this
function?" and "what does this function call?", and export the whole graph to
Graphviz.

Reading convoluted code means chasing calls across files. IDE "find usages"
helps, but there's no good free, scriptable, cross-platform way to *see the call
structure itself*. `callscope` builds that graph from source with Python's
`ast` — no language server, no dependencies.

> Inspired by a recurring request from developers who wanted "Source Insight but
> free and on Linux" and a call-graph explorer that isn't drowning in noise.
> Clean-room, not a fork.

## Use

```bash
# who calls load_config?
python3 -m callscope callers load_config path/to/pkg

# what does start() call?
python3 -m callscope callees start path/to/pkg

# every function it found, with file:line
python3 -m callscope list path/to/pkg

# export and render the graph
python3 -m callscope dot path/to/pkg > graph.dot
dot -Tsvg graph.dot -o graph.svg   # needs graphviz
```

Example against the bundled sample:

```
$ python3 -m callscope callers load_config examples/sample_pkg
callers of load_config (examples/sample_pkg/app.py:1):
  run_job  (examples/sample_pkg/worker.py:4)
  start  (examples/sample_pkg/app.py:9)
```

## How it works

callscope parses each `.py` file into an AST, records every function/method
definition with its `file:line`, and collects the names each one calls (direct
calls and `obj.method()` attribute calls). Calls to names it never saw defined
are filtered out, so the graph stays about *your* code.

## Known limits / roadmap

- Resolution is by **short name**, so two different `save()` methods are treated
  as one node. Full qualified-path resolution is the next step.
- Python only today; the design leaves room for an LSP backend to go
  language-agnostic.
- A TUI that lets you jump call→callee interactively is the headline feature to
  come.

## License

[MIT](LICENSE).
