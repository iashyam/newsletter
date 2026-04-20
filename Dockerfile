FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
COPY web/requirements.txt ./web_requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -r web_requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "web.app:app", "--host", "0.0.0.0", "--port", "8000"]
