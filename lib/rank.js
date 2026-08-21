function norm(s){return (s||'').toLowerCase()}
function has(text,term){return norm(text).includes(norm(term))}
export function rankStory(story,profile){const text=`${story.title} ${story.summary||''}`;let topic=0,region=0,entity=0,quality=0,noise=0;const topics=[];
 for(const [k,w] of Object.entries(profile.topics)){const aliases=profile.topicAliases[k]||[k];if(aliases.some(a=>has(text,a))){topics.push(k);topic+=w*10}}
 topic=Math.min(30,topic);
 for(const [r,w] of Object.entries(profile.regions))if((profile.regionAliases[r]||[]).some(a=>has(text,a)))region=Math.max(region,w*5);
 for(const [e,w] of Object.entries(profile.trackedEntities))if(has(text,e))entity=Math.max(entity,w*10);
 if(profile.preferredSources.some(s=>norm(story.source).includes(norm(s))))quality=9;else quality=6;
 for(const t of profile.noiseTerms)if(has(text,t))noise-=10;
 const ageH=Math.max(0,(Date.now()-new Date(story.publishedAt||Date.now()).getTime())/36e5);const freshness=Math.max(0,15-Math.min(15,ageH/8));
 const academic=story.type==='paper'?8:0;const importance=Math.min(20,5+entity*.8+topic*.25+academic);const novelty=Math.min(15,freshness);const future=Math.min(5,(topic/30)*3+(entity/10)*2);
 const score=Math.max(0,Math.min(100,topic+importance+novelty+quality+entity+region+future+noise));
 return {...story,topics,score,why:why(story,topics,entity,academic)};
}
function why(s,topics,entity,academic){if(academic)return 'Primary research aligned with your science and technical interests.';if(entity>=8)return 'A tracked lab, company or technology is directly involved.';if(topics.includes('neuroscience')&&topics.includes('artificial_intelligence'))return 'It sits at the AI × neuroscience intersection you care about.';if(topics.length)return `Strong overlap with ${topics.slice(0,3).map(x=>x.replaceAll('_',' ')).join(', ')}.`;return 'Included for broader significance and discovery.'}
export function dedupe(stories){const seen=new Set();return stories.filter(x=>{const k=norm(x.title).replace(/[^a-z0-9 ]/g,'').split(/\s+/).slice(0,10).join(' ');if(seen.has(k))return false;seen.add(k);return true;});}
export function digest(stories,profile,newsmarks=[]){const marked=new Set(newsmarks.map(x=>x.id));const ranked=dedupe(stories.map(s=>rankStory(s,profile))).sort((a,b)=>b.score-a.score).map(x=>({...x,newsmarked:marked.has(x.id)}));const top=ranked.slice(0,10);const cats=[['AI & Compute',['artificial_intelligence','computer_science']],['Startups & VC',['startups','venture_capital']],['Science & Neuroscience',['science','neuroscience']],['Hardware & Robotics',['hardware','semiconductors','robotics']],['Math & Ideas',['mathematics']]];
 const sections=cats.map(([name,ts])=>({name,items:ranked.filter(x=>x.topics.some(t=>ts.includes(t))).slice(0,8)})).filter(x=>x.items.length);
 const deep=ranked.filter(x=>x.type==='paper'||/research|paper|study|report/i.test(x.title)).slice(0,5);
 const outside=ranked.filter(x=>x.score>=30&&!x.topics.length).slice(0,4);
 return {top,sections,deep,outside,ranked};}
