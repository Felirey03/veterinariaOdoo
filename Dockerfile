FROM odoo:17.0

USER root

RUN apt-get update && apt-get install -y \
    python3-pip \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements si existe (opcional)
COPY requirements.txt .
RUN pip3 install -r requirements.txt || echo "No requirements.txt or install failed"

# Asegurar permisos
RUN mkdir -p /var/lib/odoo /mnt/extra-addons && \
    chown -R odoo:odoo /var/lib/odoo /mnt/extra-addons

USER odoo

# No especificamos ENTRYPOINT ni CMD, usamos el de la imagen base