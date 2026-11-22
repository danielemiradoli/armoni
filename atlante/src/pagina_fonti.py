"""Rigenera web/fonti.html da LICENZE.md, così la pagina pubblica dice le stesse cose del repository."""
from pathlib import Path
import markdown

ROOT = Path(__file__).resolve().parent.parent
PAGINA = '''<!DOCTYPE html>
<html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Fonti e licenze · ArMoni · Atlante</title><link href="lib/fonts.css" rel="stylesheet">
<style>
:root{color-scheme:light dark;--bg:light-dark(#fbfbf9,#0b1430);--ink:light-dark(#121a33,#eef0f6);--line:light-dark(#dde1ec,#22305e);--co:light-dark(#1f3c96,#8fa9ff)}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 "Instrument Sans",system-ui,sans-serif}
main{max-width:920px;margin:0 auto;padding:28px 18px 60px}
h1,h2{font-family:Newsreader,Georgia,serif;font-weight:600;line-height:1.1} h1{font-size:34px}
a{color:var(--co)} table{border-collapse:collapse;width:100%;font-size:14.5px;margin:16px 0} th,td{border-bottom:1px solid var(--line);text-align:left;vertical-align:top;padding:8px 6px}
code{font-size:.92em} .torna{display:inline-block;margin-bottom:18px}
</style></head><body><main>
<a class="torna" href="./">← Torna all'atlante</a>
@@CORPO@@
<h2>Rigenerare e verificare</h2>
<p>Codice, query e misure sono nel repository pubblico <a href="https://github.com/danielemiradoli/armoni">github.com/danielemiradoli/armoni</a>, cartella <code>atlante/</code>. Ogni livello ha il suo documento di misura in <code>atlante/out/</code>; le regole con cui entra ogni fonte sono in <code>docs/protocollo_ingestione.md</code>.</p>
</main></body></html>
'''

corpo = markdown.markdown((ROOT / 'LICENZE.md').read_text(encoding='utf-8'), extensions=['tables'])
(ROOT / 'web/fonti.html').write_text(PAGINA.replace('@@CORPO@@', corpo), encoding='utf-8')
