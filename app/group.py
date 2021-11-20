from .config import mycolp,mycolu
import bson


def profit(username):
    user=mycolu.find_one({"username":username})
    #OVO RADIM DA SE OSIGURAM DA MI SE SLAZU ID-JEVI
    a=[]
    userproductlist=mycolp.find({"user":username})
    for i in userproductlist:
        a.append(str(i['_id']))
    mycolu.update_one({"username":username},{"$set":{"product":a}})
    output=[]
    for p in user["product"]:
        product=mycolp.find_one({'_id':bson.ObjectId(p)})
        output.append(product["price"]*product["quantity"])
    return sum(output)