#!/usr/bin/env bash
set -eu

mongosh \
  --username "$MONGO_INITDB_ROOT_USERNAME" \
  --password "$MONGO_INITDB_ROOT_PASSWORD" \
  --authenticationDatabase admin \
  "$MONGO_INITDB_DATABASE" \
  --quiet <<MONGO
if (!db.getUser("$MONGODB_APP_USER")) {
  db.createUser({
    user: "$MONGODB_APP_USER",
    pwd: "$MONGODB_APP_PASSWORD",
    roles: [{ role: "readWrite", db: "$MONGO_INITDB_DATABASE" }]
  });
}
MONGO
