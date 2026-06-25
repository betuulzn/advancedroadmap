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

# Headless (CI'da kullanılan mod, lokalde de çalışır)
pytest tests/ -v --browser=chrome --headless
```

## Proje Yapısı

```
advancedRoadmap/
├── Jenkinsfile                  # CI/CD pipeline (bkz. CI/CD bölümü)
├── pytest.ini                   # testpaths ve ortak pytest ayarları
├── conftest.py                  # pytest fixture'ları, browser/headless seçimi, screenshot hook
├── requirements.txt
├── ci/
│   └── Dockerfile               # Opsiyonel: Chrome+Firefox+Python içeren hermetic Jenkins agent image
├── pages/
│   ├── base_page.py            # Tüm sayfalar için ortak metotlar (find, click, scroll…)
│   ├── home_page.py            # Insider One ana sayfası
│   ├── careers_page.py         # Careers sayfası
│   └── open_positions_page.py  # Lever job board
├── tests/
│   └── test_insider_careers.py # E2E test senaryosu
└── utils/
    ├── driver_factory.py       # Chrome / Firefox WebDriver başlatma (headless destekli)
    └── logger.py               # Oturum bazlı dosya + konsol loglama
```

## CI/CD (Jenkins)

Pipeline tanımı repo kökündeki `Jenkinsfile`'da. Her PR açılışında/güncellemesinde testleri Chrome ve Firefox üzerinde paralel (Jenkins `matrix`) olarak çalıştırır, JUnit + HTML raporları ve hata anı ekran görüntülerini artifact olarak arşivler, sonucu GitHub commit status/check olarak PR'a yazar.

**Jenkins job kurulumu**

1. Job tipi: **Multibranch Pipeline** (GitHub Branch Source Plugin) — repoyu webhook üzerinden dinler, her branch ve her PR için otomatik olarak `Jenkinsfile`'ı çalıştırır.
2. Branch Sources → GitHub → repo: `https://github.com/betuulzn/advancedroadmap` → "Discover branches" + "Discover pull requests from origin" davranışlarını ekle.
3. GitHub repo → Settings → Webhooks → `http://<jenkins-url>/github-webhook/`, content type `application/json`, event: "Pull requests" + "Pushes" (GitHub App kullanılırsa webhook otomatik yönetilir).
4. GitHub repo → Settings → Branches → `main` için branch protection rule → "Require status checks to pass before merging" → ilk build sonrası listede görünecek `jenkins/ui-tests` check'ini seç. Bu adım, testler kırmızı kaldığında merge butonunun GitHub tarafında kilitlenmesini sağlar.

**Gerekli Jenkins eklentileri**

| Eklenti | Amaç |
|---|---|
| GitHub Branch Source Plugin | Multibranch job, PR keşfi, webhook tetikleme |
| Pipeline GitHub Notify Step | `githubNotify` adımı → PR'a pending/success/failure check yazma |
| Pipeline: Declarative / Workflow Aggregator | `Jenkinsfile`, `matrix` direktifi |
| JUnit Plugin | `junit` adımı, Test Result Trend grafiği, başarısız testte build'i UNSTABLE yapma |
| HTML Publisher Plugin | `publishHTML` — pytest-html raporunu Jenkins UI içinde gösterme |
| Credentials Binding Plugin | GitHub PAT/App credential'ını güvenli saklama |
| Timestamper / Workspace Cleanup | Log timestamp'leri, build sonu workspace temizliği |
| (Opsiyonel) Docker Pipeline Plugin | `ci/Dockerfile` ile hermetic agent kullanmak istenirse |

**Chrome + Firefox**

`Jenkinsfile`'daki `matrix` bloğu `BROWSER` ekseni üzerinden `chrome` ve `firefox` için pytest'i paralel çalıştırır; her eksen kendi `reports/<browser>`, `screenshots/<browser>`, `logs/<browser>` dizinine yazar (çakışmayı engellemek için `SCREENSHOT_DIR`/`LOG_DIR` env override'ları kullanılır). `--headless` bayrağı CI'da ekran (display) gerektirmeden Chrome/Firefox'u arka planda çalıştırır. Jenkins agent'ında Chrome ve Firefox tarayıcılarının kurulu olması gerekir (driver binary'leri `webdriver-manager` ile otomatik indirilir); reprodüklenebilir bir agent isteniyorsa `ci/Dockerfile` kullanılabilir.

**Test raporları & screenshot arşivleme**

- `pytest --junitxml=...`: Jenkins'in native test sonucu/trend grafiğini besler, başarısız testte build'i `UNSTABLE` yapar.
- `pytest --html=... --self-contained-html`: insan-okunur HTML rapor, `publishHTML` ile Jenkins build sayfasına gömülür.
- Başarısız test anında `conftest.py`'daki `pytest_runtest_makereport` hook'u otomatik screenshot alır (`pages/base_page.py: take_screenshot`); bunlar `archiveArtifacts` ile her build'e bağlı kalıcı artifact olarak saklanır.

## Özellikler

- **POM mimarisi** — her sayfa ayrı bir class
- **Chrome & Firefox** desteği (`--browser` parametresi)
- **Hata anında screenshot** — `screenshots/` klasörüne kaydedilir
- **Detaylı loglama** — `logs/` klasörüne oturum bazlı log dosyası
- **Explicit wait** — tüm beklemeler `WebDriverWait` ile yönetilir
