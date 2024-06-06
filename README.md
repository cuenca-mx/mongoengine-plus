# mongoengine-plus
[![codecov](https://codecov.io/gh/cuenca-mx/mongoengine-plus/graph/badge.svg?token=CwoY4toTQU)](https://codecov.io/gh/cuenca-mx/mongoengine-plus)
[![test](https://github.com/cuenca-mx/cuenca-python/workflows/test/badge.svg)](https://github.com/cuenca-mx/mongoengine-plus/actions?query=workflow%3Atest)

Extra field types, function helpers and asyncio support for [mongoengine](https://github.com/MongoEngine/mongoengine)

## Installation
```
pip install mongoengine-plus
```

## Testing

### Requirements
**Docker**

Make sure you have Docker installed, as the unit tests require a real Mongo database instance.
It is required in order to test Client-Side Field Level Encryption (CSFLE) not supported by mongomock.
Don't worry about setting up Mongo manually; the test suite will handle that for you.

**Self-signed certificates**

To test CSFLE, you need to mock a KMS provider that supports HTTPS requests. We use [moto](https://github.com/getmoto/moto) 
as a KMS mock server running on localhost. This allows us to set up the required SSL certificates 
so that the `pymongo.encryption` classes don't raise any complaints. The current testing certificates 
are located in `tests/localhost.*`. The configuration file for the certificates is `/tests/cert.conf`.

If you need to create new self-signed certificates, you can follow these steps:

```bash
cd tests
openssl genrsa -out localhost.key 2048
openssl req -new -key localhost.key -out localhost.csr -config cert.conf
# creates a certificate valid for 1 year
openssl x509 -req -days 365 -in localhost.csr -signkey localhost.key -out localhost.crt -extensions v3_utils -extfile cert.conf
```

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
unset SSL_CERT_FILE
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
- `async_delete()`: Delete documents asynchronously.

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
    
async def delete_users(name):
    await User.objects(name=name).async_delete()

async def main():
    await insert_users(["Jane", "John"])
    await get_first_user()
    await get_user_by_name("John")
    await count_users()
    await update_user_name("John", "Johnny")
    await get_user_by_name("Johnny")
    await delete_users("Johnny")

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

Mongoengine-plus introduces a new field type called `EncryptedStringField` that implements
Client-side Field Level Encryption ([CSFLE](https://www.mongodb.com/docs/manual/core/csfle/))
using [pymongo](https://pymongo.readthedocs.io/en/stable/examples/encryption.html) encryption classes.
This feature allows explicit data encryption before sending it over the network to MongoDB,
and automatic data decryption after reading from MongoDB. It supports both synchronous
and asynchronous operations. Currently, the `EncryptedStringField` implementation supports
the AWS KMS service as the Key Management Service (KMS) provider.

```python
from mongoengine import Document, StringField
from mongoengine_plus.types import EncryptedStringField
from pymongo.encryption import Algorithm


class User(Document):
    id = StringField(primary_key=True)
    ssn = EncryptedStringField(
        algorithm=Algorithm.AEAD_AES_256_CBC_HMAC_SHA_512_Deterministic
    )


user = User(id='US1', ssn='12345')
user.save()
print(user.ssn)  # Output: '12345'

user_ = User.objects.get(id='US1')
print(user_.ssn)  # Output: '12345'

```

There are a few steps before you can start using `EncryptedStringField`. 

### 1. Create a Data Encryption Key (DEK)

Before using `EncryptedStringField`, you'll need to create a Data Encryption Key (DEK) 
for encrypting and decrypting your data. The DEK should follow the recommended 
requirements described in the official MongoDB documentation on [Keys and Key Vaults](https://www.mongodb.com/docs/manual/core/csfle/fundamentals/keys-key-vaults/#std-label-csfle-reference-keys-key-vaults).
We've provided a helper method to create your DEK easily.

```python
from mongoengine import connect
from mongoengine_plus.types.encrypted_string.base import create_data_key

connect(host='mongo://localhost:27017/db')

create_data_key(
    kms_provider=dict(
        aws=dict(
            accessKeyId='your-aws-key-id',
            secretAccessKey='your-aws-secret-access-key'
        )
    ),
    key_namespace='encryption.__keyVault',
    key_arn='arn:aws:kms:us-east-1:111122223333:key/your-key-id',
    key_name='my_key_name',
    kms_connection_url='https://kms.us-east-1.amazonaws.com',
    kms_region_name='us-east-1',
)
```

You'll need to execute this step only once during the project setup. Ensure that your 
MongoDB user has the necessary permissions for collection and index creation, and 
access to the AWS KMS key.

### 2. Configure `EncryptedStringField`

Since `EncryptedStringField` needs to read the DEK from your MongoDB instance and access the 
KMS key for encryption/decryption, you'll need to configure it as follows. This 
configuration might be in your `__init__.py` file and should be executed once.

```python
from mongoengine import Document, StringField
from mongoengine_plus.types import EncryptedStringField
from pymongo.encryption import Algorithm

EncryptedStringField.configure_aws_kms(
    'encryption.__keyVault',
    'my_key_name',
    'your-aws-key-id',
    'your-aws-secret-access-key',
    'us-east-1',
)


class User(Document):
    id = StringField(primary_key=True)
    ssn = EncryptedStringField(
        algorithm=Algorithm.AEAD_AES_256_CBC_HMAC_SHA_512_Deterministic
    )
```

Now you are ready to go!

### 3. Optimize KMS requests (optional)

There's a caveat in the `EncryptedStringField` implementation. Every time `EncryptedStringField` needs
to encrypt or decrypt data, it uses the `pymongo.encryption.ClientEncryption`,
which makes a request to the AWS KMS service endpoint. This can potentially slow down
the performance of reading and writing encrypted data to MongoDB. As a workaround,
we've created a function that patches this behavior and caches the data key.

```python
from mongoengine_plus.types.encrypted_string import cache_kms_data_key


cache_kms_data_key(
    'encryption.__keyVault',
    'my_key_name',
    'your-aws-key-id',
    'your-aws-secret-access-key',
    'us-east-1',
    'https://kms.us-east-1.amazonaws.com',
)
```

You should execute this function once before making any database write or read operations,
perhaps in your `__init__.py` file. It will retrieve the KMS key and cache it for
subsequent requests.
