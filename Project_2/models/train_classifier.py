import sys
import pandas as pd
from sqlalchemy import create_engine
import pickle

import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
nltk.download(['punkt', 'wordnet', 'averaged_perceptron_tagger'])

from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

def load_data(database_filepath):
    """Load data from the database and extract the names of the attributes"""

    engine = create_engine('sqlite:///{}'.format(database_filepath))
    df = pd.read_sql_table('disaster_response_df', engine)
    
    category_names = ['related', 'request', 'offer', 'aid_related', 'medical_help', 
                      'medical_products', 'search_and_rescue', 'security', 'military', 
                      'child_alone', 'water', 'food', 'shelter', 'clothing', 'money', 
                      'missing_people', 'refugees', 'death', 'other_aid', 'infrastructure_related', 
                      'transport', 'buildings', 'electricity', 'tools', 'hospitals', 'shops', 
                      'aid_centers', 'other_infrastructure', 'weather_related', 'floods', 
                      'storm', 'fire', 'earthquake', 'cold', 'other_weather', 'direct_report']
    
    X = df['message']
    Y = df[category_names]
    
    return X, Y, category_names

def tokenize(text):
    """A text preprocessing step."""
    tokens = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()

    clean_tokens = []
    for tok in tokens:
        clean_tok = lemmatizer.lemmatize(tok).lower().strip()
        clean_tokens.append(clean_tok)
        
    return clean_tokens


def build_model():
    """Build the model aotu training pipeline."""
    pipeline = Pipeline([
        ('vect', CountVectorizer(tokenizer = tokenize)),
        ('tfidf', TfidfTransformer()),
        ('clf', RandomForestClassifier())
    ])

    parameters = {
         "vect__max_df": (0.5, 0.75, 1.0),
        "vect__ngram_range": ((1, 1), (1, 2)),  # unigrams or bigrams
        "clf__max_iter": (20,),
        "clf__alpha": (0.00001, 0.000001),
        "clf__penalty": ("l2", "elasticnet"),
    }

    model = GridSearchCV(pipeline, parameters, verbose=1)

    return pipeline


def evaluate_model(model, X_test, Y_test, category_names):
    """Evaluate the performance of model"""
    y_pred = model.predict(X_test).astype(int)
    print(classification_report(Y_test, y_pred, target_names=category_names))

def save_model(model, model_filepath):
    """Save the best model."""
    pickle.dump(model, open(model_filepath, "wb"))


def main():
    if len(sys.argv) == 3:
        database_filepath, model_filepath = sys.argv[1:]
        print('Loading data...\n    DATABASE: {}'.format(database_filepath))
        X, Y, category_names = load_data(database_filepath)
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)
        
        print('Building model...')
        model = build_model()
        
        print('Training model...')
        model.fit(X_train, Y_train)
        
        print('Evaluating model...')
        evaluate_model(model, X_test, Y_test, category_names)

        print('Saving model...\n    MODEL: {}'.format(model_filepath))
        save_model(model, model_filepath)

        print('Trained model saved!')

    else:
        print('Please provide the filepath of the disaster messages database '\
              'as the first argument and the filepath of the pickle file to '\
              'save the model to as the second argument. \n\nExample: python '\
              'train_classifier.py ../data/DisasterResponse.db classifier.pkl')


if __name__ == '__main__':
    main()