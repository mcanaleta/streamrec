FROM python:3.12.8-slim
WORKDIR /app
COPY pyproject.toml poetry.lock .
# RUN pip install poetry && poetry install --only main --no-root --no-directory
COPY streamrec/ ./streamrec
RUN pip install .
CMD ["streamrec"]