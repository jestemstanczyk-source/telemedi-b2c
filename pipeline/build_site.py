import json
t=open('site/template.html').read()
t=t.replace('/*__CONTENT__*/',open('site/content.js').read())
t=t.replace('/*__DATA__*/',open('data.json').read()).replace('/*__CONTROL__*/',open('control_totals.json').read())
open('site/index.html','w').write(t); print('MB',len(t)/1e6)
