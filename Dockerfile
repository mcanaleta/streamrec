FROM python:3.13.2-slim
WORKDIR /app
COPY pyproject.toml poetry.lock .
# RUN pip install poetry && poetry install --only main --no-root --no-directory
COPY streamrec/ ./streamrec
RUN pip install .
CMD ["streamrec"]