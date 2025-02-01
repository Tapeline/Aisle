# Container scope

Container scope is defined as follows:
```
scope containers <project name>
```

Then containers (services) entities declarations follow:

```
[external] service <name>
```
or
```
[external] service <name>:
    [<text description>]
    [system = <what system belongs to>
    [tech = <tech text>]
    [links block]
```
The tech, system, description and links block could come in any order,
however, it's recommended to stick with proposed ordering.

<note>
When an actor should connect to a service, it's better to specify that connection in
service with a reverse arrow:
<code-block>
    actor User
    ...
    service Frontend:
        Web UI
        system = Blogging System
        tech = React, Bootstrap
        links:
            --> Backend
            <![CDATA[<-- User]]>
</code-block>
</note>
