// node render.js <out.pdf>   (Playwright with Chromium)
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + path.join(__dirname, 'manual.html')); await p.waitForTimeout(800);
  const over = await p.evaluate(() => [...document.querySelectorAll('.page')].map((pg, i) => {
    const c = pg.querySelector('.content'); return c.scrollHeight > c.clientHeight + 1 ? `page ${i + 1}: content ${c.scrollHeight} > ${c.clientHeight}` : null; }).filter(Boolean));
  console.log(over.length ? 'OVERFLOW\n' + over.join('\n') : 'all pages fit');
  await p.pdf({ path: process.argv[2] || 'manual.pdf', format: 'A4', printBackground: true, margin: { top: 0, bottom: 0, left: 0, right: 0 } });
  await b.close();
})();
