# advancedRoadmap

Insider One careers page için Selenium + Pytest ile yazılmış E2E test projesi. Page Object Model (POM) mimarisini kullanır.

## Test Senaryosu

1. Insider One ana sayfasını aç ve doğrula
2. Footer'daki "We're hiring" linkine tıkla → Careers sayfasını doğrula
3. "Explore open roles" butonunu doğrula ve tıkla → Software Development bloğundan Lever board'a geç
4. Team = `Quality Assurance`, Location = `Istanbul` filtrelerini uygula
5. Tüm iş ilanlarında department ve location bilgilerini doğrula
6. İlk ilanın "Apply" butonuna tıkla → Lever application form'una yönlendirmeyi doğrula

## Kurulum

**Gereksinimler:** Python 3.9+, Google Chrome veya Firefox

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Testleri Çalıştırma

```bash
# Chrome (varsayılan)
pytest tests/ -v

# Firefox
pytest tests/ -v --browser=firefox

# HTML rapor
pytest tests/ -v --html=report.html --self-contained-html
```

## Proje Yapısı

```
advancedRoadmap/
├── conftest.py                  # pytest fixture'ları, browser seçimi, screenshot hook
├── requirements.txt
├── pages/
│   ├── base_page.py            # Tüm sayfalar için ortak metotlar (find, click, scroll…)
│   ├── home_page.py            # Insider One ana sayfası
│   ├── careers_page.py         # Careers sayfası
│   └── open_positions_page.py  # Lever job board
├── tests/
│   └── test_insider_careers.py # E2E test senaryosu
└── utils/
    ├── driver_factory.py       # Chrome / Firefox WebDriver başlatma
    └── logger.py               # Oturum bazlı dosya + konsol loglama
```

## Özellikler

- **POM mimarisi** — her sayfa ayrı bir class
- **Chrome & Firefox** desteği (`--browser` parametresi)
- **Hata anında screenshot** — `screenshots/` klasörüne kaydedilir
- **Detaylı loglama** — `logs/` klasörüne oturum bazlı log dosyası
- **Explicit wait** — tüm beklemeler `WebDriverWait` ile yönetilir
