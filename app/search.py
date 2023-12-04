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
    print("query_index function called")
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
    print(f"Search query: {search_query}")  # Add this line
    search = app.elasticsearch.search(index=index, body=search_query)
    ids = [int(hit['_source']['id']) for hit in search['hits']['hits'] if hit['_source']['id'] is not None]
    return ids, search['hits']['total']['value']