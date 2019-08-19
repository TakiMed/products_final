from flask import Flask, render_template, request
from flask_mail import Mail, Message
import csv
import bson
from bson.objectid import ObjectId
app =Flask(__name__)
app.config['DEBUG']=True
app.config['TESTING']=False
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True
app.config['MAIL_USERNAME']='testninalogdts@gmail.com'
app.config['MAIL_PASSWORD']='TESTtest123.'
app.config['MAIL_DEFAULT_SENDER']='testninalogdts@gmail.com'
app.config['MAIL_MAX_EMAILS']=None
app.config['MAIL_ASCII_ATTACHMENTS']=False
mail=Mail(app)

def to_csv(my_dict):
    with open('New_product.csv', 'w') as f:
        for key in my_dict.keys():
            f.write("%s,%s\n"%(key,my_dict[key]))
    f.close()
    with open('New_product.csv','rb') as f:
        file_data=f.read()
        file_name=f.name
    return [file_name,file_data]
#@app.route('/mailing',methods=["POST"])
def mailing(my_dict,admin):
    data=to_csv(my_dict)[1]
    filename=to_csv(my_dict)[0]
    msg=Message('New product added',recipients=[admin["email"]],body="Please, find here attached new product added by:"+my_dict["user"])
    msg.attach(filename=filename,content_type='application/octet-stream',data=data,disposition=None,headers=None)
    mail.send(msg)
    return "Message sent!"

#app.run(debug=True, port=5000)