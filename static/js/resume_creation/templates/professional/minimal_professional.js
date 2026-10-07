export function renderMinimalProfessionalTemplate(content, escapeHtml) {
  const root=document.createElement("div");
  const e=typeof escapeHtml==="function"?escapeHtml:(v)=>String(v||"");
  const p=content.personal_information||{};
  const skillsByCategory=content.skills_by_category||{};
  const hidden=new Set(content.hidden_sections||[]);
  const has=(v)=>String(v||"").trim();
  const dates=(x)=>{const s=x.start_date||"",n=x.current?"Present":(x.end_date||"");return s||n?e(s)+(s||n?" – ":"")+e(n):""};
  const bullets=(a)=>Array.isArray(a)?a.filter(Boolean).map(v=>"<li>"+e(v)+"</li>").join(""):"";
  const section=(key,html,title)=>html?'<section data-section="'+key+'"><h2>'+title+'</h2>'+html+"</section>":"";

  const contact=[p.email,p.phone,p.location].filter(Boolean).map(e);
  [["LinkedIn",p.linkedin],["GitHub",p.github],["Portfolio",p.portfolio]].forEach(([label,url])=>{if(url)contact.push('<a href="'+e(url)+'" target="_blank" rel="noopener">'+label+"</a>")});

  const experience=(content.experience||[]).map(x=>'<article class="minimal-entry"><div class="minimal-entry-head"><h3 class="minimal-entry-title">'+e(x.title||"")+'</h3><span class="minimal-entry-date">'+dates(x)+"</span></div><div class="minimal-entry-subtitle">"+e(x.company||"")+(x.location?" · "+e(x.location):"")+"</div>"+(x.bullets||x.achievements?'<ul>'+bullets([...(x.bullets||[]),...(x.achievements||[])])+"</ul>":"")+"</article>").join("");
  const education=(content.education||[]).map(x=>'<article class="minimal-entry"><div class="minimal-entry-head"><h3 class="minimal-entry-title">'+e(x.degree||"")+(x.field_of_study?" in "+e(x.field_of_study):"")+'</h3><span class="minimal-entry-date">'+dates(x)+"</span></div><div class="minimal-entry-subtitle">"+e(x.institution||"")+(x.location?" · "+e(x.location):"")+"</div>"+(x.coursework?'<p><strong>Coursework:</strong> '+e(x.coursework)+"</p>":"")+(x.academic_achievements?'<p>'+e(x.academic_achievements)+"</p>":"")+"</article>").join("");
  const projects=(content.projects||[]).map(x=>'<article class="minimal-entry"><div class="minimal-entry-head"><h3 class="minimal-entry-title">'+e(x.name||"")+(x.role?" · "+e(x.role):"")+'</h3></div>'+(x.technologies?.length?'<div class="minimal-entry-subtitle">'+e(x.technologies.join(", "))+"</div>":"")+(x.description?'<p>'+e(x.description)+"</p>":"")+(x.achievements?.length?'<ul>'+bullets(x.achievements)+"</ul>":"")+"</article>").join("");
  const skills=Object.entries(skillsByCategory).filter(([,v])=>Array.isArray(v)&&v.length).map(([k,v])=>'<div class="minimal-skill-group"><strong>'+e(k)+'</strong><div class="minimal-skill-list">'+e(v.join(", "))+"</div></div>").join("");
  const fallbackSkills=!skills&&Array.isArray(content.skills)?'<div class="minimal-skill-group"><div class="minimal-skill-list">'+e(content.skills.join(", "))+"</div></div>":"";
  const certs=(content.certifications||[]).map(x=>'<div class="minimal-cert"><strong>'+e(x.name||"")+"</strong>"+(x.issuer?" — "+e(x.issuer):"")+(x.issue_date?" ("+e(x.issue_date)+")":"")+"</div>").join("");
  const langs=(content.languages||[]).map(x=>'<span>'+e(x.language||"")+(x.proficiency?" ("+e(x.proficiency)+")":"")+"</span>").join("");

  const customs=(content.custom_sections||[]).filter(x=>x.items?.length).map(s=>'<section class="minimal-custom"><h2>'+e(s.title||"Custom Section")+"</h2>"+s.items.map(x=>'<article class="minimal-custom-item"><div class="minimal-entry-head"><h3 class="minimal-entry-title">'+e(x.title||"")+(x.subtitle?" · "+e(x.subtitle):"")+'</h3><span class="minimal-entry-date">'+e(x.date||"")+"</span></div>"+(x.description?'<p class="minimal-description">'+e(x.description)+"</p>":"")+(x.bullets?.length?'<ul>'+bullets(x.bullets)+"</ul>":"")+"</article>").join("")+"</section>").join("");

  root.innerHTML='<div class="resume-template-minimal-professional"><header class="minimal-header"><div><h1>'+e(p.full_name||"Your Name")+'</h1><p>'+e(p.professional_title||"")+'</p></div><div class="minimal-contact">'+contact.join("<br>")+'</div></header><main>'+
    section("summary",content.summary?'<p class="minimal-summary">'+e(content.summary)+"</p>":"", "Profile")+
    section("career_objective",content.career_objective?'<p class="minimal-objective">'+e(content.career_objective)+"</p>":"", "Career Objective")+
    section("experience",experience,"Experience")+section("education",education,"Education")+section("projects",projects,"Selected Projects")+
    section("skills",skills||fallbackSkills,'Skills')+section("certifications",certs,"Certifications")+section("languages",langs?'<div class="minimal-language-list">'+langs+"</div>":"", "Languages")+customs+
    "</main></div>";

  root.querySelectorAll("[data-section]").forEach(n=>{if(hidden.has(n.dataset.section)||!n.innerHTML.replace(/<h2[^>]*>.*?<\/h2>/,"").trim())n.classList.add("is-hidden")});
  return root.firstElementChild.outerHTML;
}
window.renderMinimalProfessionalTemplate=renderMinimalProfessionalTemplate;