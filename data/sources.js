export const DEFAULT_SOURCES = [
  {name:"TechCrunch",type:"rss",url:"https://techcrunch.com/feed/",enabled:true},
  {name:"Nature",type:"rss",url:"https://www.nature.com/nature.rss",enabled:true},
  {name:"arXiv AI",type:"arxiv",query:"cat:cs.AI",maxResults:35,enabled:true},
  {name:"arXiv ML",type:"arxiv",query:"cat:cs.LG",maxResults:35,enabled:true},
  {name:"arXiv Robotics",type:"arxiv",query:"cat:cs.RO",maxResults:25,enabled:true},
  {name:"arXiv Neuroscience",type:"arxiv",query:"cat:q-bio.NC",maxResults:25,enabled:true},
  {name:"Google News · AI labs",type:"rss",url:"https://news.google.com/rss/search?q=%22OpenAI%22+OR+%22Anthropic%22+OR+%22DeepMind%22&hl=en-US&gl=US&ceid=US:en",enabled:true},
  {name:"Google News · Chips",type:"rss",url:"https://news.google.com/rss/search?q=semiconductor+OR+NVIDIA+OR+TSMC+OR+AI+chips&hl=en-US&gl=US&ceid=US:en",enabled:true},
  {name:"Google News · Startups VC",type:"rss",url:"https://news.google.com/rss/search?q=startup+venture+capital+AI&hl=en-US&gl=US&ceid=US:en",enabled:true},
  {name:"Google News · Neuroscience",type:"rss",url:"https://news.google.com/rss/search?q=neuroscience+OR+brain-computer+OR+neurotechnology&hl=en-US&gl=US&ceid=US:en",enabled:true}
];
