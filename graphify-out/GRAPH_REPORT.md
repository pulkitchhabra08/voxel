# Graph Report - voxel  (2026-10-25)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 40 nodes · 71 edges · 7 communities (1 shown, 6 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `056a4265`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6

## God Nodes (most connected - your core abstractions)
1. `transcribe()` - 8 edges
2. `handle()` - 7 edges
3. `run()` - 5 edges
4. `check()` - 5 edges
5. `record()` - 5 edges
6. `main()` - 4 edges
7. `log()` - 4 edges
8. `plan()` - 4 edges
9. `broad_rm()` - 3 edges
10. `model_path()` - 3 edges

## Surprising Connections (you probably didn't know these)
- `handle()` --calls--> `plan()`  [EXTRACTED]
  main.py → planner.py
- `handle()` --calls--> `check()`  [EXTRACTED]
  main.py → guard.py
- `handle()` --calls--> `run()`  [EXTRACTED]
  main.py → runner.py

## Import Cycles
- None detected.

## Communities (7 total, 6 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.28
Nodes (3): banner(), listen(), main()

## Knowledge Gaps
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `handle()` connect `Community 2` to `Community 0`, `Community 1`, `Community 3`?**
  _High betweenness centrality (0.154) - this node is a cross-community bridge._
- **Why does `transcribe()` connect `Community 6` to `Community 1`, `Community 2`, `Community 5`?**
  _High betweenness centrality (0.107) - this node is a cross-community bridge._
- **Why does `record()` connect `Community 4` to `Community 5`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._