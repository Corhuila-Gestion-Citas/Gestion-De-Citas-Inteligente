#!/usr/bin/env bash
set -eu

psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" --set=app_user="$POSTGRES_USER" <<'SQL'
ALTER ROLE :"app_user" WITH NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;
SQL
