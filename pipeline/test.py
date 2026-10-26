from playwright.sync_api import sync_playwright
import time,sys
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1400,'height':1000})
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    t=time.time(); pg.goto('file:///home/claude/work/site/index.html#wzrost'); pg.wait_for_timeout(1200); print('load s',round(time.time()-t,2))
    for tab in ['wzrost','kohorty','lejek','zdarzenia','prio','unk','dane']:
        t=time.time(); pg.evaluate(f"location.hash='{tab}'"); pg.wait_for_timeout(700)
        pg.screenshot(path=f'shot_{tab}.png',full_page=True)
    print('errors',errs[:10]); print(pg.inner_text('#s-dane')[:700])
    b.close()
