import datetime
import os
import boto3 as boto3
import pymysql as pymysql
from flask import Flask, render_template, request, session, redirect
Ecommerce_region_name = 'us-east-1'
Ecommerce_Bucket_Name = "ecommerce-s3-bucket-project"
ecommerce_source_email = 'sksharmila1922@gmail.com'=
ecommerce_s3_client = boto3.client('s3', aws_access_key_id="AKIA5P7EEHMML7N5IRH4", aws_secret_access_key="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")
ecommerce_ses_client = boto3.client('ses', aws_access_key_id="AKIA5P7EEHMML7N5IRH4", aws_secret_access_key="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", region_name=Ecommerce_region_name)
# conn = pymysql.connect(host="localhost", user="root", password="Sharmi@2020", db="e_comeres")
conn = pymysql.connect(host="ecommercerds.cboldmypyzso.us-east-1.rds.amazonaws.com", user="admin", password="admin123", db="e_comeres")
cursor = conn.cursor()

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_ROOT = APP_ROOT + "/static"


app = Flask(__name__)
app.secret_key = "yedghbnikulhn"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/logout")
def logout():
    session.clear()
    return render_template("index.html")


@app.route("/userReg")
def userReg():
    return render_template("userReg.html")


@app.route("/userReg1",methods=['post'])
def userReg1():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    gender = request.form.get("gender")
    userType = request.form.get("userType")
    dob = request.form.get("dob")
    address = request.form.get("address")
    count = cursor.execute("select * from user where email= '" + str(email) + "' or phone = '" + str(phone) + "'")
    if count == 0:
        emails = ecommerce_ses_client.list_identities(
            IdentityType='EmailAddress'
        )
        if email in emails['Identities']:
            print(email)
            print(ecommerce_source_email)
            ecommerce_info = 'Hi' + '' + name + ' you have Registered Sucessfully'
            ecommerce_ses_client.send_email(Source=ecommerce_source_email, Destination={'ToAddresses': [email]},
                                  Message={'Subject': {'Data': ecommerce_info, 'Charset': 'utf-8'},
                                           'Body': {'Html': {'Data': ecommerce_info, 'Charset': 'utf-8'}}})
            cursor.execute("insert into user(name,phone,email,password,gender,userType,dob,address) values('" + str(name) + "', '" + str(phone) + "', '" + str(email) + "', '" + str(password) + "', '" + str(gender) + "', '" + str(userType) + "', '" + str(dob) + "', '" + str(address) + "')")
            conn.commit()
            return render_template('msg.html', msg='User Registered Successfully', color='text-success')
        else:
            return render_template("msg.html", msg="Your email is not verified by website.", color='text-success')
    else:
        return render_template("msg.html", msg="Duplicate Details", color='text-success')

@app.route("/email_verification")
def email_verf():
    return render_template("email_verification.html")

@app.route("/email_verification1")
def email_verify1():
    email = request.args.get("email")
    ecommerce_ses_client.verify_email_address(
        EmailAddress=email
    )
    return render_template("msg.html", msg="Click on the link that sent to your emailaddress", color='text-success')

@app.route('/uLogin1',methods=['post'])
def uLogin1():
    email = request.form.get("email")
    password = request.form.get("password")
    total_count = cursor.execute("select * from user where email= '" + str(email) + "' and password = '" + str(password) + "'")
    if total_count > 0:
        results = cursor.fetchall()
        emails = ecommerce_ses_client.list_identities(
            IdentityType='EmailAddress'
        )
        if email in emails['Identities']:
            ecommerce_info = 'You' + ''  + ' have Sucessfully Logged In to Website'
            ecommerce_ses_client.send_email(Source=ecommerce_source_email, Destination={'ToAddresses': [email]},
                                            Message={'Subject': {'Data': ecommerce_info, 'Charset': 'utf-8'},
                                                     'Body': {'Html': {'Data': ecommerce_info, 'Charset': 'utf-8'}}})
            for result in results:
                session['user_id'] = result[0]
                session['userType'] = result[6]
                return render_template("uhome.html")
        else:
            return render_template("msg.html", msg="Your unable to loggin into website.", color='text-success')
    else:
        return render_template("msg.html", msg="Invalid login details", color='text-danger')


@app.route("/uhome")
def uhome():
    return render_template("uhome.html")


@app.route("/addProduct")
def addProduct():
    return render_template("addProduct.html")


@app.route("/addProduct1",methods=['post'])
def addProduct1():
    product_name = request.form.get("product_name")
    available_quantity = request.form.get("available_quantity")
    price = request.form.get("price")
    product_image = request.files.get("product_image")
    path = APP_ROOT + "/Product_Image/" + product_image.filename
    product_image.save(path)
    ecommerce_s3_client.upload_file(path, Ecommerce_Bucket_Name , product_image.filename)
    product_image_s3_file_name = product_image.filename
    product_image_url = f'https://{Ecommerce_Bucket_Name}.s3.amazonaws.com/{product_image_s3_file_name}'
    description = request.form.get("description")
    seller_id = session['user_id']
    cursor.execute("insert into product(product_name,available_quantity,price,product_image,description,seller_id) values('" + str(product_name) + "', '" + str(available_quantity) + "', '" + str(price) + "', '" + str(product_image_url) + "', '" + str(description) + "', '" + str(seller_id) + "')")
    conn.commit()
    return render_template("message.html", msg="Product Added Successfully", color='text-success')


@app.route("/viewProduct")
def viewProduct():
    seller_id = session['user_id']
    cursor.execute("select * from product where seller_id = '" + str(seller_id ) + "'")
    products = cursor.fetchall()
    return render_template("viewProduct.html", products=products)


@app.route("/EditQuantity",methods=['post'])
def EditQuantity():
    Product_id = request.form.get("Product_id")
    return render_template("EditQuantity.html",Product_id=Product_id)


@app.route("/EditQuantity1",methods=['post'])
def EditQuantity1():
    Product_id = request.form.get("Product_id")
    available_quantity = request.form.get("available_quantity")
    cursor.execute("update product set available_quantity ='"+str(available_quantity)+"' where product_id = '" + str(Product_id) + "'")
    conn.commit()
    return viewProduct()


@app.route("/addPost")
def addPost():
    return render_template("addPost.html")


@app.route("/addPost1",methods=['post'])
def addPost1():
    user_id = session['user_id']
    postType = request.form.get("postType")
    poster = request.files.get("poster")
    path = APP_ROOT + "/Poster/" + poster.filename
    poster.save(path)
    ecommerce_s3_client.upload_file(path, Ecommerce_Bucket_Name, poster.filename)
    poster_s3_file_name = poster.filename
    picture_image_url = f'https://{Ecommerce_Bucket_Name}.s3.amazonaws.com/{poster_s3_file_name}'

    description = request.form.get("description")
    cursor.execute("insert into post(postType,poster,posted_date,description,user_id) values('post', '" + str(picture_image_url) + "', '" + str(datetime.datetime.now()) + "', '" + str(description) + "', '" + str(user_id) + "')")
    conn.commit()
    return render_template("message.html", msg="Post Added Successfully", color='text-success')


@app.route("/viewPost")
def viewPost():
    cursor.execute("select * from post")
    posts = cursor.fetchall()
    posts = list(posts)
    posts.reverse()
    return render_template("viewPost.html", posts=posts, getUserByPosts=getUserByPosts, getProductById=getProductById)


def getUserByPosts(User_id):
    cursor.execute("select * from user where user_id = '" + str(User_id) + "'")
    user = cursor.fetchall()
    return user[0]


@app.route("/postProduct")
def postProduct():
    user_id = session['user_id']
    Product_id = request.args.get("Product_id")
    cursor.execute("insert into post(product_id,postType,posted_date,user_id) values('"+str(Product_id)+"', 'Product', '" + str(datetime.datetime.now()) + "', '" + str(user_id) + "')")
    conn.commit()
    return render_template("message.html", msg="Product Posted Successfully", color='text-success')


def getProductById(Product_id):
    cursor.execute("select * from product where product_id = '" + str(Product_id) + "'")
    product = cursor.fetchall()
    return product[0]


@app.route("/addToCart",methods=['post'])
def addToCart():
    number_of_items = request.form.get("number_of_items")
    Product_id = request.form.get("Product_id")
    Seller_id = request.form.get("Seller_id")
    Buyer_id = session['user_id']
    customer_order_id = None
    a = cursor.execute("select * from customer_order where seller_id= '" + str(Seller_id) + "' and buyer_id = '" + str(Buyer_id) + "' and status = 'Cart'")
    if a == 0:
        cursor.execute("insert into customer_order(seller_id,buyer_id,status,date) values('"+str(Seller_id)+"', '" + str(Buyer_id) + "', 'Cart', '" + str(datetime.datetime.now()) + "')")
        conn.commit()
        customer_order_id = cursor.lastrowid
    else:
        cursor.execute("select * from customer_order where seller_id= '" + str(Seller_id) + "' and buyer_id = '" + str(Buyer_id) + "' and status = 'Cart'")
        customer_order = cursor.fetchall()
        customer_order_id = customer_order[0][0]
        print(customer_order_id, "ccccc")
    count = cursor.execute("select * from ordered_products where customer_order_id = '" + str(customer_order_id) + "' and product_id = '" + str(Product_id) + "'")
    if count > 0:
        cursor.execute("select * from ordered_products where customer_order_id = '" + str(customer_order_id) + "' and product_id = '" + str(Product_id) + "'")
        order_product = cursor.fetchall()
        quantity2 = int(order_product[0][1]) + int(number_of_items)
        cursor.execute("update ordered_products set number_of_items ='"+str(quantity2)+"' where customer_order_id = '" + str(customer_order_id) + "' and product_id = '" + str(Product_id) + "'")
        conn.commit()
        cursor.execute("select * from product where product_id = '" + str(Product_id) + "'")
        product = cursor.fetchall()
        quantity3 = int(product[0][2]) - int(number_of_items)
        cursor.execute("update product set available_quantity ='" + str(quantity3) + "' where product_id = '" + str(Product_id) + "'")
        conn.commit()
        return render_template("message.html", msg='Item Updated In Cart', color='text-primary')
    else:
        cursor.execute("insert into ordered_products(customer_order_id,product_id,number_of_items) values('" + str(customer_order_id) + "', '" + str(Product_id) + "', '" + str(number_of_items) + "')")
        conn.commit()
        cursor.execute("select * from product where product_id = '" + str(Product_id) + "'")
        product = cursor.fetchall()
        quantity3 = int(product[0][2]) - int(number_of_items)
        cursor.execute("update product set available_quantity ='" + str(quantity3) + "' where product_id = '" + str(Product_id) + "'")
        conn.commit()
        return render_template("message.html", msg='Item Added To Cart', color='text-success')


@app.route("/viewOrderItems")
def viewOrderItems():
    query = ""
    status = request.args.get("status")
    if session['userType'] == 'Buyer':
        buyer_id = session['user_id']
        if status == 'Cart':
            query = "select * from customer_order where buyer_id = '"+str(buyer_id)+"' and status = 'Cart'"
        elif status == 'Ordered':
            query = "select * from customer_order where status = 'Dispatched' or status = 'Ordered' and buyer_id = '" + str(buyer_id) + "'"
        elif status == 'History':
            query = "select * from customer_order where status = 'Order Received' and buyer_id = '" + str(buyer_id) + "'"
    elif session['userType'] == 'Seller':
        seller_id = session['user_id']
        if status == 'Ordered':
            query = "select * from customer_order where status = 'Dispatched' or status = 'Ordered' and seller_id = '" + str(seller_id) + "'"
        elif status == 'History':
            query = "select * from customer_order where status = 'Order Received' and seller_id = '" + str(seller_id) + "'"
    cursor.execute(query)
    customer_orders = cursor.fetchall()
    return render_template("viewOrderItems.html", getProductByOrderedItems=getProductByOrderedItems,  getOrderProductsByCustomerOrder=getOrderProductsByCustomerOrder,getSellerBYCustomerOrders=getSellerBYCustomerOrders,customer_orders=customer_orders,getBuyerByCustomerOrders=getBuyerByCustomerOrders,float=float)


def getBuyerByCustomerOrders(User_id):
    cursor.execute("select * from user where user_id = '" + str(User_id) + "'")
    buyer = cursor.fetchall()
    return buyer[0]


def getSellerBYCustomerOrders(User_id):
    cursor.execute("select * from user where user_id = '" + str(User_id) + "'")
    seller = cursor.fetchall()
    return seller[0]


def getOrderProductsByCustomerOrder(customer_order_id):
    cursor.execute("select * from ordered_products where customer_order_id = '" + str(customer_order_id) + "'")
    order_items = cursor.fetchall()
    return order_items


def getProductByOrderedItems(Product_id):
    cursor.execute("select * from product where product_id = '" + str(Product_id) + "'")
    products = cursor.fetchall()
    return products


@app.route("/removeCart")
def removeCart():
    OrderedProduct_id = request.args.get("OrderedProduct_id")
    cursor.execute("select * from ordered_products where ordered_products_id = '" + str(OrderedProduct_id) + "'")
    orderProducts = cursor.fetchall()
    Product_id = orderProducts[0][2]
    cursor.execute("select * from product where product_id = '" + str(Product_id) + "'")
    products = cursor.fetchall()
    available_quantity = int(products[0][2]) + int(orderProducts[0][1])
    cursor.execute("update product set available_quantity ='" + str(available_quantity) + "' where product_id = '" + str(Product_id) + "'")
    cursor.execute("delete from ordered_products where ordered_products_id='" + str(OrderedProduct_id) + "'")
    conn.commit()
    return redirect("viewOrderItems?status=Cart")


@app.route("/orderNow")
def orderNow():
    totalPrice = request.args.get("totalPrice")
    CustomerOrder_id = request.args.get("CustomerOrder_id")
    return render_template("orderNow.html", CustomerOrder_id=CustomerOrder_id,totalPrice=totalPrice)


@app.route("/orderNow1", methods=['post'])
def orderNow1():
    cardNumber = request.form.get("cardNumber")
    nameonCard = request.form.get("nameonCard")
    cvv = request.form.get("cvv")
    Expire_date = request.form.get("Expire_date")
    totalPrice = request.form.get("totalPrice")
    CustomerOrder_id = request.form.get("CustomerOrder_id")
    cursor.execute("update customer_order set status ='Ordered' where customer_order_id = '" + str(CustomerOrder_id) + "'")
    cursor.execute("insert into transaction(customer_order_id,cardNumber,nameonCard,cvv,Expire_date,amount) values('" + str(CustomerOrder_id) + "', '" + str(cardNumber) + "', '" + str(nameonCard) + "', '" + str(cvv) + "', '" + str(Expire_date) + "', '" + str(totalPrice) + "')")
    conn.commit()
    return render_template("message.html",msg='Order Placed',color='text-primary')


@app.route("/dispatch")
def dispatch():
    CustomerOrder_id = request.args.get("CustomerOrder_id")
    cursor.execute("update customer_order set status ='Dispatched' where customer_order_id = '" + str(CustomerOrder_id) + "'")
    conn.commit()
    return redirect("viewOrderItems?status=Ordered")


@app.route("/receive")
def receive():
    CustomerOrder_id = request.args.get("CustomerOrder_id")
    cursor.execute("update customer_order set status ='Order Received' where customer_order_id = '" + str(CustomerOrder_id) + "'")
    conn.commit()
    return redirect("viewOrderItems?status=History")


@app.route("/addLike")
def addLike():
    Post_id = request.args.get('Post_id')
    user_id = session['user_id']
    count = cursor.execute("select * from likes where post_id = '" + str(Post_id) + "' and user_id = '"+str(user_id)+"'")
    isLike = False
    if count == 0:
        cursor.execute("insert into likes(post_id,user_id,date) values('" + str(Post_id) + "', '" + str(user_id) + "', '" + str(datetime.datetime.now()) + "')")
        conn.commit()
        isLike = True
    else:
        cursor.execute("delete from likes where post_id='" + str(Post_id) + "'  and user_id = '"+str(user_id)+"'")
        conn.commit()
        isLike = False
    count = cursor.execute("select * from likes where post_id = '" + str(Post_id) + "'")
    return {"likes": str(count), "isLike": isLike}


@app.route("/addShare")
def addShare():
    user_id = session['user_id']
    Post_id = request.args.get('Post_id')
    cursor.execute("select * from post where post_id = '" + str(Post_id) + "'")
    Post = cursor.execute()
    Post[0][5] = session['user_id']
    Post[0][3] = datetime.datetime.now()
    del Post[0][0]
    cursor.execute("select * from post where post_id='" + str(Post_id) + "'")
    posts = cursor.fetchall()
    post = posts[0]
    cursor.execute("insert into post(postType,poster,posted_date,description,user_id,product_id) values('" + str(post[1]) + "', '" + str(post[2]) + "', '" + str(post[3]) + "', '" + str(post[4]) + "', '" + str(post[5]) + "', '" + str(post[6]) + "')")
    post_id = cursor.lastrowid
    cursor.execute("insert into share(user_id,post_id,date) values('" + str(user_id) + "', '" + str(post_id) + "', '" + str(datetime.datetime.now()) + "')")
    conn.commit()
    return "Post Shared Successfully"


@app.route("/addComment")
def addComment():
    Post_id = request.args.get('Post_id')
    comment = request.args.get('comment')
    user_id = session['user_id']
    cursor.execute("insert into comment(post_id,comment,user_id,date) values('" + str(Post_id) + "', '" + str(comment) + "', '" + str(user_id) + "', '" + str(datetime.datetime.now()) + "')")
    conn.commit()
    return "Comment Added Successfully"


@app.route("/transaction")
def transaction():
    CustomerOrder_id = request.args.get("CustomerOrder_id")
    cursor.execute("select * from transaction where customer_order_id = '" + str(CustomerOrder_id) + "'")
    transactions = cursor.fetchall()
    return render_template("transaction.html", transactions=transactions, getSellerByTransaction=getSellerByTransaction, getBuyerByTransaction=getBuyerByTransaction)


def getSellerByTransaction(CustomerOrder_id):
    cursor.execute("select * from customer_order where customer_order_id = '" + str(CustomerOrder_id) + "'")
    customer_order = cursor.fetchall()
    User_id = customer_order[0][3]
    cursor.execute("select * from user where user_id = '" + str(User_id) + "'")
    seller = cursor.fetchall()
    return seller[0]


def getBuyerByTransaction(CustomerOrder_id):
    cursor.execute("select * from customer_order where customer_order_id = '" + str(CustomerOrder_id) + "'")
    customer_order = cursor.fetchall()
    User_id = customer_order[0][4]
    cursor.execute("select * from user where user_id = '" + str(User_id) + "'")
    buyer = cursor.fetchall()
    return buyer[0]


@app.route("/viewLikes",methods=['post'])
def viewLikes():
    Post_id = request.form.get("Post_id")
    cursor.execute("select * from likes where post_id = '" + str(Post_id) + "'")
    likes = cursor.fetchall()
    return render_template("viewLikes.html", likes=likes, getUserByLikes=getUserByLikes)


@app.route("/viewComments",methods=['post'])
def viewComments():
    Post_id = request.form.get("Post_id")
    cursor.execute("select * from comment where post_id = '" + str(Post_id) + "'")
    comments = cursor.fetchall()
    return render_template("viewComments.html", comments=comments, getUserByLikes=getUserByLikes)


@app.route("/viewShares",methods=['post'])
def viewShares():
    Post_id = request.form.get("Post_id")
    cursor.execute("select * from share where post_id = '" + str(Post_id) + "'")
    shares = cursor.fetchall()
    return render_template("viewShares.html", shares=shares, getUserByLikes=getUserByLikes)


def getUserByLikes(User_id):
    cursor.execute("select * from user where user_id = '" + str(User_id) + "'")
    user = cursor.fetchall()
    return user[0]


app.run(debug=True)