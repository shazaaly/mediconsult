from flask import current_app as app
import sqlalchemy as sa

def add_to_index(index, model):
	"""
	Add the searchable fields of the model to the Elasticsearch index.

	This function checks if the Elasticsearch instance is available and then
	creates a payload containing the searchable fields of the model. It then
	indexes the document in Elasticsearch using the payload.

	Note: Make sure to set the `__searchable` attribute on the model to specify
	the fields that should be included in the search index.

	Returns:
		None
	"""
	if not app.elasticsearch:
		return
	payload = {}  # dictionary that contains all the searchable fields of the model instance and their values.#
	for field in model.__searchable:
		payload['field'] = getattr(model, field)
	app.elasticsearch.index(index=index, id=model.id, document=payload)


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
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']