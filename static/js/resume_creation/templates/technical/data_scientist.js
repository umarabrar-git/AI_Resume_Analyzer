export function renderDataScientistTemplate(content, escapeHtml) {
  const root=document.createElement("div");
  const e=typeof escapeHtml==="function"?escapeHtml:(v)=>String(v||"");
  const p=content.personal_information||{},hidden=new Set(content.hidden_sections||[]);
  const dates=x=>{const s=x.start_date||"",n=x.current?"Present":(x.end_date||"");return s||n?e(s)+(s||n?" – ":"")+e(n):""};
  const bullets=a=>Array.isArray(a)?a.filter(Boolean).map(v=>"<li>"+e(v)+"</li>").join(""):"";
  const section=(key,html,title)=>html?'<section data-section="'+key+'"><h2>'+title+"</h2>"+html+"</section>":"";
  const contact=[p.email,p.phone,p.location].filter(Boolean).map(e);
  [["LinkedIn",p.linkedin],["GitHub",p.github],["Portfolio",p.portfolio]].forEach(([label,url])=>{if(url)contact.push('<a href="'+e(url)+'" target="_blank" rel="noopener">'+label+"</a>")});
  const skillGroups=Object.entries(content.skills_by_category||{}).filter(([,v])=>Array.isArray(v)&&v.length);
  const skills=skillGroups.map(([k,v])=>'<div class="ds-skill-group"><strong>'+e(k)+'</strong>'+e(v.join(", "))+"</div>").join("")||(content.skills||[]).length?skillGroups.length?skillGroups.map(([k,v])=>'<div class="ds-skill-group"><strong>'+e(k)+'</strong>'+e(v.join(", "))+"</div>").join(""):'<div class="ds-skill-group">'+e((content.skills||[]).join(", "))+"</div>":"";
  const experience=(content.experience||[]).map(x=>'<article class="ds-entry"><div class="ds-entry-head"><h3 class="ds-entry-title">'+e(x.title||"")+'</h3><span class="ds-entry-date">'+dates(x)+"</span></div><div class=\"ds-entry-subtitle\">"+e(x.company||"")+(x.location?" · "+e(x.location):"")+"</div>"+(x.bullets?.length||x.achievements?.length?'<ul>'+bullets([...(x.bullets||[]),...(x.achievements||[])])+"</ul>":"")+"</article>").join("");
  const projects=(content.projects||[]).map(x=>'<article class="ds-entry"><div class="ds-entry-head"><h3 class="ds-entry-title">'+e(x.name||"")+(x.role?" · "+e(x.role):"")+'</h3></div>'+(x.technologies?.length?'<div class="ds-tech"><strong>Technologies:</strong> '+e(x.technologies.join(", "))+"</div>":"")+(x.description?'<p>'+e(x.description)+"</p>":"")+(x.achievements?.length?'<ul>'+bullets(x.achievements)+"</ul>":"")+(x.github_url?'<p><strong>GitHub:</strong> <a href="'+e(x.github_url)+'">'+e(x.github_url)+"</a></p>":"")+"</article>").join("");
  const education=(content.education||[]).map(x=>'<article class="ds-entry"><div class="ds-entry-head"><h3 class="ds-entry-title">'+e(x.degree||"")+(x.field_of_study?" in "+e(x.field_of_study):"")+'</h3><span class="ds-entry-date">'+dates(x)+"</span></div><div class=\"ds-entry-subtitle\">"+e(x.institution||"")+(x.location?" · "+e(x.location):"")+"</div>"+(x.coursework?'<p><strong>Relevant Coursework:</strong> '+e(x.coursework)+"</p>":"")+(x.academic_achievements?'<p>'+e(x.academic_achievements)+"</p>":"")+"</article>").join("");
  const certs=(content.certifications||[]).map(x=>'<div class="ds-cert"><strong>'+e(x.name||"")+"</strong>"+(x.issuer?" — "+e(x.issuer):"")+(x.issue_date?" ("+e(x.issue_date)+")":"")+"</div>").join("");
  const langs=(content.languages||[]).map(x=>'<span>'+e(x.language||"")+(x.proficiency?" ("+e(x.proficiency)+")":"")+"</span>").join("");
  const customs=(content.custom_sections||[]).filter(x=>x.items?.length).map(s=>'<section class="ds-custom"><h2>'+e(s.title||"Additional Experience")+"</h2>"+s.items.map(x=>'<article class="ds-entry"><div class="ds-entry-head"><h3 class="ds-entry-title">'+e(x.title||"")+(x.subtitle?" · "+e(x.subtitle):"")+'</h3><span class="ds-entry-date">'+e(x.date||"")+"</span></div>"+(x.description?'<p>'+e(x.description)+"</p>":"")+(x.bullets?.length?'<ul>'+bullets(x.bullets)+"</ul>":"")+"</article>").join("")+"</section>").join("");
  root.innerHTML='<div class="resume-template-data-scientist"><header class="ds-header"><h1>'+e(p.full_name||"Your Name")+'</h1><p>'+e(p.professional_title||"Data Science Professional")+'</p><div>'+contact.join("<span>•</span>")+'</div></header><main>'+
    section("summary",content.summary?'<p class="ds-summary">'+e(content.summary)+"</p>":"", "Professional Profile")+
    section("skills",skills?'<div class="ds-skills">'+skills+"</div>":"", "Technical Expertise")+
    section("experience",experience,"Experience")+section("projects",projects,"Data & AI Projects")+section("education",education,"Education")+
    section("certifications",certs,"Certifications")+section("languages",langs?'<div class="ds-languages">'+langs+"</div>":"", "Languages")+
    section("career_objective",content.career_objective?'<p class="ds-objective">'+e(content.career_objective)+"</p>":"", "Career Objective")+customs+"</main></div>";
  root.querySelectorAll("[data-section]").forEach(n=>{if(hidden.has(n.dataset.section)||!n.innerHTML.replace(/<h2[^>]*>.*?<\/h2>/,"").trim())n.classList.add("is-hidden")});
  return root.firstElementChild.outerHTML;
}
window.renderDataScientistTemplate=renderDataScientistTemplate;