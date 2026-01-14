"""
职位 Dashboard 生成器

生成一个 HTML 页面，展示所有过滤后的职位
"""
import json
import os
from datetime import datetime
from typing import Optional

from scrapers.base import Job
from filters.job_filter import JobFilter
import config


def generate_dashboard(
    jobs: list[Job],
    output_path: str = "dashboard.html",
    title: str = "Crypto Job Dashboard"
) -> str:
    """
    生成 HTML Dashboard
    
    Args:
        jobs: 职位列表
        output_path: 输出文件路径
        title: 页面标题
    
    Returns:
        输出文件路径
    """
    
    # 按来源分组
    jobs_by_source = {}
    for job in jobs:
        source = job.source
        if source not in jobs_by_source:
            jobs_by_source[source] = []
        jobs_by_source[source].append(job)
    
    # 按公司分组
    jobs_by_company = {}
    for job in jobs:
        company = job.company
        if company not in jobs_by_company:
            jobs_by_company[company] = []
        jobs_by_company[company].append(job)
    
    # 生成 HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --bg-primary: #0a0a0b;
            --bg-secondary: #141416;
            --bg-card: #1a1a1d;
            --text-primary: #ffffff;
            --text-secondary: #a0a0a0;
            --accent: #6366f1;
            --accent-hover: #818cf8;
            --success: #22c55e;
            --border: #2a2a2d;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        header {{
            text-align: center;
            padding: 3rem 0;
            border-bottom: 1px solid var(--border);
            margin-bottom: 2rem;
        }}
        
        h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent), #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}
        
        .subtitle {{
            color: var(--text-secondary);
            font-size: 1.1rem;
        }}
        
        .stats {{
            display: flex;
            justify-content: center;
            gap: 3rem;
            margin-top: 2rem;
            flex-wrap: wrap;
        }}
        
        .stat {{
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--accent);
        }}
        
        .stat-label {{
            color: var(--text-secondary);
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .filters {{
            background: var(--bg-secondary);
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            align-items: center;
        }}
        
        .search-box {{
            flex: 1;
            min-width: 250px;
        }}
        
        .search-box input {{
            width: 100%;
            padding: 0.75rem 1rem;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--bg-card);
            color: var(--text-primary);
            font-size: 1rem;
        }}
        
        .search-box input:focus {{
            outline: none;
            border-color: var(--accent);
        }}
        
        .filter-select {{
            padding: 0.75rem 1rem;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--bg-card);
            color: var(--text-primary);
            font-size: 1rem;
            cursor: pointer;
        }}
        
        .jobs-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 1.5rem;
        }}
        
        .job-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            transition: all 0.2s ease;
        }}
        
        .job-card:hover {{
            border-color: var(--accent);
            transform: translateY(-2px);
        }}
        
        .job-title {{
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: var(--text-primary);
        }}
        
        .job-company {{
            font-size: 1rem;
            color: var(--accent);
            margin-bottom: 0.75rem;
        }}
        
        .job-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }}
        
        .job-tag {{
            padding: 0.25rem 0.75rem;
            background: var(--bg-secondary);
            border-radius: 20px;
            font-size: 0.8rem;
            color: var(--text-secondary);
        }}
        
        .job-tag.source {{
            background: rgba(99, 102, 241, 0.1);
            color: var(--accent);
        }}
        
        .job-tag.remote {{
            background: rgba(34, 197, 94, 0.1);
            color: var(--success);
        }}
        
        .job-link {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem 1.5rem;
            background: var(--accent);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 500;
            transition: background 0.2s ease;
        }}
        
        .job-link:hover {{
            background: var(--accent-hover);
        }}
        
        .no-results {{
            text-align: center;
            padding: 4rem;
            color: var(--text-secondary);
        }}
        
        footer {{
            text-align: center;
            padding: 3rem 0;
            margin-top: 3rem;
            border-top: 1px solid var(--border);
            color: var(--text-secondary);
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 1rem;
            }}
            
            h1 {{
                font-size: 1.8rem;
            }}
            
            .stats {{
                gap: 1.5rem;
            }}
            
            .stat-value {{
                font-size: 1.8rem;
            }}
            
            .jobs-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 {title}</h1>
            <p class="subtitle">Top Crypto VC Portfolio Jobs • Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</p>
            
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{len(jobs)}</div>
                    <div class="stat-label">Total Jobs</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{len(jobs_by_company)}</div>
                    <div class="stat-label">Companies</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{len(jobs_by_source)}</div>
                    <div class="stat-label">Sources</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{sum(1 for j in jobs if j.remote)}</div>
                    <div class="stat-label">Remote Jobs</div>
                </div>
            </div>
        </header>
        
        <div class="filters">
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="🔍 Search jobs, companies..." onkeyup="filterJobs()">
            </div>
            <select class="filter-select" id="sourceFilter" onchange="filterJobs()">
                <option value="">All Sources</option>
                {generate_source_options(jobs_by_source)}
            </select>
            <select class="filter-select" id="companyFilter" onchange="filterJobs()">
                <option value="">All Companies</option>
                {generate_company_options(jobs_by_company)}
            </select>
            <select class="filter-select" id="remoteFilter" onchange="filterJobs()">
                <option value="">All Locations</option>
                <option value="remote">Remote Only</option>
                <option value="onsite">On-site Only</option>
            </select>
        </div>
        
        <div class="jobs-grid" id="jobsGrid">
            {generate_job_cards(jobs)}
        </div>
        
        <div class="no-results" id="noResults" style="display: none;">
            <h3>😕 No jobs found</h3>
            <p>Try adjusting your search or filters</p>
        </div>
        
        <footer>
            <p>Built with ❤️ for Crypto Job Seekers</p>
            <p style="margin-top: 0.5rem; font-size: 0.9rem;">Data sourced from top VC portfolio job boards</p>
        </footer>
    </div>
    
    <script>
        function filterJobs() {{
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const sourceFilter = document.getElementById('sourceFilter').value;
            const companyFilter = document.getElementById('companyFilter').value;
            const remoteFilter = document.getElementById('remoteFilter').value;
            
            const cards = document.querySelectorAll('.job-card');
            let visibleCount = 0;
            
            cards.forEach(card => {{
                const title = card.dataset.title.toLowerCase();
                const company = card.dataset.company;
                const source = card.dataset.source;
                const isRemote = card.dataset.remote === 'true';
                
                let show = true;
                
                // Search filter
                if (searchTerm && !title.includes(searchTerm) && !company.toLowerCase().includes(searchTerm)) {{
                    show = false;
                }}
                
                // Source filter
                if (sourceFilter && source !== sourceFilter) {{
                    show = false;
                }}
                
                // Company filter
                if (companyFilter && company !== companyFilter) {{
                    show = false;
                }}
                
                // Remote filter
                if (remoteFilter === 'remote' && !isRemote) {{
                    show = false;
                }}
                if (remoteFilter === 'onsite' && isRemote) {{
                    show = false;
                }}
                
                card.style.display = show ? 'block' : 'none';
                if (show) visibleCount++;
            }});
            
            document.getElementById('noResults').style.display = visibleCount === 0 ? 'block' : 'none';
        }}
    </script>
</body>
</html>"""
    
    # 写入文件
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    return output_path


def generate_source_options(jobs_by_source: dict) -> str:
    """生成来源下拉选项"""
    options = []
    for source in sorted(jobs_by_source.keys()):
        count = len(jobs_by_source[source])
        options.append(f'<option value="{source}">{source} ({count})</option>')
    return "\n                ".join(options)


def generate_company_options(jobs_by_company: dict) -> str:
    """生成公司下拉选项"""
    options = []
    # 按职位数量排序
    sorted_companies = sorted(jobs_by_company.items(), key=lambda x: -len(x[1]))
    for company, jobs in sorted_companies[:50]:  # 只显示前50个公司
        count = len(jobs)
        options.append(f'<option value="{company}">{company} ({count})</option>')
    return "\n                ".join(options)


def generate_job_cards(jobs: list[Job]) -> str:
    """生成职位卡片 HTML"""
    cards = []
    
    for job in jobs:
        location_tag = ""
        if job.location:
            location_tag = f'<span class="job-tag">📍 {escape_html(job.location)}</span>'
        
        remote_tag = ""
        if job.remote:
            remote_tag = '<span class="job-tag remote">🌍 Remote</span>'
        
        job_type_tag = ""
        if job.job_type:
            job_type_tag = f'<span class="job-tag">⏰ {escape_html(job.job_type)}</span>'
        
        card = f"""
            <div class="job-card" 
                 data-title="{escape_html(job.title)}"
                 data-company="{escape_html(job.company)}"
                 data-source="{escape_html(job.source)}"
                 data-remote="{str(job.remote).lower()}">
                <h3 class="job-title">{escape_html(job.title)}</h3>
                <p class="job-company">{escape_html(job.company)}</p>
                <div class="job-meta">
                    <span class="job-tag source">{escape_html(job.source)}</span>
                    {location_tag}
                    {remote_tag}
                    {job_type_tag}
                </div>
                <a href="{job.url}" target="_blank" class="job-link">
                    Apply Now →
                </a>
            </div>"""
        cards.append(card)
    
    return "\n".join(cards)


def escape_html(text: str) -> str:
    """转义 HTML 特殊字符"""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )


if __name__ == "__main__":
    # 测试用
    from scrapers import create_all_scrapers
    from filters.job_filter import filter_jobs
    
    print("Collecting jobs...")
    all_jobs = []
    for scraper in create_all_scrapers():
        jobs = scraper.scrape()
        all_jobs.extend(jobs)
    
    print(f"Total jobs collected: {len(all_jobs)}")
    
    filtered_jobs = filter_jobs(all_jobs)
    print(f"After filtering: {len(filtered_jobs)}")
    
    output = generate_dashboard(filtered_jobs)
    print(f"Dashboard generated: {output}")
