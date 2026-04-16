# NewsCheck - Haber Manipülasyon Dedektörü

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

NewsCheck, haber metinlerindeki duygu sömürüsünü, taraflı bakış açılarını ve manipülasyon riskini tespit eden, ardından metni tarafsız bir şekilde yeniden yazan yapay zeka destekli bir analiz aracıdır.

Sistem, **Google Gemini 2.5 Flash Lite** modelini ve **LangChain** orkestrasyonunu kullanarak farklı yapay zeka "ajanları" (zincirleri) üzerinden çalışmaktadır.

## 🌟 Özellikler

Uygulama, haber metnini 4 farklı ajandan geçirerek derinlemesine bir analiz sunar:

1. **Duygu Avcısı (Adjective Hunter)**: Metindeki abartılı, duygusal sömürü yapan veya doğrudan yönlendirme amacı taşıyan sıfat ve zarfları tespit eder. 
2. **Perspektif Analisti (Perspective Analyst)**: Metnin kimin bakış açısıyla yazıldığını, kimin sesinin eksik olduğunu ve sorumluluğu gizlemek için edilgen yapılar kullanılıp kullanılmadığını inceler.
3. **Risk Analisti (Risk Scorer)**: Saptanan bulgulara dayanarak habere `0` ile `100` arasında bir **Manipülasyon Riski** puanı atar ve tek cümlelik net bir sebep sunar.
4. **Nötrleştirici (Neutralizer)**: Haberi tüm nesnel dışı unsurlardan ve hislerden arındırarak salt gerçekleri (5N1K) aktaran objektif bir dille yeniden yazar.

## 🚀 Kullanılan Teknolojiler

- **Python 3.x**
- **[Streamlit](https://streamlit.io/)** - Web arayüzü
- **[LangChain](https://python.langchain.com/)** - AI zincir ve prompting orkestrasyonu
- **Google Gemini API** (`langchain-google-genai`) - Üretken yapay zeka modeli

## 💻 Yerel Kurulum (Local Installation)

1. Projeyi bilgisayarınıza klonlayın:
   ```bash
   git clone <repository-url>
   cd NewsCheck
   ```

2. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

3. Geliştirme ortamınızda bir `.env` dosyası oluşturun veya terminalinizde API anahtarınızı `GOOGLE_API_KEY` ortam değişkeni olarak ayarlayın:
   - *Not: Alternatif olarak uygulamayı başlattıktan sonra Streamlit arayüzündeki Ayarlar menüsünden de girebilirsiniz.*

4. Streamlit uygulamasını başlatın:
   ```bash
   streamlit run app.py
   ```

## 🐳 Docker ile Kurulum

Eğer sisteminizde Docker kurulu ise uygulamayı kapsayıcı (container) içerisinde kolayca başlatabilirsiniz:

1. Docker imajını oluşturun:
   ```bash
   docker build -t newscheck-app .
   ```

2. Docker konteynerini çalıştırın:
   ```bash
   docker run -p 8501:8501 -e GOOGLE_API_KEY="Sizin_API_Anahtariniz" newscheck-app
   ```
   Kurulum tamamlandıktan sonra tarayıcınızda `http://localhost:8501` adresine giderek uygulamaya erişebilirsiniz.

## 📌 Kullanım
- Sol taraftaki menüden API ayarlarını yapın (eğer `.env` veya ortam değişkeni kullanmıyorsanız).
- Ana ekrandaki metin kutusuna analiz edilmesini istediğiniz Türkçe haber metnini kopyalayıp yapıştırın.
- "Analiz Et" düğmesine basarak ajanların metin üzerindeki raporlarını, puanını ve haberin objektif (nötrleştirilmiş) şeklini inceleyin.
