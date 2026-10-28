# Servidor Linux Seguro

Proyecto personal orientado a practicar administración de servidores Linux, seguridad básica, despliegue web y fundamentos de DevOps.

El laboratorio fue implementado sobre Ubuntu Server en VirtualBox y evolucionó desde una configuración tradicional con SSH, UFW, Nginx, Flask, Gunicorn y systemd hacia una arquitectura contenerizada utilizando Docker y Docker Compose.

## Tecnologías utilizadas

- Ubuntu Server
- Oracle VirtualBox
- OpenSSH
- UFW
- Nginx
- Python
- Flask
- Gunicorn
- systemd
- Docker
- Docker Compose
- Git y GitHub

## Arquitectura inicial

```text
Windows Host
    |
    | HTTP -> 127.0.0.1:8080
    v
VirtualBox NAT
    |
    v
Ubuntu Server
    |
    +-- Nginx :80
          |
          v
      Gunicorn :5000
          |
          v
        Flask
```

En esta primera etapa Nginx, Gunicorn y Flask eran ejecutados directamente sobre Ubuntu Server.

## Arquitectura contenerizada

Posteriormente la aplicación fue migrada a una arquitectura multi-contenedor:

```text
Windows
   |
   | 127.0.0.1:8080
   v
VirtualBox NAT
   |
   v
Ubuntu Server :80
   |
   v
Docker Compose
   |
   +-- Contenedor Nginx :80
   |        |
   |        | Reverse Proxy
   |        v
   +-- Contenedor Flask/Gunicorn :5000
```

Docker Compose crea además una red interna que permite la comunicación entre ambos servicios.

## Dockerización de Flask

Se creó una imagen propia para la aplicación Flask utilizando el siguiente `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
```

Las dependencias utilizadas fueron:

```text
Flask
gunicorn
```

La imagen puede construirse mediante:

```bash
docker build -t flask-seguro .
```

## Nginx en Docker

Nginx fue ejecutado en un contenedor independiente y configurado como reverse proxy.

Configuración principal:

```nginx
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://flask-app:5000;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

A diferencia de la arquitectura inicial, Nginx ya no utiliza:

```text
127.0.0.1:5000
```

para localizar Flask.

Ahora utiliza:

```text
flask-app:5000
```

porque ambos servicios se encuentran dentro de una red Docker y pueden comunicarse utilizando el nombre del contenedor.

## Docker Compose

Se utilizó Docker Compose para administrar ambos servicios desde un único archivo:

```yaml
services:

  app:
    build: .
    container_name: flask-app
    expose:
      - "5000"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: nginx_proxy
    ports:
      - "80:80"
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - app
    restart: unless-stopped
```

La aplicación completa puede iniciarse mediante:

```bash
docker compose up -d
```

Verificar los servicios:

```bash
docker compose ps
```

Detener y eliminar los contenedores:

```bash
docker compose down
```

Y volver a desplegar todo:

```bash
docker compose up -d
```

## Comunicación entre contenedores

La comunicación interna sigue este flujo:

```text
Cliente
   ↓
Nginx
   ↓
flask-app:5000
   ↓
Gunicorn
   ↓
Flask
```

Nginx utiliza la red interna de Docker para encontrar el contenedor `flask-app`.

Esto permite que el puerto `5000` no tenga que estar publicado directamente hacia el host.

## Headers del reverse proxy

La aplicación Flask permite comprobar qué dirección observa directamente y qué información recibió desde Nginx.

Ejemplo obtenido:

```text
IP vista por Flask: 172.18.0.3
X-Real-IP: 172.18.0.1
X-Forwarded-For: 172.18.0.1
```

Esto demuestra que la petición pasa primero por Nginx antes de llegar al contenedor Flask.

## Comandos útiles

Ver contenedores:

```bash
docker ps
```

Ver imágenes:

```bash
docker images
```

Ver los servicios de Compose:

```bash
docker compose ps
```

Ver logs:

```bash
docker compose logs
```

Logs específicos de Nginx:

```bash
docker logs nginx_proxy
```

Logs de Flask/Gunicorn:

```bash
docker logs flask-app
```

## Resultado final

El proyecto evolucionó desde una instalación tradicional:

```text
Ubuntu
→ Nginx
→ Gunicorn
→ Flask
```

hacia una arquitectura contenerizada:

```text
Ubuntu
→ Docker Compose
   ├── Nginx
   └── Flask + Gunicorn
```

Con esta segunda arquitectura se consiguió:

- aislar las dependencias de la aplicación;
- crear un entorno reproducible;
- separar Nginx y Flask en diferentes contenedores;
- implementar comunicación mediante una red interna de Docker;
- gestionar múltiples servicios mediante Docker Compose;
- mantener Nginx como único punto de entrada hacia la aplicación.