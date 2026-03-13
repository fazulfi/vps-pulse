FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/opt/vps-pulse

WORKDIR /opt/vps-pulse

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY config/config.example.json ./config/config.json
COPY entrypoint.sh ./entrypoint.sh

RUN chmod +x /opt/vps-pulse/entrypoint.sh

ENTRYPOINT ["/opt/vps-pulse/entrypoint.sh"]
