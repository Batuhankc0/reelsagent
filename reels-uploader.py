import requests
import time
import os
from dotenv import load_dotenv

# .env dosyasındaki ortam değişkenlerini yükle
load_dotenv()

# --- .env DOSYASINDAN BİLGİLERİ OKU ---
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION")

# --- YÜKLENECEK REELS İÇİN BİLGİLER ---
# DİKKAT: Bu URL'nin herkese açık ve doğrudan erişilebilir olması gerekir.
VIDEO_URL = "https://github.com/Batuhankc0/reelsagent/raw/refs/heads/main/test.mp4" # Test için kullanabileceğiniz örnek bir video
CAPTION = "Bu Reels Python ile API kullanılarak yüklendi! 🐍🚀\n#Python #Developer #API #InstagramAPI"

# --- KONTROL ---
if not all([ACCESS_TOKEN, INSTAGRAM_BUSINESS_ACCOUNT_ID, GRAPH_API_VERSION]):
    raise ValueError("Lütfen .env dosyasındaki tüm gerekli değişkenleri (ACCESS_TOKEN, INSTAGRAM_BUSINESS_ACCOUNT_ID, GRAPH_API_VERSION) ayarlayın.")

def create_reels_container(account_id, access_token, video_url, caption):
    """Adım 1: Reels'i yüklemek için bir medya konteyneri oluşturur."""
    print("Adım 1: Medya konteyneri oluşturuluyor...")
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{account_id}/media"
    params = {
        'media_type': 'REELS',
        'video_url': video_url,
        'caption': caption,
        'share_to_feed': 'true', # Reels'in profil akışında da görünmesini sağlar
        'access_token': access_token
    }
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()  # Bir HTTP hatası oluşursa (4xx veya 5xx) exception fırlatır
        result = response.json()
        if 'id' in result:
            print(f"Başarılı! Konteyner ID'si: {result['id']}")
            return result['id']
        else:
            print(f"Hata: Konteyner oluşturulamadı. Gelen yanıt: {result}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"API isteği sırasında kritik bir hata oluştu: {e}")
        print(f"Detaylar: {e.response.json()}")
        return None

def check_container_status(creation_id, access_token):
    """Oluşturulan konteynerin durumunu periyodik olarak kontrol eder."""
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{creation_id}"
    params = {'fields': 'status_code', 'access_token': access_token}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        status = response.json().get('status_code')
        print(f"Konteyner durumu: {status}")
        return status
    except requests.exceptions.RequestException as e:
        print(f"Durum kontrolü sırasında hata: {e}")
        return "ERROR"

def publish_reels(account_id, creation_id, access_token):
    """Adım 2: Hazır olan konteyneri yayınlayarak Reels'i görünür hale getirir."""
    print("\nAdım 2: Konteyner yayınlanıyor...")
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{account_id}/media_publish"
    params = {'creation_id': creation_id, 'access_token': access_token}
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        result = response.json()
        if 'id' in result:
            print(f"🎉 TEBRİKLER! Reels başarıyla yayınlandı! Media ID: {result['id']}")
            return result['id']
        else:
            print(f"Hata: Reels yayınlanamadı. Gelen yanıt: {result}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Yayınlama sırasında kritik bir hata oluştu: {e}")
        print(f"Detaylar: {e.response.json()}")
        return None

# --- ANA SÜRECİ BAŞLAT ---
if __name__ == "__main__":
    # 1. Video konteynerini oluştur
    creation_id = create_reels_container(
        INSTAGRAM_BUSINESS_ACCOUNT_ID, ACCESS_TOKEN, VIDEO_URL, CAPTION
    )

    if creation_id:
        # 2. Konteynerin durumu "FINISHED" olana kadar bekle
        max_retries = 20
        retry_count = 0
        while retry_count < max_retries:
            status = check_container_status(creation_id, ACCESS_TOKEN)
            
            if status == "FINISHED":
                # 3. Hazır olan konteyneri yayınla
                publish_reels(INSTAGRAM_BUSINESS_ACCOUNT_ID, creation_id, ACCESS_TOKEN)
                break
            elif status == "ERROR":
                print("Video işlenirken bir hata oluştu. Lütfen video formatını, boyutunu veya URL'yi kontrol edin.")
                break
            
            print("Video Instagram tarafından işleniyor, 15 saniye bekleniyor...")
            time.sleep(15)
            retry_count += 1
        
        if retry_count == max_retries:
            print("İşlem zaman aşımına uğradı. Video işlenemedi. Lütfen daha sonra tekrar deneyin.")