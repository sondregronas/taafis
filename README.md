# Tåfis 🧦
Enkelt API for å knytte opp webhooks til en `Docker.sock` - kun restart av containere støttes foreløpig.

## Bruk
Rediger `WEBHOOK_SECRET` i `docker-compose.yml`, dersom du ønsker å sikre webhooken.
```bash
docker-compose up -d
```
