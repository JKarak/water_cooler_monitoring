### Сборка образа
```
docker build -t wcs/backend:latest .
```

### Запуск образа
```
docker run --rm -p 127.0.0.1:8000:8000 wcs/backend:latest
```
