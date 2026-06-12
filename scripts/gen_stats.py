import os, json, urllib.request

USER = os.environ["USER"]
TOKEN = os.environ["GH_TOKEN"]
HDR = {"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"}

q = """
query($login:String!){
  user(login:$login){
    repositories(first:100, ownerAffiliations:OWNER, isFork:false){
      totalCount
      nodes{ stargazerCount }
    }
    contributionsCollection{
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
    }
    followers{ totalCount }
    pullRequests{ totalCount }
  }
}
"""
body = json.dumps({"query": q, "variables": {"login": USER}}).encode()
req = urllib.request.Request("https://api.github.com/graphql", data=body, headers=HDR)
d = json.loads(urllib.request.urlopen(req).read())["data"]["user"]

repos     = d["repositories"]["totalCount"]
stars     = sum(n["stargazerCount"] for n in d["repositories"]["nodes"])
commits   = d["contributionsCollection"]["totalCommitContributions"]
prs       = d["pullRequests"]["totalCount"]
followers = d["followers"]["totalCount"]

def fmt(n): return f"{n/1000:.1f}k" if n >= 1000 else str(n)

tiles = [
  (fmt(commits),  "Commits",   "#22d3ee", "#3b82f6"),
  (fmt(stars),    "Stars",     "#f0883e", "#db6d28"),
  (fmt(prs),      "Pull Reqs", "#a855f7", "#7c3aed"),
  (fmt(repos),    "Repos",     "#2dd4bf", "#0ea5a4"),
  (fmt(followers),"Followers", "#e3b341", "#d4a017"),
]
tw, gap, x0 = 182, 14, 22
defs = "".join(
  f'<linearGradient id="n{i}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>'
  for i,(_,_,a,b) in enumerate(tiles))
parts = [f'''<svg viewBox="0 0 1000 180" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="GitHub stats">
  <defs>
    <linearGradient id="sbg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0c0a20"/><stop offset="1" stop-color="#08060f"/></linearGradient>
    {defs}
    <filter id="g" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
  <rect width="1000" height="180" rx="16" fill="url(#sbg)" stroke="#2dd4bf" stroke-opacity="0.18"/>
  <text x="32" y="40" font-family="monospace" font-size="14" font-weight="700" fill="#8b8ba7">// github stats</text>
  <circle cx="170" cy="35" r="3.5" fill="#22d3ee"><animate attributeName="opacity" values="0.3;1;0.3" dur="2.4s" repeatCount="indefinite"/></circle>''']
for i,(num,label,a,b) in enumerate(tiles):
    x = x0 + i*(tw+gap); cxx = x + tw/2
    parts.append(f'''  <rect x="{x}" y="62" width="{tw}" height="98" rx="12" fill="#ffffff" fill-opacity="0.025" stroke="{a}" stroke-opacity="0.35"/>
  <rect x="{x+16}" y="62" width="{tw-32}" height="3" rx="1.5" fill="url(#n{i})"/>
  <text x="{cxx}" y="118" text-anchor="middle" font-family="sans-serif" font-size="38" font-weight="800" fill="url(#n{i})" filter="url(#g)">{num}</text>
  <text x="{cxx}" y="144" text-anchor="middle" font-family="sans-serif" font-size="12.5" fill="#e2e8f0">{label}</text>''')
parts.append("</svg>")
os.makedirs("assets", exist_ok=True)
open("assets/stats.svg","w").write("\n".join(parts))
print("stats.svg:", commits, "commits", stars, "stars", prs, "prs", repos, "repos", followers, "followers")
