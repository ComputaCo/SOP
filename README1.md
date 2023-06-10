# Singularity Oriented Programming (SOP)

TODO: add support for platform specific implementations in the same class:

```python
@platform('server')
def method(self):
    pass
@platform('client')
def method(self):
    pass
```

or

```python
@server
def method(self):
    pass
@client
def method(self):
    pass
```

TODO: make custom schema type for pony-pgsql and pydantic models

```python
class A(Base):
    i: int
    j: int
    k: A

A.pydantic()  # returns pydantic model
A.orm()  # returns pony orm
```

TODO: offer basic access control decorators

```python
# doesn't necessarily have to be associated with a REST endpoint
@access_control(lambda app, ctx: ctx.user.is_admin)
def method(self):
    pass

# can be associated with a REST endpoint
@app.User.get('/{id}/do_something/{arg}')
@access_control(lambda app, ctx: ctx.user.is_admin)
def do_something(self, arg):
    pass
```

TODO: custom middleware

```python
@app.middleware
def authenticate(app, ctx, next):
    user_in_db = app.User.get(ctx.session.uid)
    if user_in_db is None:
        raise Exception('User not found')
    if ctx.session_id not in user_in_db.session_ids:
        raise Exception('Session not found')
    if jwt(ctx.session_id, server.secret) != ctx.session.jwt:
        raise Exception('Invalid session')
    ctx.user = user_in_db
    return next()
```


> What do you get when you combine Object-Oriented Programming (OOP) with the 3-layer architecture of frontend-backend-database (FBD)? What happens when you squeeze all 7 layers into 2? What's a client-side active record ORM + RPCs? We call it Singularity Oriented Programming (SOP).

The singularity is coming. To prepare, we need to be able to iterate quickly and concisely. The Singularity Oriented Programming (SOP) paradigm provides a new way to achieve this by unifying Object-Oriented Programming (OOP) with the 3-layer architecture of frontend-backend-database (FBD) into a single paradigm and also consolidating the entity, data access, service, and controller layers into a single self-contained backend layer. Seamlessly retrieve and manipulate data from the database on the client with the same ease as you would on the server. Iterate like never before with the power of SOP.

## Basic Features

1. **Unified Entity-REST Classes**: Write a single class for each entity that handles schema definition, data access, public service methods, and API endpoints.

2. **Data Linking and Syncing**: Fetch and update data, including linked data, and seamlessly sync with the server in a secure and scalable manner.

3. **Authentication and Authorization**: Convenient methods for session management, login checks, and attribute hiding.

## Advanced Features

4. **Custom Endpoints**: Define custom API endpoints using the `controller.get/post/put/delete` decorator. For static methods, the API URL becomes `<host>/<class>/<method>`, while for instance methods, it's `<host>/<class>/<id>/<method>`.

5. **Remote Method Invocation**: The server uses `@controller.*` decorators to mark API routes, and vice versa for the client to call the corresponding API methods.

6. **Session Management**: The `session()` function provides the session object for the current request.

7. **Property-level security**: Implement security directly in the data model by using the `require_logged_in` and `hidden` decorators and functions.

## Getting started

### Python

1. Start by installing the `singularity-oriented-programming` package:

```bash
pip install singularity-oriented-programming
```

2. Next, define a server-side class for each entity, inheriting from the `ServerBase` class. The `ServerBase` class provides automated schema building and data access methods.

```python
from sop import ServerBase, Column, ManyToMany, endpoint, session, require_logged_in, hidden

class Account(ServerBase):
    name: str = Column(str)
    email: str = Column(str)
    show_friends_publicly: bool = Column(bool)
    friend_ids: List[int] = ManyToMany('Account')
    
    # Custom endpoint
    @endpoint('friends')
    @property
    def friends(self):
        if session().uid != self.id and not self.show_friends_publicly:
            raise Exception('Friends are not public')
        return [Account.get(id) for id in self.friend_ids]
    
    require_logged_in('email')
    hashed_password: str = Column(str)
    salt: str = Column(str)
    hidden('hashed_password', 'salt')

    @endpoint('login')
    @staticmethod
    def login(email, password) -> str:
        # check password, create session, return session id
        ...

    @endpoint('logout')
    @require_logged_in
    def logout(self):
        # delete session
        ...
```

3. Then define a client-side class for each entity, inheriting from the `ClientBase` class. This class provides primitive data access methods and an API client.

```python
from UORAP import ClientBase, StaticClient, InstanceClient

class Account(ClientBase):
    name: str
    email: str
    show_friends_publicly: bool
    friend_ids: List[int]
    
    # Client-side method to get friends
    @property
    def friends(self):
        if session().uid != self.id and not self.show_friends_publicly:
            raise Exception('Friends are not public')
        return [Account.get(id) for id in self.friend_ids]
    
    hashed_password: str
    salt: str

    @staticmethod
    def login(email, password) -> str:
        return Account.Client('login', data={'email': email, 'password': password})

    def logout(self):
        self.client('logout')
```

4. Finally, use the classes as follows:

```python
# Create a new account
new_account = Account.create(name='John Doe', email='john@example.com', password='secret')

# Log in
session_id = Account.login('john@example.com', 'secret')

# Access a property
print(new_account.name)  # 'John Doe'

# Update a property
new_account.update(name='Jane Doe')

# Log out
new_account.logout()
```

### Nodejs

1. Start by installing the `singularity-oriented-programming` package:

```bash
npm install @computaco/singularity-oriented-programming
```

2. Next, define a server-side class for each entity, inheriting from the `ServerBase` class. The `ServerBase` class provides automated schema building and data access methods.

```typescript
import { ServerBase, Column, ManyToMany, endpoint, session, require_logged_in, hidden } from 'sop';

class Account extends ServerBase {
    @Column()
    name: string;
    @Column()
    email: string;
    @Column()
    show_friends_publicly: boolean;
    @ManyToMany('Account')
    friend_ids: number[];
    
    // Custom endpoint
    @endpoint('friends')
    get friends() {
        if (session().uid != this.id && !this.show_friends_publicly) {
            throw new Error('Friends are not public');
        }
        return this.friend_ids.map(id => Account.get(id));
    }
    
    @require_logged_in('email')
    @Column()
    hashed_password: string;
    @Column()
    salt: string;
    @hidden('hashed_password', 'salt')

    @endpoint('login')
    static login(email: string, password: string) {
        // check password, create session, return session id
        ...
    }

    @endpoint('logout')
    logout() {
        // delete session
        ...
    }
}
```

3. Then define a client-side class for each entity, inheriting from the `ClientBase` class. This class provides primitive data access methods and an API client.

```typescript
import { ClientBase, StaticClient, InstanceClient } from 'sop';

class Account extends ClientBase {
    @Column()
    name: string;
    @Column()
    email: string;
    @Column()
    show_friends_publicly: boolean;
    @ManyToMany('Account')
    friend_ids: number[];
    
    // Client-side method to get friends
    get friends() {
        if (session().uid != this.id && !this.show_friends_publicly) {
            throw new Error('Friends are not public');
        }
        return this.friend_ids.map(id => Account.get(id));
    }
    
    @Column()
    hashed_password: string;
    @Column()
    salt: string;

    static login(email: string, password: string) {
        return Account.Client('login', {email, password});
    }

    logout() {
        this.client('logout');
    }
}
```

4. Finally, use the classes as follows:

```typescript
// Create a new account
const new_account = await Account.create({name: 'John Doe', email: '

// Log in
const session_id = await Account.login('

// Access a property
console.log(new_account.name);  // 'John Doe'

// Update a property
new_account.update({name: 'Jane Doe'});

// Log out
new_account.logout();
```


## Rational

Essentially, SOP simplifies your stack from this:

```
server/
    entities/
        user.ts
        post.ts
        comment.ts
        ... // entities
    services/
        user.ts
        post.ts
        comment.ts
        ... // entity-specific services
        auth.ts
        ... // general services
    controllers/
        user.ts
        post.ts
        comment.ts
        auth.ts
        ... // service controllers
    routes/
        user.ts
        post.ts
        comment.ts
        ... // controller routes
client/
    models/
        user.ts
        post.ts
        comment.ts
        ... // models
    controllers/
        user.ts
        post.ts
        comment.ts
        auth.ts
        ... // controllers
```

to this:

```
server/
    classes/
        user.ts
        post.ts
        comment.ts
    functions/
        auth.ts
client/
    classes/
        user.ts
        post.ts
        comment.ts
    functions/
        auth.ts
```

### Problem

Say we have the following database schema in `server/entities/user.ts`:

```typescript
interface User {
    @Column()
    id: number;
    @Column()
    name: string;
    @Column()
    email: string;
    @Column()
    password_hash: string;
    @Column()
    password_salt: string;
    @OneToMany('User', 'following')
    followers: User[];
    @ManyToOne('User', 'followers')
    following: User;
}
```

Now suppose you wanted to retrieve a user's followers from the client. In a traditional OOP paradigm, you would have to create a:
- a data access layer (DAL) class in `server/dal/user.ts` to retrieve the user from the database,
- a service layer class in `server/services/user.ts` to retrieve the user's followers from the DAL,
- a controller layer class in `server/controllers/user.ts` to retrieve the user's followers from the service layer,
- a route in `server/routes/user.ts` to retrieve the user's followers from the controller layer,
- a controller in `client/controllers/user.ts` to retrieve the user's followers from the model,
- and finally, a model in `client/models/user.ts` to retrieve the user's followers from the server:

    ```typescript
    class User {
        id: number;
        name: string;
        email: string;
        password_hash: string;
        password_salt: string;
        followers: User[];
        following: User;
        constructor(id: number, name: string, email: string, password_hash: string, password_salt: string, followers: User[], following: User) {
            this.id = id;
            this.name = name;
            this.email = email;
            this.password_hash = password_hash;
            this.password_salt = password_salt;
            this.followers = followers;
            this.following = following;
        }
    }

This is a lot of boilerplate code to write just to retrieve a user's followers. And this is just for one entity. Imagine having to do all 7 layers for every entity in your database! And what do you do about the friend's friends? It can't go ad infinitum when its serialized over JSON! (At leasst, unless the client ain't querying the whole db!) These are all problems that SOP provides solutions for.

### Solution

With SOP, you just need to write the 2 layers: the server and the client entity:

- `server/entities/user.ts`:

    ```typescript
    class User extends ServerEntity {
        @Column()
        id: number;
        @Column()
        name: string;
        @Column()
        email: string;
        @Column()
        password_hash: string;
        @Column()
        password_salt: string;
        @OneToMany('User', 'following')
        followers: User[];
        @ManyToOne('User', 'followers')
        following: User;
    }
    ```

- `client/models/user.ts`:

    ```typescript
    class User extends ClientEntity {
        id: number;
        name: string;
        email: string;
        password_hash: string;
        password_salt: string;
        followers: User[];
        following: User;
        constructor(id: number, name: string, email: string, password_hash: string, password_salt: string, followers: User[], following: User) {
            this.id = id;
            this.name = name;
            this.email = email;
            this.password_hash = password_hash;
            this.password_salt = password_salt;
            this.followers = followers;
            this.following = following;
        }
    }
    ```

And that's it. Now you can call `User.getFollowers()` from the client to retrieve a user's followers from the server. No more writing 7 layers of boilerplate code just to retrieve a user's followers. With SOP, you can iterate like never before.

## Details

- server-side methods can be decorated with `@endpoint` to expose them as API endpoints
  - instance methods with an `@endpoint.get/post/put/delete` decorator are available at `/<entity>/<id>/<method>`
  - static/class methods with an `@endpoint.get/post/put/delete` decorator are available at `/<entity>/<method>`
  - `@endpoint.get` arguments are passed as query parameters
  - `@endpoint.post/put/delete` arguments are passed as JSON in the request body
  - args and return types must be JSON-de/serializable (eg, pydantic models or typescript interfaces)
- clients can decorate stub methods with `@endpoint.get/post/put/delete` to automatically generate API calls to the server
  - instance methods with an `@endpoint.get/post/put/delete` decorator invoke the api endpoint with the corresponding http verb at path: `/<entity>/<id>/<method>`
  - static/class methods with an `@endpoint.get/post/put/delete` decorator invoke the api endpoint with the corresponding http verb at path `/<entity>/<method>`
  - `@endpoint.get` arguments are passed as query parameters
  - `@endpoint.post/put/delete` arguments are passed as JSON in the request body
  - args and return types must be JSON-de/serializable (eg, pydantic models or typescript interfaces)
- the server library provides DB and auth and API management
  - DB maangement:
    - `ServerEntity` entity defines the following ORM methods:
      - `create(cls, data)`
      - `get(cls, id)`
      - `get_many(cls, ids)`
      - `get_all(cls)`
      - `update(cls, data)`
      - `update_many(cls, data)`
      - `upsert(cls, data)`
      - `upsert_many(cls, data)`
      - `delete_by_id(cls, id)`
      - `delete_many_by_ids(cls, ids)`
      - `delete_all(cls)`
    - configure, init, and manage the db connection with `server/db.py/ts`
    - `ServerEntity` internally uses `SQLAlchemy` or `TypeORM`
  - auth
    - you must implement `login(params)`, `authenticate(token)`, `logout(token)` in `server/auth.py/ts` to use authentication
    - entities must subclass `Resource` to use the `is_viewer`, `is_editor`, `is_owner` access restriction decorators
  - controller
    - configure, init, and manage the api at `server/controller.py/ts`
    - `controller` internally uses `FastAPI` or `express`
    - `endpoint.get/post/put/delete` automatically detects its containing class or module and scopes itself under that path
- the client library provides entity, auth, and API management:
  - entity management:
    - `ClientEntity` entity defines the following ORM methods:
      - `create(cls, data)`
      - `get(cls, id)`
      - `get_many(cls, ids)`
      - `get_all(cls)`
      - `update(self)`
      - `push_updates(self)`
      - `pull_updates(self)`
      - `update_many(cls, data)`
      - `upsert(self)`
      - `upsert_many(cls, data)`
      - `delete(self)`
      - `delete_by_id(cls, id)`
      - `delete_many_by_ids(cls, ids)`
      - `delete_all(cls)`
  - auth
    - `client/auth.py/ts` provides stubs for `login(params)`, `authenticate(token)`, `logout(token)` that defer to the server
    - use `session()` to get the current session.
  - api:
    - supply api parameters in `client/api.ts/py`
    - most controller requests can be automatically generated by decorating stub methods with `@controller.get/post/put/delete`
    - if you need to manually create a controller, use `Controller()` in `client/controller.ts/py`
    - `ClientAPI` automatically manages the session token
    - If you're doing something crazy and have multiple sessions or multiple servers, you could do `controller1.get('/api/endpoint', params)` or `controller2.get('/api/endpoint', params)`

## License

[MIT](./LICENSE)

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [requests](https://docs.python-requests.org/en/master/)
- [TypeORM](https://typeorm.io/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [express](https://expressjs.com/)
- [axios](https://axios-http.com/)