#!/usr/bin/env python3
"""Update README.md with latest GitHub statistics"""

import re
import os
import requests
from datetime import datetime
from typing import Dict, Any

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
GITHUB_USERNAME = 'TimotheeNkwar'

def get_github_stats() -> Dict[str, Any]:
    """Fetch GitHub statistics using GraphQL API"""
    
    headers = {
        'Authorization': f'Bearer {GITHUB_TOKEN}',
        'Content-Type': 'application/json',
    }
    
    query = """
    query {
        user(login: "%s") {
            contributionsCollection {
                contributionCalendar {
                    totalContributions
                }
            }
            repositories(first: 100) {
                totalCount
            }
        }
    }
    """ % GITHUB_USERNAME
    
    try:
        response = requests.post(
            'https://api.github.com/graphql',
            json={'query': query},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        if 'errors' in data:
            print(f"GraphQL Error: {data['errors']}")
            return None
        
        user = data['data']['user']
        total_contributions = user['contributionsCollection']['contributionCalendar']['totalContributions']
        repos_count = user['repositories']['totalCount']
        
        return {
            'total_contributions': total_contributions,
            'repos_count': repos_count,
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        }
    
    except Exception as e:
        print(f"Error fetching GitHub stats: {e}")
        return None

def get_streak_stats() -> Dict[str, Any]:
    """Fetch streak statistics from API if available"""
    try:
        # Trying to fetch from a public endpoint (may need adaptation)
        response = requests.get(
            f'https://streak-stats.demolab.com/api?user={GITHUB_USERNAME}',
            timeout=10
        )
        # Note: This endpoint may not expose JSON, adjust accordingly
        return None
    except Exception as e:
        print(f"Could not fetch streak stats: {e}")
        return None

def update_readme(stats: Dict[str, Any]) -> bool:
    """Update README.md with new statistics"""
    
    if not stats:
        print("No stats available to update")
        return False
    
    readme_path = 'README.md'
    
    if not os.path.exists(readme_path):
        print(f"README.md not found")
        return False
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match the stats overview section
    pattern = r"(\*\*📈 Stats Overview:\*\*\n\n- \*\*)\d+((\*\* Total Contributions \(Since May 10, 2023\))"
    replacement = rf"\g<1>{stats['total_contributions']}\g<2>"
    
    updated_content = re.sub(pattern, replacement, content)
    
    # Check if content actually changed
    if updated_content == content:
        print("No changes detected in README")
        return False
    
    # Write updated content
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"✅ README updated successfully")
    print(f"   Total Contributions: {stats['total_contributions']}")
    print(f"   Updated at: {stats['updated_at']}")
    
    return True

def main():
    """Main function"""
    print("Fetching GitHub statistics...")
    stats = get_github_stats()
    
    if stats:
        print("\n📊 Statistics fetched:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print("\nUpdating README.md...")
        if update_readme(stats):
            print("\n✅ All done!")
        else:
            print("\n⚠️ README was not updated")
    else:
        print("❌ Failed to fetch statistics")

if __name__ == '__main__':
    main()
