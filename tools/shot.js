const {chromium}=require('playwright');
(async()=>{
 const [,,url,out,w]=process.argv;
 const b=await chromium.launch(); const p=await b.newPage({viewport:{width:+w||1440,height:900}});
 const fails=[]; p.on('requestfailed',r=>fails.push(r.url()));
 await p.goto(url,{waitUntil:'networkidle',timeout:60000}).catch(e=>console.log('goto',e.message));
 await p.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=300){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,250))}document.querySelector('#cookieBarBtn')?.click();window.scrollTo(0,0)});
 await p.waitForTimeout(1500);
 await p.screenshot({path:out,fullPage:true});
 console.log('failed:',[...new Set(fails.map(u=>new URL(u).host))].join(' '));
 await b.close();})();
