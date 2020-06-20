import json
import plotly
import pandas as pd

from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

from flask import Flask
from flask import render_template, request, jsonify
from plotly.graph_objs import Bar
from sklearn.externals import joblib
from sqlalchemy import create_engine


app = Flask(__name__)

def tokenize(text):
    tokens = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()

    clean_tokens = []
    for tok in tokens:
        clean_tok = lemmatizer.lemmatize(tok).lower().strip()
        clean_tokens.append(clean_tok)

    return clean_tokens

# load data
engine = create_engine('sqlite:///../data/DisasterResponse.db')
df = pd.read_sql_table('messages', engine)

# load model
model = joblib.load("../models/classifier.pkl")


# index webpage displays cool visuals and receives user input text for model
@app.route('/')
@app.route('/index')
def index():
    
    # extract data needed for visuals
    # TODO: Below is an example - modify to extract data for your own visuals
    genre_counts = df.groupby('genre').count()['message']
    genre_names = list(genre_counts.index)
    genre_counts_floods = df.query('floods == "1"').groupby('genre').count()['message']
    genre_names_floods = list(genre_counts_floods.index)
    categories_counts = df.iloc[:, 5:].sum()
    categories_names = df.columns[5:] 
    
    # create visuals
    # TODO: Below is an example - modify to create your own visuals
    graphs = [
        {
            'data': [
                {
                    "uid": "f4de1f",
                    "hole": 0.1,
                    "name": "Col2",
                    "pull": 0,
                    "type": "pie",
                    "domain": {
                        "x": genre_names,
                        "y": genre_counts,
                    },
                    "marker": {
                        "colors": [
                            "#7fc97f",
                            "#beaed4",
                            "#fdc086"
                        ]
                    },
                    "textinfo": "label+value",
                    "hoverinfo": "all",
                    "labels": genre_names,
                    "values": genre_counts
                }
            ],
           'layout': {
                'title': 'Distribution of Message Genres',
                'yaxis': {
                    'title': "Count"
                },
                'xaxis': {
                    'title': "Genre"
                }
            }
        },
        {
            'data': [                
                {
                    "type": "bar",
                    "x": categories_names,
                     "y": categories_counts,
                    'marker': {
                        'color': '#CC6184'
                    },
                }
            ],
            'layout': {
                'title': 'Distribution of Message Categories',
                'yaxis': {
                    'title': "Count"
                },
                'xaxis': {
                    'title': "Category"
                }
            }
        },
        {
            'data': [
                {
                    "type": "bar",
                    "x": genre_names_floods,
                     "y": genre_counts_floods,
                    'marker': {
                        'color': '#8CB5D3'
                    },
                }
            ],
            'layout': {
                'title': 'Distribution of Messages About Floods Genres',
                'yaxis': {
                    'title': "Count"
                },
                'xaxis': {
                    'title': "Genre"
                }
            }
        }
    ]
    
    # encode plotly graphs in JSON
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    
    # render web page with plotly graphs
    return render_template('master.html', ids=ids, graphJSON=graphJSON)


# web page that handles user query and displays model results
@app.route('/go')
def go():
    # save user input in query
    query = request.args.get('query', '') 

    # use model to predict classification for query
    classification_labels = model.predict([query])[0]
    classification_results = dict(zip(df.columns[4:], classification_labels))

    # This will render the go.html Please see that file. 
    return render_template(
        'go.html',
        query=query,
        classification_result=classification_results
    )


def main():
    app.run(host='0.0.0.0', port=3001, debug=True)


if __name__ == '__main__':
    main()