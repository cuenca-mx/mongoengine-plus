# mongoengine-plus
Extra field types, function helpers and asyncio support for [mongoengine](https://github.com/MongoEngine/mongoengine)

## Installation
```
pip install mongoengine-plus
```

## Testing

### Requirements
**Docker**: Make sure you have Docker installed, as the unit tests require a real Mongo database instance.
It is required in order to test Client-Side Field Level Encryption (CSFLE) not supported by mongomock.
Don't worry about setting up Mongo manually; the test suite will handle that for you.

### Clone, install requirements and run tests
```bash
git clone git@github.com:cuenca-mx/mongoengine-plus.git
cd mongoengine-plus
make install-test
# Since we're using a self-signed certificate with the moto_server
# for testing we need to configure the localhost certificate so 
# ClientEncryption object can connect to the mock KMS instance
export SSL_CERT_FILE=$(pwd)/tests/localhost.crt
make test
```

## Mongoengine + Asyncio

### Asynchronous Documents operation

Mongoengine-plus brings the power of asynchronous programming to your document operations.
We've introduced an `AsyncDocument` class that extends the standard `Document` class, 
allowing you to perform operations like `save()`, `delete()` and `reload()` asynchronously.

To get started, simply inherit your document classes from `AsyncDocument` instead of `Document`. 
You'll then have access to async counterparts of the familiar methods:

- `async_save()`: Save your document asynchronously.
- `async_delete()`: Delete your document asynchronously.
- `async_reload()`: Reload your document asynchronously.

These async methods maintain the same signature as their synchronous counterparts, 
so you can seamlessly transition your existing codebase to take advantage 
of asynchronous operations.

```python
from mongoengine import StringField
from mongoengine_plus.aio import AsyncDocument

class User(AsyncDocument):
    name = StringField(required=True)

async def main():
    user = User(name='Jane')
    # Asynchronously save the user document
    await user.async_save() 
    
    # Asynchronously update the user document
    user.name = 'John'
    await user.async_save() 
    
    # Asynchronously reload the user document
    await user.async_reload()  
    print(f"Reloaded user: {user.name}")
    
    # Asynchronously delete the user document
    await user.async_delete()  

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Asynchronous Querying the database

You can do asynchronous queries to your document collections. 
We've introduced an `AsyncQuerySet` class that [extends](https://docs.mongoengine.org/guide/querying.html#custom-querysets) 
the standard `QuerySet`, providing you with async versions of familiar
query operations.

You don't need to interact with `AsyncQuerySet` directly. 
It's already configured as the `queryset_class` for the `AsyncDocument` class. 
Once you inherit your document classes from `AsyncDocument`, 
the `objects` property will give you access to asynchronous query methods:

- `async_first()`: Retrieve the first document asynchronously.
- `async_get()`: Retrieve a specific document asynchronously.
- `async_count()`: Count the number of documents asynchronously.
- `async_update()`: Update documents asynchronously.
- `async_insert()`: Insert documents asynchronously.

```python
async def get_first_user():
    user = await User.objects.async_first()
    if user:
        print(f"First user: {user.name}")
    else:
        print("No users found")

async def get_user_by_name(name):
    user = await User.objects(name=name).async_get()
    print(f"User with name '{name}': {user.name}")

async def count_users():
    count = await User.objects.async_count()
    print(f"Number of users: {count}")

async def update_user_name(old_name, new_name):
    updated = await User.objects(name=old_name).async_update(name=new_name)
    print(f"Updated {updated} user(s) from '{old_name}' to '{new_name}'")

async def insert_users(user_names):
    users = [User(name=name) for name in user_names]
    await User.objects.async_insert(users)

async def main():
    await insert_users(["Jane", "John"])
    await get_first_user()
    await get_user_by_name("John")
    await count_users()
    await update_user_name("John", "Johnny")
    await get_user_by_name("Johnny")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

To iterate over the result set of a query asynchronously, 
you can use the `async_to_list()` method:

```python
users = await User.objects(name='Jane').async_to_list()
async for user in users:
    # Process each user 
    ...    
```

We recommend using `async_to_list()` for small result sets. 


## Client-side Field Level Encryption
