export function renderEducatorStandardTemplate(content, escapeHtml) {
  const e = typeof escapeHtml === "function" ? escapeHtml : (v) => String(v ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const d = content || {}, p = d.personal_information || {}, hidden = new Set(d.hidden_sections || []);
  const dates = x => [x.start_date, x.current ? "Present" : x.end_date].filter(Boolean).map(e).join(" – ");
  const section = (key,title,body) => body ? '<section data-section="'+key+'"><h2>'+title+'</h2>'+body+'</section>' : "";
  const list = xs => Array.isArray(xs) ? xs.filter(Boolean).map(x=>"<li>"+e(x)+"</li>").join("") : "";
  const contact = [p.email,p.phone,p.location].filter(Boolean).map(e);
  [[ "LinkedIn",p.linkedin ],["Portfolio",p.portfolio],["Website",p.website]].forEach(([label,url])=>{if(url)contact.push('<a href="'+e(url)+'" target="_blank" rel="noopener noreferrer">'+label+"</a>");});
  const skills = Object.entries(d.skills_by_category || {}).filter(([,v])=>Array.isArray(v)&&v.length).map(([k,v])=>'<div class="es-skill"><strong>'+e(k)+'</strong><span>'+e(v.join(", "))+"</span></div>").join("") || (d.skills?.length ? '<div class="es-skill">'+e(d.skills.join(", "))+"</div>" : "");
  const exp = (d.experience||[]).map(x=>'<article class="es-entry"><div class="es-entry-head"><h3>'+e(x.title||"")+'</h3><time>'+dates(x)+'</time></div><div class="es-meta">'+e(x.company||"")+(x.location?" · "+e(x.location):"")+"</div>"+(x.description?"<p>"+e(x.description)+"</p>":"")+((x.bullets||x.achievements)?"<ul>"+list([...(x.bullets||[]),...(x.achievements||[])])+"</ul>":"")+"</article>").join("");
  const education = (d.education||[]).map(x=>'<article class="es-entry"><div class="es-entry-head"><h3>'+e(x.degree||"")+(x.field_of_study?" — "+e(x.field_of_study):"")+'</h3><time>'+dates(x)+'</time></div><div class="es-meta">'+e(x.institution||"")+"</div>"+(x.coursework?"<p>"+e(x.coursework)+"</p>":"")+(x.academic_achievements?"<p>"+e(x.academic_achievements)+"</p>":"")+"</article>").join("");
  const projects = (d.projects||[]).map(x=>'<article class="es-project"><h3>'+e(x.name||"")+(x.role?" · "+e(x.role):"")+"</h3>"+(x.description?"<p>"+e(x.description)+"</p>":"")+(x.technologies?.length?'<p class="es-meta">'+e(x.technologies.join(" · "))+"</p>":"")+(x.achievements?.length?"<ul>"+list(x.achievements)+"</ul>":"")+"</article>").join("");
  const certs = (d.certifications||[]).map(x=>"<li><strong>"+e(x.name||"")+"</strong>"+(x.issuer?" — "+e(x.issuer):"")+(x.issue_date?" · "+e(x.issue_date):"")+"</li>").join("");
  const langs = (d.languages||[]).map(x=>"<span>"+e(x.language||"")+(x.proficiency?" · "+e(x.proficiency):"")+"</span>").join("");
  const custom = (d.custom_sections||[]).filter(x=>x.items?.length).map(x=>'<section class="es-custom"><h2>'+e(x.title||"Additional Teaching Experience")+"</h2>"+x.items.map(y=>"<article><h3>"+e(y.title||"")+"</h3>"+(y.description?"<p>"+e(y.description)+"</p>":"")+(y.bullets?.length?"<ul>"+list(y.bullets)+"</ul>":"")+"</article>").join("")+"</section>").join("");
  const cls = "educator-standard", short = "es";
  const root = document.createElement("div");
  root.innerHTML = '<div class="resume-template-'+cls+'"><header class="'+short+'-header">'+( false ? '<div class="la-kicker">EDUCATION / PRACTICE / IMPACT</div>' : '<div class="es-mark" aria-hidden="true">ED</div>' )+'<div><h1>'+e(p.full_name||"Your Name")+'</h1><p>'+e(p.professional_title||"Educator / Teacher")+'</p><div class="'+short+'-contact">'+contact.join(" <span>•</span> ")+"</div></div></header><main>"+
    section("summary","Professional Teaching Profile",d.summary?"<p>"+e(d.summary)+"</p>":"")+
    section("skills","Teaching & Instructional Skills",skills?'<div class="'+short+'-skills">'+skills+"</div>":"")+
    section("experience","Teaching & Professional Experience",exp)+
    section("projects","Selected Educational Projects",projects)+
    section("education","Education & Qualifications",education)+section("certifications","Teaching Credentials & Certifications",certs?"<ul>"+certs+"</ul>":"")+
    section("languages","Languages",langs?'<div class="'+short+'-languages">'+langs+"</div>":"")+
    (d.career_objective?section("career_objective","Professional Objective","<p>"+e(d.career_objective)+"</p>"):"")+custom+"</main></div>";
  root.querySelectorAll("[data-section]").forEach(n=>{const body=n.innerHTML.replace(/<h2[^>]*>.*?<\/h2>/,"").trim();if(hidden.has(n.dataset.section)||!body)n.classList.add("is-hidden");});
  return root.firstElementChild.outerHTML;
}
window.renderEducatorStandardTemplate = renderEducatorStandardTemplate;
