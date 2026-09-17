from urllib.request import Request, urlopen
from urllib.parse import quote
from xml.etree import ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import timezone
import re, html

UA = "TwinNews/0.2 (+local personal news reader)"
MEDIA='{http://search.yahoo.com/mrss/}'

def _text(el, names):
    for name in names:
        child = el.find(name)
        if child is not None and child.text: return child.text.strip()
    return ""

def _clean(s):
    if not s: return ""
    s = re.sub(r"<[^>]+>", " ", html.unescape(s)); return re.sub(r"\s+", " ", s).strip()

def _date(s):
    if not s: return None
    try: return parsedate_to_datetime(s).astimezone(timezone.utc).isoformat()
    except Exception: return s

def _image(el, raw=''):
    for tag in [f'{MEDIA}content',f'{MEDIA}thumbnail','enclosure']:
        x=el.find(tag)
        if x is not None:
            u=x.attrib.get('url','')
            if u and (tag!='enclosure' or x.attrib.get('type','').startswith('image/')): return u
    m=re.search(r'<img[^>]+src=["\']([^"\']+)', raw or '', re.I)
    return html.unescape(m.group(1)) if m else ''

def fetch_xml(url, timeout=15):
    req=Request(url, headers={"User-Agent":UA,"Accept":"application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9,*/*;q=0.1"})
    with urlopen(req, timeout=timeout) as r: return r.read()

def parse_feed(xml_bytes, source_name):
    root=ET.fromstring(xml_bytes); items=[]
    for it in root.findall(".//item"):
        title=_clean(_text(it,["title"])); link=_text(it,["link"]); guid=_text(it,["guid"])
        raw=_text(it,["description","{http://purl.org/rss/1.0/modules/content/}encoded"]); summary=_clean(raw)
        pub=_date(_text(it,["pubDate","{http://purl.org/dc/elements/1.1/}date"])); author=_clean(_text(it,["author","{http://purl.org/dc/elements/1.1/}creator"]))
        if title and (link or guid): items.append({"source":source_name,"title":title,"url":link or guid,"summary":summary,"published_at":pub,"author":author,'image_url':_image(it,raw)})
    if items: return items
    ns="{http://www.w3.org/2005/Atom}"
    for ent in root.findall(f".//{ns}entry"):
        title=_clean(_text(ent,[f"{ns}title"])); link=""
        for l in ent.findall(f"{ns}link"):
            if l.attrib.get("rel","alternate") in ("alternate","") and l.attrib.get("href"): link=l.attrib["href"]; break
        raw=_text(ent,[f"{ns}summary",f"{ns}content"]); summary=_clean(raw); pub=_text(ent,[f"{ns}published",f"{ns}updated"]); author=_clean(_text(ent,[f"{ns}author/{ns}name"]))
        if title and link: items.append({"source":source_name,"title":title,"url":link,"summary":summary,"published_at":pub,"author":author,'image_url':_image(ent,raw)})
    return items

def source_url(src):
    if src.get("type") == "arxiv":
        q=quote(src.get("query","cat:cs.AI"), safe=":"); n=int(src.get("max_results",40)); return f"https://export.arxiv.org/api/query?search_query={q}&start=0&max_results={n}&sortBy=submittedDate&sortOrder=descending"
    return src["url"]

def fetch_source(src): return parse_feed(fetch_xml(source_url(src)), src["name"])
