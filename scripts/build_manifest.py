#!/usr/bin/env python3
"""Generate dan validasi vehicles.json dari catalog.json + file di vehicles/."""

import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "catalog.json"
MANIFEST_PATH = ROOT / "vehicles.json"

BMX_MODELS = {481, 509, 510}
BIKE_MODELS = {448, 461, 462, 463, 468, 521, 522, 523, 581, 586}
UNSUPPORTED_MODELS = {
    417, 425, 430, 435, 441, 446, 447, 449, 450, 452, 453, 454, 460, 464,
    465, 469, 471, 472, 473, 476, 484, 487, 488, 493, 497, 501, 511, 512,
    513, 519, 520, 537, 538, 548, 553, 563, 564, 569, 570, 577, 584, 590,
    591, 592, 593, 594, 595, 606, 607, 608, 610, 611,
}


def classify_base_model(model_id: int):
    if model_id < 400 or model_id > 611 or model_id in UNSUPPORTED_MODELS:
        return None
    if model_id in BMX_MODELS:
        return "bmx"
    if model_id in BIKE_MODELS:
        return "bike"
    return "automobile"


def sha256_and_size(rel_path: str):
    if not rel_path or rel_path.startswith(("/", "\\")) or ".." in rel_path or ":" in rel_path:
        raise ValueError(f"Path aset tidak aman: {rel_path!r}")
    full = ROOT / rel_path
    if not full.is_file():
        raise FileNotFoundError(f"File aset tidak ditemukan: {rel_path}")
    h = hashlib.sha256()
    size = 0
    with full.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
            size += len(chunk)
    if size == 0:
        raise ValueError(f"File aset kosong (0 byte): {rel_path}")
    return h.hexdigest().lower(), size


def main() -> int:
    if not CATALOG_PATH.is_file():
        print("ERROR: catalog.json tidak ditemukan.", file=sys.stderr)
        return 1

    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    cdn_base = catalog.get("cdnBaseUrl", "")
    models_in = catalog.get("models", [])

    seen_ids = set()
    models_out = []

    for idx, item in enumerate(models_in):
        vid = int(item["virtualModelId"])
        base_id = int(item["baseModelId"])
        vclass = str(item["vehicleClass"]).strip().lower()

        if vid < 20000:
            raise ValueError(f"models[{idx}]: virtualModelId={vid} harus >= 20000")
        if vid in seen_ids:
            raise ValueError(f"models[{idx}]: duplikasi virtualModelId={vid}")
        seen_ids.add(vid)

        expected_class = classify_base_model(base_id)
        if expected_class is None or expected_class != vclass:
            raise ValueError(
                f"models[{idx}] (vid={vid}): vehicleClass={vclass!r} tidak cocok dengan baseModelId={base_id} (expected={expected_class!r})"
            )

        if vclass == "automobile" and item.get("bikeHandling") is not None:
            raise ValueError(f"models[{idx}] (vid={vid}): bikeHandling tidak boleh dipasang pada automobile")

        dff_path = str(item["dffPath"]).replace("\\", "/")
        txd_path = str(item["txdPath"]).replace("\\", "/")
        dff_sha, dff_size = sha256_and_size(dff_path)
        txd_sha, txd_size = sha256_and_size(txd_path)

        models_out.append({
            "virtualModelId": vid,
            "baseModelId": base_id,
            "vehicleClass": vclass,
            "preloadPriority": bool(item.get("preloadPriority", False)),
            "dff": {
                "path": dff_path,
                "sha256": dff_sha,
                "size": dff_size,
            },
            "txd": {
                "path": txd_path,
                "sha256": txd_sha,
                "size": txd_size,
            },
            "handling": item.get("handling", None),
            "bikeHandling": item.get("bikeHandling", None),
        })

    models_out.sort(key=lambda m: m["virtualModelId"])

    manifest = {
        "version": int(catalog.get("version", 1)),
        "cdnBaseUrl": cdn_base,
        "models": models_out,
    }

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"OK: vehicles.json berhasil dibuat ({len(models_out)} model valid).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
