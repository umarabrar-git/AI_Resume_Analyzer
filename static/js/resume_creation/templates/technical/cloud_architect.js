export function renderCloudArchitectTemplate(content, escapeHtml) {
  const e = typeof escapeHtml === "function" ? escapeHtml : (value) => String(value ?? "").replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const d = content || {}, p = d.personal_information || {}, hidden = new Set(Array.isArray(d.hidden_sections) ? d.hidden_sections : []);
  const arr = (v) => Array.isArray(v) ? v : [];
  const safeUrl = (v) => /^https?:\/\//i.test(String(v || "").trim()) ? e(String(v).trim()) : "";
  const contact = [p.email,p.phone,p.location].filter(Boolean).map(e);
  [["LinkedIn",p.linkedin],["GitHub",p.github],["Portfolio",p.portfolio]].forEach(([label,url]) => { const u=safeUrl(url); if(u) contact.push('<a href="'+u+'" target="_blank" rel="noopener noreferrer">'+label+'</a>'); });
  const section = (key,title,body) => body ? '<section class="ca-section" data-section="'+e(key)+'"><h2>'+e(title)+'</h2>'+body+'</section>' : "";
  const bullets = (items) => arr(items).filter(Boolean).map(x=>"<li>"+e(x)+"</li>").join("");
  const skills = d.skills_by_category && typeof d.skills_by_category === "object"
    ? Object.entries(d.skills_by_category).filter(([,v])=>Array.isArray(v)&&v.length).map(([k,v])=>'<div class="ca-skill"><strong>'+e(k)+'</strong><p>'+v.map(e).join(" · ")+'</p></div>').join("")
    : arr(d.skills).length ? '<p>'+arr(d.skills).map(e).join(" · ")+'</p>' : "";
  const experience = arr(d.experience).map(x=>'<article class="ca-entry"><div class="ca-entry-head"><div><h3>'+e(x.title||"")+'</h3><p>'+e(x.company||"")+'</p></div><time>'+e(x.start_date||"")+(x.end_date||x.current?" – "+e(x.current?"Present":x.end_date):"")+'</time></div>'+(x.summary?'<p>'+e(x.summary)+'</p>':"")+(x.bullets?.length?'<ul>'+bullets(x.bullets)+'</ul>':"")+'</article>').join("");
  const projects = arr(d.projects).map(x=>'<article class="ca-entry"><div class="ca-entry-head"><h3>'+e(x.name||"")+'</h3><span>'+e(x.role||"")+'</span></div>'+(x.description?'<p>'+e(x.description)+'</p>':"")+(x.technologies?.length?'<p class="ca-stack"><b>Architecture / Stack:</b> '+x.technologies.map(e).join(" · ")+'</p>':"")+(x.achievements?.length?'<ul>'+bullets(x.achievements)+'</ul>':"")+(safeUrl(x.url)?'<a href="'+safeUrl(x.url)+'" target="_blank" rel="noopener noreferrer">Project details</a>':"")+'</article>').join("");
  const education = arr(d.education).map(x=>'<article class="ca-entry"><h3>'+e(x.degree||"")+(x.field_of_study?" — "+e(x.field_of_study):"")+'</h3><p>'+e(x.institution||"")+'</p>'+(x.coursework?'<p>'+e(x.coursework)+'</p>':"")+'</article>').join("");
  const certs = arr(d.certifications).map(x=>'<p class="ca-credential"><b>'+e(x.name||"")+'</b>'+(x.issuer?" · "+e(x.issuer):"")+(x.issue_date?" · "+e(x.issue_date):"")+'</p>').join("");
  const languages = arr(d.languages).map(x=>'<p class="ca-credential">'+e(x.language||"")+(x.proficiency?" · "+e(x.proficiency):"")+'</p>').join("");
  const custom = arr(d.custom_sections).filter(x=>arr(x.items).length&&!hidden.has("custom:"+x.id)).map(x=>section("custom:"+x.id,x.title||"Additional Information",arr(x.items).map(y=>'<article class="ca-entry"><h3>'+e(y.title||"")+'</h3>'+(y.description?'<p>'+e(y.description)+'</p>':"")+(y.bullets?.length?'<ul>'+bullets(y.bullets)+'</ul>':"")+'</article>').join(""))).join("");
  const summary = d.summary ? "<p>"+e(d.summary)+"</p>" : "";
  const root=document.createElement("div");
  root.innerHTML='<div class="resume-template-cloud-architect"><header class="ca-header"><div><p class="ca-kicker">CLOUD PLATFORMS / DISTRIBUTED SYSTEMS / RELIABILITY</p><h1>'+e(p.full_name||"Your Name")+'</h1><p class="ca-role">'+e(p.professional_title||"")+'</p></div><div class="ca-contact">'+contact.join("")+'</div></header><div class="ca-layout"><aside class="ca-sidebar">'+section("skills","Cloud & Infrastructure Toolkit",skills)+section("certifications","Cloud Credentials",certs)+section("languages","Languages",languages)+'<div class="ca-note"><span>DESIGN PRINCIPLE</span><b>Secure · Scalable · Resilient</b></div></aside><main class="ca-main">'+section("summary","Architecture Profile",summary)+section("experience","Professional Experience",experience)+section("projects","Cloud Architecture & Delivery",projects)+section("education","Education",education)+custom+'</main></div></div>';
  root.querySelectorAll("[data-section]").forEach(node=>{if(hidden.has(node.dataset.section)||!node.textContent.trim())node.classList.add("is-hidden");});
  const order=arr(d.section_order), nodes=Array.from(root.querySelectorAll("[data-section]"));
  order.forEach(key=>{const node=nodes.find(n=>n.dataset.section===key);if(node?.parentElement)node.parentElement.appendChild(node);});
  return root.firstElementChild.outerHTML;
}
