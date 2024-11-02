from fastapi import FastAPI
from annoy import AnnoyIndex
from pydantic import BaseModel
from .utils import load_mappings
from pathlib import Path


class RecRequest(BaseModel):
    url: str
    n_recs: int = 7


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Welcome to Discogs Recs"}


@app.post("/recommend")
async def get_top_n_recommendations(request: RecRequest):
    ann_file = Path(__file__).resolve().parents[1] / "ann_files" / "discogs_rec.ann"
    mappings = load_mappings()
    f = 150
    t = AnnoyIndex(f, "angular")
    t.load(str(ann_file))
    release_id = int(request.url.split("release/")[-1].split("-")[0])
    item_idx = mappings.get("release_id_to_idx").get(release_id)
    nearest_indices = t.get_nns_by_item(
        item_idx, n=request.n_recs + 5, include_distances=False
    )
    seen_artists = set()
    recs = []
    for count, idx in enumerate(nearest_indices, start=1):
        if count >= request.n_recs + 1:
            break
        rel_id = mappings.get("idx_to_release_id").get(idx)
        url = f"https://www.discogs.com/release/{rel_id}"
        track_title = mappings.get("idx_to_title").get(idx)
        artist = mappings.get("idx_to_artist").get(idx).strip()
        if rel_id != release_id and artist not in seen_artists:
            recs.append((artist, track_title, url))
        seen_artists.add(artist)

    return recs
