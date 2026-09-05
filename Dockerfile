FROM python:3.11-slim-bullseye
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY ./requirements.txt requirements.txt
RUN uv pip install --no-cache-dir -r requirements.txt --system
RUN mkdir /config

ADD driver.json .
ADD uc_intg_awol_valerion ./uc_intg_awol_valerion

# Configuration path
ENV UC_CONFIG_HOME="/config"

CMD ["python3", "-m", "uc_intg_awol_valerion"]