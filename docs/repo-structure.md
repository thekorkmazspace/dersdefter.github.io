# Hedef Yapı

Geçiş yaklaşımı eski akışı kırmadan yeni yayın yüzeyi üretmek üzerine kuruldu.

## Kaynak Katmanı

- `word_planlar/`
- `json_planlar/`
- `sinif_rehberlik/`
- `sinif_rehberlik_json/`
- `curriculum.json`
- `data/official_names.json`

## Pipeline Katmanı

- `scripts/fetch/`
- `scripts/transform/`
- `scripts/publish/`
- `scripts/audit/`

## Yayın Katmanı

- `public/index.json`
- `public/plans/*.json`
- `public/meta/catalog.json`

## Notlar

- `public/` ID bazlı dosya isimleri kullanır. Böylece ders adı düzeltmeleri dosya yolunu kırmaz.
- `public/index.json` yalnızca runtime alanlarını taşır; geçiş ve izleme bilgileri `public/meta/catalog.json` içine yazılır.
- `data/` şu an uyumluluk için korunuyor.
- Sonraki adımda `json_yapici.py`, `super_sync_v2.py` ve diğer kök scriptler `scripts/` altına taşınabilir.
