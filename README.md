# 🤖 PromptLab - RAG Tabanlı Prompt Optimizasyon Chatbot

**Akbank GenAI Bootcamp 2025** kapsamında geliştirilen, **Retrieval Augmented Generation (RAG)** mimarisini kullanan yapay zeka destekli **prompt optimizasyon chatbot** projesidir.

---

## 🎯 Amaç

**PromptLab**, kullanıcıların yazdığı kısa ve belirsiz prompt’ları, RAG teknolojisiyle **profesyonel, detaylı ve etkili prompt’lara** dönüştürür.  
Sistem, **Google Gemini Pro** ve **vektör tabanlı benzerlik araması** kullanarak optimal prompt önerileri sunar.

---

## 💡 Problem Tanımı

- Kullanıcılar AI’dan istediği sonucu alamıyor (zayıf prompt’lar)  
- Prompt engineering bilgisi eksik  
- Manuel optimizasyon zaman alıcı  

---

## 🧭 Ana Hedefler

- 🧠 Prompt kalitesini otomatik olarak analiz etmek  
- 📚 Benzer başarılı prompt örneklerinden öğrenmek  
- 🧩 Kullanıcı niyetini doğru şekilde tespit etmek  
- ✍️ Prompt’u kategoriye ve amaca göre optimize etmek  

---

## ✨ Çözüm Özeti

**RAG Pipeline:** Benzer başarılı örneklerden öğrenerek optimize eder  
**Chatbot Arayüzü:** Kullanıcı dostu, konuşma tabanlı  
**Gerçek Zamanlı:** Anında optimizasyon ve geri bildirim sağlar  

---

## 📊 Veri Seti Hakkında

Veri seti tamamen açık kaynak olup ek bir toplama işlemi yapılmamıştır.
Hugging Face veri seti, proje amacına uygun olacak şekilde filtrelenip yerel örneklerle zenginleştirilmiştir.

### 🔹 1. Hugging Face - Awesome ChatGPT Prompts  
**URL:** [https://huggingface.co/datasets/fka/awesome-chatgpt-prompts](https://huggingface.co/datasets/fka/awesome-chatgpt-prompts)  
**Açıklama:** Farklı kategorilerdeki başarılı ve optimize prompt örneklerinden oluşan açık kaynak veri seti.  
**İçerik:** 150+ farklı rol ve görev için hazırlanmış profesyonel prompt örnekleri  

### 🔹 2. Yerel Eğitim Veri Seti  
Projede kullanılan 8 temel prompt kategorisi:  
`Öğretim, Kod Yazma, Yazarlık, İş Analizi, İçerik, Tasarım, Veri, Matematik`

**Veri Seti Özellikleri:**  
- Toplam Örnek: 8 + Hugging Face veri seti  
- Diller: Türkçe ve İngilizce  
- Format: JSON (act, prompt, type)  
- Boyut: Hafif (RAM optimized)  
- Depolama: In-memory (ChromaDB + TF-IDF)

---

## 🧠 Kullanılan Yöntemler

### 1️⃣ Retrieval Augmented Generation (RAG)
**Bileşenler:**
- Vector Store: ChromaDB + TF-IDF  
- Similarity Search: Cosine Similarity  
- Generative Model: Google Gemini Pro  

**Akış:**

- Kullanıcı Input 
- Prompt Analizi (Kategori, Intent) 
- Vektör Arama (Benzer Prompt Bulma) 
- RAG Context Hazırlama 
- Gemini Pro ile Optimizasyon 
- Sonuç Döndürme

---

### 2️⃣ Prompt Analiz Sistemi
- Intent Detection: Öğretim, Rol-Play, Kod, İçerik  
- Kategori Tespiti: Otomatik sınıflandırma  
- Kalite Skoru: Length, Specificity, Overall Score  
- Sorun Tespiti: Kısa / Detay eksik / Belirsiz prompt  

---

### 3️⃣ Vektör Benzerliği Araması
- Algoritma: Cosine Similarity  
- Vektörleme: TF-IDF  
- Fallback: ChromaDB → TF-IDF cascade  

---

### 4️⃣ Yapay Zeka Modelleri
- Birincil Model: **Google Gemini Pro**  
- Fallback: **Heuristic-based Optimizer**  
- Temperature: `0.7` (yaratıcılık / tutarlılık dengesi)

---

### 5️⃣ Web Arayüzü
- Framework: **Streamlit**  
- Mimari: **Interactive Chat Interface**  
- Özellikler:  
  - Gerçek zamanlı mesajlaşma  
  - Kullanıcı girdisi optimizasyonu  
  - Model & RAG mod göstergeleri  

---

## 🚀 Kurulum ve Çalıştırma

### 📦 Gereksinimler
- Python 3.9 veya üzeri

---

### 1️⃣ Repository’yi Klonlayın
```bash
git clone https://github.com/serayegee/PromptLab.git
cd PromptLab
```

### 2️⃣ Virtual Environment Oluşturun
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 4️⃣ Gemini API Key Alın
```bash
Google Makersuite üzerinden API key alın
https://makersuite.google.com/app/apikey
```

### 5️⃣ Uygulamayı Çalıştırın
```bash
streamlit run streamlit_app.py
```
--- 

## 📱 Kullanım Kılavuzu
### 🎮 Adım Adım

1️⃣ Sol panelde "🔑 Gemini API Anahtarı" bölümüne gidin

2️⃣ API key’inizi yapıştırın ve Kaydet butonuna tıklayın

3️⃣ Prompt alanına metninizi yazın veya hazır prompt seçin

4️⃣ 📤 Gönder butonuna tıklayın

5️⃣ Optimize edilmiş prompt ve analiz sonuçlarını görüntüleyin

---

## 💬 Örnek Kullanım

Girdi:

bana python öğret


Çıktı:

Sen bir Python öğretmenisin. Öğrencilere Python'ı adım adım öğret. 
Temel syntax’tan başla, her kavramı örneklerle açıkla, kod alıştırmaları ver. 
Sabırlı, net ve teşvik edici ol.

Metrikler:

- Model: Gemini Pro
- RAG Mode: ✅ Aktif
- İyileşme: +60%
- Kelime Artışı: +25
  
---

## 📈 Elde Edilen Sonuçlar

⏱ Yanıt Hızı	< 2 saniye

🎯 RAG Kalite Artışı	+30-50%

🔍 Vektör Arama Başarısı	Top-3 benzerlik: %95+

🚀 Ortalama İyileşme	%35

---

## 🧩 Proje Mimarisi
📂 PromptLab

 ┣ 📜 promptlab_model.py      → RAG & analiz pipeline
 
 ┣ 📜 streamlit_app.py        → Web arayüzü (Streamlit)
 
 ┣ 📜 requirements.txt        → Gerekli kütüphaneler
 
 ┗ 📁 __pycache__             → Derleme çıktıları

---
## 🌐 Web Uygulaması
[🔗 PromptLab Canlı Demo](https://promptlab-frvuzjrc2rvacqut6nxgsu.streamlit.app/)

---
## 🖼️ Ekran Görüntüleri ve Video

https://github.com/user-attachments/assets/1b400024-37d3-4f71-9c38-c8966befcbed

<img width="1918" height="873" alt="Ekran görüntüsü 2025-10-22 170120" src="https://github.com/user-attachments/assets/215ed3a7-66a1-49ad-8096-d03a4b57921c" />

<img width="1918" height="863" alt="Ekran görüntüsü 2025-10-22 170246" src="https://github.com/user-attachments/assets/f179171e-da3d-422f-bd9b-ca263feec22f" />



