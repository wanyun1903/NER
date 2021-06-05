# REST API for Named Entity Recognition (NER)

## Pre-requisites
Python3

## Framework:
* Flask
* Docker

## Pretrained NER model
* Spacy 

## Database:
* PostgresSQL (docker image)

## Running the flask application by building a new image with the docker file on the local machine
```
#The directory 
cd NER
# To build the image
docker-compose up -d --build

# To initiate the database
docker-compose exec web python manage.py create_db
```
The applications will be running on docker_IP_Address:5000.

### Example: 
```
http://192.168.99.100:5000/
```

## Application Routes 

- (`/`): index.html. The main page with the relevant buttons to upload the json file and to retrieve the count of the different entities 
- (`/uploader`): Post request - that will take in a file (.json), of which the file can consist of either a single or multiple news articles that have been already processed and identify the entities within each of the news article. 
```
Sample input: can be found in NER/sample_input/sample_news_10.json. 
Sample output:  {"0": "[{"row":0,"text":"Meyer Handelman Co. Increases Position","label":"ORG"}]}. row refers to the index of the news. 
```
- (`/retrieveCount`): Get request - that will retrieve count of the different entities of each unique news article from a PostgreSQL database (docker image). 
```
Sample output:
[{"label":"CARDINAL","count":22,"row":0},{"label":"DATE","count":34,"row":0}]. row refers to the index of the news. 
```

### Credit 
* **Susan Li**  - https://towardsdatascience.com/building-a-flask-api-to-automatically-extract-named-entities-using-spacy-2fd3f54ebbc6 
* **Michael Herman** - https://testdriven.io/blog/dockerizing-flask-with-postgres-gunicorn-and-nginx/ 
