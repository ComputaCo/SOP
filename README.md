# Singularity Oriented Programming (SOP)

```python
app = App()

server = app.Server('https://app.com')
client = app.Client()

# convert to @case with auto-built client case that
@server.get()
def bar():
    pass

# route based on the platform
# if no match, raises error
@case(server)
def zoo(a: int, b: User):
    pass
@case(client)
def zoo(a: int, b: User):
    pass

class User(server.Entity):
    # server.Entity makes it be a db entity on the server and a pydantic model on the client (performed on __init_subclass__)
    name: str
    email: str
    password_hash: str
    salt: str

    hidden('password_hash', 'salt') # nulls the field from the pydantic model (enforced in BaseEntity REST handler logic)
    # `hidden` is shorthand for server.Entity.hidden. (introspects calling frame to get the class)

    # Manual ACLs
    # server.Entity.hidden('email',
    #     lambda obj, ctx:
    #         not ctx.user.is_admin or # nulls email if the user is not an admin
    #         not ctx.user.id == obj.id # or not the same user
    #         )
    # Convenience ACLs
    server.Entity.hidden('email', admin_only=True, owner_only=True)

@server.acl([
    (server.Entity.create, lambda obj, ctx: ctx.user == obj.owner),
    (server.Entity.get_by_id, lambda obj, ctx: ctx.user == obj.owner),
    (server.Entity.update_by_id, lambda obj, ctx: ctx.user == obj.owner),
    (server.Entity.delete_by_id, lambda obj, ctx: ctx.user.is_admin or ctx.user == obj.owner),
    # basically, acls you put here wrap the base methods they refer to on the server.Entity class
])
class Resource(server.Entity):
    owner: User
    name: str
    description: str

    created_at: datetime
    updated_at: datetime


@server.post('/custom_path')
@server.acl(lambda ctx: ctx.user.is_admin)
def foo(res: Resource):
    pass

app.run(server if sys.argv[1] == 'server' else client)
```

## Planning

- `Server` and `Client` are both `Platform`s