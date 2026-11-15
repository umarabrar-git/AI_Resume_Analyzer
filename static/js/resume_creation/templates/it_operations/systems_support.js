const esc=(v)=>String(v==null?"":v).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const safe=(fn,v)=>typeof fn==="function"?fn(v):esc(v);
export function renderSystemsSupportTemplate(content, escapeHtml) {
 const e=v=>safe(escapeHtml,v),d=content||{},p=d.personal_information||{},hide=new Set(d.hidden_sections||[]),a=v=>Array.isArray(v)?v:[];
 const date=x=>[x.start_date||"",x.current?"Present":x.end_date||""].filter(Boolean).map(e).join(" – ");
 const sec=(k,t,b)=>b&&!hide.has(k)?'<section class="ss-section" data-section="'+k+'"><h2>'+t+'</h2>'+b+'</section>':"";
 const jobs=a(d.experience).map(x=>'<article class="ss-entry"><div class="ss-head"><div><h3>'+e(x.title||"")+'</h3><p>'+e(x.company||"")+(x.location?" · "+e(x.location):"")+'</p></div><time>'+date(x)+'</time></div>'+(x.summary?"<p>"+e(x.summary)+"</p>":"")+(a(x.bullets).length?"<ul>"+a(x.bullets).map(v=>"<li>"+e(v)+"</li>").join("")+"</ul>":"")+"</article>").join("");
 const projects=a(d.projects).map(x=>'<article class="ss-entry"><h3>'+e(x.name||"")+'</h3>'+(x.description?"<p>"+e(x.description)+"</p>":"")+(a(x.technologies).length?'<p class="ss-tools">'+a(x.technologies).map(e).join(" · ")+"</p>":"")+"</article>").join("");
 const skills=a(d.skills).length?'<p class="ss-skills">'+a(d.skills).map(e).join(" · ")+"</p>":Object.entries(d.skills_by_category||{}).filter(([,v])=>Array.isArray(v)&&v.length).map(([k,v])=>'<p class="ss-skill"><b>'+e(k)+'</b> '+v.map(e).join(" · ")+"</p>").join("");
 const education=a(d.education).map(x=>"<p><b>"+e(x.degree||"")+"</b> · "+e(x.institution||"")+" <time>"+date(x)+"</time></p>").join("");
 const certs=a(d.certifications).map(x=>"<p>"+e(x.name||"")+(x.issuer?" · "+e(x.issuer):"")+"</p>").join("");
 const contact=[p.email,p.phone,p.location].filter(Boolean).map(e);
 [["LinkedIn",p.linkedin],["Website",p.website],["Portfolio",p.portfolio]].forEach(([n,u])=>{if(u&&/^https?:\/\//i.test(String(u)))contact.push('<a href="'+e(u)+'" target="_blank" rel="noopener noreferrer">'+n+"</a>");});
 const root=document.createElement("div");
 root.innerHTML='<div class="resume-template-systems-support"><header class="ss-header"><p class="ss-kicker">IT OPERATIONS · SERVICE DELIVERY · SYSTEMS</p><h1>'+e(p.full_name||"Your Name")+'</h1><p class="ss-role">'+e(p.professional_title||"IT Support Specialist")+'</p><div class="ss-contact">'+contact.join('<span>•</span>')+'</div></header><main class="ss-main">'+sec("summary","Professional Summary",d.summary?"<p>"+e(d.summary)+"</p>":"")+sec("experience","IT Support Experience",jobs)+sec("skills","Technical Skills",skills)+sec("projects","Systems & Support Projects",projects)+sec("education","Education",education)+sec("certifications","Certifications",certs)+"</main></div>';
 const main=root.firstElementChild.querySelector(".ss-main");a(d.section_order).forEach(k=>{const n=Array.from(main.children).find(x=>x.dataset.section===k);if(n)main.appendChild(n);});return root.firstElementChild.outerHTML;
}