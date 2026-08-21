export const DEFAULT_PROFILE = {
  name: "Selin",
  briefingMinutes: 25,
  discoveryRatio: 0.15,
  topics: {
    artificial_intelligence: 1.0, startups: 0.9, science: 0.9,
    neuroscience: 0.95, hardware: 0.85, semiconductors: 0.85,
    robotics: 0.8, technology: 0.8, mathematics: 0.75,
    computer_science: 0.9, venture_capital: 0.75
  },
  topicAliases: {
    artificial_intelligence: ["AI","artificial intelligence","foundation model","LLM","machine learning","deep learning"],
    startups: ["startup","startups","founder","seed round","series a","series b"],
    science: ["science","scientists","research","physics","biology","chemistry"],
    neuroscience: ["neuroscience","brain","neural","BCI","brain-computer","cognition","neurotechnology"],
    hardware: ["hardware","compute","accelerator","datacenter","data center"],
    semiconductors: ["semiconductor","chip","GPU","CPU","silicon","foundry","lithography"],
    robotics: ["robot","robotics","humanoid","autonomous"],
    technology: ["technology","tech","software","platform"],
    mathematics: ["mathematics","math","theorem","proof","geometry","algebra"],
    computer_science: ["computer science","algorithm","compiler","database","distributed systems"],
    venture_capital: ["venture capital","VC","investor","fund","funding"]
  },
  regions: {US:1.0, UK:0.9, Europe:0.9, Asia:0.85},
  regionAliases: {
    US:["US","U.S.","United States","Silicon Valley"],
    UK:["UK","U.K.","United Kingdom","Britain","London"],
    Europe:["Europe","EU","European Union","France","Germany","Switzerland","Netherlands"],
    Asia:["Asia","China","Japan","Korea","Singapore","Taiwan","India"]
  },
  trackedEntities: {
    OpenAI:1, Anthropic:1, "Google DeepMind":1, DeepMind:1, "Meta AI":0.9,
    Microsoft:0.85, NVIDIA:1, AMD:0.8, TSMC:0.9, Apple:0.75, Google:0.8,
    Amazon:0.75, xAI:0.85, Sequoia:0.8, "Andreessen Horowitz":0.8, a16z:0.8, Benchmark:0.75
  },
  preferredSources:["TechCrunch","The Economist","WSJ","Bloomberg","Financial Times","Nature","arXiv"],
  noiseTerms:["celebrity","sports betting","horoscope","fashion week","royal family"]
};
