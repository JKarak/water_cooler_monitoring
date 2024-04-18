### Запуск контейнеров из нестандартного конфигурационного файла
```
docker compose -f docker-compose.production.yml up -d
```

### Пересоздание контейнеров из образов при запуске
```
docker compose up -d --force-recreate --build
```