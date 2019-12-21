from flask import Flask, render_template,request
from flask_mysqldb import MySQL
app = Flask(__name__)
app.config['MYSQL_HOST']='sql12.freemysqlhosting.net'
app.config['MYSQL_USER']='sql12316323'
app.config['MYSQL_PASSWORD']='dbAUcBaWYi'
app.config['MYSQL_DB']='sql12316323'
mysql = MySQL(app)

@app.route('/')
def index():
        cur = mysql.connection.cursor()
        #cur.execute("create table myuser(fname varchar(20), lname varchar(30))")
        cur.execute("create table product(pid Int Auto_Increment,prdname varchar(50),qty Int)")
        cur.execute("create table location(lid Int Auto_Increment,locname varchar(50))")
        cur.execute("create table productmove(mid Int Auto_Increment,time_st Timestamp DEFAULT CURRENT_TIMESTAMP,floc varchar(50), tloc varchar(50), prdname varchar(50), qty int)")
        
        #mysql.connection.commit()        
        #cur.execute("insert into myuser values(%s,%s)", (fname,lname))
        mysql.connection.commit()
        cur.close()
        return render_template('index.html')
if __name__=="__main__":
    app.run(debug= True)
    
  