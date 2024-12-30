# Python 3.9 tabanlı bir imaj kullanıyoruz
FROM python:3.9

# Çalışma dizinini ayarlıyoruz
WORKDIR /app

# Gereksinimleri kopyala ve yükle
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY . ./

# Eğitilmiş model dosyasını kopyala
COPY trained_model.sav ./

# Uygulamanın kullandığı portu belirt
EXPOSE 5000

# Uygulamanın başlatılma komutu
CMD ["python", "app.py"]
