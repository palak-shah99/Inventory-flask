import os
from flask import Flask, render_template, request, redirect, url_for

import sqlite3


DATABASE_NAME = 'inventory.sqlite'

app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'database', DATABASE_NAME),
)


def init_db():
    db = sqlite3.connect(DATABASE_NAME)
    cur = db.cursor()
    cur.execute("create table if not exists product(pid Integer primary key AUTOINCREMENT,prdname TEXT,qty Integer , unallocated INTEGER )")
    cur.execute("create table if not exists location(lid Integer primary key AUTOINCREMENT,locname TEXT)")
    cur.execute("create table if not exists productmove(mid Integer primary key AUTOINCREMENT,time_st Timestamp DEFAULT CURRENT_TIMESTAMP,floc INTEGER null,tloc INTEGER null, pid INTEGER not null , qty INTEGER)")    
    
    db.commit()


@app.route('/product', methods=['GET','POST'])
def product():
    db = sqlite3.connect(DATABASE_NAME)
    cur = db.cursor()
    cur.execute("SELECT * FROM product")
    product = cur.fetchall()
    if request.method == "POST":
        name = request.form['name']
        qty = request.form['quant']

        cur.execute("insert into product (prdname,qty , unallocated) values(?,?,?)",(name,qty,qty))
        
        cur.execute("select pid from product where prdname='"+name+"'") 
        pid=cur.fetchone()
        db.commit()
        print("product added succefully")
 
        return redirect(url_for('product'))

    return render_template('product.html', product=product)

@app.route('/location', methods=['GET', 'POST'])
def location():
    db = sqlite3.connect(DATABASE_NAME)
    cur = db.cursor()
    cur.execute("SELECT * FROM location")
    loc = cur.fetchall()

    if request.method == "POST":
        locname = request.form['locname']
        cur.execute("INSERT INTO location (locname) VALUES ('"+locname+"')")
        db.commit()
        print("location added succefully")
        return redirect(url_for('location'))
    
    return render_template('location.html', location=loc)

@app.route('/deleteloc/<int:lid>', methods=['POST','GET'])
def deleteloc(lid):

    db = sqlite3.connect(DATABASE_NAME)
    cur = db.cursor()
    cur.execute("delete from location where lid = ? ",  str(lid) )
    db.commit()
    return redirect(url_for('location'))

@app.route('/deleteproc/<int:pid>', methods=['POST','GET'])
def deleteproc(pid):
    db = sqlite3.connect(DATABASE_NAME)
    cur = db.cursor()
    cur.execute("delete from product where pid = ?", str(pid))  
    db.commit()
    return redirect(url_for('product'))


@app.route('/edit', methods=['POST', 'GET'])
def edit():
    error = []
    db = sqlite3.connect(DATABASE_NAME)
    cur = db.cursor()
    frompage = request.args.get('type')
    if(request.method == 'POST'):

        if frompage == 'location':
            loc_id = request.form['lid']
            loc_name = request.form['locname']
            
            if loc_name:
                cur.execute("update location set locname = ('"+loc_name+"') where lid = ("+loc_id+")")
            db.commit()
 
            return redirect(url_for('location'))    

        elif frompage == 'product' :
            cur.execute("SELECT * FROM product")
            product = cur.fetchall()

            pid = request.form['pid']
            prodname = request.form['name']
            qty = request.form['quant']
            
            cur.execute("select qty, unallocated from product where pid = ("+pid+")")
            old_val = cur.fetchone()
            
            if qty:
                if int(qty) < old_val[0]:
                    error.append("The new value is less than the old value")
                else:
                    cur.execute("update product set qty = ("+qty+") where pid = ("+pid+")")
                    qty =  int(qty) - old_val[0]
                    qty += old_val[1]
                    cur.execute("update product set unallocated = ("+str(qty)+") where pid = ("+pid+")")
                    

            if prodname:
                cur.execute("update product set prdname = ('"+prodname+"') where pid = ("+pid+")")
            
            db.commit()

            cur.execute("SELECT * FROM product")
            product = cur.fetchall()
                           
            return render_template('product.html', error = error, product = product )  
        
@app.route('/transaction', methods=['GET','POST']) 
def transaction():
    db = sqlite3.connect(DATABASE_NAME)
    cur = db.cursor()
    cur.execute("SELECT * FROM productmove")
    pmdb = cur.fetchall()
    return render_template('transaction.html', pm = pmdb )
  
@app.route('/', methods=['GET','POST']) 
def pm():

    def makeMovement( floc , tloc, pid , qty ):
        cur.execute("insert into productmove (floc,tloc,pid,qty) values(?,?,?,?) ", (floc, tloc, pid, qty))

    def setUnallocated( qty , pid):
        cur.execute("update product set unallocated= "+str(qty)+" where pid= "+pid )

    def currentQuantity(pmdb  , lid , pid ):
        tolocval = 0 
        for abc in [ pm[5] for pm in pmdb if pm[3] == int(lid) and pm[4] == int(pid)] :
            tolocval += abc

        fromlocval = 0
        for abc in [ pm[5] for pm in pmdb if pm[2] == int(lid) and pm[4] == int(pid) ] :
            fromlocval += abc
        
        return ( tolocval - fromlocval ) 

    def findUnallocated( pid):
        cur.execute("select unallocated from product where pid = " + pid )
        return cur.fetchone()[0]

    def fetchData():
        cur.execute("SELECT * FROM location")
        from_loc = cur.fetchall()

        cur.execute("SELECT * FROM product")
        from_prod = cur.fetchall()
        
        cur.execute("SELECT * FROM productmove")
        pmdb = cur.fetchall()
        
        return from_loc , from_prod , pmdb 
    init_db()
    db = sqlite3.connect(DATABASE_NAME)
    cur = db.cursor()
    error=[]

    from_loc, from_prod , pmdb = fetchData()
    
    if (request.method == 'POST'):
        pid=request.form['prdname']
        floc=request.form['floc']
        tloc=request.form['toloc']
        qty=int(request.form['qty'])
        if not floc: 

            unalloc = findUnallocated( pid)
            if qty > unalloc: 
                error.append("Quantity is greater than unallocated Quantity")
            else:
                makeMovement( 0 , tloc , pid , qty )
                qty = unalloc - qty 
                setUnallocated(qty,pid)
            
                
        elif not tloc:
            cur_q = currentQuantity(pmdb ,  floc, pid )
            
            if qty > cur_q : 
                error.append("Quantity is greater than current Quantity")
            else: 
                makeMovement( floc , 0 , pid , qty )
                unalloc = findUnallocated( pid)
                unalloc = unalloc + qty 
                setUnallocated( qty,pid)
        
        else:
            cur_q = currentQuantity(pmdb , floc, pid )
            if qty > cur_q :
                error.append("Quantity is greater than current Quantity")
            else:
                makeMovement( floc , tloc , pid , qty )
    
    db.commit()

    from_loc, from_prod , pmdb = fetchData()

    from_inv = [] 
    for p in from_prod: 
        if p[0] in [pm[4] for pm in pmdb] :
            
            for l in from_loc : 
                
                listdb = []     
                newqty = currentQuantity(pmdb ,  l[0] , p[0])
                    
                if newqty <= 0  : 
                    pass
                else : 
                    listdb.append(l[1])
                    listdb.append(p[1])
                    listdb.append(newqty)
                    from_inv.append(listdb)
                    

    return render_template('pm.html', inventory=from_inv, error=error, products=from_prod, location=from_loc )

if __name__=="__main__":
    init_db()
    app.run(debug= True)
    
  