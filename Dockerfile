FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY app.py file_storage.py ./
ENV PYTHONPATH="/app:$PYTHONPATH"

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
