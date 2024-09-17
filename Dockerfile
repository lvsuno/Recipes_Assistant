FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#COPY recipe_assistant .
COPY utils/ utils/
COPY data/data.csv data/data.csv
COPY data/time_zone.csv data/time_zone.csv
COPY data/Food_Images/ data/Food_Images/

CMD ["streamlit", "run", "recipe_assistant/app.py"]