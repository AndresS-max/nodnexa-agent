# Guía de Deploy en Oracle Cloud Infrastructure (OCI)

Esta guía documenta el despliegue del Agente Nodnexa en una VM Always Free de OCI
usando Docker. Servicios de OCI utilizados: **OCI Compute** (VM) + **VCN** (red).

## 1. Crear la instancia (VM)

En la consola de OCI ([cloud.oracle.com](https://cloud.oracle.com)):

1. Menú ☰ → **Compute** → **Instances** → **Create instance**
2. Nombre: `nodnexa-agent`
3. Image: **Ubuntu 24.04** (Canonical)
4. Shape (elegir uno, ambos Always Free):
   - **VM.Standard.A1.Flex** — ARM, hasta 4 OCPUs y 24 GB RAM (recomendado).
     Si aparece "Out of capacity", reintentar más tarde o usar el siguiente.
   - **VM.Standard.E2.1.Micro** — AMD, 1 OCPU y 1 GB RAM (alcanza, pero justo).
5. En **Add SSH keys**: generar/subir tu clave pública SSH.
6. **Create** y esperar a que el estado sea `RUNNING`. Anotar la **IP pública**.

## 2. Abrir el puerto de la app

1. En la instancia → **Virtual cloud network** → **Security Lists** → la default
2. **Add Ingress Rule**:
   - Source CIDR: `0.0.0.0/0`
   - IP Protocol: TCP · Destination Port Range: `8501`

## 3. Instalar Docker en la VM

```bash
ssh ubuntu@IP_PUBLICA
sudo apt update && sudo apt install -y docker.io git
sudo usermod -aG docker ubuntu && newgrp docker
# Firewall interno de Ubuntu (iptables de OCI): abrir el puerto también aquí
sudo iptables -I INPUT -p tcp --dport 8501 -j ACCEPT
sudo netfilter-persistent save 2>/dev/null || true
```

## 4. Desplegar el agente

```bash
git clone https://github.com/AndresS-max/nodnexa-agent.git
cd nodnexa-agent

# Crear el .env con las API keys (nunca están en el repo)
cat > .env << 'EOF'
ANTHROPIC_API_KEY=xxxx
VOYAGE_API_KEY=xxxx
EOF

docker build -t nodnexa-agent .
docker run -d --name nodnexa \
  --restart unless-stopped \
  -p 8501:8501 \
  --env-file .env \
  -v nodnexa_vectorstore:/app/data/vectorstore \
  -v nodnexa_logs:/app/logs \
  nodnexa-agent
```

El primer arranque construye el índice vectorial automáticamente
(ver `docker-entrypoint.sh`). Verificar con `docker logs -f nodnexa`.

## 5. Acceder

La app queda pública en: `http://IP_PUBLICA:8501`

## Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| "Out of capacity" al crear la VM | Sin stock de A1 en la región | Reintentar (a distintas horas) o usar E2.1.Micro |
| La página no carga desde fuera | Puerto sin abrir | Revisar Security List (paso 2) e iptables (paso 3) |
| Contenedor se reinicia | Falta el `.env` | `docker logs nodnexa` y revisar las keys |
| Respuestas con error de rate limit | Límite gratuito de Voyage (3 req/min) | Esperar 1 min o agregar método de pago en Voyage |
