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
app.config['MYSQL_PORT']=3306
app.config['MYSQL_PASSWORD']='AfwDRVUJJh'
app.config['MYSQL_DB']='sql12316562'


mysql = MySQL(app)  #initialization


def init_db():
    cur = mysql.connection.cursor() #establishing the connection
    cur.execute("create table if not exists product(pid Int primary key Auto_Increment,prdname varchar(50),qty Int)")
    cur.execute("create table if not exists location(lid Int primary key Auto_Increment,locname varchar(50))")
    cur.execute("create table if not exists productmove(mid Int primary key Auto_Increment,time_st Timestamp DEFAULT CURRENT_TIMESTAMP,floc int null,tloc int null, pid Int not null , qty int)")
    cur.execute("create table if not exists inventory(iid int primary key auto_increment, lid int default '0', pid int, qty int )")
    
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

        cur.execute("update inventory set lid=0 where lid = ("+lid+")")

        cur.execute("delete from location where lid = ("+lid+")")
        mysql.connection.commit()
        return redirect(url_for('location'))

    if frompage == 'product':
        p_id = request.args.get('pid')

        cur.execute("delete from inventory where pid= ("+p_id+")")
        
        cur.execute("delete from product where pid = ("+p_id+")")
        
        mysql.connection.commit()
        return redirect(url_for('product'))



@app.route('/edit', methods=['POST', 'GET'])
def edit():
    init_db() 
    cur = mysql.connection.cursor()
    frompage = request.args.get('type')
    if(request.method == 'POST'):

        if frompage == 'location':
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
            #if qty:
            #    cur.execute("update product set qty = ("+qty+") where pid = ("+pid+")")

            mysql.connection.commit()
            
            return redirect(url_for('product'))
        
        return render(url_for("product"))

@app.route('/', methods=['GET','POST'])
def pm():
    init_db() 
    listdb = []
    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM location")
    from_loc = cur.fetchall()

    cur.execute("SELECT * FROM product")
    from_prod = cur.fetchall()
    
    
    cur.execute("SELECT * FROM productmove")
    pmdb = cur.fetchall()

    cur.execute("SELECT * FROM inventory")
    from_inv = cur.fetchall()


    if (request.method == 'POST'):
        prdname=request.form['prdname']
        floc=request.form['frmloc']
        tloc=request.form['toloc']
        qty=request.form['qty']

    
        cur.execute("select pid from product where prdname = '"+prdname+"'")
        pid=cur.fetchall()
        if(floc == ""):
            old_lid = 0 
            
            cur.execute("select lid from location where locname = '"+tloc+"'")
            lid=cur.fetchone()

        elif(tloc == ""):

            cur.execute("select lid from location where locname = '"+floc+"'")
            old_lid = cur.fetchone()[0]
            
            lid=0
            
        else:
            
            cur.execute("select lid from location where locname = '"+floc+"'")
            old_lid = cur.fetchone()[0]
            
            cur.execute("select lid from location where locname = '"+tloc+"'")
            lid = cur.fetchone()[0]
            
        
        cur.execute("select exists( select qty from inventory where lid = %s and pid = %s ) " , (lid, pid ) )
        abc = cur.fetchone() 
        
        if(abc[0]==1):
            cur.execute("select qty from inventory where lid=%s and pid=%s",(lid,pid))
            qty_old=cur.fetchone()
            #print(qty_old[0])
            qty_new= qty_old[0] +  int(qty)  
            cur.execute("update inventory set qty= %s where lid=%s and pid=%s",(qty_new,lid,pid) ) 
        else:
            cur.execute("insert into inventory (lid,pid,qty) values(%s,%s,%s)",(lid,pid,qty))

        cur.execute("select qty from inventory where pid = %s and lid = %s ",(pid[0], old_lid) )
        unallocqty = cur.fetchone()

        newqty = unallocqty[0] - int(qty)
        if newqty == 0:
            cur.execute("delete from inventory where lid=%s and pid=%s",(old_lid , pid[0]) )

        else:
            
            cur.execute("update inventory set qty=%s where lid=%s and pid=%s",(newqty,old_lid , pid))
                    
        #display transaction
        cur.execute("insert into productmove (floc,tloc,pid,qty) values(%s,%s,%s,%s)",(old_lid,lid,pid,qty))
        mysql.connection.commit()

            
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
    #Code to display inventory table 
    for i in from_inv:
        listTemp = []
        if(i[1] != 0):
            a = [loc[1] for loc in from_loc if (i[1] == loc[0] )] 
            listTemp.append(a[0])

            b = [prod[1] for prod in from_prod if (i[2] == prod[0])]
            listTemp.append(b[0])
            listTemp.append(i[3])
        else: 
            listTemp.append("Unallocated")
            b = [prod[1] for prod in from_prod if (i[2] == prod[0])]
            listTemp.append(b[0])
            listTemp.append(i[3])
            
        listdb.append(listTemp)
    for i in from_loc:
        listTemp = [] 
        if( i[0] not in [x[1] for x in from_inv ]):
            listTemp.append(i[1])
            listTemp.append("No Product")
            listTemp.append(0)
            listdb.append(listTemp)

    return render_template('pm.html', inventory=listdb, pm=pmdb )

if __name__=="__main__":
    app.run(debug= True)
    
  