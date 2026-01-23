#!/usr/bin/env python3
"""
Generate RELEASE_X.ini files by fetching latest GitHub release tags
for sysmodules, overlays, apps, and emulatoren.
"""

import re
import json
import os
import time
import urllib.request
import urllib.error
import configparser
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# GitHub API base URL
GITHUB_API = "https://api.github.com/repos"

# Get GitHub token from environment variable if available
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')

def extract_repo_from_url(url: str) -> Optional[Tuple[str, str]]:
    """Extract owner and repo from GitHub API URL."""
    # Pattern: https://api.github.com/repos/owner/repo/releases?...
    match = re.search(r'/repos/([^/]+)/([^/]+)/releases', url)
    if match:
        return (match.group(1), match.group(2))
    return None

def get_latest_tag(owner: str, repo: str) -> Optional[str]:
    """Fetch the latest release tag from GitHub API."""
    url = f"{GITHUB_API}/{owner}/{repo}/releases?per_page=1"
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Release-Tag-Fetcher/1.0')
        if GITHUB_TOKEN:
            req.add_header('Authorization', f'token {GITHUB_TOKEN}')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            releases = json.loads(response.read().decode('utf-8'))
            if releases and len(releases) > 0:
                return releases[0].get('tag_name', releases[0].get('name', ''))
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print(f"  Rate limit exceeded. Set GITHUB_TOKEN env var for higher limits.")
        elif e.code == 404:
            print(f"  Repository not found")
        else:
            print(f"  HTTP {e.code}: {e.reason}")
    except Exception as e:
        print(f"  Error: {e}")
    return None

def parse_ini_file(file_path: Path) -> List[Dict[str, str]]:
    """Parse .ini file and extract entries with GitHub API URLs."""
    entries = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all section headers
    sections = re.finditer(r'^\[([^\]]+)\]', content, re.MULTILINE)
    
    for section_match in sections:
        section_name = section_match.group(1)
        section_start = section_match.end()
        
        # Find next section or end of file
        next_section = re.search(r'^\[', content[section_start:], re.MULTILINE)
        section_end = section_start + (next_section.start() if next_section else len(content[section_start:]))
        section_content = content[section_start:section_end]
        
        # Look for GitHub API URLs in this section
        github_urls = re.findall(r'https://api\.github\.com/repos/[^\s]+', section_content)
        
        if github_urls:
            repo_info = extract_repo_from_url(github_urls[0])
            if repo_info:
                entries.append({
                    'name': section_name,
                    'owner': repo_info[0],
                    'repo': repo_info[1],
                    'url': github_urls[0]
                })
    
    return entries

def generate_release_ini(category: str, entries: List[Dict[str, str]], output_path: Path):
    """Generate RELEASE_X.ini file for a category."""
    print(f"\nGenerating {output_path.name}...")
    print(f"Found {len(entries)} entries")
    
    # Create config parser
    config = configparser.ConfigParser()
    config.optionxform = str  # Preserve case
    
    # Create section based on category
    if category == 'sysmodules':
        section_name = 'Versions'
    elif category == 'overlays':
        section_name = 'Versions'
    elif category == 'apps':
        section_name = 'Versions'
    elif category == 'emulatoren':
        section_name = 'Versions'
    else:
        section_name = 'Release Info'
    
    config.add_section(section_name)
    
    # Monitoring statistics
    success_count = 0
    failure_count = 0
    failed_entries = []
    
    # Fetch tags for each entry
    for i, entry in enumerate(entries):
        # Add delay between requests to avoid rate limiting (except for first request)
        if i > 0:
            time.sleep(0.5)  # 500ms delay between requests
        
        print(f"  Fetching {entry['name']} ({entry['owner']}/{entry['repo']})...", end=' ')
        tag = get_latest_tag(entry['owner'], entry['repo'])
        if tag:
            # Remove 'v' prefix if present for cleaner version
            clean_tag = tag.lstrip('v')
            # Truncate very long version strings (e.g., commit hashes) to max 30 chars for Switch display
            if len(clean_tag) > 30:
                # Try to extract meaningful part (e.g., commit hash from "weekly-canary-release-25f89d3...")
                if '-' in clean_tag:
                    parts = clean_tag.split('-')
                    # If it looks like a commit hash at the end, take last part and truncate to 7 chars
                    if len(parts) > 1 and len(parts[-1]) > 20:
                        clean_tag = f"{parts[-2]}-{parts[-1][:7]}" if len(parts) > 1 else parts[-1][:7]
                    else:
                        clean_tag = clean_tag[:30]
                else:
                    clean_tag = clean_tag[:30]
            config.set(section_name, entry['name'], clean_tag)
            success_count += 1
            print(f"✓ {clean_tag}")
        else:
            failure_count += 1
            failed_entries.append(f"{entry['name']} ({entry['owner']}/{entry['repo']})")
            print("✗ Failed")
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        config.write(f, space_around_delimiters=False)
    
    # Print monitoring summary
    print(f"\n✓ Created {output_path}")
    print(f"  Success: {success_count}/{len(entries)}")
    if failure_count > 0:
        print(f"  Failed: {failure_count}/{len(entries)}")
        for failed in failed_entries:
            print(f"    - {failed}")
    
    return {
        'category': category,
        'total': len(entries),
        'success': success_count,
        'failed': failure_count,
        'failed_entries': failed_entries
    }

def main():
    """Main function."""
    base_path = Path(__file__).parent
    include_path = base_path / "include"
    
    print("GitHub Release Tag Fetcher")
    if GITHUB_TOKEN:
        print("✓ Using GitHub token (higher rate limit)")
    else:
        print("⚠ No GitHub token found. Set GITHUB_TOKEN env var for higher rate limits.")
    print("=" * 50)
    
    # Track all results for final summary
    all_results = []
    
    # Process sysmodules
    sysmodules_path = include_path / "sysmodules" / "sysmodules.ini"
    if sysmodules_path.exists():
        entries = parse_ini_file(sysmodules_path)
        if entries:
            output_path = include_path / "sysmodules" / "RELEASE_SM.ini"
            result = generate_release_ini('sysmodules', entries, output_path)
            all_results.append(result)
    
    # Process overlays
    overlays_path = include_path / "overlays" / "overlays.ini"
    if overlays_path.exists():
        entries = parse_ini_file(overlays_path)
        if entries:
            output_path = include_path / "overlays" / "RELEASE_OV.ini"
            result = generate_release_ini('overlays', entries, output_path)
            all_results.append(result)
    
    # Process apps
    apps_path = include_path / "apps" / "apps.ini"
    if apps_path.exists():
        entries = parse_ini_file(apps_path)
        if entries:
            output_path = include_path / "apps" / "RELEASE_APPS.ini"
            result = generate_release_ini('apps', entries, output_path)
            all_results.append(result)
    
    # Process emulatoren
    emulatoren_path = include_path / "emulatoren" / "emulatoren.ini"
    if emulatoren_path.exists():
        entries = parse_ini_file(emulatoren_path)
        if entries:
            output_path = include_path / "emulatoren" / "RELEASE_EM.ini"
            result = generate_release_ini('emulatoren', entries, output_path)
            all_results.append(result)
    
    # Print final monitoring summary
    print("\n" + "=" * 50)
    print("FINAL SUMMARY")
    print("=" * 50)
    total_entries = sum(r['total'] for r in all_results)
    total_success = sum(r['success'] for r in all_results)
    total_failed = sum(r['failed'] for r in all_results)
    
    print(f"Total entries processed: {total_entries}")
    print(f"Successfully fetched: {total_success} ({total_success/total_entries*100:.1f}%)" if total_entries > 0 else "Successfully fetched: 0")
    print(f"Failed: {total_failed} ({total_failed/total_entries*100:.1f}%)" if total_entries > 0 else "Failed: 0")
    
    # List all failed entries by category
    if total_failed > 0:
        print("\nFailed entries by category:")
        for result in all_results:
            if result['failed'] > 0:
                print(f"  {result['category']}:")
                for failed in result['failed_entries']:
                    print(f"    - {failed}")
    
    print("\n" + "=" * 50)
    print("Done!")

if __name__ == "__main__":
    main()

