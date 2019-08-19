from config import mycolu
from werkzeug.security import safe_str_cmp


korisnici = list(mycolu.find())
#print(korisnici)


username_mapping = {u["username"]: u for u in korisnici} #F-JA ZA NALAZENJE USERA, TJ DA IZBACI SVE

userid_mapping = {u["password"]: u for u in korisnici}

def authenticate(username, password): #OVDJE NALAZIM USERA
    user = username_mapping.get(username, None)
    if user and safe_str_cmp(user["password"].encode('utf-8'), password.encode('utf-8')):
        return user

def identity(payload): #KROZ OVO PROVJERAVAM USER JEL TO TAJ KOJEG TRAZIM
    user_id = payload["identity"]
    return userid_mapping.get(user_id, None)