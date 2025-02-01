# Deployment scope

Deployment scope is defined as follows:
```
scope deployment <project name>
```

Then deployments entities declarations follow:

```
[external] deployment <name>:
    <deployment body>
```
Deployment body:
```
[<text description>]
[{deploy <service name> [= <deploy note>]}]
[{<deployment name>:
    <deployment body>}]
```

Examples:
```
deployment VPS Deployment:
    Located at VPS
    Docker compose:
        deploy Frontend = Docker container
        deploy Backend = Docker container
    deploy Log Collector = daemon
```
