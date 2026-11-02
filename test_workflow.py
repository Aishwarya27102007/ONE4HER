import os, sys, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "w.db")
from server import workflow as W

def code(fn, *a):
    try: fn(*a)
    except W.WorkflowError as e: return e.code

class T(unittest.TestCase):
    def test_full_journey_and_rules(self):
        done = [{"title": "Price is outdated", "status": "fixed"}, {"title": "Tone too loud", "status": "disputed"}]
        self.assertEqual(code(W.submit, "Creator", "x", [{"status": "open"}]), 400)
        self.assertEqual(code(W.submit, "Creator", "  ", done), 400)
        self.assertEqual(code(W.submit, "Reviewer", "x", done), 403)
        a = W.submit("Creator", "Post one", done); b = W.submit("Creator", "Post one", done)
        self.assertEqual(a, b)  # double click is safe
        self.assertEqual(code(W.decide, "Creator", a["id"], "approve", ""), 403)
        self.assertEqual(code(W.decide, "Reviewer", a["id"], "changes", " "), 400)
        self.assertEqual(code(W.decide, "Reviewer", 999, "approve", ""), 404)
        self.assertEqual(W.decide("Reviewer", a["id"], "approve", "ok")["status"], "Approved")
        self.assertEqual(code(W.decide, "Reviewer", a["id"], "approve", ""), 409)  # same action twice
        self.assertEqual(W.drafts("Reviewer", "In review"), [])
    def test_insights_and_audit(self):
        W.submit("Admin", "Post two", [{"title": "Tone too loud", "status": "disputed"}])
        i = W.insights("Reviewer")
        self.assertGreaterEqual(i["top_disputed"]["Tone too loud"], 1)
        self.assertTrue(any(e["action"] == "sent for review" for e in W.audit("Admin")))
        self.assertEqual(code(W.insights, "Creator"), 403)
if __name__ == "__main__": unittest.main()
