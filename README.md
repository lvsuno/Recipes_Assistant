# llm_zoomcamp_project
This is the final project for llm_zoomcamp

Recipe data that can be downloaded on [kaggle](https://www.kaggle.com/datasets/pes12017000148/food-ingredients-and-recipe-dataset-with-images?resource=download).

https://www.epicurious.com/
## Additional notes for those trying the streamlit/grafana out

1) The following packages are required when you run some of .py scripts

```
pip install psycopg2-binary python-dotenv
pip install pgcli
```


2) To download the phi3 model to the container
```
docker-compose up -d
docker-compose exec ollama ollama pull phi3
```
