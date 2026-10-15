FROM python:3.12-slim
WORKDIR /course
COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m pip install --no-cache-dir .
COPY data/churn.csv data/churn.csv
RUN python -m course_ml.train --data data/churn.csv --output artifacts/churn.joblib
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "course_ml.app:app", "--host", "0.0.0.0", "--port", "8000"]
