#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../.env"
source $ENV_FILE

API_OUTPUT=src/lib/schema.ts
TEMP_OUTPUT=$(mktemp)
OPENAPI_PATH="openapi.json"
APPCONFIG_PATH="../backend/appconfig.json"

if ! bunx openapi-typescript $OPENAPI_PATH --enum -o "$TEMP_OUTPUT"; then
    rm -f $TEMP_OUTPUT
    exit 1
fi

{
    echo -n 'export const AppConfig: components["schemas"]["AppConfigSchema"] = '
    cat $APPCONFIG_PATH
    echo ';'
} >> $TEMP_OUTPUT

mv -f $TEMP_OUTPUT $API_OUTPUT
