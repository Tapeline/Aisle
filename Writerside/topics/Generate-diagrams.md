# Generate diagrams

## Command

You could generate diagrams by using the `aisle generate`
command:
```shell
aisle generate FILENAME
```
After executing this command, there will be files 
"context", "containers" and "deployment" in a newly
created directory (files may vary depending on
generator format). These files you can then render
with your layout engine of choice (by default it's
PlantUML).

## Options

`--encoding`. Allows you to specify encoding. Example:
```shell
aisle generate my_architecture.aisle --encoding UTF-8
```

`--directory`. Specify output directory. By default, it
is the project's name. Example:
```shell
aisle generate my_architecture.aisle --directory docs/diagrams
```

`--fmt`. Specift output format. Following formats are
supported:
- `plantuml` (default)
- `mermaid` - has limited support. Essentially it's 
  the same plantuml. Warning: mermaid is not perfect 
  at rendering C4 diagrams (at the moment)
- `d2` (experimental) - generates diagrams 
  in [d2lang](https://d2lang.io). It's recommended to 
  use TALA layout engine. Generates files `main.d2` and
  `deployments.d2`.

Example:
```shell
aisle generate my_architecture.aisle --fmt mermaid
```
