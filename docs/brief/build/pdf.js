const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
p.on('pageerror',e=>console.log('err',e.message));
await p.goto('file:///home/claude/brief/render.html');await p.waitForFunction('window.done',{timeout:120000});
console.log('overflow',JSON.stringify(await p.evaluate('window.overflow')),'pages',await p.evaluate('document.querySelectorAll(".page").length'));
await p.pdf({path:'/home/claude/brief/brief_v1.pdf',preferCSSPageSize:true,printBackground:true});await b.close()})();
