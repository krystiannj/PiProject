##!/bin/bash

BACKUP_DIR="$HOME/backups"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

mkdir -p "$BACKUP_DIR"

docker exec postgres \
pg_dump -U postgres monitoring \
| gzip > "$BACKUP_DIR/monitoring_${TIMESTAMP}.sql.gz"

scp "$BACKUP_DIR/monitoring_${TIMESTAMP}.sql.gz" \
nomadai@10.42.0.1:~/pi_backups/

find "$BACKUP_DIR" \
-name "monitoring_*.sql.gz" \
-mtime +14 \
-delete

echo "Backup completed"
