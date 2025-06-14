FROM python:3.11-slim

# Ρύθμιση environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Εγκατάσταση system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        gettext \
        wget \
        curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Δημιουργία directories
WORKDIR /app
RUN mkdir -p /app/static /app/media /app/logs

# Εγκατάσταση Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Αντιγραφή κώδικα
COPY . /app/

# Δημιουργία user για security
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Εντολές εκκίνησης
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]