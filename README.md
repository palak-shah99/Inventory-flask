# Inventory_flask

**Inventory Management using Flask**

## Installation


``` sourceCode console
$ pip install flask
$ pip install flask_mysqldb
$ git clone https://github.com/palak-shah99/Inventory-flask.git
$ cd inventory-flask
$ python -m flask run
```
The database used is phpmyadmin hosted at https://www.freemysqlhosting.net 

## Overview
The inventory management system keeps a track of products stored at various location along with the transactions.

## Functions 

#### Product 
The product page performs CRUD operations on products. Initially products created are unallocated.

![](screenshots/1.gif)


#### Location
The location page performs CRUD operation on locations. Initially location have no products allocated to it. 

![](screenshots/2.gif)

#### Summary 
The Summary page has three componenets. The inventory details, Movement form and the transaction details. 

![](screenshots/3.gif)


