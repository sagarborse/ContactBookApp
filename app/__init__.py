from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy

# local import
from instance.config import app_config
from flask import Flask, request, jsonify, abort, make_response, send_from_directory

# initialize sql-alchemy
db = SQLAlchemy()

def create_app(config_name):
	print(" create app")
	from app.models import ContactBook, User
	app = FlaskAPI(__name__, instance_relative_config=True, static_url_path='/')
	app.config.from_object(app_config[config_name])
	app.config.from_pyfile('config.py')
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
	db.init_app(app)

	@app.route('/loaderio-1b8c02206cb0452aff96f35c981d71b7.txt')
	def static_from_root():
		#exit(app.static)
		return send_from_directory('static/', request.path[1:])

	@app.route('/contactbooks/', methods=['POST', 'GET'])
	def contactbooks():
		# Get the access token from the header
		auth_header = request.headers.get('Authorization')
		access_token = auth_header.split(" ")[1]

		if access_token:
			# Attempt to decode the token and get the User ID
			user_id = User.decode_token(access_token)
			if not isinstance(user_id, str):
			    # Go ahead and handle the request, the user is authenticated

				if request.method == "POST":
					name = str(request.data.get('name', ''))
					if name:
						contactbook = ContactBook(name=name, created_by=user_id)
						contactbook.save()
						response = jsonify({
						    'id': contactbook.id,
						    'name': contactbook.name,
						    'date_created': contactbook.date_created,
						    'date_modified': contactbook.date_modified,
						    'created_by': user_id
						})
						#response.status_code = 201
						return make_response(response), 201
				else:
					# GET
					contactbooks = ContactBook.query.filter_by(created_by=user_id)
					results = []

					for contactbook in contactbooks:
						obj = {
						    'id': contactbook.id,
						    'name': contactbook.name,
						    'date_created': contactbook.date_created,
						    'date_modified': contactbook.date_modified,
						    'created_by': contactbook.created_by
						}
						results.append(obj)
					
					return make_response(jsonify(results)), 200
			else:
				# user is not legit, so the payload is an error message
				message = user_id
				response = {
					'message': message
				}
				return make_response(jsonify(response)), 401


	@app.route('/contactbooks/<int:id>', methods=['GET', 'PUT', 'DELETE'])
	def contactbook_manipulation(id, **kwargs):
		# get the access token from the authorization header
		auth_header = request.headers.get('Authorization')
		access_token = auth_header.split(" ")[1]

		if access_token:
			# Get the user id related to this access token
			user_id = User.decode_token(access_token)

			#print(user_id)
			if not isinstance(user_id, str):
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
						'date_modified': contactbook.date_modified,
						'created_by': contactbook.created_by
					})
					return make_response(response), 200
				else:
					# GET
					response = jsonify({
						'id': contactbook.id,
						'name': contactbook.name,
						'date_created': contactbook.date_created,
						'date_modified': contactbook.date_modified,
						'created_by': contactbook.created_by
					})
					return make_response(response), 200
			else:
				# user is not legit, so the payload is an error message
				message = user_id
				response = {
					'message': message
				}
				# return an error response, telling the user he is Unauthorized
				return make_response(jsonify(response)), 401

	# import the authentication blueprint and register it on the app
	from .auth import auth_blueprint
	app.register_blueprint(auth_blueprint)

	return app