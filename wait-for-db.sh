#!/bin/bash
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
  echo "Waiting for database at $DB_HOST:$DB_PORT..."
  sleep 1
done
exec "$@"
