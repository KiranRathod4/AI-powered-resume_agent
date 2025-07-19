FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir  -r requirements.txt

COPY . . 

EXPOSE 8501

HEALTHCHECK  CMD curl --fail http://localhost:8501/  || exit 1

ENTRYPOINT ["streamlit", "run","app.py", "--Server.port =8501", "--Server.address ==0.0.0.0"]
