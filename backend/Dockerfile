FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including build tools and LaTeX
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    ffmpeg \
    libcairo2-dev \
    libpango1.0-dev \
    pkg-config \
    python3-dev \
    texlive \
    texlive-latex-extra \
    texlive-fonts-extra \
    texlive-science \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py", "3003"]
