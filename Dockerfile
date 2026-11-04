FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY lexer.py gramatica.py interprete.py main.py ./
COPY ejemplos ./ejemplos
COPY pruebas ./pruebas
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "main.py"]
