import os
import json
from datasets import load_dataset
from huggingface_hub import HfFileSystem
from tqdm import tqdm

SAVE_DIR = "./arxivcap_filtered_samples"
IMG_DIR = os.path.join(SAVE_DIR, "images")
META_PATH = os.path.join(SAVE_DIR, "metadata.jsonl")
PROGRESS_PATH = os.path.join(SAVE_DIR, "progress_parquet.json")

os.makedirs(IMG_DIR, exist_ok=True)

DATASET_ID = "MMInstruction/ArxivCap"

TARGET_CATS = [
    "cs.CV", "cs.CL", "cs.LG", "cs.AI",
    "cs.RO", "cs.MM", "cs.IR", "eess.IV",
]

FLOW_KEYWORDS = [
    "architecture", "framework", "pipeline", "workflow",
    "overview", "diagram", "flowchart", "system",
    "method", "proposed", "network", "module", "block",
]

NEW_PAIRS = 1999

# =========================
# 기존 metadata 읽기
# =========================
saved = 0
saved_image_files = set()

if os.path.exists(META_PATH):
    with open(META_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                record = json.loads(line)
                saved += 1

                image_file = record.get("image_file", "")
                if image_file:
                    saved_image_files.add(image_file)

target = saved + NEW_PAIRS

# =========================
# parquet 파일 목록 가져오기
# =========================
fs = HfFileSystem()

parquet_files = sorted([
    f"hf://{path}"
    for path in fs.glob(f"datasets/{DATASET_ID}/data/*.parquet")
])

print(f"Total parquet shards: {len(parquet_files)}")
print(parquet_files[0])

# =========================
# progress 읽기
# =========================
if os.path.exists(PROGRESS_PATH):
    with open(PROGRESS_PATH, "r", encoding="utf-8") as f:
        progress = json.load(f)

    start_shard_idx = progress.get("shard_idx", 0)
    last_row_idx = progress.get("row_idx", -1)
    last_fig_idx = progress.get("fig_idx", -1)
    last_img_idx = progress.get("img_idx", -1)
else:
    start_shard_idx = 0
    last_row_idx = -1
    last_fig_idx = -1
    last_img_idx = -1

print(f"Already saved pairs: {saved}")
print(f"Already saved image files: {len(saved_image_files)}")
print(
    f"Resume after: shard_idx={start_shard_idx}, "
    f"row_idx={last_row_idx}, fig_idx={last_fig_idx}, img_idx={last_img_idx}"
)

with open(META_PATH, "a", encoding="utf-8") as meta_f:

    for shard_idx in range(start_shard_idx, len(parquet_files)):
        parquet_path = parquet_files[shard_idx]

        print(f"\nLoading shard {shard_idx}/{len(parquet_files)-1}")
        print(parquet_path)

        dataset = load_dataset(
            "parquet",
            data_files=parquet_path,
            split="train"
        )

        for row_idx, item in enumerate(tqdm(dataset, desc=f"Shard {shard_idx}")):

            # 같은 shard에서 이미 처리한 row skip
            if shard_idx == start_shard_idx and row_idx < last_row_idx:
                continue

            categories = item.get("meta", {}) \
                .get("meta_from_kaggle", {}) \
                .get("categories", "")

            if not any(cat in categories for cat in TARGET_CATS):
                continue

            caption_images = item.get("caption_images", [])

            for fig_idx, fig in enumerate(caption_images):

                # 같은 row에서 이미 처리한 fig skip
                if (
                    shard_idx == start_shard_idx
                    and row_idx == last_row_idx
                    and fig_idx < last_fig_idx
                ):
                    continue

                caption = fig.get("caption", "")
                caption_lower = caption.lower()

                matched_keywords = [
                    keyword for keyword in FLOW_KEYWORDS
                    if keyword in caption_lower
                ]

                if not matched_keywords:
                    continue

                cil_pairs = fig.get("cil_pairs", [])

                for img_idx, pair in enumerate(cil_pairs):

                    # 같은 fig에서 이미 처리한 image skip
                    if (
                        shard_idx == start_shard_idx
                        and row_idx == last_row_idx
                        and fig_idx == last_fig_idx
                        and img_idx <= last_img_idx
                    ):
                        continue

                    image_file = pair.get("image_file", "")

                    # 기존 저장 이미지 중복 방지
                    if image_file and image_file in saved_image_files:
                        continue

                    image = pair.get("image", None)

                    if image is None:
                        continue

                    image_path = os.path.join(
                        IMG_DIR,
                        f"{saved:06d}.png"
                    )

                    image.save(image_path)

                    record = {
                        "idx": saved,
                        "shard_idx": shard_idx,
                        "row_idx": row_idx,
                        "fig_idx": fig_idx,
                        "img_idx": img_idx,
                        "arxiv_id": item.get("arxiv_id", ""),
                        "title": item.get("title", ""),
                        "caption": caption,
                        "sub_caption": pair.get("sub_caption", ""),
                        "image_file": image_file,
                        "image_path": image_path,
                        "image_ocr": pair.get("image_ocr", []),
                        "categories": categories,
                        "matched_keywords": matched_keywords,
                        "parquet_path": parquet_path,
                    }

                    meta_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                    meta_f.flush()

                    if image_file:
                        saved_image_files.add(image_file)

                    saved += 1

                    with open(PROGRESS_PATH, "w", encoding="utf-8") as pf:
                        json.dump(
                            {
                                "shard_idx": shard_idx,
                                "row_idx": row_idx,
                                "fig_idx": fig_idx,
                                "img_idx": img_idx,
                            },
                            pf,
                            ensure_ascii=False,
                            indent=2
                        )

                    print(
                        f"Saved {saved} | "
                        f"shard={shard_idx} | row={row_idx} | "
                        f"fig={fig_idx} | img={img_idx} | "
                        f"arxiv_id={item.get('arxiv_id', '')} | "
                        f"categories={categories} | "
                        f"keywords={matched_keywords}"
                    )

                    if saved >= target:
                        print(f"Done. Total saved: {saved}")
                        raise SystemExit

        # shard 완료 시 다음 shard부터 시작하도록 저장
        with open(PROGRESS_PATH, "w", encoding="utf-8") as pf:
            json.dump(
                {
                    "shard_idx": shard_idx + 1,
                    "row_idx": -1,
                    "fig_idx": -1,
                    "img_idx": -1,
                },
                pf,
                ensure_ascii=False,
                indent=2
            )

print(f"Finished. Total saved: {saved}")