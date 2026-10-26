\# Servidor Linux Seguro Alvaro



Proyecto personal orientado a practicar administración de servidores Linux, seguridad básica, despliegue web y fundamentos de DevOps.

El laboratorio fue implementado sobre Ubuntu Server en VirtualBox y fue evolucionando desde una configuración básica con SSH y Nginx hasta una arquitectura con reverse proxy, Flask, Gunicorn y systemd.


\## Tecnologías

\- Ubuntu Server

\- VirtualBox

\- OpenSSH

\- UFW

\- Nginx

\- Git/GitHub

\- Python

\- Flask

\- systemd

- Docker


Arquitectura actual

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


\## Implementado

\- Creación de usuarios y grupos

\- Gestión de permisos con chmod y chown

\- Acceso remoto por SSH

\- Firewall UFW

\- Servidor web Nginx

\- Port forwarding

\- Revisión de logs

\- Creación de aplicación web con Flask

\- Configuración de Nginx como reverse proxy

\- Uso de headers X-Real-IP y X-Forwarded-For

\- Ejecución de Flask mediante Gunicorn

\- Creación de un servicio systemd

\- Inicio automático de la aplicación flask al arrancar Ubuntu

- Containerización de la aplicación Flask con Docker



\## USUARIOS, GRUPOS Y PERMISOS

\- Ejemplo de creación de usuario y grupo:

    sudo adduser prueba
    sudo groupadd seguro
    sudo usermod -aG seguro prueba

\- Ejemplo de configuración de propietario y permisos:

    sudo chown alvaro:seguro /proyecto-seguro
    sudo chmod 750 /proyecto-seguro

\## Firewall UFW

\- Se habilitaron únicamente los servicios necesarios:

    sudo ufw allow OpenSSH
    sudo ufw allow 'Nginx HTTP'
    sudo ufw enable
    sudo ufw status

\- Puertos principales:

    22/TCP -> SSH
    80/TCP -> HTTP / Nginx

\## Port Forwarding

\- VirtualBox utiliza NAT, por lo que se configuraron las siguientes reglas:

    SSH:
    127.0.0.1:2222 -> 10.0.2.15:22

    HTTP:
    127.0.0.1:8080 -> 10.0.2.15:80

\- Esto permite acceder desde Windows al servidor Ubuntu sin exponer directamente la    máquina virtual.

\## Nginx

Inicialmente Nginx fue utilizado como servidor web para servir un archivo HTML.

\- Posteriormente fue configurado como reverse proxy:

    location / {
        proxy_pass http://127.0.0.1:5000;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

Con esta configuración, Nginx recibe las peticiones HTTP y las reenvía hacia la aplicación Flask.

\## Aplicación Flask

La aplicación se ejecuta internamente en:

    127.0.0.1:5000

\- Ejemplo básico:

    from flask import Flask, request

    app = Flask(__name__)

    @app.route("/")
    def inicio():
        ip_real = request.headers.get("X-Real-IP")
        ip_forwarded = request.headers.get("X-Forwarded-For")

        return f"""
        <h1>Servidor de Linux Seguro</h1>
        <p>IP vista por Flask: {request.remote_addr}</p>
        <p>X-Real-IP: {ip_real}</p>
        <p>X-Forwarded-For: {ip_forwarded}</p>
        """

    if __name__ == "__main__":
        app.run(host="127.0.0.1", port=5000)

\## Gunicorn

El servidor integrado de Flask se utilizó inicialmente para desarrollo.

\- Posteriormente se utilizó Gunicorn como servidor WSGI:

    gunicorn -b 127.0.0.1:5000 app:app

Gunicorn se encarga de ejecutar la aplicación Flask de una forma más adecuada para un entorno de producción.

\## systemd

Se creó un servicio personalizado:

    /etc/systemd/system/flask-app.service

\- Configuración:

    [Unit]
    Description=Gunicorn para app Flask
    After=network.target

    [Service]
    User=alvaro
    Group=www-data
    WorkingDirectory=/home/alvaro/app-python
    Environment="PATH=/home/alvaro/app-python/venv/bin"
    ExecStart=/home/alvaro/app-python/venv/bin/gunicorn -b 127.0.0.1:5000 app:app
    Restart=always

    [Install]
    WantedBy=multi-user.target

\- Posteriormente se habilitó el servicio:

    sudo systemctl daemon-reload
    sudo systemctl enable flask-app
    sudo systemctl start flask-app

Estado:

    systemctl status flask-app

Gracias a systemd, Gunicorn se inicia automáticamente cuando arranca Ubuntu Server.

\## Logs

\- Logs de Nginx:

    sudo tail -f /var/log/nginx/access.log
    sudo tail -f /var/log/nginx/error.log

\- Logs de autenticación:

    sudo tail -f /var/log/auth.log

\- Logs del servicio Flask/Gunicorn:

    sudo journalctl -u flask-app

## Docker

Como evolución del despliegue original, la aplicación Flask fue containerizada con Docker.

Se creó una imagen basada en `python:3.12-slim` que incluye las dependencias necesarias para ejecutar la aplicación mediante Gunicorn.

### Archivos utilizados

```text
app-python/
├── app.py
├── requirements.txt
└── Dockerfile
```

El archivo `requirements.txt` contiene las dependencias principales:

```text
Flask
gunicorn
```

El `Dockerfile` utilizado es:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
```

### Construcción de la imagen

La imagen se construyó con:

```bash
docker build -t flask-seguro .
```

La imagen generada se puede verificar mediante:

```bash
docker images
```

### Ejecución del contenedor

Para ejecutar la aplicación se utilizó:

```bash
docker run -d --name flask-app -p 5000:5000 flask-seguro
```

El mapeo:

```text
5000:5000
```

representa:

```text
Puerto 5000 del host Ubuntu -> Puerto 5000 del contenedor
```

El contenedor puede verificarse con:

```bash
docker ps
```

y la aplicación puede probarse desde Ubuntu mediante:

```bash
curl http://127.0.0.1:5000
```

Con esta etapa, Gunicorn y Flask se ejecutan dentro de un contenedor Docker, permitiendo empaquetar la aplicación y sus dependencias en un entorno reproducible.

> Nota: la integración de Nginx dentro de Docker y el uso de Docker Compose quedan como una siguiente etapa del proyecto.