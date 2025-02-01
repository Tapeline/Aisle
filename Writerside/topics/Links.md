# Links

Links could be defined for actors, systems and services (containers):
```
links:
    {<link type> <linked entity> [over <technology>]}
```

Link types:
- `-->` outgoing
- `<--` incoming
- `<->` bidirectional
- `---` non-directed

Examples:
```
links:
    --> Service 1
    <-- Actor 2 over HTTP
    <-> Message Queue
    --- Metrics Collector
```