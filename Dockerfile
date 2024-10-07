FROM  --platform=${BUILDPLATFORM} python:3.10-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# RUN apt-get update && apt-get install -y \
#     build-essential \
#     curl \
#     software-properties-common \
#     git \
#     && rm -rf /var/lib/apt/lists/*


#COPY recipe_assistant .
# COPY utils/ utils/
# COPY data/data.csv data/data.csv
# COPY data/time_zone.csv data/time_zone.csv
# COPY data/Food_Images/ data/Food_Images/

COPY data/ data/

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD ["streamlit", "run", "recipe_assistant/app.py"]
