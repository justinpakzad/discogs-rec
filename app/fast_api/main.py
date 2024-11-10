from fastapi import FastAPI, HTTPException
from annoy import AnnoyIndex
from pydantic import BaseModel
from .utils import load_mappings, get_n_components
from pathlib import Path


class RecRequest(BaseModel):
    url: str
    n_recs: int = 5


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Welcome to Discogs Recs"}


@app.post("/recommend")
async def get_top_n_recommendations(request: RecRequest):
    # try to load necessary mappings/files
    ann_file = Path(__file__).resolve().parents[1] / "ann_files" / "discogs_rec.ann"
    if not ann_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Annoy index file not found, please make sure it exists!",
        )
    try:
        mappings = load_mappings()
        f = get_n_components()
        t = AnnoyIndex(f, "angular")
        t.load(str(ann_file))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Failed to load mappings/annoy index files"
        )
    release_id = int(request.url.split("release/")[-1].split("-")[0])
    item_idx = mappings.get("release_id_to_idx").get(release_id)
    nearest_indices = t.get_nns_by_item(
        item_idx, n=request.n_recs + 25, include_distances=False
    )
    seen_artists = set()
    recs = []
    for idx in nearest_indices:
        if len(recs) >= request.n_recs:
            break
        rel_id = mappings.get("idx_to_release_id").get(idx)
        url = f"https://www.discogs.com/release/{rel_id}"
        track_title = mappings.get("idx_to_title").get(idx)
        artist = mappings.get("idx_to_artist").get(idx).strip()
        if rel_id != release_id and artist not in seen_artists:
            recs.append((artist, track_title, url))
        seen_artists.add(artist)

    return recs
