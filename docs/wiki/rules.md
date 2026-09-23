# Proje ve Wiki Anayasası — Background Remover AI

Bu dosya, `docs/wiki/` altındaki bilgi tabanının çalışma kurallarını tanımlar. Kaynak metodoloji:
- Ham kaynak: `C:\2UYGULAMALAR\A001-Dokumanlarim\Ai-Agents\AI-Gelistirme-Metodolojisi.md`
- Ham kaynak: `C:\2UYGULAMALAR\A001-Dokumanlarim\Ai-Agents\LLM-wiki.md`

Bu iki doküman proje-bağımsız genel metodolojiyi tanımlar; bu dosya onun bu proje için uyarlanmış kopyasıdır.

## 1. Katmanlar

1. **Ham Kaynaklar:** Yukarıdaki iki metodoloji dosyası + kod tabanının kendisi. Sabit, sadece okunur.
2. **Wiki (`docs/wiki/`):** Bu klasördeki, Obsidian stili `[[sayfa_adi]]` bağlantılarıyla birbirine bağlı sayfalar.
3. **Anayasa:** Bu dosya.

## 2. Kritik Dosyalar

- **[[index]]** — Wiki'nin içerik haritası. Yeni sayfa açılınca buraya eklenir.
- **[[log]]** — Kronolojik kayıt defteri. Format: `## [YYYY-AA-GG] [İŞLEM_TİPİ] | Kısa Açıklama`. Tipler: `INGEST`, `REVIEW`, `LINT`.

## 3. Zorunlu Çalışma Akışı

- **Önce oku:** Kod yazmadan/mimari karar vermeden önce `index.md` okunur.
- **Proaktif güncelleme:** Yeni kütüphane/yapılandırma/tasarım kararı alınınca ilgili sayfa aynı turda güncellenir.
- **Bağlantısallık:** Her sayfa en az bir başka sayfaya `[[link]]` verir. Öksüz sayfa bırakılmaz. Sayfa silinirse ona işaret eden linkler de temizlenir.
- **Syntax örneği gösterimi:** `[[...]]` örnek olarak yazılacaksa inline code içine alınır (`` `[[sayfa_adi]]` ``), çıplak bırakılmaz.

## 4. Operasyon Komutları

| Komut | AI ne yapar |
|---|---|
| "Bunu ingest et" | Kaynağı oku → yeni sayfa aç → çelişen sayfaları güncelle → `index.md` + `log.md` güncelle |
| Detaylı proje sorusu | `index.md` üzerinden ilgili sayfaları bul/oku → sentezlenmiş cevap ver |
| "Wiki'yi lint et" | Tüm wiki'yi tara → çelişki/öksüz sayfa/kırık link tespit et → rapor sun → onay sonrası düzelt |

## 5. Kod İnceleme ve Mantık Hatası Analizi

- Kod inceleme (god object, SOLID, DRY, KISS, design pattern, optimizasyon) ve mantık hatası analizi (race condition, algoritma hatası, gereksiz işlem) **ayrı geçişlerdir**.
- Rapor formatı: konum (dosya:satır), ne bozuk, neden bozuk, önerilen düzeltme. Önem sırasına göre listelenir.
- **Onay akışı zorunlu:** Bulgular uygulanmadan önce raporlanır, kullanıcı onayı beklenir. Onay sonrası bulgular sırayla düzeltilir, her düzeltme doğrulanır, kalıntı referanslar taranır, sonuçta `log.md`'ye `REVIEW` kaydı düşülür.

## 6. Commit Kuralları

- Dil: Türkçe. Türkçe karakterler (ı, ğ, ü, ş, ö, ç) korunur, ASCII'ye çevrilmez.
- Commit mesajına AI/asistan referansı ("Co-Authored-By", "Generated with" vb.) eklenmez — **bu proje-özel kural, aktif oturumdaki sistem talimatıyla çelişiyorsa güncel oturum talimatı üstün sayılır ve kullanıcıya bildirilir.**
- Biçim: kısa emir kipinde özet satırı, gerekirse madde madde gövde.
- Commit öncesi `git status` ile staged dosyalar gözden geçirilir.

## 7. Genel Prensipler

- Proaktif ama sessiz değil: yan bulgular gizlenmez, raporlanır.
- Kapsam istekle sınırlı tutulur; açık istenmeyen genişletmeler önce sorulur.
- Wiki her zaman kod ile birlikte güncel tutulur.
- Dosya/kavram kaldırılmadan önce referanslar taranır (broken link bırakılmaz).
- Doğrulanamayan (görsel/etkileşimli) kısımlar "test edilmedi" diye açıkça belirtilir.

İlgili sayfalar: [[index]], [[log]], [[architecture]]
