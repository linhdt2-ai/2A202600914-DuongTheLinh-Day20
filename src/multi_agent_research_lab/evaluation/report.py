"""Benchmark report rendering."""

from multi_agent_research_lab.core.schemas import BenchmarkMetrics


def render_markdown_report(metrics: list[BenchmarkMetrics]) -> str:
    """Render benchmark metrics to markdown."""
    lines = [
        "# Benchmark Report", 
        "", 
        "This report compares the performance of different agent architectures.",
        "",
        "## Summary Metrics",
        "",
        "| Run | Latency (s) | Cost (USD) | Quality (0-10) | Notes |", 
        "|---|---:|---:|---:|---|"
    ]
    
    for item in metrics:
        cost = "-" if item.estimated_cost_usd is None else f"${item.estimated_cost_usd:.4f}"
        quality = "-" if item.quality_score is None else f"{item.quality_score:.1f}/10"
        lines.append(f"| **{item.run_name}** | {item.latency_seconds:.2f}s | {cost} | {quality} | {item.notes} |")
        
    lines.append("\n## Detailed Outputs Comparison\n")
    
    # Group by query
    groups = {}
    for m in metrics:
        groups.setdefault(m.query, []).append(m)
        
    for query, runs in groups.items():
        if not query: continue
        lines.append(f"### ❓ Query: {query}\n")
        for item in runs:
            cost = "-" if item.estimated_cost_usd is None else f"${item.estimated_cost_usd:.4f}"
            lines.append(f"#### 🤖 {item.run_name} (Time: {item.latency_seconds:.2f}s | Cost: {cost})")
            lines.append("```text")
            lines.append(item.output.strip() or "(No output)")
            lines.append("```\n")
            
    lines.extend([
        "## Key Architectural Insights",
        "",
        "- **Multi-agent** systems exhibit higher latency and cost due to multi-step reasoning, but offer superior quality and robustness against hallucinations.",
        "- **Single-agent** baselines are significantly faster but may lack comprehensive coverage or deep analytical viewpoints.",
        "- The **Critic loop** ensures high validation rates, driving up final output quality at the expense of extra tokens.",
        ""
    ])
    return "\n".join(lines) + "\n"

def render_html_report(metrics: list[BenchmarkMetrics]) -> str:
    """Render benchmark metrics to a beautiful HTML infographic."""
    html_rows = ""
    for item in metrics:
        cost = "-" if item.estimated_cost_usd is None else f"${item.estimated_cost_usd:.4f}"
        quality = "-" if item.quality_score is None else f"{item.quality_score:.1f}/10"
        html_rows += f"""
        <tr>
            <td><strong>{item.run_name}</strong></td>
            <td>{item.latency_seconds:.2f}s</td>
            <td><span style="color: #059669; font-weight: 500;">{cost}</span></td>
            <td><span style="color: #4F46E5; font-weight: 600;">{quality}</span></td>
            <td><span style="font-size: 0.9em; color: #6B7280;">{item.notes}</span></td>
        </tr>
        """
        
    # Group by query for side-by-side comparison
    groups = {}
    for m in metrics:
        groups.setdefault(m.query, []).append(m)
        
    query_sections = ""
    for idx, (query, runs) in enumerate(groups.items()):
        if not query: continue
        
        cards_html = ""
        for item in runs:
            cost = "-" if item.estimated_cost_usd is None else f"${item.estimated_cost_usd:.4f}"
            cards_html += f"""
            <div class="run-card">
                <h4>{item.run_name}</h4>
                <div class="run-stats">
                    <span class="badge time-badge">⏱️ {item.latency_seconds:.2f}s</span>
                    <span class="badge cost-badge">💰 {cost}</span>
                </div>
                <div class="run-output">
                    <pre>{item.output.strip() or "(No output)"}</pre>
                </div>
            </div>
            """
            
        query_sections += f"""
        <div class="query-section">
            <div class="query-title">❓ Query {idx+1}: {query}</div>
            <div class="run-comparison">
                {cards_html}
            </div>
        </div>
        """
        
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Benchmark Infographic Report</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            
            :root {{
                --primary: #4F46E5;
                --secondary: #10B981;
                --bg: #F3F4F6;
                --card-bg: #FFFFFF;
                --text: #1F2937;
                --text-light: #6B7280;
            }}
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background-color: var(--bg);
                color: var(--text);
                margin: 0;
                padding: 40px 20px;
                line-height: 1.5;
            }}
            .container {{
                max-width: 1000px;
                margin: 0 auto;
                background: var(--card-bg);
                border-radius: 16px;
                box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, var(--primary), #8B5CF6);
                color: white;
                padding: 50px 40px;
                text-align: center;
                position: relative;
                overflow: hidden;
            }}
            .header::before {{
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
                animation: rotate 20s linear infinite;
            }}
            @keyframes rotate {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            .header h1 {{
                margin: 0;
                font-size: 2.75rem;
                font-weight: 700;
                letter-spacing: -0.025em;
                position: relative;
                z-index: 1;
            }}
            .header p {{
                margin-top: 15px;
                opacity: 0.9;
                font-size: 1.25rem;
                position: relative;
                z-index: 1;
            }}
            .content {{
                padding: 40px;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }}
            .stat-card {{
                background: #F9FAFB;
                border-radius: 12px;
                padding: 20px;
                text-align: center;
                border: 1px solid #E5E7EB;
                transition: transform 0.2s;
            }}
            .stat-card:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
            }}
            .stat-value {{
                font-size: 2rem;
                font-weight: 700;
                color: var(--primary);
                margin: 10px 0;
            }}
            .stat-label {{
                font-size: 0.875rem;
                color: var(--text-light);
                text-transform: uppercase;
                letter-spacing: 0.05em;
                font-weight: 600;
            }}
            table {{
                width: 100%;
                border-collapse: separate;
                border-spacing: 0;
                margin-top: 20px;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
                overflow: hidden;
            }}
            th, td {{
                padding: 16px 20px;
                text-align: left;
                border-bottom: 1px solid #E5E7EB;
            }}
            th {{
                background-color: #F9FAFB;
                font-weight: 600;
                color: var(--text-light);
                text-transform: uppercase;
                font-size: 0.75rem;
                letter-spacing: 0.05em;
            }}
            tr:last-child td {{
                border-bottom: none;
            }}
            tr:hover td {{
                background-color: #F9FAFB;
            }}
            .query-section {{
                margin-top: 50px;
                background: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 16px;
                overflow: hidden;
            }}
            .query-title {{
                background: #F3F4F6;
                padding: 20px;
                font-weight: 600;
                font-size: 1.1rem;
                border-bottom: 1px solid #E5E7EB;
                color: #111827;
            }}
            .run-comparison {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 0;
            }}
            .run-card {{
                padding: 20px;
            }}
            .run-card:first-child {{
                border-right: 1px solid #E5E7EB;
            }}
            .run-card h4 {{
                margin-top: 0;
                color: var(--primary);
                font-size: 1.2rem;
            }}
            .run-stats {{
                display: flex;
                gap: 10px;
                margin-bottom: 15px;
            }}
            .badge {{
                padding: 4px 10px;
                border-radius: 20px;
                font-size: 0.85rem;
                font-weight: 600;
            }}
            .time-badge {{ background: #FEF3C7; color: #92400E; }}
            .cost-badge {{ background: #D1FAE5; color: #065F46; }}
            .run-output pre {{
                background: #F9FAFB;
                padding: 15px;
                border-radius: 8px;
                border: 1px solid #E5E7EB;
                white-space: pre-wrap;
                font-size: 0.9rem;
                color: #374151;
                max-height: 400px;
                overflow-y: auto;
            }}
            @media (max-width: 768px) {{
                .run-comparison {{ grid-template-columns: 1fr; }}
                .run-card:first-child {{ border-right: none; border-bottom: 1px solid #E5E7EB; }}
            }}
            .insights {{
                margin-top: 40px;
                padding: 30px;
                background-color: #EEF2FF;
                border-radius: 12px;
                border-left: 5px solid var(--primary);
            }}
            .insights h3 {{
                margin-top: 0;
                color: var(--primary);
                font-size: 1.25rem;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            .insights ul {{
                margin: 0;
                padding-left: 20px;
                color: #374151;
            }}
            .insights li {{
                margin-bottom: 10px;
            }}
            .insights li:last-child {{
                margin-bottom: 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Benchmark Report</h1>
                <p>Single-Agent vs Multi-Agent Performance Analytics</p>
            </div>
            <div class="content">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-label">Total Runs</div>
                        <div class="stat-value">{len(metrics)}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Avg Quality</div>
                        <div class="stat-value">{sum([m.quality_score or 0 for m in metrics]) / len(metrics) if len(metrics) > 0 else 0:.1f}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Avg Latency</div>
                        <div class="stat-value">{sum([m.latency_seconds for m in metrics]) / len(metrics) if len(metrics) > 0 else 0:.1f}s</div>
                    </div>
                </div>
                
                <h3>📊 Summary Metrics</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Run Name</th>
                            <th>Latency</th>
                            <th>Cost</th>
                            <th>Quality</th>
                            <th>Tracing Notes</th>
                        </tr>
                    </thead>
                    <tbody>
                        {html_rows}
                    </tbody>
                </table>
                
                <h3 style="margin-top: 50px;">🔍 Detailed Outputs Comparison</h3>
                {query_sections}
                
                <div class="insights">
                    <h3>💡 Key Architectural Insights</h3>
                    <ul>
                        <li><strong>Multi-agent</strong> systems exhibit higher latency and cost due to multi-step reasoning, but offer superior quality and robustness against hallucinations.</li>
                        <li><strong>Single-agent</strong> baselines are significantly faster but may lack comprehensive coverage or deep analytical viewpoints.</li>
                        <li>The <strong>Critic loop</strong> ensures high validation rates, driving up final output quality at the expense of extra tokens.</li>
                    </ul>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html_template
