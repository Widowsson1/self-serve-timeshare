from flask import Blueprint, render_template_string, send_from_directory, abort
import os
import json

seo_bp = Blueprint('seo', __name__)

@seo_bp.route('/blog')
def blog_index():
    """Blog index page listing all SEO articles"""
    try:
        # Load content calendar
        calendar_path = os.path.join('static', 'seo_content', 'content_calendar.json')
        with open(calendar_path, 'r') as f:
            calendar = json.load(f)
        
        articles = calendar['content_calendar']['publication_schedule']
        
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Self Serve Timeshare Blog - Commission-Free Selling Tips & Guides</title>
    <meta name="description" content="Expert guides and tips for commission-free timeshare selling. Learn how to sell your timeshare without agents and save thousands in fees.">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #1f2937;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            background-color: #f8fafc;
        }
        
        .header {
            background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
            color: white;
            padding: 3rem 2rem;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 3rem;
        }
        
        .header h1 {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        .articles-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }
        
        .article-card {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        
        .article-card:hover {
            transform: translateY(-5px);
        }
        
        .article-card h3 {
            color: #2563eb;
            font-size: 1.3rem;
            margin-bottom: 1rem;
        }
        
        .article-meta {
            color: #6b7280;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }
        
        .read-more {
            background: #10b981;
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            display: inline-block;
        }
        
        .cta-section {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            padding: 3rem 2rem;
            border-radius: 12px;
            text-align: center;
        }
        
        .cta-button {
            background: #2563eb;
            color: white;
            padding: 1rem 2rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            display: inline-block;
            margin-top: 1rem;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Self Serve Timeshare Blog</h1>
        <p>Expert guides for commission-free timeshare selling</p>
    </div>
    
    <div class="articles-grid">
        {% for article in articles %}
        <div class="article-card">
            <h3>{{ article.title }}</h3>
            <div class="article-meta">
                Published: {{ article.date }} | Type: {{ article.content_type.title() }}
            </div>
            <a href="/blog/{{ article.filename.replace('.md', '') }}" class="read-more">Read Article</a>
        </div>
        {% endfor %}
    </div>
    
    <div class="cta-section">
        <h2>Ready to Start Selling Commission-Free?</h2>
        <p>Join thousands of timeshare owners who have discovered the benefits of autonomous selling.</p>
        <a href="/" class="cta-button">Get Started Today</a>
    </div>
</body>
</html>
        """
        
        return render_template_string(html_template, articles=articles)
    
    except Exception as e:
        return f"Error loading blog: {str(e)}", 500

@seo_bp.route('/blog/<article_name>')
def blog_article(article_name):
    """Serve individual blog articles"""
    try:
        # Serve HTML version of the article
        article_path = os.path.join('static', 'seo_content', 'blog_posts', f'{article_name}.html')
        
        if os.path.exists(article_path):
            with open(article_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            abort(404)
    
    except Exception as e:
        return f"Error loading article: {str(e)}", 500

@seo_bp.route('/commission-free-timeshare-selling')
def commission_free_landing():
    """Commission-free timeshare selling landing page"""
    try:
        landing_path = os.path.join('static', 'competitive_landing_pages', 'commission-free-timeshare-selling.html')
        with open(landing_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error loading page: {str(e)}", 500

@seo_bp.route('/self-serve-timeshare-vs-sellatimeshare')
def competitive_comparison():
    """Competitive comparison landing page"""
    try:
        landing_path = os.path.join('static', 'competitive_landing_pages', 'self-serve-timeshare-vs-sellatimeshare.html')
        with open(landing_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error loading page: {str(e)}", 500

@seo_bp.route('/sell-timeshare-without-agent')
def agent_free_landing():
    """Agent-free timeshare selling landing page"""
    try:
        landing_path = os.path.join('static', 'competitive_landing_pages', 'sell-timeshare-without-agent.html')
        with open(landing_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error loading page: {str(e)}", 500

@seo_bp.route('/sitemap.xml')
def sitemap():
    """Generate XML sitemap for SEO"""
    try:
        # Load content calendar for blog articles
        calendar_path = os.path.join('static', 'seo_content', 'content_calendar.json')
        with open(calendar_path, 'r') as f:
            calendar = json.load(f)
        
        articles = calendar['content_calendar']['publication_schedule']
        
        sitemap_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://www.selfservetimeshare.com/</loc>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://www.selfservetimeshare.com/blog</loc>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://www.selfservetimeshare.com/listings</loc>
        <changefreq>daily</changefreq>
        <priority>0.9</priority>
    </url>
    <url>
        <loc>https://www.selfservetimeshare.com/commission-free-timeshare-selling</loc>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://www.selfservetimeshare.com/self-serve-timeshare-vs-sellatimeshare</loc>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://www.selfservetimeshare.com/sell-timeshare-without-agent</loc>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>'''
        
        # Add blog articles to sitemap
        for article in articles:
            article_url = f"https://www.selfservetimeshare.com/blog/{article['filename'].replace('.md', '')}"
            sitemap_xml += f'''
    <url>
        <loc>{article_url}</loc>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>'''
        
        sitemap_xml += '\n</urlset>'
        
        return sitemap_xml, 200, {'Content-Type': 'application/xml'}
    
    except Exception as e:
        return f"Error generating sitemap: {str(e)}", 500

@seo_bp.route('/robots.txt')
def robots():
    """Generate robots.txt for SEO"""
    robots_txt = """User-agent: *
Allow: /

Sitemap: https://www.selfservetimeshare.com/sitemap.xml

# Optimize crawl budget
Crawl-delay: 1

# Allow all important pages
Allow: /blog/
Allow: /listings/
Allow: /commission-free-timeshare-selling
Allow: /self-serve-timeshare-vs-sellatimeshare
Allow: /sell-timeshare-without-agent
"""
    
    return robots_txt, 200, {'Content-Type': 'text/plain'}

