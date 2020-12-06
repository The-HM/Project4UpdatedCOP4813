#Henry Murillo
#12/5/2020
from flask import Flask, render_template, request, url_for
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField,DateField
import requests



app = Flask(__name__)
app.config["SECRET_KEY"]="cop4813project"
app.config["MONGO_URI"] = "mongodb+srv://cop48133:B8HuDj4mZxESFKyv@cluster0.f6uas.mongodb.net/Cluster0?retryWrites=true&w=majority"
mongo = PyMongo(app)

class Expenses(FlaskForm):
    description = StringField('Description')
    category = SelectField('Category', choices=[('groceries', 'Groceries'), ('health insurance', 'Health Insurance'),
                                                ('electricity', 'Electricity'), ('car insurance', 'Car Insurance'),
                                                ('rent', 'Rent'), ('telephone', 'Telephone'),
                                                ('clothing', 'Clothing'), ('tolls', 'Tolls'),
                                                ('maintenance', 'Car Maintenance'), ('gas', 'Gasoline')])
    cost = DecimalField('Cost')
    currency = SelectField('Currency Category',choices=[('usd','US Dollars'),('hnl','Honduran Lempira'),('jpy','Japanese Yen')
                                                        ,('eur','Euro')])
    date = DateField('Date', format='%m-%d-%Y')

def get_total_expenses(category):
    expense_category = 0
    query = {"category": category}
    records = mongo.db.expenses.find(query)

    for i in records:
        expense_category += float(i["cost"])
    return expense_category

def currency_converter(cost,currency):
    global converted_cost
    url="http://api.currencylayer.com/live?access_key=e901ab5df17332056e3f3e96829664e2"
    response = requests.get(url).json()

    if currency == 'usd':
        converted_cost = cost
    elif currency == 'hnl':
        converted_cost = cost/response["quotes"]["USDHNL"]
    elif currency == 'jpy':
        converted_cost = cost/response["quotes"]["USDJPY"]
    elif currency == 'eur':
        converted_cost = cost / response["quotes"]["USDEUR"]

    return converted_cost


@app.route('/')
def index():
    my_expenses = mongo.db.expenses.find()
    categories = mongo.db.expenses.find({}, {"category": 1})
    total_expenses = 0

    for i in my_expenses:
        total_expenses += float(i["cost"])

    expensesByCategory = {}

    for x in categories:
        expensesByCategory[x["category"]] = get_total_expenses(x["category"])

    return render_template("index.html", expenses=total_expenses, expensesByCategory=expensesByCategory)

@app.route('/addExpenses',methods=["GET","POST"])
def addExpenses():
    expensesForm = Expenses(request.form)
    if request.method == 'POST':
        description = request.form['description']
        category = request.form['category']
        cost = request.form['cost']
        currency = request.form['currency']
        date = request.form['date']

        cost = currency_converter(float(cost),currency)

        record = {'description': description, 'category': category, 'cost': float(cost), 'date': date}

        mongo.db.expenses.insert_one(record)
        return render_template("expenseAdded.html")
    return render_template("addExpenses.html", form=expensesForm)

app.run()