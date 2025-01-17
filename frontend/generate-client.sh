#! /usr/bin/env bash

set -e
set -x

cd ..
uv run openapi.py > openapi.json
node frontend/modify-openapi-operationids.js
mv openapi.json frontend/
cd frontend
npm run generate-client
npx biome format --write ./src/client
