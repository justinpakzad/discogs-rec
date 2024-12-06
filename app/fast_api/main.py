from fastapi import FastAPI, HTTPException
from annoy import AnnoyIndex
from pydantic import BaseModel
from .utils import load_mappings, get_n_components
from pathlib import Path

app = FastAPI()

t = None


class RecRequest(BaseModel):
    url: str
    n_recs: int = 5


def load_annoy_index():
    global t
    ann_file_path = Path("ann_files/discogs_rec.ann")
    if not ann_file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Annoy index file not found, please make sure it exists!",
        )
    f = get_n_components()
    t = AnnoyIndex(f, "angular")
    t.load(str(ann_file_path))


app.add_event_handler("startup", load_annoy_index)


def extract_release_id(request):
    release_id = int(request.url.split("release/")[-1].split("-")[0])
    return release_id


def get_nearest_indices(item_index, t, request):
    nearest_indices = t.get_nns_by_item(
        item_index, n=request.n_recs + 25, include_distances=False
    )
    return nearest_indices


def get_n_nearest_recs(request, indices, mappings, release_id):
    seen_artists = set()
    recs = []
    for idx in indices:
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


@app.get("/")
async def root():
    return {"message": "Welcome to Discogs Recs"}


@app.post("/recommend")
async def get_recommendations(request: RecRequest):
    global t
    try:
        mappings = load_mappings()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Failed to load mappings/annoy index files"
        )
    release_id = extract_release_id(request)
    item_idx = mappings.get("release_id_to_idx").get(release_id)
    nearest_indices = get_nearest_indices(item_index=item_idx, t=t, request=request)
    recs = get_n_nearest_recs(
        indices=nearest_indices,
        mappings=mappings,
        release_id=release_id,
        request=request,
    )
    return recs
