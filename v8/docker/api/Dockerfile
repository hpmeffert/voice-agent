FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY v8/docker/api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY v8/docker/api/app.py /app/app.py
COPY v8/docker/api/protocol_renderer.py /app/protocol_renderer.py
COPY v8/docker/api/event_bus.py /app/event_bus.py
COPY v8/templates/ /app/templates/
COPY v8/docs/admin/ /app/docs/admin/

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
