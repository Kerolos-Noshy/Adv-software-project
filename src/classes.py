import datetime
from initial import db,app
from abc import abstractmethod,ABC
import os
from werkzeug.utils import secure_filename
class Account(): 
    def __init__(self,name,mail,password):
        self.name = name
        self.mail = mail
        self.password = password


class Client(Account,db.Model):
    ID = db.Column(db.Integer,nullable = False,primary_key = True)
    Account.name = db.Column(db.Text,nullable = False)
    Account.mail = db.Column(db.Text,nullable = False)
    Account.password = db.Column(db.Text,nullable = False)
    phone = db.Column(db.Text,nullable = False)
    state = db.Column(db.Boolean,nullable = True)
    Rejreason = db.Column(db.Text,nullable=True)
    photoext = db.Column(db.String(10),nullable = False)

    def __init__(self,name,mail,password,phone,photoext,state,Rejreason):
        Account.__init__(self,name,mail,password)
        self.phone = phone
        self.state = state
        self.Rejreason = Rejreason
        self.photoext=photoext

    @staticmethod
    def signin(mail,password):
        clients = Client.query.all()
        client = None
        for clien in clients:
            if mail == clien.mail:
                client = clien
                break
        if client != None:
            if client.password == password:
                return client
        else:
            return None
    @staticmethod
    def signup(mail,name,phone,password,nimage):
        clients = Client.query.all()
        client = None
        for clien in clients:
            if mail == clien.mail:
                client = clien
        if client != None:
            if client.state == None or  client.state == True:
                return client
            else:
                os.remove(app.config['UPLOAD_FOLDER']+"\\"+client.mail.split(".")[0]+"."+client.photoext)
                db.session.delete(client)
                db.session.commit()
        filename = secure_filename(nimage.filename)
        client = Client(name,mail,password,phone,filename.split(".")[1],None,None)
        db.session.add(client)
        db.session.commit()
        nimage.save(os.path.join(app.config["UPLOAD_FOLDER"],client.mail.split(".")[0]+"."+filename.split(".")[1]))
        nimage.close()
        return None
    @staticmethod
    def signout(session,id):
        if id in session:
            session.pop(id)
    @staticmethod
    def checkifsigned(session,id):
        if id in session:
            return True
        else:
            return False         
    @staticmethod
    def checkavail(roomtype,view,sdate,edate,roomnum,special):
        if roomtype == "Single":
            singlerooms = Single.query.filter(Single.view == view).all()
            contradicts = set()
            bookings1 = Booking.query.filter(Booking.roomtype==roomtype,Booking.startdate >= sdate,Booking.startdate < edate)
            if bookings1 != None:
                for booking in bookings1:
                    contradicts.add(booking.roomnum)
            bookings2 = Booking.query.filter(Booking.roomtype==roomtype,Booking.enddate > sdate,Booking.enddate <= edate)
            if bookings2 != None:
                for booking in bookings2:
                    contradicts.add(booking.roomnum)
            bookings3 = Booking.query.filter(Booking.roomtype==roomtype,Booking.startdate < sdate,Booking.enddate > edate)
            if bookings3 != None:
                for booking in bookings3:
                    contradicts.add(booking.roomnum)
            if special:
                return contradicts                            
            if (len(singlerooms)-len(contradicts)) < int(roomnum):
                return False
            else:
                return True

        if roomtype == "Double":
            doublerooms = Double.query.filter(Double.view==view).all()
            contradicts = set()
            bookings1 = Booking.query.filter(Booking.roomtype==roomtype,Booking.startdate >= sdate,Booking.startdate < edate)
            if bookings1 != None:
                for booking in bookings1:
                    contradicts.add(booking.roomnum)
            bookings2 = Booking.query.filter(Booking.roomtype==roomtype,Booking.enddate > sdate,Booking.enddate <= edate)
            if bookings2 != None:
                for booking in bookings2:
                    contradicts.add(booking.roomnum)
            bookings3 = Booking.query.filter(Booking.roomtype==roomtype,Booking.startdate < sdate,Booking.enddate > edate)
            if bookings3 != None:
                for booking in bookings3:
                    contradicts.add(booking.roomnum)     
            if special:
                return contradicts                       
            if (len(doublerooms)-len(contradicts)) < int(roomnum):
                return False
            else:
                return True
    @staticmethod
    def createbooking(sdate,edate,view,roomno,type,mail):
        if type == "Single":
            rooms = Single.query.filter(Single.view == view)
        else:
            rooms = Double.query.filter(Double.view == view)
        contradicts = Client.checkavail(type,view,sdate,edate,roomno,True)
        counter = 0
        sdate = datetime.date(int(sdate.split("-")[0]),int(sdate.split("-")[1]),int(sdate.split("-")[2]))
        edate = datetime.date(int(edate.split("-")[0]),int(edate.split("-")[1]),int(edate.split("-")[2]))
        for room in rooms:
            if room.roomnum not in contradicts:
                booking = Booking(False,room.roomnum,type,view,mail,sdate,edate)
                db.session.add(booking)
                counter += 1
            if counter == roomno:
                db.session.commit()
                break
        



class Admin(Account,db.Model):
    Account.name = db.Column(db.Text,nullable = False)
    Account.mail = db.Column(db.Text,nullable = False,primary_key = True)
    Account.password = db.Column(db.Text,nullable = False)
    def __init__(self,name,mail,password):
        Account.__init__(self,name,mail,password)
    @staticmethod
    def addClient(name,mail,password,phone,photoext):
        client = Client(name,mail,password,phone,photoext,None,None)
        db.session.add(client)
        db.session.commit()
    @staticmethod
    def approveClient(id):
        client = Client.query.get(id)
        client.Rejreason = None
        client.state = True
        db.session.commit()
    @staticmethod
    def rejectClient(id):
        client = Client.query.get(id)
        client.state = False
        db.session.commit()
    @staticmethod
    def signin(a):
        a["admin"] = True
    @staticmethod
    def signout(session):
        if "admin" in session:
            session.pop("admin")
    @staticmethod
    def checkifsigned(session):
        if "admin" in session:
            return True
        else:
            return False
    @staticmethod
    def modifyadmindata(name,mail,password):
        admin = Admin.query.all()[0]
        admin.name = name
        admin.mail=mail
        admin.password=password
        db.session.commit()
    @staticmethod
    def makeroomavailable(id):
        room = Room.query.get(id)
        if room != None:
            room.state = True
    @staticmethod
    def makeroomunavailable(id):
        room = Room.query.get(id)
        if room != None:
            room.state = False
class Room():

    def __init__(self,state,roomnum,view,costpernight):
        self.state = state
        self.roomnum = roomnum
        self.view = view
        self.costpernight=costpernight

class Single(db.Model,Room):
    Room.state = db.Column(db.Boolean,nullable = False)
    Room.roomnum = db.Column(db.Integer,primary_key=True)
    Room.view = db.Column(db.Text,nullable = False)
    Room.costpernight = db.Column(db.Float,nullable = False)
    def __init__(self,state,roomnum,view,costpernight):
        Room.__init__(self,state,roomnum,view,costpernight)
    
class Double(db.Model,Room):
    Room.state = db.Column(db.Boolean,nullable = False)
    Room.roomnum = db.Column(db.Integer,primary_key=True)
    Room.view = db.Column(db.Text,nullable = False)
    Room.costpernight = db.Column(db.Float,nullable = False)
    def __init__(self,state,roomnum,view,costpernight):
        Room.__init__(self,state,roomnum,view,costpernight)

class Booking(db.Model):
    ID = db.Column(db.Integer,primary_key = True)
    isrequest = db.Column(db.Boolean,nullable = False)
    roomnum = db.Column(db.Integer,nullable = False)
    roomtype = db.Column(db.Text,nullable = False)
    viewtype = db.Column(db.Text,nullable = False)
    client = db.Column(db.Text,nullable = False)
    startdate = db.Column(db.DateTime(),nullable = False)
    enddate = db.Column(db.DateTime(),nullable = False)
    def __init__(self,isrequest,roomnum,roomtype,viewtype,client,startdate,enddate):
        self.isrequest = isrequest
        self.roomnum = roomnum
        self.client = client
        self.startdate=startdate
        self.enddate = enddate
        self.roomtype = roomtype
        self.viewtype = viewtype

        
if __name__ == "__main__":
    db.create_all()


    

