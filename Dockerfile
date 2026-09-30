FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

CMD ["python", "flasktest.py"]