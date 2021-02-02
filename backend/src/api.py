import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


def populate_db():
    drink1 = {'title':'Americano',
              'recipe':[{'color': 'black', 'name': 'coffee', 'parts': 1}]}
    drink2 = {'title':'Cappuccino',
              'recipe':[{'color': 'black', 'name': 'coffee', 'parts': 2},
                        {'color': 'white', 'name': 'milk', 'parts': 1}]}
    drink3 = {'title':'White Mocha',
              'recipe':[{'color': 'black', 'name': 'coffee', 'parts': 2},
                        {'color': 'white', 'name': 'milk', 'parts': 1},
                        {'color': 'brown', 'name': 'white sirup', 'parts': 1}]}

    for drink in (drink1, drink2, drink3):
        new_drink = Drink()
        new_drink.title = drink['title']
        new_drink.recipe = json.dumps(drink['recipe'])
        new_drink.insert()

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()
# populate_db()

## ROUTES
'''
@DONE implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.order_by(Drink.title).all()
    data = {'success': True,
            'drinks': [drink.short() for drink in drinks]}

    # Abort if the database query returned no drinks
    if len(drinks) == 0:
        abort(404)

    return jsonify(data), 200

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
def get_drinks_detail():
    drinks = Drink.query.order_by(Drink.title).all()
    data = {'success': True,
            'drinks': [drink.long() for drink in drinks]}

    # Abort if the database query returned no drinks
    if len(drinks) == 0:
        abort(404)

    return jsonify(data), 200


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
def post_drinks():
    body = request.get_json()

    try:
        # Check presence of necessary attributes
        title = body['title']
        recipe = body['recipe']
        # Check recipe is in valid format
        if not isinstance(recipe, list) or len(recipe)==0:
            raise Exception
    except:
        abort(400)

    try:
        new_drink = Drink()
        new_drink.title = title
        new_drink.recipe = json.dumps(recipe)
        new_drink.insert()
    except:
        abort(422)

    data = {'success': True,
            'drinks': [new_drink.long()]}

    return jsonify(data), 200


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
def patch_drinks(id):
    drink = Drink.query.get(id)
    body = request.get_json()

    if drink is None:
        abort(404)

    try:
        # Check presence of necessary attributes
        new_title = body['title']
        new_recipe = body['recipe']
        # Check recipe is in valid format
        if not isinstance(new_recipe, list) or len(new_recipe)==0:
            raise Exception
    except:
        abort(400)

    try:
        drink.title = new_title
        drink.recipe = new_recipe
        drink.update()
    except:
        abort(422)

    data = {'success': True,
            'drinks': [drink.long()]}

    return jsonify(data), 200


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@DONE implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
