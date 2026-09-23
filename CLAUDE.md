# CLAUDE.md — Background Remover AI

Kod yazmadan veya mimari karar vermeden önce **önce `docs/wiki/index.md`** oku — proje sıfırdan keşfedilmez, biriken bilgi kullanılır.

## Wiki

- `docs/wiki/rules.md` — çalışma kuralları, operasyon komutları (INGEST/QUERY/LINT), commit kuralları.
- `docs/wiki/index.md` — tüm sayfaların içerik haritası.
- `docs/wiki/log.md` — kronolojik değişiklik günlüğü.
- `docs/wiki/architecture.md` — mimari, design pattern'ler, işlem akışı.

## Kısa Özet

- **"Bunu ingest et"** → kaynağı oku, ilgili wiki sayfasını oluştur/güncelle, `index.md` + `log.md`'yi güncelle.
- **Detaylı proje sorusu** → önce `index.md` üzerinden ilgili sayfayı bul, oradan cevap ver.
- **"Wiki'yi lint et"** → çelişki/öksüz sayfa/kırık link tara, rapor sun, onay sonrası düzelt.
- Kod inceleme ve mantık hatası bulguları **onay alınmadan uygulanmaz** (bkz `docs/wiki/rules.md` Bölüm 5).

Detay için: `docs/wiki/rules.md`.
