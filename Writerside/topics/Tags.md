# Tags

You can assign tags to systems, actors, services and
deployments:

```
service Postgres [db]:
    My db service
```

## Bound tags

Some tags are bound to specific actions in Aisle.
For example, using a `database` (or `db`) tag
will result into service looking as a database
(a cylinder in C4). Here is a full list:

- `database`, `db` - mark service as a database
- `queue` - mark service as a message queue

> Please note that some bound tags may not be
> implemented in different generators.
