import os
from flask import Flask, render_template,redirect,request, url_for, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask_bcrypt import bcrypt


app = Flask(__name__)
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.secret_key = os.urandom(24)


mongo = PyMongo(app)

@app.route("/")
def get_index():
    if "username" in session:
        return "You are logged in as " + session["username"]
    return render_template("index.html")
    

@app.route("/register", methods=["POST","GET"])
def register():
    if request.method == "POST":
        users = mongo.db.users
        current_users = users.find_one({"Username":request.form.get("username")})
        
        if current_users is None:
            hashpassword = bcrypt.hashpw(request.form.get("password").encode('utf-8'), bcrypt.gensalt())
            users.insert({"username": request.form.get("username"), "password" : hashpassword})
            session["username"] = request.form.get("username")
            return redirect (url_for("get_index"))
        
        return "This Username is taken"
    return render_template("register.html")
        
    




#----- Recipe Functions -----#

@app.route("/get_recipe")
def get_recipe():
    recipes = mongo.db.recipes.find()
    return render_template("get_recipe.html", recipes=recipes)
    

@app.route("/add_recipe")
def add_recipe():
    cuisine = mongo.db.cuisine.find()
    return render_template("add_recipe.html", cuisine=cuisine) 
    
    
@app.route("/insert_recipe", methods=["POST"])
def insert_recipe():
    recipes = mongo.db.recipes
    recipes.insert_one(request.form.to_dict())
    return redirect(url_for("get_recipe")) 
    
    
@app.route("/edit_recipe/<recipe_id>")
def edit_recipe(recipe_id):
    _recipe = mongo.db.recipes.find_one({"_id":ObjectId(recipe_id)})
    _cuisine = mongo.db.cuisine.find()
    cuisine_list = [ cuisine for cuisine in _cuisine]
    return render_template("edit_recipe.html", recipe=_recipe, cuisine=cuisine_list)
        
        
@app.route("/update_recipe/<recipe_id>", methods=["POST"])
def update_recipe(recipe_id):
    recipes = mongo.db.recipes
    recipes.update(
        {"_id":ObjectId(recipe_id)},
    {
        "recipe_title" : request.form.get("recipe_title"),
        "recipe_cuisine" : request.form.get("recipe_cuisine"),
        "recipe_summary" : request.form.get("recipe_summary"),
        "recipe_ingredients" : request.form.get("recipe_ingredients"),
        "recipe_instructions" : request.form.get("recipe_instructions"),
        "recipe_portion" : request.form.get("recipe_portion"),
        "recipe_difficulty" : request.form.get("recipe_difficulty"),
        "recipe_preparation_time" : request.form.get("recipe_preparation_time"),
        "recipe_cooking_time" : request.form.get("recipe_cooking_time")
        
    })
    return redirect(url_for("get_recipe"))
    
    
@app.route("/delete_recipe/<recipe_id>")
def delete_recipe(recipe_id):
    mongo.db.recipes.remove({"_id":ObjectId(recipe_id)})
    return redirect(url_for("get_recipe"))
    
    
    
#----- Cuisine Functions -----#

@app.route("/get_cuisines")
def get_cuisines():
    cuisine = mongo.db.cuisine.find()
    return render_template("cuisines.html", cuisine=cuisine) 
    
    
@app.route("/add_cuisine")
def add_cuisine():
    cuisine = mongo.db.cuisine.find()
    return render_template("add_cuisine.html", cuisine=cuisine) 

    
@app.route("/insert_cuisine", methods=["POST"])
def insert_cuisine():
    cuisines = mongo.db.cuisine
    cuisines.insert_one(request.form.to_dict())
    return redirect(url_for("get_cuisines"))


@app.route("/delete_cuisine/<cuisine_id>")
def delete_cuisine(cuisine_id):
    mongo.db.cuisine.remove({"_id":ObjectId(cuisine_id)})
    return redirect(url_for("get_cuisines"))
    
    
@app.route("/edit_cuisine/<cuisine_id>") 
def edit_cuisine(cuisine_id):
    cuisine = mongo.db.cuisine.find_one({"_id":ObjectId(cuisine_id)})
    return render_template("edit_cuisine.html", cuisine = cuisine)
    
    
@app.route("/update_cuisine/<cuisine_id>", methods=["POST"])
def update_cuisine(cuisine_id):
    cuisine = mongo.db.cuisine
    cuisine.update(
        {"_id":ObjectId(cuisine_id)},
        {"recipe_cuisine" : request.form.get("recipe_cuisine")})
    return redirect(url_for("get_cuisines"))



if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)),debug=True)
    