#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../.env"
source $ENV_FILE

API_OUTPUT=src/lib/schema.ts
TEMP_OUTPUT=$(mktemp)
TEMP_JSON=$(mktemp)
OPENAPI_PATH=${1:-"$PUBLIC_API_ENDPOINT/api/openapi.json"}

if ! bunx openapi-typescript $OPENAPI_PATH --enum -o "$TEMP_OUTPUT"; then
    rm -f $TEMP_OUTPUT
    exit 1
fi

if ! curl -sS -f -X GET "$PUBLIC_API_ENDPOINT/api/config" > "$TEMP_JSON"; then
    rm -f $TEMP_OUTPUT $TEMP_JSON
    exit 1
fi

{
    echo -n 'export const AppConfig: components["schemas"]["AppConfigSchema"] = '
    cat $TEMP_JSON
    echo ';'
} >> $TEMP_OUTPUT
rm -f $TEMP_JSON

if [[ $2 == "--check" ]]; then
    cmp -s $TEMP_OUTPUT $API_OUTPUT
    STATUS=$?
    rm -f $TEMP_OUTPUT
    exit $STATUS
else
    mv -f $TEMP_OUTPUT $API_OUTPUT
fi
