#!/bin/sh
set -e
# Attend que le poste de contrôle ait généré la clé publique
i=0
while [ ! -f /keys/id_ed25519.pub ]; do
  i=$((i+1)); [ "$i" -gt 60 ] && { echo "clé publique introuvable" >&2; exit 1; }
  sleep 1
done
mkdir -p /run/sshd /home/deploy/.ssh
cp /keys/id_ed25519.pub /home/deploy/.ssh/authorized_keys
chown -R deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys
ssh-keygen -A
exec /usr/sbin/sshd -D -e
