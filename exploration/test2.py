from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); errs=[]
    pg=b.new_page(viewport={'width':1400,'height':1000}); pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/work/site/index.html#zdarzenia'); pg.wait_for_timeout(900)
    pg.screenshot(path='shot_zdarzenia.png',full_page=True)
    pg.click("button[data-e='E4'][data-k='lejek']"); pg.wait_for_timeout(1200)
    pg.screenshot(path='shot_e4.png',full_page=True)
    print(pg.inner_text('#f3')); print(pg.inner_text('#f4')[:900])
    # filter test: uncheck all acq except tiktok in cohorts
    pg.evaluate("location.hash='kohorty'"); pg.wait_for_timeout(800)
    m=b.new_page(viewport={'width':390,'height':844},color_scheme='dark'); m.on('pageerror',lambda e:errs.append('m:'+str(e)))
    m.goto('file:///home/claude/work/site/index.html#wzrost'); m.wait_for_timeout(1200); m.screenshot(path='shot_mobile_dark.png',full_page=False)
    print('errors',errs); b.close()
