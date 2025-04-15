from flask import Flask,render_template, request, flash, session, redirect, url_for
import sqlite3
import uuid
import bcrypt
import base64
import validators
import datetime

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

class Publikacija:
    tituls = None
    posta_teksts = None
    bildes_saite = None
    user_id = None
    post_id = None
    def __init__(self, tituls, posta_teksts, bildes_saite, user_id):
        self.tituls = tituls
        self.posta_teksts = posta_teksts
        self.bildes_saite = bildes_saite
        self.user_id = user_id
        self.post_id = str(uuid.uuid4()) #identifikators
    def pievienot_post(self):
        try:
            con = sqlite3.connect("lietotaji.sqlite", check_same_thread=False)
            con.execute('pragma journal_mode=wal')
            cur = con.cursor()
            cur.execute("INSERT INTO posti (tituls, posta_teksts, bildes_saite, user_id, post_id, aktivs) VALUES (?, ?, ?, ?, ?, ?)",((self.tituls), self.posta_teksts, (self.bildes_saite), self.user_id, self.post_id, 1),)
            con.commit()
            return True
        except sqlite3.IntegrityError as kluda:
            if "UNIQUE constraint failed" in str(kluda):
                #print("posts nav sataisits")
                return False
            else:
                print("Datubāzes kļūda")
                return False
    def publikajicas_paradit(self):
        con = sqlite3.connect("lietotaji.sqlite", check_same_thread=False)
        con.execute('pragma journal_mode=wal')
        cur = con.cursor()
        cur.execute("SELECT * FROM posti")

class Komentars:
   def __init__(self, komentarateksts, uuid, post_id):
      self.komentarateksts = komentarateksts
      self.uuid = uuid
      self.post_id = post_id
   def pievienot_komentaru(self):
       try:
            con = sqlite3.connect("lietotaji.sqlite", check_same_thread=False)
            con.execute('pragma journal_mode=wal')
            cur = con.cursor()
            dt = datetime.datetime.now()
            laiks = dt.strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("INSERT INTO komentari (komentarateksts, uuid, post_id, datums) VALUES (?, ?, ?, ?)", (self.komentarateksts, self.uuid, self.post_id, laiks))
            con.commit()
            return True
       except sqlite3.IntegrityError as kluda:
            if "NOT NULL constraint failed" in str(kluda):
                #print("posts nav sataisits")
                return False
            else:
                print("Datubāzes kļūda")
                return False
       finally:
         con.close()
      
def get_publikacijas():
    con = sqlite3.connect("lietotaji.sqlite", check_same_thread=False)
    con.execute('pragma journal_mode=wal')
    cur = con.cursor()
    cur.execute("SELECT posti.tituls, posti.posta_teksts, posti.bildes_saite, posti.user_id, posti.post_id, lietotaju_info.vards FROM posti JOIN lietotaju_info ON posti.user_id = lietotaju_info.uuid")
    rows = cur.fetchall()
    con.close()
    return rows
 
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
      flash("Lietotājvārds aizņemts", "danger")
   
#klase, kur izveidosies lietotājs
#klase lietotājs beigas   
salt = bcrypt.gensalt()   
app = Flask(__name__)
app.secret_key = bcrypt.hashpw(b"", salt)
#TEMPLATES_AUTO_RELOAD = True
@app.route("/izkartosanas", methods=["GET","POST"])
def izkartojums():
   return render_template('izkartojums.html')

@app.route("/izkartosanas2", methods=["GET","POST"])
def izkartojums2():
   return render_template('izkartojums2.html')


@app.route("/parmums", methods=["GET", "POST"])
def parmums():
   if request.method == "POST":
      loginosanas()
   return render_template('parmums.html')

@app.route("/", methods=["GET","POST"])
def index():
   if request.method == "POST":
      loginosanas()
   dati = get_publikacijas()
   return render_template('index.html', dati=dati)

@app.route("/register", methods=["GET","POST"])
def register():
   if request.method == "POST":
      regosanas()
   return render_template('register.html')
    
@app.route('/delete')
def delete():
    session.pop('lietotaja_id', default=None)
    session.pop('ir_sessija', default=False)
    return redirect(url_for('index'))
   

@app.route('/posts', methods=["GET","POST"])
def posts():
   if request.method =='POST':
      teksts = request.form.get("publikacijasteksts")
      tituls = request.form.get("publikacijastituls")
      linksbilde = request.form.get("bildesaite")
      vai_saite = validators.url(linksbilde)
      if vai_saite and not linksbilde.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
         linksbilde = "https://media-hosting.imagekit.io/f36f5ddbea9349cc/nonefoto.png?Expires=1838783557&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=Favu3gN1SvNk~T26-J66rqlEyCVx-e1qTPKlahtL7sjWNrCQlV0EOx2Kz4YKS79~XwGahbS-A06WZdTxTpXzSm-75vyt13Q1QLLJVdbF0cu-aBdY5cGefY7892cRdQp85UGQt~Cg5g9vPLdmyV2inIhS1uQZEMNl7Fq8J6PhgK6HRAwXOwY25igsv2odd2gscIBVs-70hrp3IN4Dn-K6-CS6iLX4KZudajVjbQl5ck9zsvF6RlyiTy~jNrILtnU6ohh0FvPvenEdvUfWXt1cCZ2b3j~VU3QH9BxK0tMRE6AiFzJNfvDeiot~prG--ZUAKhdZwSbrJvgAWreZU0dQsg__"
      if linksbilde == "":
         linksbilde = "https://media-hosting.imagekit.io/f36f5ddbea9349cc/nonefoto.png?Expires=1838783557&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=Favu3gN1SvNk~T26-J66rqlEyCVx-e1qTPKlahtL7sjWNrCQlV0EOx2Kz4YKS79~XwGahbS-A06WZdTxTpXzSm-75vyt13Q1QLLJVdbF0cu-aBdY5cGefY7892cRdQp85UGQt~Cg5g9vPLdmyV2inIhS1uQZEMNl7Fq8J6PhgK6HRAwXOwY25igsv2odd2gscIBVs-70hrp3IN4Dn-K6-CS6iLX4KZudajVjbQl5ck9zsvF6RlyiTy~jNrILtnU6ohh0FvPvenEdvUfWXt1cCZ2b3j~VU3QH9BxK0tMRE6AiFzJNfvDeiot~prG--ZUAKhdZwSbrJvgAWreZU0dQsg__"
      lietotaja_posts = Publikacija(tituls, teksts, linksbilde, session['lietotaja_id']) #
      lietotaja_posts.pievienot_post()
      print(linksbilde)
      flash("publikācija ir ievietota", "success")
   if session.get('ir_sessija') == True:
      return render_template('posts.html')
   else:
      return redirect(url_for('index'))

@app.route('/publikacijaaa/<string:post_id>', methods=['GET', 'POST'])
def publikacijaa(post_id):
    con = sqlite3.connect("lietotaji.sqlite", check_same_thread=False)
    con.execute('pragma journal_mode=wal')
    cur = con.cursor()
    cur.execute('SELECT posti.tituls, posti.posta_teksts, posti.bildes_saite, posti.user_id, posti.post_id, lietotaju_info.vards FROM posti JOIN lietotaju_info ON posti.user_id = lietotaju_info.uuid WHERE posti.post_id = ?', (post_id,))
    dati = cur.fetchone()
    cur.execute('SELECT komentari.komentarateksts, komentari.datums, lietotaju_info.vards FROM komentari JOIN lietotaju_info ON komentari.uuid = lietotaju_info.uuid WHERE komentari.post_id = ?', (post_id,))
    komentarii = cur.fetchall()
    con.close()
    if request.method == 'POST':
        komentars = request.form.get('komentars')
        if komentars.strip():
            try:
                komentarssss = Komentars(komentars, session['lietotaja_id'], post_id)
                veiksme = komentarssss.pievienot_komentaru()
                if veiksme:
                    flash('Komentārs ir ievietots', 'success')
                else:
                    flash('Kļūda: komentāru nevarēja ievietot.', 'danger')
                return redirect(url_for('publikacijaa', post_id=post_id))
            except Exception as e:
                flash('Kļūda, pievienojot komentāru.', 'danger')
        else:
            flash('Komentārs ir tukšs', 'danger')
    if dati:
        return render_template('publikacijas.html', dati=dati, komentarii=komentarii)
    else:
        flash('404 kļūda! Publikācija nav atrasta.', 'error')
        return redirect(url_for('index'))
 
@app.route('/publikacijas', methods=['GET'])
def publikacijas():
    dati = get_publikacijas()
    return (dati)
 
@app.route('/profils', methods=["GET","POST"])
def profils():
   if request.method == "POST":
      loginosanas()
   if session.get('ir_sessija') == True:
      return render_template('profils.html')
   else:
      return redirect(url_for('index'))

#app.run(debug=True,host="0.0.0.0", port=80) # atkļūdošanai