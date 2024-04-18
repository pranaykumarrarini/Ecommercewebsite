drop database e_comeres;
create database e_comeres;
use e_comeres;


create table user(
user_id int auto_increment primary key,
name varchar(255) not null,
email varchar(255) not null,
phone varchar(255) not null,
password varchar(255) not null,
gender varchar(255) not null,
userType varchar(255) not null,
dob varchar(255) not null,
address varchar(255) not null
);

create table product(
product_id int auto_increment primary key,
product_name varchar(255) not null,
available_quantity varchar(255) not null,
price varchar(255) not null,
product_image varchar(255) not null,
description varchar(255) not null,
seller_id int,
foreign key(seller_id) references user(user_id)
);

create table post(
post_id int auto_increment primary key,
postType varchar(255) not null,
poster varchar(255),
posted_date datetime not null,
description varchar(255),
user_id int,
product_id int,
foreign key(user_id) references user(user_id),
foreign key(product_id) references product(product_id)
);


create table likes(
like_id int auto_increment primary key,
date datetime not null,
post_id int,
user_id int,
foreign key(post_id) references post(post_id),
foreign key(user_id) references user(user_id)
);

create table share(
share_id int auto_increment primary key,
date datetime not null,
post_id int,
user_id int,
foreign key(post_id) references post(post_id),
foreign key(user_id) references user(user_id)
);

create table comment(
comment_id int auto_increment primary key,
date datetime not null,
comment varchar(255) not null,
post_id int,
user_id int,
foreign key(post_id) references post(post_id),
foreign key(user_id) references user(user_id)
);

create table customer_order(
customer_order_id int auto_increment primary key,
status varchar(255) not null,
date datetime not null,
seller_id int,
buyer_id int,
foreign key(seller_id) references user(user_id),
foreign key(buyer_id) references user(User_id)
);


create table ordered_products(
ordered_products_id int auto_increment primary key,
number_of_items varchar(255) not null,
customer_order_id int,
Product_id int,
foreign key(customer_order_id) references customer_order(customer_order_id),
foreign key(product_id) references product(product_id)
);


create table transaction(
transaction_id int auto_increment primary key,
cardNumber varchar(255) not null,
nameonCard varchar(255) not null,
cvv varchar(255) not null,
Expire_date varchar(255) not null,
amount varchar(255) not null,
customer_order_id int,
foreign key(customer_order_id) references customer_order(customer_order_id)
);