# Backend Setup Guide

## İlk Kurulum

### 1. Virtual Environment Oluştur (Önerilen)
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
```

### 2. Bağımlılıkları Kur
```powershell
pip install -r requirements.txt
```

### 3. Veritabanını Oluştur
```powershell
python manage.py makemigrations
python manage.py migrate
```

### 4. Admin Kullanıcısı Oluştur
```powershell
python manage.py createsuperuser
```

### 5. Sunucuyu Başlat
```powershell
python manage.py runserver
```

## Kullanım

- **API Endpoint:** http://127.0.0.1:8000/api/
- **Admin Panel:** http://127.0.0.1:8000/admin/
- **Frontend:** `frontend/index.html` dosyasını tarayıcıda aç

## API Endpoints

- `GET /api/teams/` - Tüm takımlar
- `GET /api/teams/{id}/` - Takım detayı
- `GET /api/players/` - Tüm oyuncular
- `GET /api/players/{id}/` - Oyuncu detayı
- `GET /api/players/leaderboard/goals/` - Gol kralları
- `GET /api/players/leaderboard/assists/` - Asist kralları
- `GET /api/matches/` - Tüm maçlar
- `GET /api/matches/{id}/` - Maç detayı

## Veri Girişi

Admin panelden (http://127.0.0.1:8000/admin/) giriş yaparak:

1. **Teams** - Takım ekle (logo yükleyebilirsin)
2. **Players** - Oyuncu ekle (fotoğraf yükleyebilirsin, stats ayarla)
3. **Matches** - Maç ekle
4. **Player Match Stats** - Maç içinde inline olarak oyuncu istatistikleri ekle

Not: Maç bittiğinde (is_finished=True) takım istatistikleri otomatik güncellenir.
