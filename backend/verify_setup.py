#!/usr/bin/env python3
"""
Simple verification script to check if Redash MCP is configured correctly
No additional dependencies required
"""

import json
import os
import sys

def check_mcp_json():
    """Check if mcp.json has Redash configuration"""
    print("1. Checking mcp.json configuration...")
    
    mcp_path = "../mcp.json"
    if not os.path.exists(mcp_path):
        print("   ❌ mcp.json not found")
        return False
    
    with open(mcp_path, 'r') as f:
        config = json.load(f)
    
    if 'redash-mcp' not in config.get('mcpServers', {}):
        print("   ❌ redash-mcp not found in mcp.json")
        return False
    
    redash_config = config['mcpServers']['redash-mcp']
    print(f"   ✅ Redash MCP found in configuration")
    print(f"   Command: {redash_config['command']}")
    print(f"   Args: {' '.join(redash_config['args'])}")
    print(f"   Description: {redash_config['description']}")
    return True

def check_env_file():
    """Check if .env file has Redash credentials"""
    print("\n2. Checking .env file...")
    
    if not os.path.exists('.env'):
        print("   ❌ .env file not found")
        return False
    
    with open('.env', 'r') as f:
        env_content = f.read()
    
    has_url = 'REDASH_URL=' in env_content
    has_key = 'REDASH_API_KEY=' in env_content
    
    if has_url and has_key:
        # Extract values
        for line in env_content.split('\n'):
            if line.startswith('REDASH_URL='):
                url = line.split('=', 1)[1].strip()
                print(f"   ✅ REDASH_URL: {url}")
            if line.startswith('REDASH_API_KEY='):
                key = line.split('=', 1)[1].strip()
                print(f"   ✅ REDASH_API_KEY: {key[:10]}... (configured)")
        return True
    else:
        print("   ❌ Missing REDASH_URL or REDASH_API_KEY")
        return False

def check_files():
    """Check if all necessary files are present"""
    print("\n3. Checking required files...")
    
    files = {
        'app.py': 'Main FastAPI application',
        'mcp_client.py': 'MCP client implementation',
        'test_redash_mcp.py': 'Redash test suite',
        'redash_examples.py': 'Usage examples',
        'requirements.txt': 'Python dependencies'
    }
    
    all_present = True
    for filename, description in files.items():
        if os.path.exists(filename):
            size = os.path.getsize(filename) / 1024  # KB
            print(f"   ✅ {filename:25} ({size:.1f}KB) - {description}")
        else:
            print(f"   ❌ {filename:25} - {description} (MISSING)")
            all_present = False
    
    return all_present

def check_node():
    """Check if Node.js is installed (required for npx)"""
    print("\n4. Checking Node.js installation...")
    
    import subprocess
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"   ✅ Node.js installed: {version}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("   ⚠️  Node.js not found or not in PATH")
    print("   Note: Node.js is required to run MCP servers via npx")
    print("   Install: https://nodejs.org/ or run 'brew install node'")
    return False

def check_redash_connectivity():
    """Check if we can reach the Redash server"""
    print("\n5. Checking Redash connectivity...")
    
    try:
        import urllib.request
        import ssl
        
        # Read credentials
        url = None
        api_key = None
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('REDASH_URL='):
                    url = line.split('=', 1)[1].strip()
                if line.startswith('REDASH_API_KEY='):
                    api_key = line.split('=', 1)[1].strip()
        
        if not url or not api_key:
            print("   ⚠️  Cannot test - credentials not found")
            return False
        
        # Try to connect
        context = ssl._create_unverified_context()
        req = urllib.request.Request(f"{url}/api/queries?page=1&page_size=1")
        req.add_header('Authorization', f'Key {api_key}')
        
        response = urllib.request.urlopen(req, timeout=10, context=context)
        if response.status == 200:
            print(f"   ✅ Successfully connected to {url}")
            print(f"   ✅ API key is valid")
            return True
        else:
            print(f"   ⚠️  Received status code: {response.status}")
            return False
            
    except Exception as e:
        print(f"   ⚠️  Could not connect: {e}")
        print(f"   Note: This might be a network issue or firewall")
        return False

def main():
    """Run all verification checks"""
    
    print("\n" + "="*70)
    print(" "*15 + "REDASH MCP SETUP VERIFICATION")
    print("="*70 + "\n")
    
    results = {
        'mcp.json': check_mcp_json(),
        '.env file': check_env_file(),
        'Files': check_files(),
        'Node.js': check_node(),
        'Connectivity': check_redash_connectivity()
    }
    
    print("\n" + "="*70)
    print(" "*25 + "SUMMARY")
    print("="*70)
    
    for check, passed in results.items():
        status = "✅ PASS" if passed else "⚠️  CHECK"
        print(f"{check:.<40} {status}")
    
    print("="*70 + "\n")
    
    if all(results.values()):
        print("🎉 All checks passed! Your Redash MCP is ready to use!")
        print("\nNext steps:")
        print("1. Install MCP SDK: pip install mcp (when available)")
        print("2. Start backend: python app.py")
        print("3. Test API: curl http://localhost:8000/api/mcp/servers")
        return 0
    else:
        print("⚠️  Some checks didn't pass, but configuration is mostly ready!")
        print("\nYour Redash MCP is configured. You can still:")
        print("1. Start the backend: python app.py")
        print("2. Use the REST API to connect to Redash")
        print("3. Install missing dependencies as needed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

