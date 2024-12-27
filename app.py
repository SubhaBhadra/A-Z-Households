from flask import Flask,render_template,request,redirect,url_for 
from backend.models import db
from backend.models import *
from werkzeug.utils import secure_filename 
import matplotlib.pyplot as plt
import os

app=None

def setup_app():
    global app  # Reference the global app object
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///a-z-household.sqlite3" # having a db
    db.init_app(app) #Flask app connected to db
    app.app_context().push() #Direct access to other modules
    app.debug =True
    print('The app is running...')



setup_app()


# Defining the routes

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/login',methods=['GET','POST'])
def signin():
    if request.method == "POST":
        uname = request.form.get("user_name")
        
        usr1 = Customer.query.filter_by(email=uname).first()

             
        usr2 = Professional.query.filter_by(email=uname).first()
        
             
        
        
        if usr1 and usr1.role == "admin": 
                return redirect(url_for("admin_dashboard"))
        elif usr1 and usr1.role == "customer":
                cid=usr1.id
                return redirect(url_for("customer_dashboard",id=cid))
        elif usr2 and usr2.role == "professional":
                pid=usr2.id
                return redirect(url_for("professional_dashboard",id=pid))
        else:
             return render_template("login.html",msg="Invalid user credentials.......")

    return render_template("login.html",msg='')


@app.route('/register',methods=['POST','GET'])
def signup():
     if request.method == "POST":
        uname = request.form.get("user_name")
        pwd = request.form.get("password")
        full_name=request.form.get("full_name")
        address=request.form.get("address")
        pin=request.form.get("pin")
        phn=request.form.get("phone_number")
        usr1 = Customer.query.filter_by(email=uname).first()
        usr2 = Professional.query.filter_by(email=uname).first()
        if usr1 or usr2:
             return render_template("signup.html",msg='Sorry this mail is already registered')

        new_user=Customer(email=uname,password=pwd,phone_number=phn,full_name=full_name,address=address,pin=pin)
        db.session.add(new_user)
        db.session.commit()
        return render_template("login.html",msg="Registration Successfull")
        
     return render_template("signup.html",msg='')
    


@app.route('/registerasprofessional',methods=['POST','GET'])
def signup_professional():
    if request.method == "POST":
        uname = request.form.get("user_name")
        pwd = request.form.get("password")
        full_name=request.form.get("full_name")
        exp=request.form.get("experience")
        phn=request.form.get("phonenumber")
        serv=request.form.get("service_name")
        file=request.files["resume_upload"]
        url=""
        if file.filename:
             file_name=secure_filename(file.filename) #verification of the file id done
             url=("./uploaded_files/"+file_name+"_"+full_name)
             file.save(url)

        
        address=request.form.get("address")
        pin=request.form.get("pin")
        usr1 = Professional.query.filter_by(email=uname).first()
        usr2 = Customer.query.filter_by(email=uname).first()
        if usr1 or usr2 :
             return render_template("professional.html",Service=get_service(),msg='Sorry this mail is already registered')

        new_prof = Professional(
            email=uname,
            password=pwd,
            phone_number=phn,
            service_name=serv,
            full_name=full_name,
            experience=exp,
            address=address,
            resume_url=url,
            pin=pin,
        )
        db.session.add(new_prof)
        db.session.commit()
        return render_template("login.html",msg="Registration Successfull")
        
     
    return render_template("professional.html",msg='',Service=get_service())

@app.route("/admin")
def admin_dashboard():
     Service=get_service()
     Professional=get_professional()
     return render_template("admindashboard.html",Service=Service,Professional=Professional)

@app.route("/customer/<id>")
def customer_dashboard(id):
     professional=get_approvedprofessional()
     ServiceRequest=get_servicerequest(id)
     return render_template("customerdashboard.html",ServiceRequest=ServiceRequest,Professional=professional,id=id)

@app.route("/professional/<id>")
def professional_dashboard(id):
     sr=get_servicerequestbyprofessionalid(id)
     return render_template("professionaldashboard.html",id=id,ServiceRequest=sr)


@app.route('/addservice',methods=['POST','GET'])
def add_service():
      if request.method == "POST":
        name = request.form.get("name")
        price = request.form.get("price")
        time=request.form.get("time_required")
        desc=request.form.get("description")
        new_service=Service(name=name,price=price,time_required=time,description=desc)
        db.session.add(new_service)
        db.session.commit()
        return redirect(url_for("admin_dashboard"))

        

      return render_template("add_service.html")
      
        
def get_service():
     srvc=Service.query.all()
     return srvc

def get_servicerequest(id):
     srv=ServiceRequest.query.filter(ServiceRequest.customer_id==id).all()
     return srv


def get_servicerequestbyprofessionalid(id):
     srv=ServiceRequest.query.filter(ServiceRequest.professional_id==id).all()
     return srv

def get_professional():
     prf=Professional.query.all()
     return prf

def get_approvedprofessional():
     prf=Professional.query.filter(Professional.status=="Approved").all()
     return prf

@app.route('/admin_search',methods=['POST','GET'])
def admin_search():
     if request.method == "POST":
          search_txt=request.form.get("search_txt")
          by_service=search_by_service(search_txt)
          by_customer=search_by_customer(search_txt)
          by_professional=search_by_professional(search_txt)
          if by_service:
            return render_template("admin_search.html",Service=by_service)
     
          elif by_customer:
            return render_template("admin_search.html",Customer=by_customer)
          
          elif by_professional:
            return render_template("admin_search.html",Professional=by_professional)
          
     return render_template("admin_search.html")
          





def search_by_service(search_txt):
     srvc=Service.query.filter(Service.name.ilike(f"%{search_txt}%")).all()
     return srvc

def search_by_customer(search_txt):
     cstmr=Customer.query.filter(Customer.full_name.ilike(f"%{search_txt}%")).all()
     return cstmr

def search_by_professional(search_txt):
     prf=Professional.query.filter(Professional.full_name.ilike(f"%{search_txt}%")).all()
     return prf


@app.route('/editservice/<id>',methods=['POST','GET'])
def edit_service(id):
      s=get_srvc(id)
      if request.method == "POST":
        name = request.form.get("name")
        price = request.form.get("price")
        time=request.form.get("time_required")
        desc=request.form.get("description")
        s.name=name
        s.price=price
        s.time_required=time
        s.description=desc
        db.session.commit()

        return redirect(url_for("admin_dashboard"))

        

      return render_template("edit_service.html", Service=s)

def get_srvc(id):
     srvc=Service.query.filter_by(id=id).first()
     return srvc


@app.route('/deleteservice/<id>',methods=['POST','GET'])
def delete_service(id):
      s=get_srvc(id)
      db.session.delete(s)
      db.session.commit()
      return redirect(url_for("admin_dashboard"))


@app.route('/editprofessional/<id>',methods=['POST','GET'])
def edit_professional(id):
      p=get_prf(id)
      if request.method == "POST":
        p.status="Approved"
        db.session.commit()

        

        return redirect(url_for("admin_dashboard"))

        

      return render_template("edit_professional.html", Professional=p)

@app.route('/deleteprofessional/<id>',methods=['POST','GET'])
def delete_professional(id):
      p=get_prf(id)
      db.session.delete(p)
      db.session.commit()
      return redirect(url_for("admin_dashboard"))

        
def get_prf(id):
     prf=Professional.query.filter_by(id=id).first()
     return prf 

@app.route('/editcustomer/<id>',methods=['POST','GET'])
def edit_customer(id):
      c=get_customer(id)
      if request.method == "POST":
        return redirect(url_for("admin_dashboard"))

        

      return render_template("edit_customer.html", Customer=c)


@app.route('/deletecustomer/<id>',methods=['POST','GET'])
def delete_customer(id):
      c=get_customer(id)
      db.session.delete(c)
      db.session.commit()
      return redirect(url_for("admin_dashboard"))

def get_customer(id):
     cmr=Customer.query.filter_by(id=id).first()
     return cmr 

@app.route('/customereditprofile/<id>',methods=['POST','GET'])
def customer_edit_profile(id):
      c=get_customer(id)
      if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        address = request.form.get("address")
        phn=request.form.get("phone_number")
        pin=request.form.get("pin")

        c.full_name=name
        c.email=email
        c.password=password
        c.address=address
        c.phone_number=phn
        c.pin=pin
        db.session.commit()

        return redirect(url_for("customer_dashboard",id=id))

      return render_template("customer_edit_profile.html", Customer=c,id=id)


@app.route('/customersearch/<id>',methods=['POST','GET'])
def customer_search(id):
     if request.method == "POST":
          search_txt=request.form.get("search_txt")
          by_service=search_by_profession(search_txt)
          by_pin=search_by_pin(search_txt)
          
          if by_service:
            return render_template("customer_search.html",Professional=by_service,id=id)
     
          elif by_pin:
            return render_template("customer_search.html",Professional=by_pin,id=id)
          
          
     return render_template("customer_search.html",id=id)

  
def search_by_pin(search_txt):
     prf=Professional.query.filter(Professional.pin.ilike(f"%{search_txt}%")).filter(Professional.status=="Approved").all()
     return prf  

def search_by_profession(search_txt):
     prf=Professional.query.filter(Professional.service_name.ilike(f"%{search_txt}%")).filter(Professional.status=="Approved").all()
     return prf 
           

@app.route('/bookprofessional/<cid>/<pid>',methods=['POST','GET'])
def book_professional(cid,pid):
      remark=request.form.get("remark")
      p=get_prf(pid)
      c=get_customer(cid)
      if request.method == "POST":
           new_request=ServiceRequest(customer_id=cid,customer_name=c.full_name,customer_phno=c.phone_number,professional_name=p.full_name,professional_phno=p.phone_number,service_name=p.service_name,professional_id=pid,remarks=remark,date_of_request=datetime.now())
           db.session.add(new_request)
           db.session.commit()
           return redirect(url_for("customer_dashboard",id=cid))
      


      return render_template("book_professional.html",id=cid,Professional=p)


def get_prf(id):
     prf=Professional.query.filter_by(id=id).first()
     return prf 

     
        
@app.route('/editrequest/<cid>/<srid>',methods=['POST','GET'])
def edit_request(cid,srid):
      s=get_srid(srid)
      if request.method == "POST":
        
        Status = request.form.get("status")
        remark=request.form.get("remarks")

        s.service_status=Status
        s.remarks=remark
        db.session.commit()

        return redirect(url_for("customer_dashboard",id=cid))

        

      return render_template("edit_request.html",ServiceRequest=s,id=cid)  

def get_srid(srid):
     sr=ServiceRequest.query.filter_by(id=srid).first()
     return sr       
   
@app.route('/deleterequest/<cid>/<srid>',methods=['POST','GET'])
def delete_request(cid,srid):
      sr=get_srid(srid)
      db.session.delete(sr)
      db.session.commit()
      return redirect(url_for("customer_dashboard",id=cid))

@app.route('/review/<cid>/<srid>',methods=['POST','GET'])
def review(cid,srid):
      prid=get_srid(srid)
      if request.method == "POST":
        
        rating = request.form.get("rating")
        comment=request.form.get("comment")
        

        new_review=Review(customer_id=cid,service_request_id=srid,professional_id=prid.professional_id,rating=rating,comment=comment)

        db.session.add(new_review)

        db.session.commit()

        return redirect(url_for("customer_dashboard",id=cid))

      return render_template("review.html",id=cid,ServiceRequest=prid) 

def get_review(pid,srid):
     sr=Review.query.filter(Review.customer_id==pid and Review.id==srid).first()
     return sr

@app.route('/acceptrequest/<pid>/<srid>',methods=['POST','GET'])
def accept_request(pid,srid):
      s=get_srid(srid)
      if request.method == "POST":
        
        Status = request.form.get("status")

        s.service_status=Status
        db.session.commit()

        return redirect(url_for("professional_dashboard",id=pid))

        

      return render_template("accept_request.html",ServiceRequest=s,id=pid)  


@app.route('/seereview/<pid>/<srid>',methods=['POST','GET'])
def seereview(pid,srid):
      rvw=get_review(pid,srid)
      return render_template("see_review.html",id=pid,Review=rvw) 


@app.route('/professionaleditprofile/<id>',methods=['POST','GET'])
def professional_edit_profile(id):
      p=get_prf(id)
      if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        address = request.form.get("address")
        experience=request.form.get("experience")
        phn=request.form.get("phone_number")
        pin=request.form.get("pin")

        p.full_name=name
        p.email=email
        p.password=password
        p.experience=experience
        p.address=address
        p.phone_number=phn
        p.pin=pin
        db.session.commit()

        return redirect(url_for("professional_dashboard",id=id))

      return render_template("professional_edit_profile.html", Professional=p,id=id)


@app.route("/adminsummary")
def admin_summary():
     plot=get_request_summary_admin()
     plot.savefig("./static/images/admin_request_summary.jpeg")
     plot.clf()

     return render_template("admin_summary.html")

@app.route("/customersummary/<cid>")
def customer_summary(cid):
     plot=get_request_summary_customer(cid)
     plot.savefig("./static/images/customer_request_summary.jpg")
     plot.clf()

     return render_template("customer_summary.html",id=cid)

@app.route("/professionalsummary/<pid>")
def professional_summary(pid):
     plot=get_request_summary_professional(pid)
     plot.savefig("./static/images/professional_request_summary.jpg")
     plot.clf()

     return render_template("professional_summary.html",id=pid)

def get_request_summary_admin():
     request=get_request()
     summary={}
     accepted=0
     rejected=0
     closed=0
     requested=0
     for req in request:
          if(req.service_status=="accepted"):
               accepted+=1
          elif(req.service_status=="rejected"):
               rejected+=1
          elif(req.service_status=="closed"):
               closed+=1
          elif(req.service_status=="requested"):
               requested+=1
     summary['accepted']=accepted
     summary['rejected']=rejected
     summary['closed']=closed
     summary['requested']=requested

     x=list(summary.keys())
     y=list(summary.values())
     plt.bar(x,y,color="orange",width=0.5)
     plt.title("Request Status / Number")
     plt.xlabel("Request Status")
     plt.ylabel("Number")
     return plt


def get_request_summary_customer(cid):
     request=get_servicerequest(cid)
     summary={}
     accepted=0
     rejected=0
     closed=0
     requested=0
     for req in request:
          if(req.service_status=="accepted"):
               accepted+=1
          elif(req.service_status=="rejected"):
               rejected+=1
          elif(req.service_status=="closed"):
               closed+=1
          elif(req.service_status=="requested"):
               requested+=1
     summary['accepted']=accepted
     summary['rejected']=rejected
     summary['closed']=closed
     summary['requested']=requested

     x=list(summary.keys())
     y=list(summary.values())
     plt.bar(x,y,color="orange",width=0.5)
     plt.title("Request Status / Number")
     plt.xlabel("Request Status")
     plt.ylabel("Number")
     return plt

def get_request_summary_professional(pid):
     request=get_servicerequestbyprofessionalid(pid)
     summary={}
     accepted=0
     rejected=0
     closed=0
     requested=0
     for req in request:
          if(req.service_status=="accepted"):
               accepted+=1
          elif(req.service_status=="rejected"):
               rejected+=1
          elif(req.service_status=="closed"):
               closed+=1
          elif(req.service_status=="requested"):
               requested+=1
     summary['accepted']=accepted
     summary['rejected']=rejected
     summary['closed']=closed
     summary['requested']=requested

     x=list(summary.keys())
     y=list(summary.values())
     plt.bar(x,y,color="orange",width=0.5)
     plt.title("Request Status / Number")
     plt.xlabel("Request Status")
     plt.ylabel("Number")
     return plt


def get_request():
     req=ServiceRequest.query.all()
     return req


if __name__ == "__main__":
    app.run()
