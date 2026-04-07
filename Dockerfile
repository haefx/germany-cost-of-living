FROM python:3.12-slim

WORKDIR /app

# System-Dependencies für BeautifulSoup/lxml
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python-Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Quellcode kopieren
COPY . .

# DB-Verzeichnis anlegen und Seed ausführen
RUN mkdir -p data && python -c "import sys; sys.path.insert(0, 'src'); from db import init_db; init_db()" && python src/seed_data.py

# Umami Analytics in Streamlit's index.html injizieren
RUN python -c "import streamlit, os; p=os.path.join(os.path.dirname(streamlit.__file__),'static','index.html'); \
    html=open(p).read(); \
    html=html.replace('</head>','<script defer src=\"https://analytics.world-on-fire.com/script.js\" data-website-id=\"673dd04a-aa25-45cb-8aeb-92db1e1bfc04\"></script></head>'); \
    open(p,'w').write(html)"

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8501/_stcore/health')"

CMD ["streamlit", "run", "app/streamlit_app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
