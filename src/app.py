from initial import app,db
from flask import render_template,redirect,session,request
import os
from classes import Admin,Client,Single,Double,Booking
from datetime import date,timedelta,datetime
import datetime

################################################################################
##anything after @app.route is the route that the user enters or is directed to
################################################################################

#######################    Important Notes   ##########################
##1) to use admin functionalities type /adminlog in the url manually##
##2) Do not under any condition remove the databse file##
##########################################################################

############################################################################
## any methods unmentioned in the comments are in class.py##
#############################################################################
#initial configurations
app.secret_key=os.urandom(32)
repo_path2 = os.path.abspath(os.path.dirname(__name__))
app.config["UPLOAD_FOLDER"] = os.path.join(repo_path2,"static\\nphotos")
app.permanent_session_lifetime = timedelta(minutes=30)
#upon entering the website redirect to /home
@app.route("/")
def start():
   return redirect("/home")
#renders the home page
@app.route("/home")
def home():
    return render_template("index.html",id=None)
#renders the room info page
@app.route("/rooms")
def rooms():
    return render_template("rooms.html")
#renders the facility services page
@app.route("/fac")
def fac():
    return render_template("facility.html")


@app.route("/contact")
def cont():
    return render_template("contact.html")

#renders the availabilty check page
@app.route("/availcheck")
def preavailcheck():
    return render_template("availability.html")

#gets the result of the availability check
@app.route("/availcheck" , methods = ["POST"])
def postavailcheck():
    sdate = request.form.get("sdate")
    edate = request.form.get("edate")
    roomnum = request.form.get("roomno")
    roomtype = request.form.get("type")
    view = request.form.get("view")
    if Client.checkavail(roomtype,view,sdate,edate,roomnum,False):
        return render_template("availresult.html" , avail = True)
    else:
        return render_template("availresult.html" , avail = False)        

#renders the user login page        
@app.route("/login")
def preuserlog():
    return render_template("login.html",admin = False)

#validates the data from the user if incorrect redirects to the signup page
@app.route("/login" , methods = ["POST"])
def postuserlog():
    mail = request.form.get("Email")
    password = request.form.get("Password")
    client = Client.signin(mail,password)
    #if data not in database redirect to sign up page
    if client == None:
        return redirect("/signup")
    #if data in the database view the request info or log in
    else:
        session[str(client.ID)] = client.ID
        if client.state == None:
            return render_template("yourrequest.html",client = client)
        elif client.state == False:
            return render_template("yourrequest.html",client = client)
        else:
            return redirect("/user/" + str(client.ID))
#page after login
@app.route("/user/<int:id>")
def userwelcome(id):
    return render_template("index.html" , id = id)
#renders profile page of a user
@app.route("/profile/<int:id>")
def cpfile(id):
    if Client.checkifsigned(session,str(id)):
        client = Client.query.get(id)
        return render_template("profile.html" , client = client)
    else:
        return redirect("/home")
#clears user session i.e.: signs out user
@app.route("/signout/<int:id>")
def usout(id):
    Client.signout(session,str(id))
    return redirect("/home")
#renders signup page
@app.route("/signup")
def presignup():
    return render_template("signup.html")
#gets user data for sign up
@app.route("/signup" , methods = ["POST"])
def postsignup():
    mail = request.form.get("Email")
    name = request.form.get("Fname") +" "+ request.form.get("Sname") + " "+request.form.get("Lname")
    phone = request.form.get("Phone")
    password = request.form.get("Password")
    nimage = request.files["IDPhoto"]
    client = Client.signup(mail,name,phone,password,nimage)
    if client != None:
        #if request exists in system view its info
        #else add request info to database
        return render_template("yourrequest.html",client = client)
    return redirect("/login")
#renders admin login page
@app.route("/adminlog")
def preadmin():
    session["admin"] = None
    session["counter"] = 0
    return render_template("login.html",admin = True)
#validates admin data maximum amount of failed tries is 3 times
@app.route("/adminlog",methods=["POST"])
def postadmin():
    mail = request.form.get("Email")
    admin = Admin.query.get(mail)
    if session["counter"] != 3:
        if not admin:
            session["counter"] = session["counter"] +1
            return redirect("/adminlog")
        else:
            passcode = request.form.get("Password")
            if admin.password != passcode:
                session["counter"] = session["counter"] +1
                return redirect("/adminlog")
            else:
                session["counter"] = None
                Admin.signin(session)
                return redirect("/adminprofile")
#allows admin to modify their data
@app.route("/adminmodify")
def ma():
    data = Admin.query.all()[0]
    return render_template("modify.html",admin = True,data = data)
#updates the data of the admin
@app.route("/adminmodify" , methods = ["POST"])
def postma():
    name = request.form.get("fname") + " " + request.form.get("lname")
    mail = request.form.get("Email")
    password = request.form.get("Password")
    Admin.modifyadmindata(name,mail,password)
    return redirect("/adminprofile")


#allows user to modify their data
@app.route("/usermodify/<int:id>")
def mc(id):
    if Client.checkifsigned(session,str(id)):
        data = Client.query.get(id)
        return render_template("modify.html",admin=False,data=data)
    else:
        return redirect("/home")
#allows admin to modify data of a certain user
@app.route("/adminusermodify/<int:id>")
def preadminusermodify(id):
    if Admin.checkifsigned(session):
        data = Client.query.get(id)
        return render_template("modify.html",admin=None,data=data)
    else:
        return redirect("/home")
#updates data of user
@app.route("/adminusermodify/<int:id>",methods = ["POST"])
def adminusermodify(id):
    if Admin.checkifsigned(session):
        client = Client.query.get(id)
        name = request.form.get("Fname")+" "+request.form.get("Sname")+" "+request.form.get("Lname")
        phone = request.form.get("Phone")
        mail = request.form.get("Email")
        password = request.form.get("Password")
        client.name = name
        client.phone = phone
        client.mail = mail
        client.password = password
        db.session.commit()
        return redirect("/accrequests/"+str(id))
    else:
        return redirect("/home")
#updates the data of the user
@app.route("/usermodify/<int:id>",methods = ["POST"])
def mcc(id):
    if Client.checkifsigned(session,str(id)):
        client = Client.query.get(id)
        name = request.form.get("Fname")+" "+request.form.get("Sname")+" "+request.form.get("Lname")
        phone = request.form.get("Phone")
        mail = request.form.get("Email")
        password = request.form.get("Password")
        client.name = name
        client.phone = phone
        client.mail = mail
        client.password = password
        db.session.commit()
        return redirect("/profile/" + str(id))
    else:
        return redirect("/home")


#signs out admin
@app.route("/signout")
def asout():
    Admin.signout(session)
    return redirect("/home")
#renders admin home page
@app.route("/adminprofile")
def ap():
    return render_template("adminprofile.html")

#views all account requests
@app.route("/accrequests")
def accreq():
    if Admin.checkifsigned(session):
        return render_template("accrequests.html")
    else: 
        return redirect("/home")               
#view accepted account requests
@app.route("/accrequests/accepted")
def accept():
    if Admin.checkifsigned(session):
        accclients = Client.query.filter(Client.state == True)
        return render_template("reqtype.html",accclients=accclients,req = True)
    else: 
        return redirect("/home")
#view pending account requests  
@app.route("/accrequests/pending")
def pending():
    if Admin.checkifsigned(session):
        accclients = Client.query.filter(Client.state == None)
        return render_template("reqtype.html",accclients=accclients,req = None)
    else: 
        return redirect("/home")  
#view rejected account requests
@app.route("/accrequests/rejected")
def rejected():
    if Admin.checkifsigned(session):
        accclients = Client.query.filter(Client.state == False)
        return render_template("reqtype.html",accclients=accclients,req = False)
    else: 
        return redirect("/home")  
#views the selected account request
@app.route("/accrequests/<int:id>")
def requ(id):
    if Admin.checkifsigned(session):    
        client = Client.query.get(id)
        return render_template("reqdetail.html" , client=client)
    else: 
        return redirect("/home")  
#approve a request
@app.route("/accrequests/accept/<int:id>")
def approve(id):
    if Admin.checkifsigned(session):    
        Admin.approveClient(id)
        return redirect("/accrequests/accepted")
    else: 
        return redirect("/home") 
#reject a request and getting rejection reason from admin
@app.route("/accrequests/reject/<int:id>")
def reject(id):
    if Admin.checkifsigned(session):    
        client = Client.query.get(id)
        return render_template("rejreason.html" , id = client.ID)
    else: 
        return redirect("/home") 
#adds request to rejected ones
@app.route("/accrequests/reject/<int:id>",methods = ["POST"])
def rej(id):
    if Admin.checkifsigned(session): 
        rejreason = request.form.get("Rej")
        client = Client.query.get(id)
        client.Rejreason = rejreason
        client.state = False
        db.session.commit()
        return redirect("/accrequests/rejected")
    else: 
        return redirect("/home")
#view hotel rooms
@app.route("/adminrooms")
def modrooms():
    return render_template("hotelrooms.html")
#select room type to modify its price
@app.route("/roomprices")
def price():
    return render_template("roomprices.html")
#modify price of single street view
@app.route("/roomprices/sstv")
def sstvprice():
    priceroom = Single.query.filter(Single.view == "Street").first()
    cost = priceroom.costpernight
    return render_template("changeprice.html",header="Single Street View",cost=cost,acronym="sstv")
#modify price of single sea view
@app.route("/roomprices/ssv")
def ssvprice():
    priceroom = Single.query.filter(Single.view == "Sea").first()
    cost = priceroom.costpernight
    return render_template("changeprice.html",header="Single Sea View",cost=cost,acronym="ssv")
#modify price of double street view
@app.route("/roomprices/dstv")
def dstvprice():
    priceroom = Double.query.filter(Double.view == "Street").first()
    cost = priceroom.costpernight
    return render_template("changeprice.html",header="Double Street View",cost=cost,acronym="dstv")
#modify price of double sea view
@app.route("/roomprices/dsv")
def dsvprice():
    priceroom = Double.query.filter(Double.view == "Sea").first()
    cost = priceroom.costpernight
    return render_template("changeprice.html",header="Double Sea View",cost=cost,acronym="dsv")
#adds new price to database
@app.route("/changeprice" , methods = ["POST"])
def cp():
    acronym = request.form.get("ac")
    cost = request.form.get("Cost")
    if acronym == "sstv":
        singles = Single.query.filter(Single.view == "Street")
        for single in singles:
            single.costpernight = cost
    elif acronym=="ssv":
        singles = Single.query.filter(Single.view == "Sea")
        for single in singles:
            single.costpernight = cost
    elif acronym == "dstv":
        doubles = Double.query.filter(Double.view == "Street")
        for double in doubles:
            double.costpernight = cost
    else:
        doubles = Double.query.filter(Double.view == "Sea")
        for double in doubles:
            double.costpernight = cost
    db.session.commit()
    return redirect("/roomprices")
#views all rooms by number        
@app.route("/roomdata")
def data():
    rooms = Single.query.all() + Double.query.all()
    return render_template("roomdata.html",rooms = rooms)
#view certain room data
@app.route("/roomdata/<int:id>")
def roomdata(id):
    room = Single.query.get(id)
    if room == None:
        room = Double.query.get()
        return render_template("roomdetail.html",room = room,type="d")
    return render_template("roomdetail.html",room = room,type ="s")

#view all bookings
@app.route("/bookingall")
def bookreq():
    return render_template("bookingall.html",admin=True)
#view previous bookings
@app.route('/bookingpast')
def past():
    bookings = Booking.query.filter(Booking.isrequest==False,Booking.enddate<date.today())
    return render_template("bookingtype.html",bookings=bookings,admin=True)
#view current bookings
@app.route('/bookingnow')
def now():
    bookings = Booking.query.filter(Booking.isrequest==False,Booking.enddate>date.today(),Booking.startdate<=date.today())
    return render_template("bookingtype.html",bookings=bookings,admin=True)    
#view future bookings
@app.route('/bookingfut')
def fut():
    bookings = Booking.query.filter(Booking.isrequest==False,Booking.startdate>date.today())
    return render_template("bookingtype.html",bookings=bookings,admin=True)
#view booking requests
@app.route('/bookingreq')
def breq():
    bookings = Booking.query.filter(Booking.isrequest==True)
    return render_template("bookingtype.html",bookings=bookings)
#view booking form for client
@app.route("/book/<int:id>")
def bokk(id):
    if Client.checkifsigned(session,str(id)):
        return render_template("bookingform.html",id=id)
    else:
        return redirect("/home")
#takes booking info
@app.route("/book/<int:id>" , methods=["POST"])
def postbokk(id):
    client = Client.query.get(id)
    sdate = request.form.get("sdate")
    edate = request.form.get("edate")
    roomno = request.form.get("roomno")
    view = request.form.get("view")
    type = request.form.get("type")
    #if available create the booking
    if Client.checkavail(type,view,sdate,edate,int(roomno),False):
        Client.createbooking(sdate,edate,view,int(roomno),type,client.mail)
        return redirect("/bookhistory/" +str(id))
    #if not available display exception page
    else:
        return render_template("availresult.html",avail=False)
#allows user to view their booking history
@app.route("/bookhistory/<int:id>")
def bookhistory(id):
    if Client.checkifsigned(session,str(id)):
        return render_template("bookingall.html",admin = False,id = id)
    else:
       return redirect("/home")

@app.route("/bookhistorypast/<int:id>")
def bookhistorypast(id):
    if Client.checkifsigned(session,str(id)): 
        client = Client.query.get(id)
        bookings = Booking.query.filter(Booking.isrequest==False,Booking.enddate<date.today(),Booking.client == client.mail)
        return render_template("bookingtype.html",bookings=bookings,id=id,admin=False)  
    else:
       return redirect("/home")

@app.route("/bookhistorypresent/<int:id>")
def bookhistorypresent(id):
    if Client.checkifsigned(session,str(id)): 
        client = Client.query.get(id)
        bookings = Booking.query.filter(Booking.isrequest==False,Booking.enddate>date.today(),Booking.startdate<=date.today(),Booking.client == client.mail)
        return render_template("bookingtype.html",bookings=bookings,id=id,admin=False)  
    else:
       return redirect("/home")

@app.route("/bookhistoryfuture/<int:id>")
def bookhistoryfuture(id):
    if Client.checkifsigned(session,str(id)): 
        client = Client.query.get(id)
        bookings = Booking.query.filter(Booking.isrequest==False,Booking.startdate>date.today(),Booking.client == client.mail)
        return render_template("bookingtype.html",bookings=bookings,id=id,admin=False)  
    else:
        return redirect("/home")
#get booking info of a certain booking
@app.route("/bookinginfo/<int:bookid>/<int:id>")
def ssss(id,bookid):
    if Client.checkifsigned(session,str(id)): 
        booking = Booking.query.get(bookid)
        client = Client.query.get(id)
        name = client.name
        stay = booking.enddate-booking.startdate
        if booking.roomtype == "Single":
            pricepernight = Single.query.filter(Single.roomnum==booking.roomnum,Single.view==booking.viewtype).all()[0].costpernight
        else:
            pricepernight = Double.query.filter(Double.roomnum==booking.roomnum,Double.view==booking.viewtype).all()[0].costpernight
        total = pricepernight * stay.days
        return render_template("bookingdetail.html",booking = booking , name=name,admin=False,id=id,total=total)
    else:
        return redirect("/home")

#get booking info for admin
@app.route("/bookinginfo/<int:id>")
def sss(id):
    booking = Booking.query.get(id)
    stay = booking.enddate-booking.startdate
    if booking.roomtype == "Single":
        pricepernight = Single.query.filter(Single.roomnum==booking.roomnum,Single.view==booking.viewtype).all()[0].costpernight
    else:
        pricepernight = Double.query.filter(Double.roomnum==booking.roomnum,Double.view==booking.viewtype).all()[0].costpernight
    total = pricepernight * stay.days
    client = Client.query.filter(Client.mail==booking.client).all()
    name = client[0].name
    return render_template("bookingdetail.html",booking = booking , name=name,admin=True,id=id,total=total)

#modifies booking info
@app.route("/bookingmodify/<int:id>")
def modbook(id):
    booking = Booking.query.get(id)
    return render_template("modbook.html",booking=booking)

#updates booking info in database
@app.route("/bookingmodify/<int:id>",methods = ["POST"])
def postmodbook(id):
    booking = Booking.query.get(id)
    roomno = request.form.get("roomno")
    sdate = request.form.get("sdate")
    edate = request.form.get("edate")
    room = Single.query.get(int(roomno))
    if room == None:
        room = Double.query.get(int(roomno))
    sdateasdatetime = datetime.date(int(sdate.split("-")[0]),int(sdate.split("-")[1]),int(sdate.split("-")[2]))
    edateAsDateTime = datetime.date(int(edate.split("-")[0]),int(edate.split("-")[1]),int(edate.split("-")[2]))
    contradicts = Client.checkavail(booking.roomtype,booking.viewtype,sdate,edate,1,True)
    if int(roomno) in contradicts:
        return render_template("availresult.html",avail=False)
    else:
        booking.roomnum = roomno
        booking.viewtype = room.view
        booking.roomtype = (str(room).split(" ")[0])[1:]
        booking.startdate = sdateasdatetime
        booking.enddate = edateAsDateTime
        db.session.commit()
        return redirect("/bookinginfo/" + str(id)) 

#deletes a certain user
@app.route("/deleteuser/<int:id>")
def deleteuser(id):
    user = Client.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return redirect("/accounts")
#deletes a certain booking by admin
@app.route("/deletebooking/<int:id>")
def deletebooking(id):
    booking = Booking.query.get(id)
    db.session.delete(booking)
    db.session.commit()
    return redirect("/bookingall")
#deletes a certain booking by client
@app.route("/deletebooking/<int:bookid>/<int:id>")
def deletebookinguser(bookid,id):
    if Client.checkifsigned(session,str(id)):
        booking = Booking.query.get(bookid)
        db.session.delete(booking)
        db.session.commit()
        return redirect("/bookhistory/" +str(id))
    else:
        return redirect("/home")

#view all accounts
@app.route("/accounts")
def acc():
    accounts = Client.query.filter(Client.state == True)
    return render_template("reqtype.html",accclients=accounts,req=True)
#starts the program
if __name__ == "__main__" :
    app.run(debug=False,port=5000)