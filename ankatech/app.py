from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import psycopg2
from psycopg2 import sql
import psycopg2
from psycopg2 import extras
import psycopg2.extras
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import traceback
import pickle
import numpy as np
from sklearn.preprocessing import LabelEncoder
from flask_cors import CORS
import hashlib
from sklearn.base import BaseEstimator
import smtplib
from flask import request, render_template


lbe = LabelEncoder()
app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key'

# Model dosyasını yükleme
try:
    with open("trained_model.sav", "rb") as file:
        model = pickle.load(file)
except FileNotFoundError:
    print("Model dosyası bulunamadı!")
    model = None

@app.route('/predict_case', methods=['POST'])
def predict_case():
    try:
        # Giriş verilerini al ve kontrol et
        dava_turu = int(request.form.get('dava_turu', 0))
        delil_durumu = int(request.form.get('delil_durumu', 0))
        tanik_sayisi = int(request.form.get('tanik_sayisi', 0))
        delil_sayisi = int(request.form.get('delil_sayisi', 0))
        hukuki_dayanak = int(request.form.get('hukuki_dayanak', 0))
        hukuki_temsil = int(request.form.get('hukuki_temsil', 0))
        onceki_davalar = int(request.form.get('onceki_davalar', 0))
        dava_suresi = int(request.form.get('dava_suresi', 0))
        hukuki_menfaat = int(request.form.get('hukuki_menfaat', 0))
        karmasiklik = int(request.form.get('karmasiklik', 0))
        yargi_durumu = int(request.form.get('yargi_durumu', 0))
        uzlasma = int(request.form.get('uzlasma', 0))
        uzman_gorus = int(request.form.get('uzman_gorus', 0))

        # Verileri modele uygun formata çevir
        input_data = np.array([[dava_turu, delil_durumu, tanik_sayisi, delil_sayisi, hukuki_dayanak, hukuki_temsil,
                                onceki_davalar, dava_suresi, hukuki_menfaat, karmasiklik, yargi_durumu, uzlasma, uzman_gorus]])

        # Model ile tahmin yap
        prediction = model.predict(input_data)
        result = {'prediction': 'Dava kazanılabilir' if prediction[0] == 1 else 'Dava kaybedilebilir'}

        return jsonify(result), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}),  400

    


def get_db_connection():
    try:
        connection = psycopg2.connect(
            host='localhost',
            port='5432',
            database='avukat-portali-db2',
            user='postgres',
            password='123'
        )
        return connection
    except psycopg2.Error as e:
        print(f"PostgreSQL bağlantı hatası: {e}")
        return None


    

@app.route('/')
def index():
   
 return render_template('index.html') 
import hashlib

# Giriş sayfası
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['userType']

        # Şifreyi MD5 ile hashle
        hashed_password = hashlib.md5(password.encode()).hexdigest()

        conn = get_db_connection()  # Veritabanı bağlantısını al
        if conn:
            cursor = conn.cursor()
            if user_type == 'avukat':
                # Avukatlar tablosu için sorgu
                cursor.execute(
                    """SELECT k.kullanici_id, k.kullanici_adi, k.ad, k.rol, k.eposta, a.sicil_no, a.avukat_id 
                    FROM kullanicilar k
                    JOIN avukatlar a ON k.kullanici_id = a.kullanici_id
                    WHERE k.kullanici_adi = %s AND k.sifre = %s""",
                    (username, hashed_password)
                )
            elif user_type == 'admin':
                # Admin tablosu için sorgu
                cursor.execute(
                    "SELECT kullanici_id, kullanici_adi, ad, rol, eposta FROM kullanicilar WHERE kullanici_adi = %s AND sifre = %s",
                    (username, hashed_password)
                )
            else:
                # Kullanıcılar tablosu için sorgu
                cursor.execute(
                    "SELECT kullanici_id, kullanici_adi, ad, rol, eposta FROM kullanicilar WHERE kullanici_adi = %s AND sifre = %s",
                    (username, hashed_password)
                )

            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user:
                # Kullanıcı türüne göre oturum verisi ayarı
                session['user_id'] = user[0]  # Kullanıcı ID
                session['username'] = user[1]  # Kullanıcı adı
                session['ad'] = user[2]  # Kullanıcı adı ve soyadı
                session['user_type'] = user[3]  # Rol bilgisi ("avukat", "admin", vs.)
                session['email'] = user[4]  # E-posta

                if user_type == 'avukat':
                    session['sicil_no'] = user[5]  # Sicil numarası
                    session['avukat_id'] = user[6]  # Avukat ID

                flash('Giriş başarılı!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Kullanıcı adı veya şifre hatalı.', 'danger')

    return render_template('login.html')
from flask import request, jsonify
import psycopg2

@app.route('/create_meeting', methods=['POST'])
def create_meeting():
    try:
        data = request.get_json()
        avukat_id = data['avukat_id']
        kullanici_id = data['kullanici_id']
        mesaj = data['mesaj']
        tarih = data['tarih']
        
        # Database bağlantısı
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Görüşme kaydını ekleme
        cur.execute("""
            INSERT INTO gorusmeler (avukat_id, kullanici_id, mesaj, tarih)
            VALUES (%s, %s, %s, %s)
        """, (avukat_id, kullanici_id, mesaj, tarih))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({"message": "Görüşme başarıyla oluşturuldu!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/gorusmeler', methods=['GET'])
def gorusmeler():
    try:
        avukat_id = session.get('user_id')  # Avukat ID'yi session'dan al
        if not avukat_id:
            return redirect(url_for('login'))  # Eğer avukat giriş yapmadıysa login sayfasına yönlendir

        # Database bağlantısı
        conn = get_db_connection()
        cur = conn.cursor()

        # Görüşmeleri çek
        cur.execute("""
            SELECT kullanici_id, mesaj, tarih
            FROM gorusmeler
            WHERE avukat_id = %s
            ORDER BY tarih DESC
        """, (avukat_id,))
        gorusmeler = cur.fetchall()
        cur.close()
        conn.close()

        # Görüşmeleri HTML'e gönder
        return render_template('gorusmeler.html', gorusmeler=[{
            'kullanici_id': row[0],
            'mesaj': row[1],
            'tarih': row[2]
        } for row in gorusmeler])
    except Exception as e:
        return str(e), 500

#register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        username = request.form['registerUsername']
        password = request.form['registerPassword']
        e_mail=request.form['email']
        user_type = request.form['registerUserType']
        hashed_password = hashlib.md5(password.encode()).hexdigest()

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()

            # Kullanıcı türüne göre farklı işlemler
            if user_type == 'avukat':
                sicil_no = request.form['sicilNo']
                baro_id = request.form['baroId']
                #uzmanlik_id = request.form['uzmanlikId']
                
                # Uzmanlık alanı eşleme
                uzmanlik_mapping = {
                    "familyLaw": 1,
                    "criminalLaw": 2,
                    "workteLaw": 3,
                    "tradeLaw": 4
                }

                # Formdan gelen uzmanlık değerini eşleme ile ID'ye çevir
                uzmanlik_key = request.form['uzmanlikId']  # Örneğin "familyLaw"
                uzmanlik_id = uzmanlik_mapping.get(uzmanlik_key, 1)#yoksa 1 atayacak

                if uzmanlik_id is None:
                    flash('Geçersiz uzmanlık alanı seçimi.', 'danger')
                    return redirect(url_for('register'))

                
                # Baro ID mevcut mu kontrol et
                cursor.execute("SELECT baro_id FROM barolar WHERE baro_id = %s", (baro_id,))
                baro = cursor.fetchone()
                
                if not baro:
                    flash('Geçerli bir Baro ID giriniz.', 'danger')
                    return redirect(url_for('register'))

                # Avukatlar tablosuna veri ekleyelim
                cursor.execute(
                    """INSERT INTO kullanicilar (ad, soyad, eposta, sifre, rol, kullanici_adi) 
                    VALUES (%s, %s, %s, %s, %s, %s)""",
                    (first_name, last_name,e_mail, hashed_password, user_type, username)
                )
                # Kullanıcının ID sini alma
                cursor.execute("SELECT kullanici_id FROM kullanicilar WHERE kullanici_adi = %s", (username,))
                result = cursor.fetchone()
                # cursor.execute("SELECT kullanici_id FROM kullanicilar WHERE eposta = %s", (e_mail,))
                # result = cursor.fetchone()
                if result:
                    kullanici_id = result[0]
                else:
                     flash("Kullanıcı ID alınamadı!", "danger")
                     return redirect(url_for("register"))
                # Avukat tablosuna veri ekleme
                cursor.execute(                    
                    """INSERT INTO avukatlar (kullanici_id,sicil_no, baro_id) 
                    VALUES (%s, %s, %s)""",
                    (kullanici_id, sicil_no, baro_id)

                )
                
                # # Yeni eklenen avukatın id'sini al
                cursor.execute("SELECT avukat_id FROM avukatlar WHERE sicil_no = %s", (sicil_no,))
                avukat_id = cursor.fetchone()[0]
                
                # Uzmanlık alanını ekle
                cursor.execute("INSERT INTO avukat_uzmanlik (avukat_id, uzmanlik_id) VALUES (%s, %s)", 
                               (avukat_id, uzmanlik_id))
        
            else:
                # Normal kullanıcı ekle
                cursor.execute(
                    """INSERT INTO kullanicilar (ad, soyad, kullanici_adi, eposta, sifre, rol) 
                    VALUES (%s, %s, %s, %s, %s, %s)""",
                    (first_name, last_name, username, e_mail, hashed_password, user_type)
                )

            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Kayıt başarılı! Giriş yapmayı deneyin.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Veritabanına bağlanılamadı.', 'danger')

    # Uzmanlık alanlarını almak
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM uzmanlik_alanlari")
    uzmanliklar = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('register.html', uzmanliklar=uzmanliklar)


#Log Out
@app.route('/logout')
def logout():
    session.pop('username', None)  # Oturumdan kullanıcı adını kaldır
    session.pop('sicil_no', None)  # Sicil numarasını session'dan kaldır
    session.pop('user_type', None)  # Kullanıcı tipi oturumdan kaldır
    flash('Çıkış başarılı!', 'success')  # Başarı mesajı
    return redirect(url_for('index'))  # Anasayfaya yönlendir

# Diğer sayfa rotaları
@app.route('/hakkımızda')
def hakkımızda():
    return render_template('hakkımızda.html')

@app.route('/sss')
def sss():
    return render_template('sss.html')

@app.route('/yapayzeka')
def yapayzeka():
    return render_template('yapayzeka.html')



# Avukat ilanlarını listeleme
@app.route('/avukat')
def avukat():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                a.avukat_id,
                k.ad AS ad,
                k.soyad AS soyad,
                a.sicil_no,
                i.deneyim_yili,
                i.bolum,
                i.ilan_metni
            FROM ilanlar i
            JOIN avukatlar a ON i.avukat_id = a.avukat_id
            JOIN kullanicilar k ON a.kullanici_id = k.kullanici_id
        """)
        ilanlar = cursor.fetchall()
        cursor.close()
        conn.close()

        # Veriyi kontrol etme (isteğe bağlı)
        print(ilanlar)

        return render_template('avukat.html', ilanlar=ilanlar)
    else:
        flash('Veritabanına bağlanılamadı.', 'danger')
        return render_template('avukat.html', ilanlar=[])

# İlan ekleme


@app.route('/ilan', methods=['GET', 'POST'])
def ilan():
    avukat_id = request.args.get('avukat_id')
    conn = get_db_connection()
    ilanlar = []
    mesaj = None
    
    if conn:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        if request.method == 'POST':
            try:
                print(f"İlan ekleme işlemi başlatılıyor - Avukat ID: {avukat_id}")
                deneyim_yili = request.form.get('deneyim_yili')
                bolum = request.form.get('bolum')
                ilan_metni = request.form.get('ilan_metni')

                cursor.execute("""
                    INSERT INTO ilanlar (avukat_id, deneyim_yili, bolum, ilan_metni)
                    VALUES (%s, %s, %s, %s)
                """, (avukat_id, deneyim_yili, bolum, ilan_metni))
                conn.commit()
                mesaj = "İlan başarıyla oluşturuldu."
                print("İlan başarıyla eklendi")
                
            except psycopg2.Error as e:
                conn.rollback()
                hata_mesaji = str(e)
                print(f"Hata oluştu: {hata_mesaji}")
                
                if "Maksimum 5 ilan oluşturabilirsiniz" in hata_mesaji:
                    mesaj = "Maksimum ilan sayısına ulaştınız. Daha fazla ilan oluşturamazsınız."
                    try:
                        print("Bildirim ekleme işlemi başlatılıyor...")
                        bildirim_mesaji = f"Avukat (ID: {avukat_id}) maksimum ilan sayısını (5) aşmaya çalıştı. İlan oluşturma işlemi reddedildi."
                        
                        # Debug için SQL sorgusunu yazdır
                        print(f"SQL: CALL kaydet_ilan_bildirimi({avukat_id}, '{bildirim_mesaji}')")
                        
                        cursor.execute("""
                            CALL kaydet_ilan_bildirimi(%s, %s);
                        """, (avukat_id, bildirim_mesaji))
                        
                        conn.commit()
                        print("Bildirim başarıyla eklendi")
                        
                    except psycopg2.Error as bildirim_hatasi:
                        print(f"Bildirim eklenirken hata oluştu: {bildirim_hatasi}")
                        conn.rollback()
                else:
                    mesaj = "İlan oluşturulurken bir hata oluştu."
                    print(f"Beklenmeyen hata: {hata_mesaji}")

        # Mevcut ilanları çekme
        cursor.execute("""
            SELECT 
                i.ilan_id,
                a.avukat_id,
                k.ad,
                k.soyad,
                a.sicil_no,
                i.deneyim_yili,
                i.bolum,
                i.ilan_metni
            FROM ilanlar i
            JOIN avukatlar a ON i.avukat_id = a.avukat_id
            JOIN kullanicilar k ON a.kullanici_id = k.kullanici_id
            WHERE a.avukat_id = %s
        """, (avukat_id,))
        ilanlar = cursor.fetchall()
        
        # Debug için bildirimler tablosunu kontrol et
        try:
            cursor.execute("""
                SELECT * FROM bildirimler 
                WHERE avukat_id = %s 
                ORDER BY olusturma_tarihi DESC 
                LIMIT 5
            """, (avukat_id,))
            son_bildirimler = cursor.fetchall()
            print("Son bildirimler:", son_bildirimler)
        except psycopg2.Error as e:
            print(f"Bildirimleri kontrol ederken hata: {e}")
            
        conn.close()

    return render_template('ilan.html', ilanlar=ilanlar, avukat_id=avukat_id, mesaj=mesaj)



#iletisime geç kısmı
def contact():
    if request.method == 'POST':
        email = request.form['email']
        # E-posta ile ilgili işlemleri burada yapın (örneğin, veritabanına kaydetme veya e-posta gönderme)
        return redirect(url_for('thank_you'))  # Teşekkür sayfasına yönlendirme
    return render_template('contact.html')
@app.route('/thank-you')
def thank_you():
    return "Teşekkürler! Mesajınız alınmıştır."
import psycopg2
from psycopg2 import extras

@app.route('/iletisim', methods=['GET', 'POST'])
def iletisim():
    avukat_id = request.args.get('avukat_id')  # URL'den avukat_id al
    eposta = ''
    ilan_id = request.args.get('ilan_id', '')

    if avukat_id:
        conn = get_db_connection()
        if conn:
            try:
                # DictCursor kullanarak sonuçları sözlük formatında al
                cursor = conn.cursor(cursor_factory=extras.DictCursor)
                
                # İlk olarak avukat_id ile kullanici_id'yi çek
                cursor.execute("SELECT kullanici_id FROM avukatlar WHERE avukat_id = %s", (avukat_id,))
                avukat = cursor.fetchone()
                
                if avukat:
                    kullanici_id = avukat['kullanici_id']
                    
                    # Şimdi kullanici tablosundan e-posta adresini al
                    cursor.execute("SELECT eposta FROM kullanicilar WHERE kullanici_id = %s", (kullanici_id,))
                    kullanici = cursor.fetchone()
                    
                    if kullanici:
                        eposta = kullanici['eposta']

            except Exception as e:
                print(f"Database error: {e}")
            finally:
                cursor.close()
                conn.close()

    if request.method == 'POST':
        # Burada e-posta gönderme işlemleri yapılabilir
        pass

    return render_template('iletisim.html', eposta=eposta)


# Asistan sayfası
@app.route('/asistan')
def asistan():
    return render_template('asistan.html')

# E-Mail servisi
@app.route('/send_email', methods=['POST'])
def send_email():
    ad = request.form['ad']
    soyad = request.form['soyad']
    adres = request.form['adres']
    kullanici_email = request.form['kullanici_e-posta']
    avukat_email = request.form['email']
    randevu_tarihi = request.form['randevu_tarihi']
    mesaj = request.form['mesaj']

    # Yandex SMTP ayarları
    yandex_email = 'huaweiargekodlama@yandex.com'  # Yandex e-posta adresiniz
    yandex_password = 'vxnzekvivqjrisne'  # Yandex uygulama şifreniz

    # E-posta içeriği oluşturma
    msg = MIMEMultipart()
    msg['From'] = yandex_email
    msg['To'] = avukat_email
    msg['Subject'] = 'Avukatınız ile iletişime geçin'  # Dinamik başlık

    body = f'''
    <p><strong>Ad:</strong> {ad}</p>
    <p><strong>Soyad:</strong> {soyad}</p>
    <p><strong>Adres:</strong> {adres}</p>
    <p><strong>Kullanıcı E-posta:</strong> {kullanici_email}</p>
    <p><strong>Randevu Tarihi:</strong> {randevu_tarihi}</p>
    <p><strong>Mesaj:</strong> {mesaj}</p>
    '''
    msg.attach(MIMEText(body, 'html'))

    try:
        # Yandex SMTP sunucusuna bağlan
        server = smtplib.SMTP_SSL('smtp.yandex.com', 465)  # SSL kullanarak bağlantı
        server.login(yandex_email, yandex_password)  # Giriş yap
        server.send_message(msg)  # E-postayı gönder
        server.quit()  # Bağlantıyı kapat
        return 'E-posta başarıyla gönderildi!', 200
    except Exception as e:
        print(f"Hata: {e}")
        return f"E-posta gönderilemedi! Hata: {e}", 500
    
#profil 
@app.route('/profil')
def profil():
    print ("hi")
    return render_template('profil.html')

#Admin_Panel
@app.route('/admin_panel',methods=['GET', 'POST'])
def admin_panel():
    
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))  # Yetkisi olmayan kullanıcıları yönlendir
    conn = get_db_connection()
    if conn:
            cursor = conn.cursor()
            # buraya işlemler
    else:
        flash('Veritabanına bağlanılamadı.', 'danger')    
    return render_template('admin_panel.html')

#admin panel
@app.route('/try')
def trye():
    conn = get_db_connection()
    
    if conn:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Toplam Kullanıcı Sayısı
        cursor.execute("SELECT COUNT(*) FROM kullanicilar")
        toplam_kullanici = cursor.fetchone()[0]
        
        # Avukat Sayısı
        cursor.execute("SELECT COUNT(*) FROM avukatlar")
        avukat_sayisi = cursor.fetchone()[0]
        
        # Baro Sayısı
        cursor.execute("SELECT COUNT(*) FROM barolar")
        baro_sayisi = cursor.fetchone()[0]
        
        # İlan Sayısı
        cursor.execute("SELECT COUNT(*) FROM ilanlar")
        ilan_sayisi = cursor.fetchone()[0]
        
        # İlanlar Verisini Çekme
        cursor.execute("""
            SELECT 
                i.ilan_id,
                a.avukat_id,
                k.ad,
                k.soyad,
                a.sicil_no,
                i.deneyim_yili,
                i.bolum,
                i.ilan_metni
            FROM ilanlar i
            JOIN avukatlar a ON i.avukat_id = a.avukat_id
            JOIN kullanicilar k ON a.kullanici_id = k.kullanici_id
        """)
        ilanlar = cursor.fetchall()
        ilanlar = [dict(row) for row in ilanlar]
        
        cursor.close()
        conn.close()
        
        return render_template('try.html',
                             toplam_kullanici=toplam_kullanici,
                             avukat_sayisi=avukat_sayisi,
                             baro_sayisi=baro_sayisi,
                             ilan_sayisi=ilan_sayisi,
                             ilanlar=ilanlar)
    else:
        return render_template('try.html')

@app.route('/get_ilanlar')
def get_ilanlar():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""
            SELECT 
                i.ilan_id,
                a.avukat_id,
                k.ad,
                k.soyad,
                a.sicil_no,
                i.deneyim_yili,
                i.bolum,
                i.ilan_metni
            FROM ilanlar i
            JOIN avukatlar a ON i.avukat_id = a.avukat_id
            JOIN kullanicilar k ON a.kullanici_id = k.kullanici_id
        """)
        ilanlar = cursor.fetchall()
        
        # Sözlük listesine dönüştürme
        ilanlar = [dict(row) for row in ilanlar]
        
        cursor.close()
        conn.close()

        return jsonify({'ilanlar': ilanlar})
    return jsonify({'error': 'Veritabanı bağlantısı sağlanamadı.'}), 500


@app.route('/edit_ilan/<int:ilan_id>', methods=['GET', 'POST'])
def edit_ilan(ilan_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    if request.method == 'GET':
        # İlan bilgilerini çek
        cur.execute("""
            SELECT 
                i.ilan_id,
                i.avukat_id,
                k.ad,
                k.soyad,
                a.sicil_no,
                i.deneyim_yili,
                i.bolum,
                i.ilan_metni
            FROM ilanlar i
            JOIN avukatlar a ON i.avukat_id = a.avukat_id
            JOIN kullanicilar k ON a.kullanici_id = k.kullanici_id
            WHERE i.ilan_id = %s
        """, (ilan_id,))
        ilan_data = cur.fetchone()
        
        if ilan_data is None:
            flash('İlan bulunamadı.', 'error')
            return redirect(url_for('trye'))
        
        ilan = {
            'ilan_id': ilan_data['ilan_id'],
            'avukat_id': ilan_data['avukat_id'],
            'ad': ilan_data['ad'],
            'soyad': ilan_data['soyad'],
            'sicil_no': ilan_data['sicil_no'],
            'deneyim_yili': ilan_data['deneyim_yili'],
            'bolum': ilan_data['bolum'],
            'ilan_metni': ilan_data['ilan_metni']
        }
        
        cur.close()
        conn.close()
        
        return render_template('edit_ilan.html', ilan=ilan)
        
    elif request.method == 'POST':
        try:
            deneyim_yili = request.form['deneyim_yili']
            bolum = request.form['bolum']
            ilan_metni = request.form['ilan_metni']
            
            cur.execute("""
                UPDATE ilanlar
                SET deneyim_yili = %s, bolum = %s, ilan_metni = %s
                WHERE ilan_id = %s
            """, (deneyim_yili, bolum, ilan_metni, ilan_id))
            
            conn.commit()
            flash('İlan başarıyla güncellendi.', 'success')
            return redirect(url_for('trye'))
            
        except Exception as e:
            conn.rollback()
            flash(f'Güncelleme sırasında bir hata oluştu: {str(e)}', 'error')
            return redirect(url_for('edit_ilan', ilan_id=ilan_id))
        finally:
            cur.close()
            conn.close()

@app.route('/delete_ilan/<int:ilan_id>', methods=['POST'])
def delete_ilan(ilan_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    try:
        cur.execute("DELETE FROM ilanlar WHERE ilan_id = %s", (ilan_id,))
        conn.commit()
        flash('İlan başarıyla silindi.', 'success')
        return redirect(url_for('trye'))
        
    except Exception as e:
        conn.rollback()
        flash(f'Silme işlemi sırasında bir hata oluştu: {str(e)}', 'error')
        return redirect(url_for('trye'))
    finally:
        cur.close()
        conn.close()
@app.route('/get_bildirimler')
def get_bildirimler():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""
            SELECT 
                b.bildirim_id,
                b.avukat_id,
                b.bildirim_mesaji,
                b.okundu,
                b.olusturma_tarihi,
                k.ad,
                k.soyad
            FROM bildirimler b
            JOIN avukatlar a ON b.avukat_id = a.avukat_id
            JOIN kullanicilar k ON a.kullanici_id = k.kullanici_id
            ORDER BY b.olusturma_tarihi DESC
        """)
        bildirimler = cursor.fetchall()
        
        # Convert to list of dictionaries
        bildirimler = [{
            'bildirim_id': b['bildirim_id'],
            'avukat_id': b['avukat_id'],
            'bildirim_mesaji': b['bildirim_mesaji'],
            'okundu': b['okundu'],
            'olusturma_tarihi': b['olusturma_tarihi'].strftime("%d-%m-%Y %H:%M"),
            'avukat_adi': f"{b['ad']} {b['soyad']}"
        } for b in bildirimler]
        
        cursor.close()
        conn.close()
        return jsonify({'bildirimler': bildirimler})
    return jsonify({'error': 'Veritabanı bağlantısı sağlanamadı.'}), 500

@app.route('/mark_notification_read/<int:bildirim_id>', methods=['POST'])
def mark_notification_read(bildirim_id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE bildirimler 
                SET okundu = TRUE 
                WHERE bildirim_id = %s
            """, (bildirim_id,))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Veritabanı bağlantısı sağlanamadı.'}), 500

@app.route('/clients')
def clients():
    conn = get_db_connection()
    if conn:
        # DictCursor kullanılarak verilerin sözlük formatında alınması sağlanır
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Avukatları ve ilgili bilgileri çekme
        cursor.execute("""
            SELECT 
                a.avukat_id,
                k.ad,
                k.soyad,
                a.sicil_no,
                b.baro_adi,
                array_agg(u.uzmanlik_adi) AS uzmanliklar
            FROM avukatlar a
            JOIN kullanicilar k ON a.kullanici_id = k.kullanici_id
            JOIN barolar b ON a.baro_id = b.baro_id
            LEFT JOIN avukat_uzmanlik au ON a.avukat_id = au.avukat_id
            LEFT JOIN uzmanlik_alanlari u ON au.uzmanlik_id = u.uzmanlik_id
            GROUP BY a.avukat_id, k.ad, k.soyad, a.sicil_no, b.baro_adi
        """)
        avukatlar = cursor.fetchall()

        # Sözlük listesine dönüştürülmüş veri
        avukatlar = [dict(row) for row in avukatlar]

        cursor.close()
        conn.close()

        return render_template('try.html', avukatlar=avukatlar)
    return render_template('try.html')
@app.route('/get_users')
def get_users():
    search_term = request.args.get('search', '')
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            if search_term:
                cursor.execute("SELECT * FROM search_users(%s)", (search_term,))
            else:
                cursor.execute("SELECT * FROM kullanici_listesi")
            users = cursor.fetchall()
            
            users = [{
                'kullanici_id': user['kullanici_id'],
                'ad': user['ad'],
                'soyad': user['soyad'],
                'eposta': user['eposta'],
                'rol': user['rol'],
                'kullanici_adi': user['kullanici_adi'],
                'kullanici_tipi': user['kullanici_tipi'],
                'sicil_no': user['sicil_no']
            } for user in users]
            
            return jsonify({'users': users})
        finally:
            cursor.close()
            conn.close()
    return jsonify({'error': 'Veritabanı bağlantısı sağlanamadı.'}), 500

@app.route('/update_user', methods=['POST'])
def update_user():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            data = request.json
            cursor.execute("""
                UPDATE kullanicilar 
                SET ad = %s, soyad = %s, eposta = %s, kullanici_adi = %s
                WHERE kullanici_id = %s
                """, (data['ad'], data['soyad'], data['eposta'], 
                      data['kullanici_adi'], data['kullanici_id']))
            conn.commit()
            return jsonify({'success': True})
        except Exception as e:
            conn.rollback()
            return jsonify({'error': str(e)}), 500
        finally:
            cursor.close()
            conn.close()
    return jsonify({'error': 'Veritabanı bağlantısı sağlanamadı.'}), 500

@app.route('/delete_user/<int:kullanici_id>', methods=['POST'])
def delete_user(kullanici_id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Önce avukatlar tablosundan silme
            cursor.execute("DELETE FROM avukatlar WHERE kullanici_id = %s", (kullanici_id,))
            # Sonra kullanicilar tablosundan silme
            cursor.execute("DELETE FROM kullanicilar WHERE kullanici_id = %s", (kullanici_id,))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'success': True})
        except Exception as e:
            conn.rollback()
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Veritabanı bağlantısı sağlanamadı.'}), 500

@app.route('/edit_avukat/<int:avukat_id>', methods=['GET', 'POST'])

def edit_avukat(avukat_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    if request.method == 'GET':
        # Ana avukat bilgilerini çek
        cur.execute("""
            SELECT 
                a.avukat_id,
                k.ad,
                k.soyad,
                a.sicil_no,
                b.baro_id,
                b.baro_adi,
                array_agg(ua.uzmanlik_adi) as uzmanliklar
            FROM avukatlar a
            JOIN kullanicilar k ON a.kullanici_id = k.kullanici_id
            JOIN barolar b ON a.baro_id = b.baro_id
            LEFT JOIN avukat_uzmanlik au ON a.avukat_id = au.avukat_id
            LEFT JOIN uzmanlik_alanlari ua ON au.uzmanlik_id = ua.uzmanlik_id
            WHERE a.avukat_id = %s
            GROUP BY a.avukat_id, k.ad, k.soyad, a.sicil_no, b.baro_id, b.baro_adi
        """, (avukat_id,))
        avukat_data = cur.fetchone()
        
        # Veriyi kontrol et
        if avukat_data is None:
            flash('Avukat bulunamadı.', 'error')
            return redirect(url_for('trye'))
        
        # Eğer DictCursor çalışıyorsa sözlük döner, yoksa tuple döner
        try:
            avukat = {
                'avukat_id': avukat_data['avukat_id'],
                'ad': avukat_data['ad'],
                'soyad': avukat_data['soyad'],
                'sicil_no': avukat_data['sicil_no'],
                'baro_adi': avukat_data['baro_adi'],
                'uzmanliklar': avukat_data['uzmanliklar'] if avukat_data['uzmanliklar'][0] is not None else []
            }
        except (KeyError, TypeError):
            avukat = {
                'avukat_id': avukat_data[0],
                'ad': avukat_data[1],
                'soyad': avukat_data[2],
                'sicil_no': avukat_data[3],
                'baro_adi': avukat_data[5],
                'uzmanliklar': avukat_data[6] if avukat_data[6][0] is not None else []
            }

        # Tüm baroları çek
        cur.execute("SELECT baro_id, baro_adi FROM barolar ORDER BY baro_adi")
        barolar = [dict(row) for row in cur.fetchall()]

        # Tüm uzmanlık alanlarını çek
        cur.execute("SELECT uzmanlik_adi FROM uzmanlik_alanlari ORDER BY uzmanlik_adi")
        tum_uzmanliklar = [row['uzmanlik_adi'] for row in cur.fetchall()]

        cur.close()
        conn.close()

        return render_template('edit_avukat.html', 
                             avukat=avukat, 
                             barolar=barolar, 
                             tum_uzmanliklar=tum_uzmanliklar)

    elif request.method == 'POST':
        try:
            # Form verilerini al
            ad = request.form['ad']
            soyad = request.form['soyad']
            sicil_no = request.form['sicil_no']
            baro_adi = request.form['baro_adi']
            uzmanliklar = request.form.getlist('uzmanliklar')

            # Baro ID'sini bul
            cur.execute("SELECT baro_id FROM barolar WHERE baro_adi = %s", (baro_adi,))
            baro_result = cur.fetchone()
            if baro_result is None:
                raise ValueError("Geçersiz baro adı")
            baro_id = baro_result['baro_id']

            # Avukatın kullanici_id'sini bul
            cur.execute("SELECT kullanici_id FROM avukatlar WHERE avukat_id = %s", (avukat_id,))
            kullanici_data = cur.fetchone()
            if kullanici_data is None:
                raise ValueError("Avukat bulunamadı")
            kullanici_id = kullanici_data['kullanici_id']

            # Kullanıcı bilgilerini güncelle
            cur.execute("""
                UPDATE kullanicilar
                SET ad = %s, soyad = %s
                WHERE kullanici_id = %s
            """, (ad, soyad, kullanici_id))

            # Avukat bilgilerini güncelle
            cur.execute("""
                UPDATE avukatlar
                SET sicil_no = %s, baro_id = %s
                WHERE avukat_id = %s
            """, (sicil_no, baro_id, avukat_id))

            # Uzmanlıkları güncelle
            cur.execute("DELETE FROM avukat_uzmanlik WHERE avukat_id = %s", (avukat_id,))
            
            if uzmanliklar:  # Eğer uzmanlık seçildiyse
                for uzmanlik in uzmanliklar:
                    cur.execute("""
                        INSERT INTO avukat_uzmanlik (avukat_id, uzmanlik_id)
                        SELECT %s, uzmanlik_id 
                        FROM uzmanlik_alanlari 
                        WHERE uzmanlik_adi = %s
                    """, (avukat_id, uzmanlik))

            conn.commit()
            flash('Avukat bilgileri başarıyla güncellendi.', 'success')
            return redirect(url_for('trye'))

        except ValueError as e:
            conn.rollback()
            flash(f'Geçersiz veri: {str(e)}', 'error')
            return redirect(url_for('edit_avukat', avukat_id=avukat_id))
        except Exception as e:
            conn.rollback()
            flash(f'Güncelleme sırasında bir hata oluştu: {str(e)}', 'error')
            return redirect(url_for('edit_avukat', avukat_id=avukat_id))
        finally:
            cur.close()
            conn.close()


@app.route('/delete_avukat/<int:avukat_id>', methods=['POST'])
def delete_avukat(avukat_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    try:
        # Önce avukatın kullanici_id'sini alalım
        cur.execute("SELECT kullanici_id FROM avukatlar WHERE avukat_id = %s", (avukat_id,))
        kullanici_data = cur.fetchone()
        
        if kullanici_data is None:
            raise ValueError("Avukat bulunamadı")
            
        kullanici_id = kullanici_data['kullanici_id']
        
        # İlişkili kayıtları silelim
        cur.execute("DELETE FROM avukat_uzmanlik WHERE avukat_id = %s", (avukat_id,))
        cur.execute("DELETE FROM ilanlar WHERE avukat_id = %s", (avukat_id,))
        cur.execute("DELETE FROM avukatlar WHERE avukat_id = %s", (avukat_id,))
        cur.execute("DELETE FROM kullanicilar WHERE kullanici_id = %s", (kullanici_id,))
        
        conn.commit()
        flash('Avukat başarıyla silindi.', 'success')
        return redirect(url_for('trye'))
        
    except Exception as e:
        conn.rollback()
        flash(f'Silme işlemi sırasında bir hata oluştu: {str(e)}', 'error')
        return redirect(url_for('edit_avukat', avukat_id=avukat_id))
    finally:
        cur.close()
        conn.close()

# Baro işlemleri admin sayfasındaki 
@app.route('/get_barolar')
def get_barolar():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""
            SELECT 
                b.baro_id,
                b.baro_adi,
                b.sehir,
                COALESCE(k.ad || ' ' || k.soyad, 'Atanmamış') as baskan_adi
            FROM barolar b
            LEFT JOIN avukatlar a ON b.baskani_avukat_id = a.avukat_id
            LEFT JOIN kullanicilar k ON a.kullanici_id = k.kullanici_id
            ORDER BY b.baro_adi
        """)
        barolar = cursor.fetchall()
        barolar = [dict(row) for row in barolar]
        cursor.close()
        conn.close()
        return jsonify({'barolar': barolar})
    return jsonify({'error': 'Veritabanı bağlantısı sağlanamadı.'}), 500

@app.route('/edit_baro/<int:baro_id>', methods=['GET', 'POST'])
def edit_baro(baro_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    if request.method == 'GET':
        # Baro bilgilerini çek
        cur.execute("""
            SELECT 
                b.baro_id,
                b.baro_adi,
                b.sehir,
                b.baskani_avukat_id,
                COALESCE(k.ad || ' ' || k.soyad, 'Atanmamış') as baskan_adi
            FROM barolar b
            LEFT JOIN avukatlar a ON b.baskani_avukat_id = a.avukat_id
            LEFT JOIN kullanicilar k ON a.kullanici_id = k.kullanici_id
            WHERE b.baro_id = %s
        """, (baro_id,))
        baro = dict(cur.fetchone())
        
        # Avukatları çek (baro başkanı seçimi için)
        cur.execute("""
            SELECT 
                a.avukat_id,
                k.ad || ' ' || k.soyad as tam_ad
            FROM avukatlar a
            JOIN kullanicilar k ON a.kullanici_id = k.kullanici_id
            ORDER BY k.ad, k.soyad
        """)
        avukatlar = cur.fetchall()
        
        cur.close()
        conn.close()
        return render_template('edit_baro.html', baro=baro, avukatlar=avukatlar)
        
    elif request.method == 'POST':
        try:
            baro_adi = request.form['baro_adi']
            sehir = request.form['sehir']
            baskan_id = request.form['baskan_id'] if request.form['baskan_id'] != '' else None
            
            cur.execute("""
                UPDATE barolar
                SET baro_adi = %s, sehir = %s, baskani_avukat_id = %s
                WHERE baro_id = %s
            """, (baro_adi, sehir, baskan_id, baro_id))
            
            conn.commit()
            flash('Baro bilgileri başarıyla güncellendi.', 'success')
            return redirect(url_for('trye'))
            
        except Exception as e:
            conn.rollback()
            flash(f'Güncelleme sırasında bir hata oluştu: {str(e)}', 'error')
            return redirect(url_for('edit_baro', baro_id=baro_id))
        finally:
            cur.close()
            conn.close()

@app.route('/delete_baro/<int:baro_id>', methods=['POST'])
def delete_baro(baro_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("DELETE FROM barolar WHERE baro_id = %s", (baro_id,))
        conn.commit()
        flash('Baro başarıyla silindi.', 'success')
        return redirect(url_for('trye'))
    except Exception as e:
        conn.rollback()
        flash(f'Silme işlemi sırasında bir hata oluştu: {str(e)}', 'error')
        return redirect(url_for('trye'))
    finally:
        cur.close()
        conn.close()        
@app.route('/get_avukatlar')
def get_avukatlar():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                a.avukat_id,
                k.ad AS ad,
                k.soyad AS soyad,
                a.sicil_no,
                b.baro_adi,
                array_agg(uzmanlik_alanlari.uzmanlik_adi) AS uzmanliklar
            FROM avukatlar a
            JOIN kullanicilar k ON a.kullanici_id = k.kullanici_id
            JOIN barolar b ON a.baro_id = b.baro_id
            LEFT JOIN avukat_uzmanlik au ON a.avukat_id = au.avukat_id
            LEFT JOIN uzmanlik_alanlari ON au.uzmanlik_id = uzmanlik_alanlari.uzmanlik_id
            GROUP BY a.avukat_id, k.ad, k.soyad, a.sicil_no, b.baro_adi
        """)
        avukatlar = cursor.fetchall()
        cursor.close()
        conn.close()

        # JSON formatında avukatları döndürme
        avukatlar_list = [{
            'avukat_id': avukat[0],
            'ad': avukat[1],
            'soyad': avukat[2],
            'sicil_no': avukat[3],
            'baro_adi': avukat[4],
            'uzmanliklar': avukat[5]
        } for avukat in avukatlar]

        return jsonify({'avukatlar': avukatlar_list})

    return jsonify({'error': 'Veritabanı bağlantısı sağlanamadı.'}), 500



@app.route('/avukat_sorgu', methods=['GET'])
def avukat_sorgu():
    avukat_turu = request.args.get('avukat')  # Kullanıcının girdiği avukat türünü al

    # PostgreSQL bağlantısı
    try:
        conn = get_db_connection()  # Daha önce tanımladığımız fonksiyonu kullanıyoruz
        if not conn:
            flash('Veritabanına bağlanılamadı.', 'danger')
            return render_template('avukat_sorgu.html', ilanlar=[])

        cursor = conn.cursor()

        # SQL sorgusu
        query = """
        SELECT
            avukatlar.avukat_id,
            ilanlar.ilan_id,
            kullanicilar.ad || ' ' || kullanicilar.soyad AS isim_soyisim,
            uzmanlik_alanlari.uzmanlik_adi AS uzmanlik,
            kullanicilar.eposta AS email,
            ilanlar.deneyim_yili,
            ilanlar.bolum AS buro_konum,
            ilanlar.ilan_metni AS aciklama
        FROM
            ilanlar
        INNER JOIN avukatlar ON ilanlar.avukat_id = avukatlar.avukat_id
        INNER JOIN kullanicilar ON avukatlar.kullanici_id = kullanicilar.kullanici_id
        INNER JOIN avukat_uzmanlik ON avukatlar.avukat_id = avukat_uzmanlik.avukat_id
        INNER JOIN uzmanlik_alanlari ON avukat_uzmanlik.uzmanlik_id = uzmanlik_alanlari.uzmanlik_id
        WHERE
            uzmanlik_alanlari.uzmanlik_adi ILIKE %s
        """
        cursor.execute(query, ('%' + avukat_turu + '%',))  # Anahtar kelime ile filtreleme

        # Sonuçları al
        ilanlar = cursor.fetchall()

        if not ilanlar:
            flash('Aradığınız kriterlere uygun ilan bulunamadı.', 'warning')

    except psycopg2.Error as e:  # Hataları daha iyi yakalamak için psycopg2 hatası kullanılıyor
        print(f"Veritabanı hatası: {e}")
        ilanlar = []  # Hata durumunda boş sonuç döndürüyoruz
        flash('Veritabanı hatası oluştu.', 'danger')  # Kullanıcıya hata mesajı veriyoruz

    finally:
        # Veritabanı kaynaklarını düzgün bir şekilde kapatıyoruz
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

    return render_template('avukat_sorgu.html', ilanlar=ilanlar)  # Sonuçları HTML şablonuna gönder


# Avukat ilan düzenleme
@app.route('/ilanlarim/<int:avukat_id>')
def ilanlarim(avukat_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""
            SELECT 
                i.ilan_id,
                a.avukat_id,
                k.ad,
                k.soyad,
                a.sicil_no,
                i.deneyim_yili,
                i.bolum,
                i.ilan_metni
            FROM ilanlar i
            JOIN avukatlar a ON i.avukat_id = a.avukat_id
            JOIN kullanicilar k ON a.kullanici_id = k.kullanici_id
            WHERE a.avukat_id = %s
        """, (avukat_id,))
        ilanlar = cursor.fetchall()
        
        # Convert to list of dictionaries
        ilanlar = [dict(row) for row in ilanlar]
        
        cursor.close()
        conn.close()
        
        return render_template('ilanlarim.html', ilanlar=ilanlar, avukat_id=avukat_id)
    return jsonify({'error': 'Veritabanı bağlantısı sağlanamadı.'}), 500
    
@app.route('/ilan/sil/<int:ilan_id>')
def ilan_sil(ilan_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    try:
        conn = get_db_connection()
        if not conn:
            flash('Veritabanına bağlanılamadı.', 'danger')
            return redirect(url_for('ilanlarim', avukat_id=session.get('avukat_id')))

        cursor = conn.cursor()
        
        # İlanı sil
        cursor.execute("DELETE FROM ilanlar WHERE ilan_id = %s", (ilan_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        flash('İlan başarıyla silindi.', 'success')
        return redirect(url_for('ilanlarim', avukat_id=session.get('avukat_id')))
        
    except Exception as e:
        print(f"Hata detayı: {e}")
        flash('İlan silinirken bir hata oluştu.', 'danger')
        return redirect(url_for('ilanlarim', avukat_id=session.get('avukat_id')))
    
@app.route('/edit_av_ilan/<int:avukat_id>')
def edit_av_ilan(avukat_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""
            SELECT 
                i.ilan_id,
                a.avukat_id,
                k.ad,
                k.soyad,
                a.sicil_no,
                i.deneyim_yili,
                i.bolum,
                i.ilan_metni
            FROM ilanlar i
            JOIN avukatlar a ON i.avukat_id = a.avukat_id
            JOIN kullanicilar k ON a.kullanici_id = k.kullanici_id
            WHERE a.avukat_id = %s
        """, (avukat_id,))
        ilanlar = cursor.fetchall()
        
        # Convert to list of dictionaries
        ilanlar = [dict(row) for row in ilanlar]
        
        cursor.close()
        conn.close()
        
        return render_template('edit_av_ilan.html', ilanlar=ilanlar, avukat_id=avukat_id)
    return jsonify({'error': 'Veritabanı bağlantısı sağlanamadı.'}), 500
@app.route('/update_ilan/<int:ilan_id>', methods=['GET', 'POST'])
def update_ilan(ilan_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Veritabanı bağlantısı sağlanamadı.'}), 500
    
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    if request.method == 'POST':
        deneyim_yili = request.form['deneyim_yili']
        bolum = request.form['bolum']
        ilan_metni = request.form['ilan_metni']

        cursor.execute("""
            UPDATE ilanlar
            SET deneyim_yili = %s, bolum = %s, ilan_metni = %s
            WHERE ilan_id = %s
        """, (deneyim_yili, bolum, ilan_metni, ilan_id))
        conn.commit()
        
        cursor.close()
        conn.close()
        return redirect(url_for('edit_av_ilan', avukat_id=session['avukat_id']))
    
    # GET metodu ile mevcut ilan verilerini getir
    cursor.execute("""
        SELECT ilan_id, deneyim_yili, bolum, ilan_metni
        FROM ilanlar
        WHERE ilan_id = %s
    """, (ilan_id,))
    ilan = cursor.fetchone()

    cursor.close()
    conn.close()
    return render_template('update_ilan.html', ilan=ilan)
   
 #baro
@app.route('/baro_yonetim')
def baro_yonetim():
    # Session'da avukat_id kontrolü
    if 'avukat_id' not in session:
        flash('Lütfen önce giriş yapın.')
        return redirect(url_for('login'))
    
    avukat_id = session['avukat_id']
    baro_bilgileri = None
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            # Avukatın baro başkanı olduğu baroyu sorgula
            cursor.execute("""
                SELECT * FROM barolar 
                WHERE baskani_avukat_id = %s
            """, (avukat_id,))
            
            baro_bilgileri = cursor.fetchone()
            
        except Exception as e:
            flash(f'Bir hata oluştu: {str(e)}')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('baro_yonetim.html', baro_bilgileri=baro_bilgileri)



@app.route('/baro_bilgileri')
def baro_bilgileri():
    if 'avukat_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    avukat_id = session['avukat_id']
    
    cursor.execute("""
        SELECT b.*, 
               CASE WHEN b.baskani_avukat_id = %s THEN 'baskan' ELSE 'uye' END as user_type
        FROM barolar b
        JOIN avukatlar a ON a.baro_id = b.baro_id
        WHERE a.avukat_id = %s
    """, (avukat_id, avukat_id))
    
    result = cursor.fetchone()
    
    if result:
        baro = dict(result)
        user_type = result['user_type']
    else:
        baro = None
        user_type = 'uye'
    
    cursor.close()
    conn.close()
    
    return render_template('baro_bilgileri.html', 
                         baro=baro, 
                         user_type=user_type)

@app.route('/baro_guncelle', methods=['POST'])
def baro_guncelle():
    if 'avukat_id' not in session:
        return redirect(url_for('login'))
    
    avukat_id = session['avukat_id']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Başkan kontrolü
    cursor.execute("""
        SELECT baro_id 
        FROM barolar 
        WHERE baskani_avukat_id = %s
    """, (avukat_id,))
    
    baro = cursor.fetchone()
    
    if baro:
        baro_id = baro[0]
        baro_adi = request.form.get('baro_adi')
        sehir = request.form.get('sehir')
        yeni_baskan_id = request.form.get('baskani_avukat_id')
        
        # Yeni başkanın bu baroya üye olup olmadığını kontrol et
        cursor.execute("""
            SELECT 1 FROM avukatlar 
            WHERE avukat_id = %s AND baro_id = %s
        """, (yeni_baskan_id, baro_id))
        
        if cursor.fetchone():
            cursor.execute("""
                UPDATE barolar 
                SET baro_adi = %s, 
                    sehir = %s, 
                    baskani_avukat_id = %s
                WHERE baro_id = %s
            """, (baro_adi, sehir, yeni_baskan_id, baro_id))
            
            conn.commit()
            flash('Baro bilgileri güncellendi')
        else:
            flash('Seçilen avukat bu baronun üyesi değil!')
    else:
        flash('Bu işlem için yetkiniz yok')
    
    cursor.close()
    conn.close()
    
    return redirect(url_for('baro_bilgileri'))

if __name__ == '__main__':
    app.run(debug=True)
