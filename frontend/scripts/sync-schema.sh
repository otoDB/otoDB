#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../.env"
source $ENV_FILE

API_OUTPUT=src/lib/schema.ts
TEMP_JSON=$(mktemp)

if ! bunx openapi-typescript "$PUBLIC_API_ENDPOINT/api/openapi.json" --enum -o "$API_OUTPUT"; then
    exit 1
fi

if ! curl -sS -f -X GET "$PUBLIC_API_ENDPOINT/api/config" > "$TEMP_JSON"; then
    rm -f $TEMP_JSON
    exit 1
fi

{
    echo -n 'export const AppConfig: components["schemas"]["AppConfigSchema"] = '
    cat $TEMP_JSON
    echo ';'
} >> $API_OUTPUT

rm -f $TEMP_JSON
