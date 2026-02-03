import requests
import json
from datetime import datetime

USERNAME = "mohamed-faisal-salem"

def get_github_stats():
    """Get comprehensive GitHub statistics"""
    
    # Get user info
    user_url = f"https://api.github.com/users/{USERNAME}"
    user_data = requests.get(user_url).json()
    
    # Get repositories
    repos_url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100"
    repos = requests.get(repos_url).json()
    
    # Calculate statistics
    stats = {
        "total_repos": len(repos),
        "total_stars": sum(repo.get("stargazers_count", 0) for repo in repos),
        "total_forks": sum(repo.get("forks_count", 0) for repo in repos),
        "total_watchers": sum(repo.get("watchers_count", 0) for repo in repos),
        "followers": user_data.get("followers", 0),
        "following": user_data.get("following", 0),
    }
    
    # Get language statistics
    languages = {}
    for repo in repos:
        if repo.get("fork"):  # Skip forked repos
            continue
        repo_name = repo["name"]
        lang_url = f"https://api.github.com/repos/{USERNAME}/{repo_name}/languages"
        try:
            lang_data = requests.get(lang_url).json()
            for lang, size in lang_data.items():
                languages[lang] = languages.get(lang, 0) + size
        except:
            continue
    
    # Calculate percentages
    total = sum(languages.values())
    if total > 0:
        language_percentages = {
            k: round(v / total * 100, 1) 
            for k, v in sorted(languages.items(), key=lambda x: x[1], reverse=True)[:6]
        }
    else:
        language_percentages = {}
    
    stats["languages"] = language_percentages
    
    return stats

def get_contribution_count():
    """Get contribution count (approximation based on repos activity)"""
    repos_url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100"
    repos = requests.get(repos_url).json()
    
    total_commits = 0
    for repo in repos[:10]:  # Check last 10 repos to avoid rate limiting
        try:
            commits_url = f"https://api.github.com/repos/{USERNAME}/{repo['name']}/commits?per_page=100"
            commits = requests.get(commits_url).json()
            if isinstance(commits, list):
                total_commits += len(commits)
        except:
            continue
    
    return total_commits

def generate_language_bars(languages):
    """Generate SVG bars for languages"""
    colors = {
        "Python": "#3572A5",
        "Java": "#b07219",
        "C++": "#f34b7d",
        "JavaScript": "#f1e05a",
        "Kotlin": "#A97BFF",
        "C": "#555555",
        "HTML": "#e34c26",
        "CSS": "#563d7c",
        "Shell": "#89e051",
        "Jupyter Notebook": "#DA5B0B"
    }
    
    bars_svg = ""
    y_position = 120
    max_width = 280
    
    for lang, percent in languages.items():
        color = colors.get(lang, "#858585")
        bar_width = int((percent / 100) * max_width)
        
        bars_svg += f'''
    <g transform="translate(0, {y_position})">
      <text x="20" y="15" class="lang-name">{lang}</text>
      <text x="360" y="15" class="percentage">{percent}%</text>
      <rect x="20" y="20" width="{max_width}" height="8" rx="4" fill="#21262d"/>
      <rect x="20" y="20" width="{bar_width}" height="8" rx="4" fill="{color}">
        <animate attributeName="width" from="0" to="{bar_width}" dur="1.5s" fill="freeze"/>
      </rect>
    </g>
    '''
        y_position += 45
    
    return bars_svg

def generate_stats_svg(stats):
    """Generate complete stats SVG"""
    
    languages_bars = generate_language_bars(stats["languages"])
    total_height = 120 + (len(stats["languages"]) * 45) + 40
    
    svg = f'''<svg width="400" height="{total_height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#00D9FF;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#7B2FF7;stop-opacity:1" />
    </linearGradient>
    
    <style>
      .title {{ 
        font: 600 18px 'Segoe UI', Ubuntu, Sans-serif; 
        fill: #FFFFFF;
      }}
      .stat-label {{ 
        font: 400 12px 'Segoe UI', Ubuntu, Sans-serif; 
        fill: #8B949E;
      }}
      .stat-value {{ 
        font: 600 14px 'Segoe UI', Ubuntu, Sans-serif; 
        fill: #FFFFFF;
      }}
      .lang-name {{ 
        font: 500 13px 'Segoe UI', Ubuntu, Sans-serif; 
        fill: #FFFFFF;
      }}
      .percentage {{ 
        font: 600 13px 'Segoe UI', Ubuntu, Sans-serif; 
        fill: #00D9FF;
      }}
    </style>
  </defs>
  
  <!-- Background -->
  <rect width="400" height="{total_height}" rx="10" fill="#0D1117" stroke="url(#grad1)" stroke-width="2"/>
  
  <!-- Title -->
  <text x="200" y="30" class="title" text-anchor="middle">📊 GitHub Statistics</text>
  
  <!-- Stats Row -->
  <g transform="translate(0, 50)">
    <g transform="translate(40, 0)">
      <text x="0" y="0" class="stat-label">Total Repos</text>
      <text x="0" y="20" class="stat-value">{stats["total_repos"]}</text>
    </g>
    <g transform="translate(140, 0)">
      <text x="0" y="0" class="stat-label">Total Stars</text>
      <text x="0" y="20" class="stat-value">⭐ {stats["total_stars"]}</text>
    </g>
    <g transform="translate(240, 0)">
      <text x="0" y="0" class="stat-label">Followers</text>
      <text x="0" y="20" class="stat-value">👥 {stats["followers"]}</text>
    </g>
  </g>
  
  <!-- Separator Line -->
  <line x1="20" y1="110" x2="380" y2="110" stroke="#21262d" stroke-width="2"/>
  
  <!-- Language Statistics -->
  {languages_bars}
  
  <!-- Last Updated -->
  <text x="200" y="{total_height - 15}" class="stat-label" text-anchor="middle">
    Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}
  </text>
</svg>'''
    
    return svg

def main():
    print("🚀 Fetching GitHub statistics...")
    
    try:
        stats = get_github_stats()
        print("✅ Statistics retrieved successfully!")
        print(f"📊 Total Repositories: {stats['total_repos']}")
        print(f"⭐ Total Stars: {stats['total_stars']}")
        print(f"👥 Followers: {stats['followers']}")
        print("\n📈 Language Distribution:")
        for lang, percent in stats['languages'].items():
            print(f"   {lang}: {percent}%")
        
        # Generate SVG
        svg_content = generate_stats_svg(stats)
        
        # Save to file
        with open("stats.svg", "w", encoding="utf-8") as f:
            f.write(svg_content)
        
        print("\n✅ SVG generated successfully: stats.svg")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("⚠️  Make sure you have internet connection and GitHub API is accessible")

if __name__ == "__main__":
    main()
