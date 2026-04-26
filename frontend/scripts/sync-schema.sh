#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../.env"
source $ENV_FILE

API_OUTPUT=src/lib/schema.ts
TEMP_OUTPUT=$(mktemp)
TEMP_JSON=$(mktemp)
OPENAPI_PATH="$PUBLIC_API_ENDPOINT/api/openapi.json"
APPCONFIG_PATH="$PUBLIC_API_ENDPOINT/api/config"

CHECK_MODE=false
if [[ "$1" == "--check" ]]; then
    CHECK_MODE=true
    OPENAPI_PATH=$2
    APPCONFIG_PATH=$3
fi

if ! bunx openapi-typescript $OPENAPI_PATH --enum -o "$TEMP_OUTPUT"; then
    rm -f $TEMP_OUTPUT
    exit 1
fi
if [ $CHECK_MODE = false ]; then
    if ! curl -sS -f -X GET $APPCONFIG_PATH > "$TEMP_JSON"; then
        rm -f $TEMP_OUTPUT $TEMP_JSON
        exit 1
    fi
else
    cat $APPCONFIG_PATH > $TEMP_JSON
fi

{
    echo -n 'export const AppConfig: components["schemas"]["AppConfigSchema"] = '
    cat $TEMP_JSON
    echo ';'
} >> $TEMP_OUTPUT
rm -f $TEMP_JSON

if [ $CHECK_MODE = true ]; then
    cmp -s $TEMP_OUTPUT $API_OUTPUT
    STATUS=$?
    rm -f $TEMP_OUTPUT
    exit $STATUS
else
    mv -f $TEMP_OUTPUT $API_OUTPUT
fi
