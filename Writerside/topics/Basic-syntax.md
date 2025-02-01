# Basic syntax

This page will help you to start using Aisle quickly by 
providing basic examples of markup language syntax.


## A quick note on names

Aisle supports names without quotes, unless name does not
contain any keyword, or other grammatically meaningful
character like `(`, `[`, `:`, etc. If you wish to use these
characters, please enclose your text with double quotes `"`
(escape sequences supported).


## Project definition

To start, you should create a project:
```
scope project My Awesome Blog
```

You can provide a description, if you wish:
```
scope project My Awesome Blog:
    A simple blogging app
```

<note>
Aisle uses exactly 4 spaces for indentation.
</note>


## Defining context

Now you want to specify the context. Start by defining the
scope:
```
scope context My Awesome Blog
```

<note>
Project and scope names must match
</note>

Now you can create a system:
```
system Blogging System:
    Manages blogs
```

Or an actor:
```
actor User:
    Creates and reads blogs
```

## Connecting nodes

Now you want your user to use the blogging system.
You can create a link for that:
```
system Blogging System:
    Manages blogs

actor User:
    Creates and reads blogs
    links:
        --> Blogging System
```


## Defining containers

After you've created to context map, you should think about
writing a container map. Again, start by defining the scope:
```
scope containers My Awesome Blog
```

Now create a container and mark that it belongs to aforementioned
system:
``` 
service Frontend:
    system = Blogging System
```

You can specify the tech stack:
```
service Frontend:
    system = Blogging System
    tech = React, Bootstrap
```

Now create a backend:
```
service Backend:
    system = Blogging System
    tech = Python, Litestar
```

You also need a database:
```
service DB:
    system = Blogging System
    tech = Postrges
```

Now connect it all together with links and provide description. 
Also, don't forget about user, that uses the frontend:
```
service Frontend:
    Web UI
    system = Blogging System
    tech = React, Bootstrap
    links:
        --> Backend
        <-- User
    
service Backend:
    Blogging API
    system = Blogging System
    tech = Python, Litestar
    links:
        --> DB
    
service DB:
    system = Blogging System
    tech = Postrges
```

We can add a little tech note on our link:
```
service Frontend:
    Web UI
    system = Blogging System
    tech = React, Bootstrap
    links:
        --> Backend over HTTP REST API
        <-- User
```

## Defining deployment

Finally, define how the app should be deployed using deployment
scope:
```
scope deployment My Awesome Blog
```

Create the deployment:
```
deployment VPS Deployment:
    deploy Frontend = Docker container
    deploy Backend = Docker container
    deploy DB = Docker container
```

## Putting it all together

This is the final result:

```
scope project My Awesome Blog:
    A simple blogging app


scope context My Awesome Blog

system Blogging System:
    Manages blogs

actor User:
    Creates and reads blogs
    links:
        --> Blogging System


scope containers My Awesome Blog

service Frontend:
    Web UI
    system = Blogging System
    tech = React, Bootstrap
    links:
        --> Backend over HTTP REST API
        <-- User
    
service Backend:
    Blogging API
    system = Blogging System
    tech = Python, Litestar
    links:
        --> DB
    
service DB:
    system = Blogging System
    tech = Postrges


scope deployment My Awesome Blog

deployment VPS Deployment:
    deploy Frontend = Docker container
    deploy Backend = Docker container
    deploy DB = Docker container
```