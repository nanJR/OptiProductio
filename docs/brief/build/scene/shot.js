const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch({args:['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist']});
for(const v of [1,2]){const p=await b.newPage({viewport:{width:1800,height:1100},deviceScaleFactor:2});
p.on('console',m=>console.log('console',m.text()));p.on('pageerror',e=>console.log('err',e.message));
await p.goto('file:///home/claude/brief/scene/scene.html#'+v);await p.waitForFunction('window.done',{timeout:60000});
await p.screenshot({path:`/home/claude/brief/view${v}.png`});}
await b.close()})();
