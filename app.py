from flask import *
# Connection to database
import pymysql
import pymysql.cursors
import os #file path

app = Flask(__name__)
# configure the file path of the static folder
app.config["UPLOAD_FOLDER"] = 'static/images'

@app.route('/api/signup', methods=['POST'])
def signup():
    # Extract the values posted in the request and store them in variables
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    phone = request.form['phone']

    # Connection to the database
    connection = pymysql.connect(host='localhost', user='root', password='', database='sokogarden')
    # Create a cursor object to initialize  connection
    cursor = connection.cursor()
    sql = "INSERT INTO users (username, email, password, phone) VALUES (%s, %s, %s, %s)"
    data = (username, email, password, phone)

# Use cursor to execute the SQL and the data
    cursor.execute(sql, data)
    # Commit/Save changes to the database
    connection.commit()

    return jsonify({"message": "Account created successfully!"})

@app.route('/api/signin', methods=['POST'])
def signin():
    # Extract the values posted in the request and store them in variables
    username = request.form['username']
    password = request.form['password']

    connection = pymysql.connect(host='localhost', user='root', password='', database='sokogarden')
     # Use DictCursor to get results as dictionaries
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM users WHERE username=%s AND password=%s"
    data = (username, password)

    cursor.execute(sql, data)
    # Check if the cursor has returned a row
    count = cursor.rowcount
    if count == 0:
        return jsonify({"message": "Log in failed! Invalid username or password!"})
    else:
        #else there's a user
        user = cursor.fetchone()
        return jsonify({"message": "Logged in successfully!","user": user})
    
# Adding a product
@app.route('/api/addproduct', methods=['POST'])
def add_product():
    # Extract the values posted in the request and store them in variables
    product_name = request.form['product_name']
    product_description = request.form['product_description']
    product_cost = request.form['product_cost']
    photo = request.files['product_photo']
    # Get the filename from the uploaded photo
    filename = photo.filename
    # Save the photo to the upload folder(specify computer path to save the photo)
    photo_path = os.path.join(app.config["UPLOAD_FOLDER"],filename)

    # Save the photo to the specified path
    photo.save(photo_path)

    # Connection to the database
    connection = pymysql.connect(host='localhost', user='root', password='', database='sokogarden')
    # Create a cursor object to initialize  connection
    cursor = connection.cursor()
    sql = "INSERT INTO product_details (product_name, product_description, product_cost, product_photo) VALUES (%s, %s, %s, %s)"
    data = (product_name, product_description, product_cost, filename)  # Store only the filename in the database

    # Use cursor to execute the SQL and the data
    cursor.execute(sql, data)
    # Commit/Save changes to the database
    connection.commit()
    return jsonify({"message": "Product added successfully!"})

    # /api/getproducts route to retrieve all products from the database
@app.route('/api/getproducts', methods=['GET'])
def get_products():
    connection = pymysql.connect(host='localhost', user='root', password='', database='sokogarden')
    # Create a cursor object to initialize  connection
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM product_details"
    # use cursor to execute the SQL query
    cursor.execute(sql)
    # fetch all the products from the database
    product_details = cursor.fetchall()
    # return the product details as a dictionary in JSON format
    return jsonify({"products": product_details})

# Mpesa payment route
import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth

@app.route('/api/mpesa_payment', methods=['POST'])
def mpesa_payment():
        if request.method == 'POST':
            # Extract POST Values sent
            amount = request.form['amount']
            phone = request.form['phone']

            # Provide consumer_key and consumer_secret provided by safaricom
            consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
            consumer_secret = "amFbAoUByPV2rM5A"

            # Authenticate Yourself using above credentials to Safaricom Services, and Bearer Token this is used by safaricom for security identification purposes - Your are given Access
            api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"  # AUTH URL
            # Provide your consumer_key and consumer_secret 
            response = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
            # Get response as Dictionary
            data = response.json()
            # Retrieve the Provide Token
            # Token allows you to proceed with the transaction
            access_token = "Bearer" + ' ' + data['access_token']

            #  GETTING THE PASSWORD
            timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')  # Current Time
            passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'  # Passkey(Safaricom Provided)
            business_short_code = "174379"  # Test Paybile (Safaricom Provided)
            # Combine above 3 Strings to get data variable
            data = business_short_code + passkey + timestamp
            # Encode to Base64
            encoded = base64.b64encode(data.encode())
            password = encoded.decode()

            # BODY OR PAYLOAD
            payload = {
                "BusinessShortCode": "174379",
                "Password":password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": "1",  # use 1 when testing
                "PartyA": phone,  # change to your number
                "PartyB": "174379",
                "PhoneNumber": phone,
                "CallBackURL": "https://coding.co.ke/api/confirm.php",
                "AccountReference": "SokoGarden Online",
                "TransactionDesc": "Payments for Products"
            }

            # POPULAING THE HTTP HEADER, PROVIDE THE TOKEN ISSUED EARLIER
            headers = {
                "Authorization": access_token,
                "Content-Type": "application/json"
            }

            # Specify STK Push  Trigger URL
            url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  
            # Create a POST Request to above url, providing headers, payload 
            # Below triggers an STK Push to the phone number indicated in the payload and the amount.
            response = requests.post(url, json=payload, headers=headers)
            print(response.text) # 
            # Give a Response
            return jsonify({"message": "An MPESA Prompt has been sent to Your Phone, Please Check & Complete Payment"})
        

if __name__=='__main__':
    app.run(debug=True)