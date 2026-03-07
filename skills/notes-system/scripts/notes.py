#!/usr/bin/env python3
"""備忘錄管理工具"""
import os
import sys
import json
import argparse
import re
from datetime import datetime
from pathlib import Path

NOTES_DIR = Path("/home/node/.openclaw/workspace/notes")

def parse_frontmatter(content):
    """解析 YAML frontmatter"""
    if not content.startswith('---'):
        return {}, content
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content
    
    frontmatter = {}
    for line in parts[1].strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            # Handle arrays
            if value.startswith('[') and value.endswith(']'):
                value = [v.strip().strip('"\'') for v in value[1:-1].split(',')]
            frontmatter[key] = value
    
    return frontmatter, parts[2].strip()

def list_notes(category=None):
    """列出所有備忘錄"""
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    notes = []
    
    for f in sorted(NOTES_DIR.glob('*.md')):
        content = f.read_text(encoding='utf-8')
        meta, body = parse_frontmatter(content)
        
        if category and meta.get('category') != category:
            continue
        
        notes.append({
            'file': f.name,
            'title': meta.get('title', f.stem),
            'category': meta.get('category', 'other'),
            'tags': meta.get('tags', []),
            'created': meta.get('created', ''),
            'preview': body[:100] + '...' if len(body) > 100 else body
        })
    
    return notes

def search_notes(query=None, category=None, tag=None):
    """搜尋備忘錄"""
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    
    for f in sorted(NOTES_DIR.glob('*.md')):
        content = f.read_text(encoding='utf-8')
        meta, body = parse_frontmatter(content)
        
        # Filter by category
        if category and meta.get('category') != category:
            continue
        
        # Filter by tag
        if tag:
            tags = meta.get('tags', [])
            if isinstance(tags, str):
                tags = [tags]
            if tag.lower() not in [t.lower() for t in tags]:
                continue
        
        # Filter by query (search in title, tags, body)
        if query:
            query_lower = query.lower()
            title = meta.get('title', '').lower()
            tags = meta.get('tags', [])
            if isinstance(tags, str):
                tags = [tags]
            tags_str = ' '.join(tags).lower()
            body_lower = body.lower()
            
            if query_lower not in title and query_lower not in tags_str and query_lower not in body_lower:
                continue
        
        results.append({
            'file': f.name,
            'title': meta.get('title', f.stem),
            'category': meta.get('category', 'other'),
            'tags': meta.get('tags', []),
            'created': meta.get('created', ''),
            'preview': body[:200] + '...' if len(body) > 200 else body
        })
    
    return results

def add_note(title, category, content, tags=None):
    """新增備忘錄"""
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now().strftime('%Y-%m-%d')
    date_prefix = datetime.now().strftime('%Y%m%d')
    
    # Sanitize title for filename
    safe_title = re.sub(r'[^\w\u4e00-\u9fff-]', '', title)[:30]
    filename = f"{date_prefix}-{safe_title}.md"
    filepath = NOTES_DIR / filename
    
    # Handle duplicate filenames
    counter = 1
    while filepath.exists():
        filename = f"{date_prefix}-{safe_title}-{counter}.md"
        filepath = NOTES_DIR / filename
        counter += 1
    
    tags_str = str(tags) if tags else '[]'
    
    note_content = f"""---
title: {title}
category: {category}
tags: {tags_str}
created: {today}
updated: {today}
---

{content}
"""
    
    filepath.write_text(note_content, encoding='utf-8')
    return {'status': 'ok', 'file': filename}

def get_note(filename):
    """讀取備忘錄"""
    filepath = NOTES_DIR / filename
    if not filepath.exists():
        return {'status': 'error', 'message': f'找不到檔案: {filename}'}
    
    content = filepath.read_text(encoding='utf-8')
    meta, body = parse_frontmatter(content)
    
    return {
        'status': 'ok',
        'file': filename,
        'meta': meta,
        'content': body
    }

def main():
    parser = argparse.ArgumentParser(description='備忘錄管理工具')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # list
    list_parser = subparsers.add_parser('list', help='列出備忘錄')
    list_parser.add_argument('--category', help='依分類篩選')
    
    # search
    search_parser = subparsers.add_parser('search', help='搜尋備忘錄')
    search_parser.add_argument('--query', help='關鍵字')
    search_parser.add_argument('--category', help='分類')
    search_parser.add_argument('--tag', help='標籤')
    
    # add
    add_parser = subparsers.add_parser('add', help='新增備忘錄')
    add_parser.add_argument('--title', required=True, help='標題')
    add_parser.add_argument('--category', default='other', help='分類')
    add_parser.add_argument('--tags', help='標籤 (逗號分隔)')
    add_parser.add_argument('--content', required=True, help='內容')
    
    # get
    get_parser = subparsers.add_parser('get', help='讀取備忘錄')
    get_parser.add_argument('--file', required=True, help='檔名')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        result = list_notes(args.category)
    elif args.command == 'search':
        result = search_notes(args.query, args.category, args.tag)
    elif args.command == 'add':
        tags = [t.strip() for t in args.tags.split(',')] if args.tags else []
        result = add_note(args.title, args.category, args.content, tags)
    elif args.command == 'get':
        result = get_note(args.file)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
