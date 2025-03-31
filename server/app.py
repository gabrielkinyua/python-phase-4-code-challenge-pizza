#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JSON_PRETTYPRINT_REGULAR"] = True


db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

class RestaurantResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [restaurant.to_dict() for restaurant in restaurants], 200
  

class PizzaResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [pizza.to_dict() for pizza in pizzas], 200


class RestaurantPizzaResource(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_restaurant_pizza = RestaurantPizza(
                restaurant_id=data["restaurant_id"],
                pizza_id=data["pizza_id"],
                price=data["price"]
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            return new_restaurant_pizza.to_dict(), 201
        
        except ValueError as e:
            return {"errors":["validation errors"]}, 400
        
        except Exception as e:
            return {"errors":["An expected error occurred"]}, 400

api.add_resource(RestaurantResource, "/restaurants")
api.add_resource(PizzaResource, "/pizzas")
api.add_resource(RestaurantPizzaResource, "/restaurant_pizzas")




@app.route('/restaurants/<int:id>', methods=['GET', 'DELETE'])
def get_or_delete_restaurant(id):
    restaurant = Restaurant.query.get(id)

    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404
    
    if request.method == 'DELETE':
        RestaurantPizza.query.filter_by(restaurant_id=id).delete()
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204
    
    return jsonify({
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address,
        "restaurant_pizzas": [rp.to_dict() for rp in restaurant.restaurant_pizzas]
    }), 200



if __name__ == "__main__":
    app.run(port=5555, debug=True)
