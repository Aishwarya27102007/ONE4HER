"""BrandShield AI - run with:  python app.py
Then open http://localhost:8000 (it opens automatically).
Needs only Python 3, no installs."""
import http.server, socketserver, threading, webbrowser

PAGE = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>BrandShield AI: pre-publication brand review</title>
<style>
:root{--bg:#f6f7f9;--card:#fff;--ink:#17202e;--mute:#5d6878;--line:#dde1e8;--acc:#2b4dff;--acc-ink:#fff;--hi:#c62828;--hib:#fdeaea;--me:#a25b00;--meb:#fff3df;--lo:#2b5fa8;--lob:#e8f0fb;--ok:#1b7a43;--okb:#e5f5ec;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#10141b;--card:#181e28;--ink:#e8ecf3;--mute:#9aa5b8;--line:#2a3342;--acc:#7b93ff;--acc-ink:#0b1020;--hi:#ff8a80;--hib:#3a1c1c;--me:#ffc46b;--meb:#3a2d12;--lo:#8ab4f8;--lob:#172439;--ok:#6fd49a;--okb:#14301f}}
:root[data-theme="dark"]{--bg:#10141b;--card:#181e28;--ink:#e8ecf3;--mute:#9aa5b8;--line:#2a3342;--acc:#7b93ff;--acc-ink:#0b1020;--hi:#ff8a80;--hib:#3a1c1c;--me:#ffc46b;--meb:#3a2d12;--lo:#8ab4f8;--lob:#172439;--ok:#6fd49a;--okb:#14301f}
html{scroll-padding-top:env(safe-area-inset-top,0px)}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 "Segoe UI",system-ui,-apple-system,Roboto,Helvetica,Arial,sans-serif}
header{display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between;padding:14px 20px;border-bottom:1px solid var(--line);background:var(--card)}
h1{font:700 19px/1.2 Georgia,"Times New Roman",serif;margin:0}
h1 small{display:block;font:400 12.5px/1.4 "Segoe UI",system-ui,sans-serif;color:var(--mute);margin-top:2px}
h2{font:700 16px/1.3 Georgia,serif;margin:0 0 8px}
.roles{display:flex;gap:6px;align-items:center;font-size:13px;color:var(--mute)}
.roles button{padding:6px 12px}
button{font:inherit;cursor:pointer;border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:8px;padding:7px 12px}
button:hover{border-color:var(--acc)}
button:focus-visible,textarea:focus-visible,input:focus-visible,select:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
button.on,button.pri{background:var(--acc);color:var(--acc-ink);border-color:var(--acc)}
button:disabled{opacity:.45;cursor:not-allowed}
main{display:grid;grid-template-columns:260px minmax(0,1fr) 300px;gap:16px;padding:16px 20px;max-width:1400px;margin:0 auto}
@media(max-width:1000px){main{grid-template-columns:1fr}}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px}
.stack>*+*{margin-top:12px}
textarea,input[type=text],select{width:100%;font:inherit;color:var(--ink);background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:9px}
textarea{min-height:130px;resize:vertical}
.row{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.pill{display:inline-block;padding:2px 9px;border-radius:99px;font-size:12px;font-weight:600}
.s-draft{background:var(--lob);color:var(--lo)}.s-review{background:var(--meb);color:var(--me)}.s-ok{background:var(--okb);color:var(--ok)}.s-chg{background:var(--hib);color:var(--hi)}
.kb h3{font-size:13px;margin:12px 0 4px;color:var(--mute);font-weight:600}
.kb ul{margin:0;padding-left:18px;font-size:13.5px}
.kb li{margin:2px 0}
.f{border:1px solid var(--line);border-left-width:5px;border-radius:8px;padding:11px 12px;background:var(--card)}
.f.HIGH{border-left-color:var(--hi)}.f.MEDIUM{border-left-color:var(--me)}.f.LOW{border-left-color:var(--lo)}
.f.done{opacity:.72}
.f .t{display:flex;flex-wrap:wrap;gap:8px;align-items:center;font-weight:600}
.sev{font-size:12px;padding:1px 8px;border-radius:6px;font-weight:700}
.sev.HIGH{background:var(--hib);color:var(--hi)}.sev.MEDIUM{background:var(--meb);color:var(--me)}.sev.LOW{background:var(--lob);color:var(--lo)}
.src{font-size:13px;color:var(--mute);margin:6px 0;padding:6px 9px;background:var(--bg);border-radius:6px}
.src b{color:var(--ink)}
.chk{color:var(--ok);font-weight:600}
.warn{color:var(--me);font-weight:600}
mark{background:var(--meb);color:inherit;padding:0 2px;border-radius:3px}
.hist{font-size:13px;max-height:260px;overflow:auto}
.hist div{padding:5px 0;border-bottom:1px solid var(--line)}
.hist span{color:var(--mute)}
.mut{color:var(--mute);font-size:13px}
.empty{text-align:center;color:var(--mute);padding:26px 10px;border:1px dashed var(--line);border-radius:8px}
.stat{display:flex;gap:6px;flex-wrap:wrap}
</style>
</head>
<body>
<header>
 <h1>BrandShield AI<small>Check a draft against GlowMax’s approved sources, review the reasons, then let a human decide.</small></h1>
 <div class="roles" role="group" aria-label="Viewing as"><span>Viewing as</span>
  <button id="rCreator" class="on">Creator</button><button id="rReviewer">Reviewer</button></div>
</header>
<main>
 <aside class="card kb stack" aria-label="Approved brand sources">
  <div><h2>Approved sources</h2><div class="mut">Brand: GlowMax (skincare). Every finding cites one of these.</div></div>
  <div id="kb"></div>
 </aside>
 <section class="stack" aria-label="Review">
  <div class="card">
   <div class="row" style="justify-content:space-between"><h2 style="margin:0">Draft post</h2><span id="status" class="pill s-draft">Draft</span></div>
   <textarea id="draft" aria-label="Draft post text" placeholder="Paste your post here"></textarea>
   <div class="row" style="margin-top:8px">
    <label class="row"><input type="checkbox" id="hasImg"> Image attached</label>
    <input type="file" id="file" accept="image/*" aria-label="Upload image">
    <img id="prev" alt="" style="display:none;max-height:56px;border-radius:6px;border:1px solid var(--line)">
    <input type="text" id="alt" placeholder="Alt text for the image (leave empty to test)" style="flex:1;min-width:180px" aria-label="Image alt text">
   </div>
   <div class="row" style="margin-top:10px">
    <button class="pri" id="run">Check against approved sources</button>
    <button id="sample">Load sample post</button>
    <button id="submit" disabled>Send to reviewer</button>
   </div>
   <p class="mut" id="hint" style="margin:8px 0 0"></p>
  </div>
  <div id="results"></div>
 </section>
 <aside class="stack" aria-label="Review trail">
  <div class="card" id="rev"></div>
  <div class="card"><h2>History</h2><div class="hist" id="hist"><div class="mut">Nothing yet.</div></div></div>
  <div class="card mut">This demo runs a rule engine over the approved sources, in your browser. Nothing you type is sent anywhere. AI never publishes: only a reviewer can approve.</div>
 </aside>
</main>
<script>
const SRC={
 C1:{name:"Claims policy §2",text:"Absolute safety claims such as “100% safe” are not permitted. Approved wording: “Dermatologically tested”.",quote:"Approved wording: “Dermatologically tested”"},
 C2:{name:"Claims policy §4",text:"Superlative or ranking claims (“No.1”, “best in India”) need a published ranking source attached, or must be removed.",quote:"need a published ranking source attached, or must be removed"},
 C3:{name:"Claims policy §5",text:"Words that promise results (“guaranteed”, “miracle”, “cure”, “instant”) are not permitted for cosmetics.",quote:"promise results"},
 P1:{name:"Price sheet, Oct 2026",text:"GlowMax Cream: ₹549 (inclusive of taxes). Older prices must not be used.",quote:"GlowMax Cream: ₹549"},
 T1:{name:"Terminology",text:"Write the brand as “GlowMax” (one word, capital G and M). Say “affordable”, never “cheap”.",quote:"Write the brand as “GlowMax”"},
 T2:{name:"Terminology",text:"Say “affordable”, never “cheap”.",quote:"never “cheap”"},
 V1:{name:"Tone guide",text:"Warm and confident, never shouting. One exclamation mark at most; no all-caps words.",quote:"One exclamation mark at most"},
 A1:{name:"Accessibility standard",text:"Every image must carry alt text that describes what it shows.",quote:"must carry alt text"}
};
const SRC_ALL=Object.values(SRC).map(s=>s.text).join(" ");
const rules=[
 {re:/100\s?%\s?safe/gi,sev:"HIGH",title:"Unsupported safety claim",why:"“100% safe” is an absolute claim with no approved source behind it.",s:"C1",fix:()=>"Dermatologically tested",conf:96},
 {re:/,?\s*(the\s+)?no\.?\s?1\b[^,.!?]*/gi,sev:"HIGH",title:"Ranking claim cannot be proven",why:"“No.1” needs a published ranking source. None is on file.",s:"C2",fix:()=>"",conf:92,hint:"Remove it, or attach a valid ranking source."},
 {re:/\b(guaranteed|miracle|cure[sd]?|instant results?)\b/gi,sev:"HIGH",title:"Promises a result",why:"Cosmetics cannot promise results.",s:"C3",fix:m=>"visibly cared-for skin",conf:70},
 {re:/glow\s?max/gi,sev:"LOW",title:"Brand name written differently",why:"The brand must be written exactly as “GlowMax”.",s:"T1",fix:()=>"GlowMax",conf:90,skip:m=>m==="GlowMax"},
 {re:/\bcheap(est)?\b/gi,sev:"LOW",title:"Off-brand word",why:"The terminology list says never to use “cheap”.",s:"T2",fix:()=>"affordable",conf:88},
 {re:/!{2,}/g,sev:"LOW",title:"Tone too loud",why:"The tone guide allows one exclamation mark at most.",s:"V1",fix:()=>"!",conf:85},
 {re:/\b[A-Z]{4,}\b/g,sev:"LOW",title:"All-caps word",why:"The tone guide says no all-caps words.",s:"V1",fix:m=>m[0]+m.slice(1).toLowerCase(),conf:55}
];
let st={text:"",findings:[],ran:false,status:"Draft",hist:[],role:"Creator",revNote:"",img:false,alt:""};
const $=id=>document.getElementById(id);
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const log=(who,msg)=>{st.hist.unshift({t:new Date().toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"}),who,msg});};
const verified=k=>SRC_ALL.includes(SRC[k].quote);

function analyse(text){
 const out=[];let n=0;
 rules.forEach(r=>{for(const m of text.matchAll(r.re)){const raw=m[0];if(r.skip&&r.skip(raw))continue;
  out.push({id:++n,sev:r.sev,matched:raw,title:r.title,why:r.why,s:r.s,conf:r.conf,fix:r.fix(raw),hint:r.hint||"",status:"open",note:""});}});
 for(const m of text.matchAll(/₹\s?([\d,]+)/g)){const v=parseInt(m[1].replace(/,/g,""),10);
  if(v!==549)out.push({id:++n,sev:"MEDIUM",matched:m[0],title:"Price is outdated",why:"The approved price sheet says ₹549, not ₹"+v+".",s:"P1",conf:94,fix:"₹549",hint:"",status:"open",note:""});}
 if(st.img&&!st.alt.trim())out.push({id:++n,sev:"LOW",matched:"",title:"Image has no alt text",why:"Screen-reader users cannot tell what the image shows.",s:"A1",conf:99,fix:null,hint:"Add a short description in the alt text box above, then check again.",status:"open",note:""});
 const o={HIGH:0,MEDIUM:1,LOW:2};return out.sort((a,b)=>o[a.sev]-o[b.sev]);
}
function tidy(t){return t.replace(/\s+,/g,",").replace(/,\s*,/g,",").replace(/ {2,}/g," ").trim();}
function act(id,kind){
 const f=st.findings.find(x=>x.id===id);if(!f)return;
 if(kind==="fix"){
  if(f.fix===null){return;}
  if(!st.text.includes(f.matched)){$("hint").textContent="That text is no longer in the draft. Run the check again.";return;}
  st.text=tidy(st.text.replace(f.matched,f.fix));f.status="fixed";log("Creator","Accepted fix: "+f.title);
 }else if(kind==="edit"||kind==="dis"){st.pending={id:id,kind:kind};}
 else if(kind==="save"){
  const v=($("pin")||{value:""}).value;
  if(st.pending.kind==="edit"){
   if(f.matched&&st.text.includes(f.matched))st.text=tidy(st.text.replace(f.matched,v));
   f.status="edited";f.note=v;log("Creator","Edited wording for: "+f.title);
  }else{
   if(!v.trim()){$("pin").placeholder="Please write a reason";$("pin").focus();return;}
   f.status="disputed";f.note=v;log("Creator","Disputed: "+f.title+" (“"+v+"”)");
  }
  st.pending=null;
 }else if(kind==="cancel"){st.pending=null;}
 render();
}
function render(){
 // roles
 $("rCreator").className=st.role==="Creator"?"on":"";$("rReviewer").className=st.role==="Reviewer"?"on":"";
 const isC=st.role==="Creator",locked=st.status==="In review"||st.status==="Approved";
 $("draft").value=st.text;$("draft").disabled=!isC||locked;
 $("run").disabled=!isC||locked;$("hasImg").disabled=!isC||locked;$("alt").disabled=!isC||locked;
 const open=st.findings.filter(f=>f.status==="open").length;
 $("submit").disabled=!(isC&&st.ran&&open===0&&!locked);
 $("hint").textContent=!isC?"Reviewers read the draft and the creator’s decisions on the right.":locked?"The draft is locked while it is with the reviewer or approved.":!st.ran?"Step 1: check the draft. Step 2: decide on each finding. Step 3: send to a reviewer.":open?open+" finding"+(open>1?"s":"")+" still need your decision before you can send.":"All findings decided. You can send this to a reviewer.";
 const cls={Draft:"s-draft","In review":"s-review",Approved:"s-ok","Changes requested":"s-chg"}[st.status];
 $("status").className="pill "+cls;$("status").textContent=st.status;
 // results
 const R=$("results");
 if(!st.ran){R.innerHTML='<div class="empty">No findings yet. Load the sample post and press “Check against approved sources”.</div>';}
 else if(!st.findings.length){R.innerHTML='<div class="card"><b class="chk">No issues found.</b> This draft matches the approved sources. A reviewer still signs off.</div>';}
 else{
  const c={HIGH:0,MEDIUM:0,LOW:0};st.findings.forEach(f=>c[f.sev]++);
  R.innerHTML='<div class="card"><h2>Findings</h2><div class="stat"><span class="sev HIGH">'+c.HIGH+' high</span><span class="sev MEDIUM">'+c.MEDIUM+' medium</span><span class="sev LOW">'+c.LOW+' low</span></div></div>'+
  st.findings.map(f=>{const S=SRC[f.s],done=f.status!=="open",human=f.conf<70;
   const pend=st.pending&&st.pending.id===f.id;const btns=pend?'<input type="text" id="pin" style="flex:1;min-width:200px" aria-label="Your input" placeholder="'+(st.pending.kind==="edit"?"Type your own wording":"Why is this flag wrong?")+'" value="'+(st.pending.kind==="edit"?esc(f.fix||""):"")+'"><button class="pri" data-a="save" data-i="'+f.id+'">Save</button><button data-a="cancel" data-i="'+f.id+'">Cancel</button>':!done&&isC&&!locked?(f.fix!==null?'<button class="pri" data-a="fix" data-i="'+f.id+'">'+(f.fix===""?"Remove it":"Apply fix: “"+esc(f.fix)+"”")+'</button>':'')+'<button data-a="edit" data-i="'+f.id+'">Edit wording</button><button data-a="dis" data-i="'+f.id+'">Dispute</button>':
   (done?'<span class="pill s-ok">'+({fixed:"Fix applied",edited:"Edited",disputed:"Disputed"})[f.status]+'</span>'+(f.note?' <span class="mut">“'+esc(f.note)+'”</span>':''):'');
   return '<div class="f '+f.sev+(done?' done':'')+'"><div class="t"><span class="sev '+f.sev+'">'+f.sev+'</span>'+esc(f.title)+(f.matched?' <mark>'+esc(f.matched.trim())+'</mark>':'')+(human?' <span class="warn">Needs human check</span>':'')+'</div>'+
   '<div>'+esc(f.why)+(f.hint?' '+esc(f.hint):'')+'</div>'+
   '<div class="src"><b>Source: '+esc(S.name)+'.</b> “'+esc(S.quote)+'” <span class="'+(verified(f.s)?'chk':'warn')+'">'+(verified(f.s)?'Quote verified':'Quote not found')+'</span> · Confidence '+f.conf+'%</div>'+
   '<div class="row">'+btns+'</div></div>';}).join("");
  R.querySelectorAll("button[data-a]").forEach(b=>b.onclick=()=>act(+b.dataset.i,b.dataset.a));const pi=$("pin");if(pi)pi.focus();
 }
 // reviewer panel
 const rv=$("rev");
 if(st.status==="In review"&&st.role==="Reviewer"){
  const dis=st.findings.filter(f=>f.status==="disputed");
  rv.innerHTML='<h2>Your decision</h2><p class="mut" style="margin-top:0">'+st.findings.length+' findings were decided by the creator.'+(dis.length?' <b class="warn">'+dis.length+' disputed:</b> check the reasons on the left.':'')+'</p><textarea id="cmt" style="min-height:70px" placeholder="Comment (required if you request changes)"></textarea><div class="row" style="margin-top:8px"><button class="pri" id="ap">Approve for publishing</button><button id="rc">Request changes</button></div>';
  $("ap").onclick=()=>{st.status="Approved";log("Reviewer","Approved"+($("cmt").value?": "+$("cmt").value:""));render();};
  $("rc").onclick=()=>{const c=$("cmt").value.trim();if(!c){$("cmt").focus();$("cmt").placeholder="Please explain what to change";return;}st.status="Changes requested";st.ran=false;st.findings=[];log("Reviewer","Requested changes: "+c);st.revNote=c;render();};
 }else if(st.status==="Approved"){rv.innerHTML='<h2>Approved</h2><p class="mut" style="margin:0">A reviewer approved this version. It can now be published. The full trail is below.</p>';}
 else if(st.status==="Changes requested"){rv.innerHTML='<h2>Changes requested</h2><p style="margin:0">'+esc(st.revNote)+'</p><p class="mut">Switch to Creator, update the draft and check again.</p>';}
 else if(st.status==="In review"){rv.innerHTML='<h2>With the reviewer</h2><p class="mut" style="margin:0">Switch to “Reviewer” (top right) to approve or request changes.</p>';}
 else rv.innerHTML='<h2>Review</h2><p class="mut" style="margin:0">After you decide on every finding, send the draft to a reviewer. AI never publishes by itself.</p>';
 $("hist").innerHTML=st.hist.length?st.hist.map(h=>'<div><span>'+h.t+'</span> <b>'+h.who+'</b> '+esc(h.msg)+'</div>').join(""):'<div class="mut">Nothing yet.</div>';
}
function kb(){
 const li=a=>"<ul>"+a.map(x=>"<li>"+x+"</li>").join("")+"</ul>";
 $("kb").innerHTML='<h3>Approved claims</h3>'+li(["Dermatologically tested","Suitable for sensitive skin","Paraben-free"])+
 '<h3>Price sheet</h3>'+li(["GlowMax Cream: ₹549"])+
 '<h3>Not allowed</h3>'+li(["Absolute claims (“100% safe”)","Rankings without a source (“No.1”)","Result promises (“guaranteed”, “miracle”)"])+
 '<h3>Terms</h3>'+li(["Brand is “GlowMax”","“affordable”, never “cheap”"])+
 '<h3>Tone and access</h3>'+li(["One “!” at most, no all-caps","Every image needs alt text"]);
}
$("draft").oninput=e=>{st.text=e.target.value;};
$("alt").oninput=e=>{st.alt=e.target.value;};
$("hasImg").onchange=e=>{st.img=e.target.checked;};
$("file").onchange=e=>{const f=e.target.files[0];if(!f)return;if(!f.type.startsWith("image/")){$("hint").textContent="Please choose an image file.";return;}const p=$("prev");p.src=URL.createObjectURL(f);p.style.display="inline-block";$("hasImg").checked=true;st.img=true;log("Creator","Uploaded image: "+f.name);render();};
$("sample").onclick=()=>{st={text:"Meet GlowMax Cream: 100% safe, the No.1 cream in India! Now only ₹499. Buy today!!",findings:[],ran:false,status:"Draft",hist:[],role:"Creator",revNote:"",img:true,alt:""};$("hasImg").checked=true;$("alt").value="";log("Creator","Loaded sample post");render();};
$("run").onclick=()=>{st.text=$("draft").value;st.img=$("hasImg").checked;st.alt=$("alt").value;if(!st.text.trim()){$("hint").textContent="Write or paste a draft first.";return;}
 st.findings=analyse(st.text);st.ran=true;if(st.status==="Changes requested")st.status="Draft";log("AI check",st.findings.length+" finding"+(st.findings.length===1?"":"s")+" against approved sources");render();};
$("submit").onclick=()=>{st.status="In review";log("Creator","Sent to reviewer");render();};
$("rCreator").onclick=()=>{st.role="Creator";render();};
$("rReviewer").onclick=()=>{st.role="Reviewer";render();};
kb();render();
</script>
</body>
</html>
'''

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body = PAGE.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, *a):
        pass

if __name__ == "__main__":
    PORT = 8000
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as srv:
        url = f"http://localhost:{PORT}"
        print("BrandShield AI running at", url, "(Ctrl+C to stop)")
        threading.Timer(1, lambda: webbrowser.open(url)).start()
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("Stopped.")
