from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)
'''
app.config['MYSQL_HOST']='db4free.net'
app.config['MYSQL_USER']='invent123'
app.config['MYSQL_PASSWORD']='invent123'
app.config['MYSQL_DB']='inventory1'

app.config['MYSQL_HOST']='sql12.freemysqlhosting.net'
app.config['MYSQL_USER']='sql12316323'
app.config['MYSQL_PASSWORD']='dbAUcBaWYi'
app.config['MYSQL_DB']='sql12316323'
'''

app.config['MYSQL_HOST']='sql12.freemysqlhosting.net'
app.config['MYSQL_USER']='sql12316562'
app.config['MYSQL_PASSWORD']='AfwDRVUJJh'
app.config['MYSQL_DB']='sql12316562'


mysql = MySQL(app)


def init_db():
    cur = mysql.connection.cursor()
    cur.execute("create table if not exists product(pid Int primary key Auto_Increment,prdname varchar(50),qty Int)")
    cur.execute("create table if not exists location(lid Int primary key Auto_Increment,locname varchar(50))")
    cur.execute("create table if not exists productmove(mid Int primary key Auto_Increment,time_st Timestamp DEFAULT CURRENT_TIMESTAMP,floc int null,tloc int null, pid Int not null , qty int)")
    cur.execute("create table if not exists inventory(iid int primary key auto_increment, lid int default '0', pid int, qty int )")
    #cur.execute("CREATE TRIGGER `removeInventory` AFTER INSERT ON `productmove`  FOR EACH ROW BEGIN delete from inventory where qty = 0;   END;" )
    
    mysql.connection.commit()

    cur.close()

@app.route('/product', methods=['GET','POST'])
def product():
    init_db()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM product")
    product = cur.fetchall()

    if request.method == "POST":
        name = request.form['name']
        qty = request.form['quant']
        
        try:
            cur.execute("insert into product (prdname,qty) values(%s,%s)",(name,qty))
            
            cur.execute("select pid from product where prdname='"+name+"'") 
            pid=cur.fetchone()
            cur.execute("insert into inventory (pid,qty) values(%s,%s)" , ( pid,qty ))
            mysql.connection.commit()
            print("product added succefully")
        except NameError as e:
            print(e)
            
            return "error occurred"
        return redirect(url_for('product'))

    return render_template('product.html', product=product)

@app.route('/location', methods=['GET', 'POST'])
def location():
    init_db()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM location")
    loc = cur.fetchall()

    if request.method == "POST":
        locname = request.form['locname']
        try:
            cur.execute("INSERT INTO location (locname) VALUES ('"+locname+"')")
            mysql.connection.commit()
            print("location added succefully")
        #cur.close()
        except (NameError ) as e:
            print(e)
        return redirect(url_for('location'))
    
    return render_template('location.html', location=loc)


@app.route('/delete', methods=['POST','GET'])
def delete():
    init_db()
    frompage = request.args.get('type')
    cur = mysql.connection.cursor()
    if frompage == 'location':
        lid = request.args.get('lid')
        cur.execute("delete from location where lid = ("+lid+")")
        mysql.connection.commit()
        return redirect(url_for('location'))

    if frompage == 'product':
        p_id = request.args.get('pid')
        cur.execute("delete from product where pid = ("+p_id+")")
        mysql.connection.commit()
        return redirect(url_for('product'))



@app.route('/edit', methods=['POST', 'GET'])
def edit():
    #some databse code
    init_db() 
    cur = mysql.connection.cursor()
    frompage = request.args.get('type')
    if(request.method == 'POST'):

        if frompage == 'location' :
            loc_id = request.form['lid']
            loc_name = request.form['locname']
            
            if loc_name:
                cur.execute("update location set locname = ('"+loc_name+"') where lid = ("+loc_id+")")
            mysql.connection.commit()
 
            return redirect(url_for('location'))    

        elif frompage == 'product' :
            pid = request.form['pid']
            prodname = request.form['name']
            qty = request.form['quant']

            if prodname:
                cur.execute("update product set prdname = ('"+prodname+"') where pid = ("+pid+")")
            if qty:
                cur.execute("update product set qty = ("+qty+") where pid = ("+pid+")")

            mysql.connection.commit()
            
            return redirect(url_for('product'))
        
        return render(url_for("/"))

@app.route('/', methods=['GET','POST'])
def pm():
    init_db()

    listdb = []

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM location")
    from_loc = cur.fetchall()
    #from_loc = [x for x in locdb] #[id name]

    cur.execute("SELECT * FROM product")
    from_prod = cur.fetchall()
    #from_prod = [x for x in prodb] #[id name qty]
    
    
    cur.execute("SELECT * FROM productmove")
    pmdb = cur.fetchall()

    cur.execute("SELECT * FROM inventory")
    from_inv = cur.fetchall()
    #from_inv = [x for x in invdb] #[id lid pid qty]

    
    # listdb [ listdb_temp , listdb_temp ]

    for i in from_inv:
        listTemp = []
        if(i[1] != 0):
            a = [loc[1] for loc in from_loc if (i[1] == loc[0] )] 
            listTemp.append(a[0])

            b = [prod[1] for prod in from_prod if (i[2] == prod[0])]
            listTemp.append(b[0])
            listTemp.append(i[3])

            print(listTemp)
        else: 
            listTemp.append("Unallocated")
            b = [prod[1] for prod in from_prod if (i[2] == prod[0])]
            listTemp.append(b[0])
            listTemp.append(i[3])
            
            print(listTemp)
        listdb.append(listTemp)
    for i in from_loc:
        listTemp = [] 
        if( i[0] not in [x[1] for x in from_inv ]):
            listTemp.append(i[1])
            listTemp.append("No Product")
            listTemp.append(0)
            print(listTemp)
            listdb.append(listTemp)

    return render_template('pm.html', inventory=listdb)


    #code for display 
    # fetch location product and pm
    
    # for every location find what product is in that location and what quantity
    ''' for location id :
        for that location id in pm :
            find the pid :
            display 
        display unallocated 
    '''# display every product that is unallocated 



if __name__=="__main__":
    app.run(debug= True)
    
  