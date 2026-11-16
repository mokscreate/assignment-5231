from playwright.sync_api import sync_playwright
js="""(policy)=>{const T=window.__test;T.setSel('Jurong East');T.start();document.getElementById('bs').click();const out=[];
 for(let d=1;d<=7;d++){let G=T.G;
  if(policy!='none'){const lim={gate:4,esc:3,sign:2,guide:2,crew:3},cost={gate:120,esc:160,sign:90,guide:80,crew:140};
    const lv=()=>({gate:G.gates-2,esc:G.esc-1,sign:G.sign,guide:G.guide,crew:G.crew});
    for(const k of G.rec){G=T.G;if(k!='clean'&&lv()[k]<lim[k]&&G.coins>cost[k]+30)T.buy(k);}
    if(policy=='smart'){G=T.G;if(G.gates<3&&G.coins>200)T.buy('gate');G=T.G;if(G.esc<2&&G.coins>240)T.buy('esc');}}
  T.openDay();document.getElementById('modal').classList.remove('on');G=T.G;
  let n=0;while(G.phase=='run'&&n<80000){T.step(0.05);n++;}
  const rep=JSON.stringify(G.report.top),inc=G.incK;out.push([d,inc,Math.round(G.coins),+G.rating.toFixed(2),rep,G.rec.join('+')]);
  if(G.over)break;T.next();}
 return out;}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/build/game3.html'); pg.wait_for_timeout(200)
    for pol in ('none','follow','follow','smart','smart'):
        print(pol); [print('  ',r) for r in pg.evaluate(js,pol)]
    print(errs); b.close()
