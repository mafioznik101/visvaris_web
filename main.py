from flask import Flask,render_template, request, flash
import sqlite3
import uuid
import bcrypt
import base64
#sqlite con sākums
#con.isolation_level = None


#klase, kur izveidosies lietotājs
class Lietotajaizveide:
    vards = None
    parole = None
    uuid = None
    email = None
    def __init__(self, vards, parole, email):
        self.uuid = str(uuid.uuid4()) #identifikators
        self.vards = vards
        self.parole = self.sifresana(parole)
        self.email = self.base64_sifresana(email)
        
    def base64_sifresana(self, email):
        sifrs1 = email.encode("ascii")
        base64_sifrs = base64.b64encode(sifrs1)
        return base64_sifrs.decode("ascii")
    
    def base64_atsifresana(self):
        sifrs2 = (self.email).encode("ascii")
        base64_atsifrs = base64.b64decode(sifrs2)
        return base64_atsifrs.decode("ascii")
    
    def sifresana(self, parole):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(parole.encode(), salt)
    
    def saglabat_db(self):
        try:
            con = sqlite3.connect("file:lietotaji.sqlite?mode=rw&cache=shared", uri=True")
            cur = con.cursor()
            cur.execute("INSERT INTO lietotaju_info (vards, parole, email, uuid) VALUES (?, ?, ?, ?)",(self.vards, self.parole, self.email, self.uuid),)
            con.commit()
            print(f"Lietotājs {self.vards} pievienots")
            con.close()
            return True
        except sqlite3.IntegrityError as kluda:
            if "UNIQUE constraint failed" in str(kluda):
                #print("Lietotājvārds ir aizņemts")
                return False
            else:
                print("Datubāzes kļūda")
    def parbaudit_db(self, parole_ievade):
      try:
         con = sqlite3.connect("file:lietotaji.sqlite?mode=rw&cache=shared", uri=True")
         cur = con.cursor()
         cur.execute("SELECT parole FROM lietotaju_info WHERE vards = ?",(self.vards,))
         db_parole = cur.fetchone()
         if db_parole is None:
            print("Lietotājvārds nav atrasts!")
            return False
         db_parole = db_parole[0]
         con.commit()
         # print("Self parole ievade:", parole_ievade)
         # print("DB parole:", db_parole)
         if bcrypt.checkpw(parole_ievade.encode(), db_parole):
            return True
         else:
            return False
      except:
         return False
      finally:
         con.close()
#klase lietotājs beigas   
salt = bcrypt.gensalt()   
app = Flask(__name__)
app.secret_key = bcrypt.hashpw(b"", salt)
#TEMPLATES_AUTO_RELOAD = True
@app.route("/izkartosanas", methods=["GET","POST"])
def izkartojums():
   lietotaja_vards = None
   if request.method == "POST":
      lietotaja_vards = request.form.get("tavsvards")
      #lietotaja_parole = request.form.get("psw")
      print(f"vaicājums login. lietotājs: {lietotaja_vards}")
      #if lietotaja_vards == 
   return render_template('izkartojums.html')


@app.route("/parmums")
def parmums():
   return render_template('parmums.html')

@app.route("/", methods=["GET","POST"])
def index():
   if request.method == "POST":
      lietotajparole = request.form.get("psw")
      lietotajvards = request.form.get("tavsvards")
      lietotajs = Lietotajaizveide(lietotajvards, lietotajparole, "email")
      if lietotajs.parbaudit_db(lietotajparole):
         flash("pieslēgšānās veiksmīga", "success")
         print("YAAA")
      else:
         flash("Nepareizs lietotājvārds vai parole!", "danger")
   return render_template('index.html')

@app.route("/register", methods=["GET","POST"])
def register():
   if request.method == "POST":
      lietotajvards = request.form.get("regvards")
      lietotajparole = request.form.get("regparole")
      lietotajemail = request.form.get("regepasts")
      jauns_lietotajs = Lietotajaizveide(lietotajvards, lietotajparole, lietotajemail)
      if jauns_lietotajs.saglabat_db():
         flash("Reģistrācija veiksmīga!", "success")
         print("YAAA")
      else:
         flash("Lietotājvārds jau aizņemts!", "danger")

   return render_template('register.html')
    
@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html'), 404
    
@app.route('/posts')
def renderThisPath():
  res = render_template('posts.html', 
                       some='variables',
                       you='want',
                       toPass=['to','your','template'])
  return res
# if __name__ == '__main__':  
#    app.run(debug = True)
#app.run(debug=True,host="0.0.0.0", port=80)
app.run(debug=False,host="0.0.0.0", port=80)
