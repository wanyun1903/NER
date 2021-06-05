from flask import Flask, jsonify,render_template,url_for,request
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import spacy
import json
import os
import datetime
from collections import Counter
from project.config import Config

#http://192.168.99.100:5000/

nlp = spacy.load('en_core_web_sm')

# Set up the application
app = Flask(__name__)
app.config.from_object("project.config.Config")

# Set up the database
db = SQLAlchemy(app)

#Define the model class
class entitiescount(db.Model):

    __tablename__ = 'entitiescount'

    id = db.Column(db.Integer, primary_key=True)
    label=db.Column(db.String, nullable=False)
    count = db.Column(db.Integer,nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    row =  db.Column(db.Integer,nullable=False)

    def __hash__(self):
        return hash(self.name)

#Set up the route
#Main route
@app.route('/')
def index():
	return render_template("index.html")

def allowed_file(filename):
    '''
    Returns: Bool 
    Parameter value: filename as str
    '''
    ALLOWED_EXTENSIONS = set(['json'])
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def read_json_file(filename):
    '''
    Returns: pandas dataframe
    Parameter value: filename as str
    '''
    with open(filename) as f:
        json_data = json.load(f)
        df = pd.DataFrame.from_dict(json_data, orient="index")
    return df 

def processing_func(jsonfilename):
    '''
    Returns: dictionary
    Parameter value: filename as str
    '''
    #Read the json file
    df = read_json_file(jsonfilename)
    
    #Set the current time
    ct = datetime.datetime.now()
    
    #Initialize empty dataframe
    df_label = pd.DataFrame()
    df_count = pd.DataFrame()
    
    #Retrieve the label for each news and keep track of the counts
    for row in range(0,len(df)):
        doc = nlp(df['news'][row])
        tuple_list = [(row,X.text, X.label_) for X in doc.ents]
        df_label = df_label.append(pd.DataFrame(tuple_list, columns =['row', 'text', 'label']))
    
        labels = [x.label_ for x in doc.ents]
        labels_count = Counter(labels)
        df_current_count = pd.DataFrame.from_dict(labels_count, orient='index').reset_index()
        df_current_count = df_current_count.rename(columns={'index':'label', 0:'count'})
        df_current_count['timestamp']=ct
        df_current_count['row']=row
        df_count = df_count.append(df_current_count)

    #Save the count to the database
    df_count.set_index('label', inplace=True)
    df_count.to_sql('entitiescount', con = db.session.bind, if_exists = 'append', chunksize = 8000)
    db.session.commit()

    df_json_label = df_label.groupby(['row']).apply(lambda x: x.to_json(orient='records')).to_dict()
    return df_json_label

@app.route('/uploader', methods=['POST'])
def uploader_func():
    if request.method == 'POST':
        file = request.files['input-1']
        if file and allowed_file(file.filename):
            filename = os.path.join(Config.UPLOAD_FOLDER, file.filename)
            file.save(filename)
            json_data = processing_func(filename)
            return json_data

@app.route('/retrieveCount',methods=['GET'])
def retrieve_count():
    if request.method=='GET':
        df_count = pd.read_sql("""
               SELECT DISTINCT label,count,row FROM public.entitiescount ORDER BY row,label
                """,con = db.session.bind)

        json_list = df_count.to_json(orient = "records")
        return(json_list)


# To start the container
#docker-compose up -d --build
# To reinitiate the database
#docker-compose exec web python manage.py create_db

#Credit 
#https://towardsdatascience.com/building-a-flask-api-to-automatically-extract-named-entities-using-spacy-2fd3f54ebbc6
#Susan Li

#https://testdriven.io/blog/dockerizing-flask-with-postgres-gunicorn-and-nginx/
#Michael Herman 
#

'''
MIT License

Copyright (c) 2021 Michael Herman

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''