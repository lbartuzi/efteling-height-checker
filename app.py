#!/usr/bin/env python3
"""
Efteling Height Requirements Web Server
Serves attraction data with nice HTML/CSS interface
"""

import json
import os
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

# Security headers
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    # Prevent XSS attacks
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:;"
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    # Prevent MIME-sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # XSS filter
    response.headers['X-XSS-Protection'] = '1; mode=block'
    # Control referrer information
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    # Restrict permissions
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    return response

DATA_DIR = Path("/app/data")
DATA_FILE = DATA_DIR / "attractions.json"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Efteling Height Requirements</title>
    <link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --efteling-green: #1a5f2a;
            --efteling-gold: #c9a227;
            --efteling-dark: #0d2818;
            --efteling-light: #f5f0e6;
            --success: #22c55e;
            --warning: #f59e0b;
            --danger: #ef4444;
            --purple: #8b5cf6;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Quicksand', sans-serif;
            background: linear-gradient(135deg, var(--efteling-dark) 0%, var(--efteling-green) 100%);
            min-height: 100vh;
            color: var(--efteling-light);
        }
        
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        
        header {
            text-align: center;
            padding: 40px 20px;
            background: rgba(0,0,0,0.3);
            border-radius: 20px;
            margin-bottom: 30px;
        }
        
        h1 {
            font-size: 2.5rem;
            color: var(--efteling-gold);
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            margin-bottom: 10px;
        }
        
        .subtitle { font-size: 1.1rem; opacity: 0.9; }
        
        .stats {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        
        .stat-badge {
            background: rgba(255,255,255,0.15);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
        }
        
        .height-selector {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .height-btn {
            padding: 12px 24px;
            font-size: 1.1rem;
            font-weight: 600;
            border: none;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-family: inherit;
            background: rgba(255,255,255,0.2);
            color: white;
        }
        
        .height-btn:hover { transform: scale(1.05); background: rgba(255,255,255,0.3); }
        .height-btn.active { background: var(--efteling-gold); color: var(--efteling-dark); transform: scale(1.1); box-shadow: 0 0 0 3px white; }
        
        .hint { text-align: center; margin-bottom: 25px; opacity: 0.8; font-size: 0.95rem; }
        
        .results { display: none; }
        .results.active { display: block; }
        
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }
        
        .summary-card {
            background: rgba(255,255,255,0.15);
            border-radius: 15px;
            padding: 15px;
            text-align: center;
        }
        
        .summary-number { font-size: 2.5rem; font-weight: 700; color: var(--efteling-gold); }
        .summary-label { font-size: 0.85rem; opacity: 0.9; }
        
        .category {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
        }
        
        .category h2 {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
            font-size: 1.3rem;
        }
        
        .category-icon {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
        }
        
        .category.available .category-icon { background: var(--success); }
        .category.companion .category-icon { background: var(--warning); }
        .category.unavailable .category-icon { background: var(--danger); }
        
        .attractions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 12px;
        }
        
        .attraction-card {
            background: rgba(255,255,255,0.95);
            color: var(--efteling-dark);
            border-radius: 12px;
            padding: 15px;
            transition: all 0.2s ease;
            text-decoration: none;
            display: block;
            cursor: pointer;
            position: relative;
        }
        
        .attraction-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        }
        
        .attraction-card::after {
            content: '↗';
            position: absolute;
            top: 10px;
            right: 12px;
            opacity: 0.3;
            font-size: 1rem;
            transition: opacity 0.2s;
        }
        
        .attraction-card:hover::after { opacity: 1; }
        
        .attraction-name {
            font-weight: 700;
            font-size: 1.05rem;
            margin-bottom: 4px;
            color: var(--efteling-green);
            padding-right: 20px;
        }
        
        .attraction-type {
            font-size: 0.8rem;
            color: #666;
            margin-bottom: 8px;
        }
        
        .attraction-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-bottom: 8px;
        }
        
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .badge-height { background: #dbeafe; color: #1e40af; }
        .badge-companion { background: #fef3c7; color: #92400e; }
        .badge-age { background: #f3e8ff; color: #7c3aed; }
        .badge-none { background: #d1fae5; color: #065f46; }
        
        .attraction-notes {
            font-size: 0.8rem;
            color: #555;
            font-style: italic;
            line-height: 1.3;
        }
        
        .section-title {
            color: var(--efteling-gold);
            margin: 40px 0 20px;
            text-align: center;
            font-size: 1.5rem;
        }
        
        .shows-section {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(139, 92, 246, 0.1) 100%);
            border-radius: 15px;
            padding: 25px;
            margin-top: 30px;
        }
        
        .shows-section h2 { color: var(--efteling-gold); margin-bottom: 15px; text-align: center; }
        
        .show-card { border-left: 4px solid var(--purple); }
        
        table {
            width: 100%;
            border-collapse: collapse;
            background: rgba(255,255,255,0.95);
            border-radius: 12px;
            overflow: hidden;
            font-size: 0.9rem;
        }
        
        th, td { padding: 10px 12px; text-align: left; color: var(--efteling-dark); }
        th { background: var(--efteling-green); color: white; font-weight: 600; }
        tr:nth-child(even) { background: rgba(0,0,0,0.03); }
        tr:hover { background: rgba(201, 162, 39, 0.15); }
        
        .clickable-row { cursor: pointer; }
        
        .external-link {
            color: var(--efteling-green);
            text-decoration: none;
            font-weight: 600;
        }
        
        .external-link:hover { text-decoration: underline; }
        
        .sources-section {
            background: rgba(0,0,0,0.3);
            border-radius: 15px;
            padding: 25px;
            margin-top: 40px;
        }
        
        .sources-section h2 { color: var(--efteling-gold); margin-bottom: 15px; }
        
        .source-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            flex-wrap: wrap;
        }
        
        .source-item:last-child { border-bottom: none; }
        
        .source-status {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            flex-shrink: 0;
        }
        
        .source-status.success { background: var(--success); }
        .source-status.failed { background: var(--danger); }
        
        .source-link { color: var(--efteling-gold); text-decoration: none; word-break: break-all; }
        .source-link:hover { text-decoration: underline; }
        
        .access-icons {
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid rgba(0,0,0,0.1);
        }
        
        .access-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            font-size: 12px;
            cursor: help;
        }
        
        .access-icon.warning { background: #fee2e2; color: #b91c1c; }
        .access-icon.info { background: #dbeafe; color: #1e40af; }
        .access-icon.good { background: #d1fae5; color: #065f46; }
        .access-icon.neutral { background: #f3f4f6; color: #374151; }
        
        .wait-time {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-top: 6px;
        }
        .wait-time.open { background: #dcfce7; color: #166534; }
        .wait-time.closed { background: #f3f4f6; color: #6b7280; }
        .wait-time.busy { background: #fef3c7; color: #92400e; }
        .wait-time.very-busy { background: #fee2e2; color: #991b1b; }
        
        .park-status {
            text-align: center;
            padding: 12px 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            font-weight: 600;
        }
        .park-status.open { background: #dcfce7; color: #166534; }
        .park-status.closed { background: #f3f4f6; color: #6b7280; }
        
        .attribution {
            text-align: center;
            font-size: 0.8rem;
            opacity: 0.7;
            margin-top: 10px;
        }
        .attribution a { color: var(--efteling-gold); }
        
        footer {
            text-align: center;
            padding: 30px;
            opacity: 0.7;
            font-size: 0.85rem;
        }
        
        @media (max-width: 768px) {
            h1 { font-size: 1.8rem; }
            .height-btn { padding: 10px 16px; font-size: 0.95rem; }
            .attractions-grid { grid-template-columns: 1fr; }
            th, td { padding: 8px; font-size: 0.8rem; }
            .summary-number { font-size: 2rem; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏰 Efteling Height Requirements</h1>
            <p class="subtitle">Find out which attractions are available for your children</p>
            <div class="stats">
                <span class="stat-badge">🎢 {{ total_attractions }} Attractions</span>
                <span class="stat-badge">🎭 {{ total_shows }} Shows</span>
                <span class="stat-badge">🕐 Updated: {{ last_updated }}</span>
            </div>
        </header>
        
        <div class="height-selector">
            {% for height in [95, 100, 110, 120, 130, 135] %}
            <button class="height-btn {% if height == 120 %}active{% endif %}" onclick="showHeight({{ height }})">{{ height }} cm</button>
            {% endfor %}
        </div>
        
        <p class="hint">💡 Click any attraction card to view official details on Efteling.com</p>
        
        {% for height, categories in height_categories.items() %}
        <div class="results {% if height == '120' %}active{% endif %}" id="results-{{ height }}">
            <div class="summary-cards">
                <div class="summary-card">
                    <div class="summary-number">{{ categories.independent|length }}</div>
                    <div class="summary-label">✅ Independent</div>
                </div>
                <div class="summary-card">
                    <div class="summary-number">{{ categories.with_companion|length }}</div>
                    <div class="summary-label">👨‍👧 With Companion</div>
                </div>
                <div class="summary-card">
                    <div class="summary-number">{{ categories.not_available|length }}</div>
                    <div class="summary-label">❌ Not Available</div>
                </div>
                <div class="summary-card">
                    <div class="summary-number">{{ categories.independent|length + categories.with_companion|length }}</div>
                    <div class="summary-label">🎯 Total Accessible</div>
                </div>
            </div>
            
            {% if wait_times_info and wait_times_info.park_open is not none %}
            <div class="park-status {{ 'open' if wait_times_info.park_open else 'closed' }}">
                {% if wait_times_info.park_open %}
                🎢 Park is OPEN - Live wait times available
                {% else %}
                🌙 Park is CLOSED - Wait times unavailable
                {% endif %}
            </div>
            {% endif %}
            
            <div class="category available">
                <h2><span class="category-icon">✅</span> Can Ride Independently ({{ categories.independent|length }})</h2>
                <div class="attractions-grid">
                    {% for attr in categories.independent %}
                    <a href="{{ attr.url }}" target="_blank" rel="noopener" class="attraction-card">
                        <div class="attraction-name">{{ attr.name }}</div>
                        <div class="attraction-type">{{ attr.type_dutch or attr.type }}</div>
                        {% if attr.wait_time is not none or attr.is_open is not none %}
                        <div class="wait-time {% if attr.is_open == false %}closed{% elif attr.wait_time and attr.wait_time >= 45 %}very-busy{% elif attr.wait_time and attr.wait_time >= 20 %}busy{% else %}open{% endif %}">
                            {% if attr.is_open == false %}
                            🔴 Closed
                            {% elif attr.wait_time is not none %}
                            ⏱️ {{ attr.wait_time }} min
                            {% else %}
                            🟢 Open
                            {% endif %}
                        </div>
                        {% endif %}
                        <div class="attraction-badges">
                            {% if attr.min_height_cm %}
                            <span class="badge badge-height">Min: {{ attr.min_height_cm }} cm</span>
                            {% elif attr.supervision_height_cm %}
                            <span class="badge badge-none">No min height</span>
                            {% else %}
                            <span class="badge badge-none">No height req.</span>
                            {% endif %}
                            {% if attr.advisory_age %}
                            <span class="badge badge-age">Age {{ attr.advisory_age }}+</span>
                            {% endif %}
                        </div>
                        {% if attr.notes %}<div class="attraction-notes">{{ attr.notes }}</div>{% endif %}
                        {% if attr.access %}
                        <div class="access-icons">
                            {% if attr.access.wheelchair == 'accessible' %}<span class="access-icon good" title="Wheelchair accessible">♿</span>{% endif %}
                            {% if attr.access.wheelchair == 'transfer' %}<span class="access-icon info" title="Wheelchair with transfer">🔄</span>{% endif %}
                            {% if attr.access.wheelchair == 'not_accessible' %}<span class="access-icon warning" title="Not wheelchair accessible">🚫</span>{% endif %}
                            {% if attr.access.pregnant %}<span class="access-icon warning" title="Not suitable for pregnant women">🤰</span>{% endif %}
                            {% if attr.access.injuries %}<span class="access-icon warning" title="Not suitable with injuries">🩹</span>{% endif %}
                            {% if attr.access.cameras %}<span class="access-icon warning" title="Cameras not allowed">📵</span>{% endif %}
                            {% if attr.access.guide_dogs %}<span class="access-icon good" title="Guide dogs allowed">🦮</span>{% endif %}
                            {% if attr.access.single_rider %}<span class="access-icon info" title="Single rider available">👤</span>{% endif %}
                            {% if attr.access.dark %}<span class="access-icon neutral" title="Partly in the dark">🌙</span>{% endif %}
                            {% if attr.access.loud %}<span class="access-icon neutral" title="Loud noises">🔊</span>{% endif %}
                            {% if attr.access.wet %}<span class="access-icon info" title="You may get wet">💦</span>{% endif %}
                            {% if attr.access.dizzy %}<span class="access-icon neutral" title="May cause dizziness">😵</span>{% endif %}
                            {% if attr.access.fog %}<span class="access-icon neutral" title="Smoke/fog effects">🌫️</span>{% endif %}
                            {% if attr.access.fire %}<span class="access-icon neutral" title="Fire effects">🔥</span>{% endif %}
                            {% if attr.access.surprising %}<span class="access-icon neutral" title="Surprising effects">⚡</span>{% endif %}
                        </div>
                        {% endif %}
                    </a>
                    {% endfor %}
                </div>
            </div>
            
            {% if categories.with_companion %}
            <div class="category companion">
                <h2><span class="category-icon">👨‍👧</span> With Supervision/Companion ({{ categories.with_companion|length }})</h2>
                <p style="margin-bottom: 15px; opacity: 0.9; font-size: 0.9rem;">
                    {% if categories.with_companion[0].companion_age %}
                    Children this height need an accompanying person aged {{ categories.with_companion[0].companion_age }}+
                    {% else %}
                    Children this height need adult supervision
                    {% endif %}
                </p>
                <div class="attractions-grid">
                    {% for attr in categories.with_companion %}
                    <a href="{{ attr.url }}" target="_blank" rel="noopener" class="attraction-card">
                        <div class="attraction-name">{{ attr.name }}</div>
                        <div class="attraction-type">{{ attr.type_dutch or attr.type }}</div>
                        {% if attr.wait_time is not none or attr.is_open is not none %}
                        <div class="wait-time {% if attr.is_open == false %}closed{% elif attr.wait_time and attr.wait_time >= 45 %}very-busy{% elif attr.wait_time and attr.wait_time >= 20 %}busy{% else %}open{% endif %}">
                            {% if attr.is_open == false %}
                            🔴 Closed
                            {% elif attr.wait_time is not none %}
                            ⏱️ {{ attr.wait_time }} min
                            {% else %}
                            🟢 Open
                            {% endif %}
                        </div>
                        {% endif %}
                        <div class="attraction-badges">
                            {% if attr.supervision_height_cm %}
                            <span class="badge badge-companion">&lt;{{ attr.supervision_height_cm }}cm needs companion</span>
                            {% endif %}
                            {% if attr.min_height_cm %}
                            <span class="badge badge-height">Solo: {{ attr.min_height_cm }}cm+</span>
                            {% endif %}
                            {% if attr.advisory_age %}
                            <span class="badge badge-age">Age {{ attr.advisory_age }}+</span>
                            {% endif %}
                        </div>
                        {% if attr.notes %}<div class="attraction-notes">{{ attr.notes }}</div>{% endif %}
                        {% if attr.access %}
                        <div class="access-icons">
                            {% if attr.access.wheelchair == 'accessible' %}<span class="access-icon good" title="Wheelchair accessible">♿</span>{% endif %}
                            {% if attr.access.wheelchair == 'transfer' %}<span class="access-icon info" title="Wheelchair with transfer">🔄</span>{% endif %}
                            {% if attr.access.wheelchair == 'not_accessible' %}<span class="access-icon warning" title="Not wheelchair accessible">🚫</span>{% endif %}
                            {% if attr.access.pregnant %}<span class="access-icon warning" title="Not suitable for pregnant women">🤰</span>{% endif %}
                            {% if attr.access.injuries %}<span class="access-icon warning" title="Not suitable with injuries">🩹</span>{% endif %}
                            {% if attr.access.cameras %}<span class="access-icon warning" title="Cameras not allowed">📵</span>{% endif %}
                            {% if attr.access.guide_dogs %}<span class="access-icon good" title="Guide dogs allowed">🦮</span>{% endif %}
                            {% if attr.access.single_rider %}<span class="access-icon info" title="Single rider available">👤</span>{% endif %}
                            {% if attr.access.dark %}<span class="access-icon neutral" title="Partly in the dark">🌙</span>{% endif %}
                            {% if attr.access.loud %}<span class="access-icon neutral" title="Loud noises">🔊</span>{% endif %}
                            {% if attr.access.wet %}<span class="access-icon info" title="You may get wet">💦</span>{% endif %}
                            {% if attr.access.dizzy %}<span class="access-icon neutral" title="May cause dizziness">😵</span>{% endif %}
                            {% if attr.access.fog %}<span class="access-icon neutral" title="Smoke/fog effects">🌫️</span>{% endif %}
                            {% if attr.access.fire %}<span class="access-icon neutral" title="Fire effects">🔥</span>{% endif %}
                            {% if attr.access.surprising %}<span class="access-icon neutral" title="Surprising effects">⚡</span>{% endif %}
                        </div>
                        {% endif %}
                    </a>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
            
            {% if categories.not_available %}
            <div class="category unavailable">
                <h2><span class="category-icon">❌</span> Not Available Yet ({{ categories.not_available|length }})</h2>
                <div class="attractions-grid">
                    {% for attr in categories.not_available %}
                    <a href="{{ attr.url }}" target="_blank" rel="noopener" class="attraction-card">
                        <div class="attraction-name">{{ attr.name }}</div>
                        <div class="attraction-type">{{ attr.type_dutch or attr.type }}</div>
                        <div class="attraction-badges">
                            {% if attr.supervision_height_cm %}
                            <span class="badge badge-companion">With companion: {{ attr.supervision_height_cm }}cm+</span>
                            {% endif %}
                            {% if attr.min_height_cm %}
                            <span class="badge badge-height">Solo: {{ attr.min_height_cm }}cm+</span>
                            {% endif %}
                            {% if attr.advisory_age %}
                            <span class="badge badge-age">Age {{ attr.advisory_age }}+</span>
                            {% endif %}
                        </div>
                        {% if attr.notes %}<div class="attraction-notes">{{ attr.notes }}</div>{% endif %}
                        {% if attr.access %}
                        <div class="access-icons">
                            {% if attr.access.wheelchair == 'accessible' %}<span class="access-icon good" title="Wheelchair accessible">♿</span>{% endif %}
                            {% if attr.access.wheelchair == 'transfer' %}<span class="access-icon info" title="Wheelchair with transfer">🔄</span>{% endif %}
                            {% if attr.access.wheelchair == 'not_accessible' %}<span class="access-icon warning" title="Not wheelchair accessible">🚫</span>{% endif %}
                            {% if attr.access.pregnant %}<span class="access-icon warning" title="Not suitable for pregnant women">🤰</span>{% endif %}
                            {% if attr.access.injuries %}<span class="access-icon warning" title="Not suitable with injuries">🩹</span>{% endif %}
                            {% if attr.access.cameras %}<span class="access-icon warning" title="Cameras not allowed">📵</span>{% endif %}
                            {% if attr.access.guide_dogs %}<span class="access-icon good" title="Guide dogs allowed">🦮</span>{% endif %}
                            {% if attr.access.single_rider %}<span class="access-icon info" title="Single rider available">👤</span>{% endif %}
                            {% if attr.access.dark %}<span class="access-icon neutral" title="Partly in the dark">🌙</span>{% endif %}
                            {% if attr.access.loud %}<span class="access-icon neutral" title="Loud noises">🔊</span>{% endif %}
                            {% if attr.access.wet %}<span class="access-icon info" title="You may get wet">💦</span>{% endif %}
                            {% if attr.access.dizzy %}<span class="access-icon neutral" title="May cause dizziness">😵</span>{% endif %}
                            {% if attr.access.fog %}<span class="access-icon neutral" title="Smoke/fog effects">🌫️</span>{% endif %}
                            {% if attr.access.fire %}<span class="access-icon neutral" title="Fire effects">🔥</span>{% endif %}
                            {% if attr.access.surprising %}<span class="access-icon neutral" title="Surprising effects">⚡</span>{% endif %}
                        </div>
                        {% endif %}
                    </a>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
        </div>
        {% endfor %}
        
        {% if shows %}
        <div class="shows-section">
            <h2>🎭 Shows (No Height Requirements)</h2>
            <p style="text-align: center; margin-bottom: 15px; opacity: 0.8;">Shows are separate from attractions - everyone can enjoy!</p>
            <div class="attractions-grid">
                {% for show in shows %}
                <a href="{{ show.url }}" target="_blank" rel="noopener" class="attraction-card show-card">
                    <div class="attraction-name">🎭 {{ show.name }}</div>
                    <div class="attraction-type">{{ show.type }}</div>
                    <div class="attraction-badges">
                        <span class="badge badge-none">All ages welcome</span>
                    </div>
                    {% if show.notes %}<div class="attraction-notes">{{ show.notes }}</div>{% endif %}
                </a>
                {% endfor %}
            </div>
        </div>
        {% endif %}
        
        <h2 class="section-title">📋 Complete Requirements Table</h2>
        <p style="text-align: center; margin-bottom: 15px; opacity: 0.9; font-size: 0.9rem;">
            💡 "Ride Alone" = minimum height to ride independently | "Companion Needed" = children below this height need adult supervision
        </p>
        <table>
            <thead>
                <tr>
                    <th>Attraction</th>
                    <th>Type</th>
                    <th>Ride Alone</th>
                    <th>Companion Needed</th>
                    <th>Age</th>
                </tr>
            </thead>
            <tbody>
                {% for attr in attractions %}
                <tr class="clickable-row" onclick="window.open('{{ attr.url }}', '_blank')">
                    <td><a href="{{ attr.url }}" target="_blank" class="external-link" onclick="event.stopPropagation()">{{ attr.name }} ↗</a></td>
                    <td>{{ attr.type }}</td>
                    <td>
                        {% if attr.min_height_cm %}
                            {{ attr.min_height_cm }}cm+
                        {% elif attr.supervision_height_cm %}
                            {{ attr.supervision_height_cm }}cm+
                        {% else %}
                            ✓ Any height
                        {% endif %}
                    </td>
                    <td>
                        {% if attr.min_height_cm and attr.supervision_height_cm %}
                            {{ attr.supervision_height_cm }}-{{ attr.min_height_cm }}cm
                        {% elif attr.supervision_height_cm and not attr.min_height_cm %}
                            Below {{ attr.supervision_height_cm }}cm
                        {% else %}
                            -
                        {% endif %}
                    </td>
                    <td>{% if attr.advisory_age %}{{ attr.advisory_age }}+{% else %}-{% endif %}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <div class="sources-section" style="margin-top: 30px;">
            <h2>🔑 Access Icon Legend</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; margin-top: 15px;">
                <div><span class="access-icon good">♿</span> Wheelchair accessible</div>
                <div><span class="access-icon info">🔄</span> Wheelchair with transfer</div>
                <div><span class="access-icon warning">🚫</span> Not wheelchair accessible</div>
                <div><span class="access-icon warning">🤰</span> Not for pregnant women</div>
                <div><span class="access-icon warning">🩹</span> Not suitable with injuries</div>
                <div><span class="access-icon warning">📵</span> Cameras not allowed</div>
                <div><span class="access-icon good">🦮</span> Guide dogs allowed</div>
                <div><span class="access-icon info">👤</span> Single rider available</div>
                <div><span class="access-icon neutral">🌙</span> Partly in the dark</div>
                <div><span class="access-icon neutral">🔊</span> Loud noises</div>
                <div><span class="access-icon info">💦</span> You may get wet</div>
                <div><span class="access-icon neutral">😵</span> May cause dizziness</div>
                <div><span class="access-icon neutral">🌫️</span> Smoke/fog effects</div>
                <div><span class="access-icon neutral">🔥</span> Fire effects</div>
                <div><span class="access-icon neutral">⚡</span> Surprising effects</div>
            </div>
        </div>
        
        <div class="sources-section">
            <h2>📚 Data Sources</h2>
            {% for source in sources %}
            <div class="source-item">
                <span class="source-status {{ source.status }}"></span>
                <strong>{{ source.name }}</strong>
                <a href="{{ source.url }}" target="_blank" class="source-link">{{ source.url }}</a>
                {% if source.attractions_scraped is defined %}
                <span style="opacity: 0.7; font-size: 0.85rem; margin-left: auto;">({{ source.attractions_scraped }} scraped)</span>
                {% endif %}
            </div>
            {% endfor %}
            {% if wait_times_info and wait_times_info.source %}
            <div class="source-item">
                <span class="source-status success"></span>
                <strong>Wait Times</strong>
                <a href="{{ wait_times_info.source }}" target="_blank" class="source-link">{{ wait_times_info.source }}</a>
                <span style="opacity: 0.7; font-size: 0.85rem; margin-left: auto;">(updates every 5 min)</span>
            </div>
            {% endif %}
        </div>
        
        <footer>
            <p>Height data auto-updates every 6 hours | Wait times update every 5 minutes</p>
            {% if wait_times_info and wait_times_info.attribution %}
            <p class="attribution"><a href="https://queue-times.com/parks/160" target="_blank">{{ wait_times_info.attribution }}</a></p>
            {% endif %}
            <p>🎢 Made with ❤️ for Efteling families | Always verify at the park</p>
        </footer>
    </div>
    
    <script>
        function showHeight(height) {
            document.querySelectorAll('.results').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.height-btn').forEach(btn => btn.classList.remove('active'));
            document.getElementById('results-' + height).classList.add('active');
            event.target.classList.add('active');
        }
    </script>
</body>
</html>
"""

def load_data():
    """Load attraction data from JSON file"""
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            return json.load(f)
    return None

@app.route('/')
def index():
    """Main page"""
    data = load_data()
    
    if data is None:
        return """
        <html><head><title>Efteling Height Requirements</title></head>
        <body style="font-family: sans-serif; text-align: center; padding: 50px; background: #0d2818; color: white;">
            <h1>⏳ Data Loading...</h1>
            <p>The scraper is collecting data. Please refresh in a few minutes.</p>
            <p><a href="/api/scrape" style="color: #c9a227;">Trigger manual scrape</a></p>
        </body></html>
        """
    
    try:
        dt = datetime.fromisoformat(data['last_updated'])
        last_updated = dt.strftime('%b %d, %Y %H:%M')
    except:
        last_updated = 'Unknown'
    
    return render_template_string(
        HTML_TEMPLATE,
        attractions=data.get('attractions', []),
        shows=data.get('shows', []),
        height_categories=data.get('height_categories', {}),
        sources=data.get('sources', []),
        last_updated=last_updated,
        total_attractions=data.get('total_attractions', 0),
        total_shows=data.get('total_shows', 0),
        wait_times_info=data.get('wait_times_info', {})
    )

@app.route('/api/data')
def api_data():
    """JSON API endpoint"""
    data = load_data()
    return jsonify(data) if data else (jsonify({'error': 'No data'}), 404)

@app.route('/api/scrape')
def api_scrape():
    """Trigger manual scrape of height requirements"""
    import subprocess
    try:
        result = subprocess.run(['python', '/app/scraper.py'], capture_output=True, text=True, timeout=300)
        return jsonify({'status': 'success' if result.returncode == 0 else 'error', 'stdout': result.stdout, 'stderr': result.stderr})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/wait_times')
def api_wait_times():
    """Trigger manual refresh of wait times"""
    import subprocess
    try:
        result = subprocess.run(['python', '/app/wait_times.py'], capture_output=True, text=True, timeout=60)
        return jsonify({'status': 'success' if result.returncode == 0 else 'error', 'stdout': result.stdout, 'stderr': result.stderr})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/height/<int:height>')
def api_height(height):
    """Get attractions for specific height"""
    data = load_data()
    if data and str(height) in data.get('height_categories', {}):
        return jsonify(data['height_categories'][str(height)])
    return jsonify({'error': 'Invalid height'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
