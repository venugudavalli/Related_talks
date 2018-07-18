from flask import current_app, g
#from pydocumentdb import document_client
from pymongo import MongoClient

# connect to Mongodb and return client instance
def get_client():
    if 'client' not in g:
        g.client = MongoClient(current_app.config['MONGO_URI'])
    return g.client

# return database name
def get_db():
    client = get_client()
    if 'db' not in g:
        g.db = current_app.config['MONGO_DATABASE']
    return g.db

# return colllection name 'talks'
def get_talks_collection():
    client = get_client()
    db = get_db()
    if 'talks_coll' not in g:
        g.talks_coll = 'talks'
    return g.talks_coll

def get_similarities_collection():
    client = get_client()
    db = get_db()
    if 'similarities_coll' not in g:
        g.similarities_coll = 'similarities'

    return g.similarities_coll


def get_similar_talks(talk_id, n=10):
    client = get_client()
    db = get_db()
    coll = "similarities"
    #coll = get_similarities_collection()
    query = {'id': talk_id}
    fields = {'_id': 0, 'id': 1, 'similarities.similarity': 1 , 'similarities.other_id': 1}
    ordby  = [('similarities.similarity',-1)]
    
    try:
        talk_similarities = client[db][coll].find(query, fields).sort(ordby)

        similar_talks = []
        for sim in talk_similarities:
            for k , val in sim.items():
                if k =='similarities' :
            
                    for d in val:
                
                        similar_talks.append([d['other_id'], d['similarity']])


        similar_talks.sort(key=lambda x: x[1], reverse=True)
        #print(similar_talks[0:10])
        talk_ids = [x[0] for x in similar_talks[0:10]]
        #print(talk_ids)
        similar_talks = dict(similar_talks[0:10])
        query = { 'id': { "$in": talk_ids } }
        fields = {'_id': 0, 'id': 1, 'published_at': 1, 'title' : 1}
        ordby  = [('published_at',-1)]
        
        other_talks = list(query_talks(query, fields, ordby, n))
        #print(len(other_talks))
        #ctr = 0
        for row in other_talks:
            #print(similar_talks[row['id']])
            row['similarity'] = similar_talks[row['id']]
            #print(row)
        other_talks.sort(key=lambda x: x['similarity'], reverse=True)
        
    except StopIteration:
        return []
    
    return other_talks

def query_talks(q, sfields, orderby, nrows):
    client = get_client()
    db = get_db()
    coll = get_talks_collection()
    return list(client[db][coll].find(q, sfields).sort(orderby).limit(nrows))
