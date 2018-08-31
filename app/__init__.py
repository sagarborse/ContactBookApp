from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy

# local import
from instance.config import app_config
from flask import request, jsonify, abort

# initialize sql-alchemy
db = SQLAlchemy()

def create_app(config_name):
	print(" create app")
	from app.models import ContactBook
	app = FlaskAPI(__name__, instance_relative_config=True)
	app.config.from_object(app_config[config_name])
	app.config.from_pyfile('config.py')
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
	db.init_app(app)


	@app.route('/contactbooks/', methods=['POST', 'GET'])
	def contactbooks():
		if request.method == "POST":
			name = str(request.data.get('name', ''))
			if name:
				contactbook = ContactBook(name=name)
				contactbook.save()
				response = jsonify({
				    'id': contactbook.id,
				    'name': contactbook.name,
				    'date_created': contactbook.date_created,
				    'date_modified': contactbook.date_modified
				})
				response.status_code = 201
				return response
		else:
			# GET
			contactbooks = ContactBook.get_all()
			results = []

			for contactbook in contactbooks:
				obj = {
				    'id': contactbook.id,
				    'name': contactbook.name,
				    'date_created': contactbook.date_created,
				    'date_modified': contactbook.date_modified
				}
				results.append(obj)
			response = jsonify(results)
			response.status_code = 200
			return response


	@app.route('/contactbooks/<int:id>', methods=['GET', 'PUT', 'DELETE'])
	def contactbook_manipulation(id, **kwargs):
		# retrieve a contactbook using it's ID
		contactbook = ContactBook.query.filter_by(id=id).first()
		if not contactbook:
			# Raise an HTTPException with a 404 not found status code
			abort(404)

		if request.method == 'DELETE':
			contactbook.delete()
			return {
			"message": "contactbook {} deleted successfully".format(contactbook.id) 
			}, 200

		elif request.method == 'PUT':
			name = str(request.data.get('name', ''))
			contactbook.name = name
			contactbook.save()
			response = jsonify({
				'id': contactbook.id,
				'name': contactbook.name,
				'date_created': contactbook.date_created,
				'date_modified': contactbook.date_modified
			})
			response.status_code = 200
			return response
		else:
			# GET
			response = jsonify({
				'id': contactbook.id,
				'name': contactbook.name,
				'date_created': contactbook.date_created,
				'date_modified': contactbook.date_modified
			})
			response.status_code = 200
			return response

	# import the authentication blueprint and register it on the app
	from .auth import auth_blueprint
	app.register_blueprint(auth_blueprint)

	return app