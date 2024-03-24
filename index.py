from flask import Flask, render_template, request, session
import json
from calculate import UserData
from zipcode import storesZIP
app = Flask(__name__)
app.secret_key="YESFDIAHFIOEAWNKONFECDA"
food_names = []
images = []
food_data = []
def get_food_data():
    food_data = []
    with open('food_items.json', 'r') as file:
        raw_data = json.load(file)
        food_data = raw_data["foods"]

    for item in food_data:
        food_names.append(item['food_name'])
        images.append("food_images/" + item["food_name"] + ".jpg")
    return food_data
food_data = get_food_data()
@app.route('/')
def home():
    #This routes to the home page
    return render_template('home1.html', title="Home", food_names=food_names, len=len(food_names), images=images, heading="FOOD DONE FAST!!!", description = "Get instant recipes and delicious meals while keeping your body in shape. Enjoy the store!!!")

@app.route('/item', methods=["GET","POST"])
def item():
    
    if(request.method == "POST"):
        item_name = request.form.get("item_data")
        image = "food_images/"+item_name+".jpg"
        data = {}
        print(item_name)
        for item in food_data:
            print(item["food_name"])
            if(item["food_name"]==item_name):
                print('true')
                data["prot"] = item["proteins"]
                data["fats"] = item["fats"]
                data["carbs"] = item["carbohydrates"]
                data["fibers"] = item["fibers"]
                data["calories"] = item["calories"]
                data["price"] = item["price"]

        return render_template("item.html", image=image, heading=item_name, prot=data["prot"], carbs=data["carbs"], calories=data["calories"], fats=data["fats"], fibers=data["fibers"],price =data["price"])

#@app.route('/form')
#def render_form():
#    return render_template('form.html', title="Form", food_names=food_names, len=len(food_names), images=images, heading="Food", description = "This is the description text.", webappdata=[], datalen=0)

@app.route('/form', methods=["GET","POST"])
def form():
    #This routes to the home page
    print("Data")
    if(request.method == "POST"):
        print("shit")
        print(float(request.form.get("weight")))

        print(request.form.get("gender"))
        u = UserData(float(request.form.get("weight")), float(request.form.get("height")), float(request.form.get("age")), request.form.get("gender"),request.form.get("activity"), request.form.get("goal"), request.form.get("diet"), allergies_input=request.form.get("allergies"), meals=float(request.form.get("meals")))
        print(u.get_user_data())
        session['groceries'] = u.get_groceries()
    else:
        print("GET")
    try:
    
        return render_template('form.html', title="Form", food_names=food_names, len=len(food_names), images=images, heading="Health Made Delicious", description = "Get your groceries and personalized recipes with just one click!", webdata = u.get_user_data(), datalen = len(u.get_user_data()))
    
    except:
        return render_template('form.html', title="Form", food_names=food_names, len=len(food_names), images=images, heading="Health Made Delicious", description = "Get your groceries and personalized recipes with just one click!", webdata = [], datalen =0)

@app.route('/findstore', methods=["GET", "POST"])
def findstore():
    
    if(request.method == "POST"):
        zip_code = request.form.get("zipcode")
        print(zip_code)
        szip = storesZIP(zip_code)
        data = szip.get_closest_stores()
    try:
        return render_template("nearshop.html", title="Find Nearest", addresses = data[0], len=len(data[0]), phones = data[1], heading="Stores Near You", description="Find the closest grocery stores near you.z")
    except:
        return render_template("nearshop.html", title="Find Nearest", addresses = [], len=0, phones = [], heading="Stores Near You", description="Find the closest grocery stores near you.")
        

@app.route('/cart')
def cart():
    s = True
    txt=""
    x = session.get('groceries', {})
    if(len(x)!=0):
        grocery_names=[]
        txt = "Groceries List"
        total_price = 0
        for item in x:
            grocery_names.append(item["food_name"])
            total_price+=float(item["price"])
        
        return render_template("cart.html", title="Cart", heading=txt, price=total_price, groceries=grocery_names, len=len(grocery_names), status = s)
    else:
        txt ="Sorry... You have to create a nutrition plan"
        s=False
        return render_template("cart.html", title="Cart", heading=txt, price=0, groceries=[], len=0, status = s)
    
        

if __name__ == '__main__':
    app.run()