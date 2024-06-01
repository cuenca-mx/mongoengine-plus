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

## Mongoengine + asyncio integration

## Client-side Field Level Encryption
