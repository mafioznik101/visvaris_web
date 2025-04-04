from flask import Flask,render_template, request, flash, session, redirect, url_for
import sqlite3
import uuid
import bcrypt
import base64

#sqlite con sākums
#con.isolation_level = None
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
            con = sqlite3.connect("lietotaji.sqlite", check_same_thread=False)
            con.execute('pragma journal_mode=wal')
            cur = con.cursor()
            cur.execute("INSERT INTO lietotaju_info (vards, parole, email, uuid) VALUES (?, ?, ?, ?)",((self.vards).lower(), self.parole, (self.email).lower(), self.uuid),)
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
         con = sqlite3.connect("lietotaji.sqlite", check_same_thread=False)
         con.execute('pragma journal_mode=wal')
         cur = con.cursor()
         cur.execute("SELECT parole FROM lietotaju_info WHERE vards = ?",((self.vards).lower(),))
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
    def iegut_id(self):
       con = sqlite3.connect("lietotaji.sqlite", check_same_thread=False)
       con.execute('pragma journal_mode=wal')
       cur = con.cursor()
       cur.execute("SELECT uuid FROM lietotaju_info WHERE vards = ?",((self.vards).lower(),))
       id_lietotajs = (cur.fetchone())[0]
       if id_lietotajs == None:
         print(f"lietotāja kļūda : {self.vards}")
       else:
         return id_lietotajs
          
def loginosanas():
   lietotajparole = request.form.get("psw")
   lietotajvards = request.form.get("tavsvards")
   lietotajs = Lietotajaizveide(lietotajvards, lietotajparole, "email")
   if lietotajs.parbaudit_db(lietotajparole):
      flash("pieslēgšānās veiksmīga", "success")
      #print(lietotajs.iegut_id()) #iedo uuid no eksistējošā lietotāja sqlitā
      session['lietotaja_id'] = lietotajs.iegut_id()
      session['lietotaja_vards'] = lietotajvards
      session['ir_sessija'] = True
   else:
      flash("Nepareizs lietotājvārds vai parole!", "danger")
def regosanas():
   lietotajparole = request.form.get("regparole")
   lietotajvards = request.form.get("regvards")
   lietotajemail = request.form.get("regepasts")
   lietotajs = Lietotajaizveide(lietotajvards, lietotajparole, lietotajemail)
   if lietotajs.saglabat_db():
      print("Jauns users")
      flash("reģistrēšanās veiksmīga", "success")
   else:
      flash("Lietājvārds aizņemts", "danger")
   
#klase, kur izveidosies lietotājs
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


@app.route("/parmums", methods=["GET", "POST"])
def parmums():
   if request.method == "POST":
      loginosanas()
   return render_template('parmums.html')

@app.route("/", methods=["GET","POST"])
def index():
   if request.method == "POST":
      loginosanas()
   return render_template('index.html')

@app.route("/register", methods=["GET","POST"])
def register():
   if request.method == "POST":
      regosanas()

   return render_template('register.html')
    
@app.route('/delete')
def delete_email():
    session.pop('lietotaja_id', default=None)
    session.pop('ir_sessija', default=False)
    return redirect(url_for('index'))
   
      
@app.route('/posts', methods=["GET","POST"])
def posts():
   if request.method == "POST":
      loginosanas()
   if session.get('ir_sessija') == True:
      return render_template('posts.html')
   else:
      return redirect(url_for('index'))

@app.route('/profils', methods=["GET","POST"])
def profils():
   if request.method == "POST":
      loginosanas()
   if session.get('ir_sessija') == True:
      return render_template('profils.html')
   else:
      return redirect(url_for('index'))

#app.run(debug=True,host="0.0.0.0", port=80)
#app.run(debug=False,host="0.0.0.0", port=80)