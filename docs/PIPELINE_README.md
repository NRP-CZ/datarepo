# Prerequisites

1. Available `pipeline_preset` in repository model (`from oarepo_file_pipeline.model.presets.pipeline import pipeline_preset`)
2. Running repository instance
3. Running cache in the repository
4. Running S3 storage in the repository (presigned URLs must support seek operations)
5. HSM server docker image built and running with configured crypt4gh keys
6. File pipeline server docker image built

# High-Level Flow

When a user accesses `/pipeline?args`, the repository performs the following steps:

1. Retrieves presigned S3 URL of the file
2. Creates a helper data structure holding the required steps (validate crypt4gh file, decrypt, etc.)
3. Creates a signed payload with the repository's RSA private key
4. Encrypts the signed payload with the pipeline server's RSA public key
5. Stores the final encrypted data in Redis cache under a randomly generated UUID
6. Redirects the user to `PIPELINE_REDIRECT_URL/{redis_token_id}`
7. Pipeline server processes the steps (e.g., validate step)
8. Decrypts the data using the pipeline server's RSA private key
9. Decodes the JWT token with the repository's public key
10. Validates the data
11. Processes the file by seeking/reading from the presigned S3 URL

# Configuration

```python
# oarepo_file_pipeline/config.py
# Imported automatically from invenio.cfg
PIPELINE_SIGNING_ALGORITHM = "RS256"
PIPELINE_ENCRYPTION_ALGORITHM = "RSA-OAEP"
PIPELINE_ENCRYPTION_METHOD = "A256GCM"
```

The same algorithms are used in the pipeline server configuration:

```python
# oarepo_file_pipeline_server/config.py
"""Default algorithms"""
PIPELINE_SIGNING_ALGORITHM = "RS256"
PIPELINE_ENCRYPTION_ALGORITHM = "RSA-OAEP"
PIPELINE_ENCRYPTION_METHOD = "A256GCM"
```

These settings do not need to be changed, but they must match between the repository and pipeline server.

## Repository Configuration (invenio.cfg)

Add the following to `invenio.cfg`:

```python
from joserfc.jwk import RSAKey

# RSAKey.import_key: You can import an RSAKey from string, bytes, or a JWK (in dict).
# https://jose.authlib.org/en/guide/jwk/#import-an-rsa-key

repo_private_key = """-----BEGIN PRIVATE KEY-----..."""

repo_public_key = """-----BEGIN PUBLIC KEY-----..."""

server_public_key = """-----BEGIN PUBLIC KEY-----..."""

# Private and public RSA keys for signing JWT token
PIPELINE_REPOSITORY_JWK = {
    "private_key": RSAKey.import_key(repo_private_key),
    "public_key": RSAKey.import_key(repo_public_key),
}

# Public RSA key of FILE_PIPELINE_SERVER to encrypt JWE token with payload
PIPELINE_JWK = {
    "public_key": RSAKey.import_key(server_public_key),
}

PIPELINE_REDIRECT_URL = "https://127.0.0.1:5555/pipeline"
```

# Pipeline Server

## Configuration File

Create a JSON configuration file for the pipeline server. It must contain two sections: `hsm_servers` and `rsa_keys`.

The pipeline server will not start unless:

- At least one HSM server is configured
- RSA keys are defined
- Redis is available

Example configuration file:

```json
{
  "hsm_servers": {
    "default": "http://localhost:8080/mykey/x25519/",
    "secondary": "http://localhost:8080/myanotherkey/x25519/"
  },
  "rsa_keys": {
    "server_private_key": "",
    "server_public_key": "",
    "repo_public_key": ""
  }
}
```

Note: `mykey` and `myanotherkey` are crypt4gh key file names without extensions, which were mounted in the HSM server at startup.

The `hsm_servers` section stores crypt4gh keys needed for encryption/decryption steps. Keys can be either local or HTTP-based (see 'Environment Variables' and 'Configuration File Structure' sections in the pipeline server README for details).

## Environment Variables

Main environment variables:

- `REDIS_HOST` - Default: localhost
- `REDIS_PORT` - Default: 6379
- `REDIS_DB` - Default: 0
- `CONFIG_FILE` - Default: /config/config.json
- `KEY_PROVIDER` - Default: http

## Running the Pipeline Server

The pipeline server requires access to Redis, S3, and the HSM server.

**Important:** The pipeline server container must be able to communicate with other containers (Redis, S3, HSM server). Ensure that:
- All containers are on the same Docker network, or
- The appropriate networking configuration is in place to allow inter-container communication

Run the docker image:

```shell
docker run \
  --network your_docker_network \
  -v /path/to/config.json:/config/config.json:ro \
  -p 5555:5555 \
  image_name
```

Replace `your_docker_network` with the name of your Docker network where Redis, S3, and HSM server containers are running.

# Testing the Setup

To verify that the pipeline is working correctly:

1. Create a record with crypt4gh files
2. Ensure you have a file (e.g., `test.c4gh`) encrypted with the pipeline server's crypt4gh key (the one defined in the `hsm_servers` configuration)
3. Access the following URL:
   ```
   https://127.0.0.1:5000/api/datasets/{record_id}/files/test.c4gh/pipeline?pipeline=validate_crypt4gh
   ```
4. The validation step will process the entire file and attempt to decrypt it. If any errors occur, `valid` will be set to `false`.

Expected successful response:

```json
{
  "valid": true,
  "error": null,
  "file_name": "unknown"
}
```
