import base64, binascii, os
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from . import store, workflow as W
from .core import Index, make_chunks, review, review_image

app = FastAPI(title="BrandShield AI")
WEB = os.path.join(os.path.dirname(__file__), "..", "web")
STATE = {}

def rebuild():
    STATE["chunks"] = make_chunks() + store.uploaded_chunks()
    STATE["index"] = Index(STATE["chunks"])
rebuild()

def role(x_role: str = Header("Creator")):
    if x_role not in W.ROLES: raise HTTPException(400, "Unknown role.")
    return x_role

def run(fn, *a):
    try: return fn(*a)
    except W.WorkflowError as e: raise HTTPException(e.code, e.msg)

def admin_only(r):
    if r != "Admin": raise HTTPException(403, "Only the Admin role can change guidelines.")

class Draft(BaseModel):
    text: str = ""
class Submit(BaseModel):
    text: str = ""
    findings: list = []
class Decision(BaseModel):
    decision: str
    comment: str = ""
class FileIn(BaseModel):
    filename: str
    data_b64: str
class Doc(BaseModel):
    name: str
    text: str
class Img(BaseModel):
    data_b64: str
    media_type: str = ""
    alt: str = ""

@app.get("/api/health")
def health():
    return {"ok": True, "ai_configured": bool(os.environ.get("ANTHROPIC_API_KEY")), "guideline_chunks": len(STATE["chunks"])}

@app.get("/api/guidelines")
def guidelines():
    return {"docs": [{"id": i, "name": n} for i, n, _ in store.list_docs()], "chunks": len(STATE["chunks"])}

@app.post("/api/guidelines")
def add_guideline(d: Doc, r: str = Depends(role)):
    admin_only(r)
    if not d.text.strip(): raise HTTPException(400, "Empty guideline text.")
    i = store.add_doc(d.name or "Untitled", d.text.strip()[:60000]); rebuild(); W.log(r, "added guideline", d.name, None); return {"id": i}

@app.delete("/api/guidelines/{i}")
def del_guideline(i: int, r: str = Depends(role)):
    admin_only(r); store.delete_doc(i); rebuild(); W.log(r, "removed guideline", "#%d" % i); return {"ok": True}

@app.post("/api/extract")
def extract(f: FileIn):
    try: raw = base64.b64decode(f.data_b64, validate=True)
    except (binascii.Error, ValueError): raise HTTPException(400, "Could not read the uploaded file.")
    try: return {"text": store.extract_text(f.filename, raw)}
    except ValueError as e: raise HTTPException(400, str(e))

@app.post("/api/ai-review")
def ai_review(d: Draft):
    return review(d.text, STATE["index"])

@app.post("/api/image-review")
def image_review(i: Img):
    return review_image(i.data_b64, i.media_type, STATE["chunks"])

@app.post("/api/drafts")
def submit(s: Submit, r: str = Depends(role)):
    return run(W.submit, r, s.text, s.findings)

@app.get("/api/drafts")
def drafts(status: str = "", r: str = Depends(role)):
    return run(W.drafts, r, status or None)

@app.post("/api/drafts/{i}/decision")
def decision(i: int, d: Decision, r: str = Depends(role)):
    return run(W.decide, r, i, d.decision, d.comment)

@app.get("/api/audit")
def audit(r: str = Depends(role)):
    return run(W.audit, r)

@app.get("/api/insights")
def insights(r: str = Depends(role)):
    return run(W.insights, r)

@app.get("/")
def home():
    return FileResponse(os.path.join(WEB, "index.html"))
