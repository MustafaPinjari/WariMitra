const fs = require('fs');
const path = require('path');

function walk(dir) {
  let results = [];
  const list = fs.readdirSync(dir);
  list.forEach(file => {
    file = path.join(dir, file);
    const stat = fs.statSync(file);
    if (stat && stat.isDirectory()) { 
      results = results.concat(walk(file));
    } else { 
      results.push(file);
    }
  });
  return results;
}

const files = walk('d:\\91901\\WariMitra\\frontend\\src\\app').filter(f => f.endsWith('.tsx'));
files.forEach(f => {
  let content = fs.readFileSync(f, 'utf8');
  if (content.includes("import GoogleMapContainer from '@/components/maps/GoogleMapContainer';")) {
    const replacement = `import dynamic from 'next/dynamic';\nconst GoogleMapContainer = dynamic(() => import('@/components/maps/GoogleMapContainer'), { ssr: false });`;
    if (content.includes("import dynamic from 'next/dynamic';")) {
       content = content.replace("import GoogleMapContainer from '@/components/maps/GoogleMapContainer';", `const GoogleMapContainer = dynamic(() => import('@/components/maps/GoogleMapContainer'), { ssr: false });`);
    } else {
       content = content.replace("import GoogleMapContainer from '@/components/maps/GoogleMapContainer';", replacement);
    }
    fs.writeFileSync(f, content, 'utf8');
    console.log('Fixed', f);
  }
});
