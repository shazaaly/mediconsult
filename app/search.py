from flask import current_app as app
import sqlalchemy as sa

def add_to_index(index, model):
    if not app.elasticsearch:
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    payload['id'] = model.id  # add the database ID to the document
    app.elasticsearch.index(index=index, id=model.id, body=payload)

def remove_from_index(index, model):
	if not app.elasticsearch:
		return
	app.elasticsearch.delete(index=index, id=model.id)

def query_index(index, query, page, per_page):
    if not app.elasticsearch:
        return [], 0
    search_query = {
        'query': {
            'multi_match': {
                'query': query,
                'fields': ['*']
            }
        }
    }
    search = app.elasticsearch.search(index=index, body=search_query)
    ids = [int(hit['_source']['id']) for hit in search['hits']['hits']]  # get the database ID from the document
    return ids, search['hits']['total']['value']