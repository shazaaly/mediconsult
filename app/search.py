from flask import current_app

def add_to_index():
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
	if not current_app.elasticsearch:
		return
	payload = {}  # dictionary that contains all the searchable fields of the model instance and their values.#
	for field in model.__searchable:
		payload['field'] = getattr(model, field)
	current_app.elasticsearch.index(index=index, id=model.id, document=payload)
