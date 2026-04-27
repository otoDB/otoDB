#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../.env"
source $ENV_FILE

API_OUTPUT=src/lib/schema.ts
OPENAPI_PATH="openapi.json"

bunx openapi-typescript $OPENAPI_PATH --enum -o $API_OUTPUT
