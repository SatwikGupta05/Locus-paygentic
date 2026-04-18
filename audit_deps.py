import os
import re
import json

def audit():
    package_path = 'frontend/package.json'
    if not os.path.exists(package_path):
        print(f"Error: {package_path} not found")
        return

    with open(package_path, 'r', encoding='utf-8') as f:
        pkg_data = json.load(f)
    
    dependencies = set(pkg_data.get('dependencies', {}).keys())
    dev_dependencies = set(pkg_data.get('devDependencies', {}).keys())
    all_known = dependencies.union(dev_dependencies)

    missing = set()
    
    # Regex to find imports: import ... from 'pkg' or from "pkg"
    # Also handles: import 'pkg'
    import_re = re.compile(r'(?:from|import)\s+[\'\"](@?[\w\-/]+)[\'\"]')

    for root, dirs, files in os.walk('frontend'):
        if 'node_modules' in dirs:
            dirs.remove('node_modules')
        if '.next' in dirs:
            dirs.remove('.next')
            
        for file in files:
            if file.endswith(('.ts', '.tsx')):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    matches = import_re.findall(content)
                    for match in matches:
                        # Filter out relative imports and aliases
                        if match.startswith(('.') or match.startswith('@/')):
                            continue
                        
                        # Filter out built-ins or special Next.js imports
                        if match in ['react', 'react-dom'] or match.startswith('next/'):
                            continue
                            
                        # Handle scoped packages (e.g., @radix-ui/react-tabs)
                        # We only want the base package name
                        parts = match.split('/')
                        base_pkg = parts[0]
                        if base_pkg.startswith('@') and len(parts) > 1:
                            base_pkg = f"{parts[0]}/{parts[1]}"
                        
                        if base_pkg not in all_known:
                            missing.add(base_pkg)
                except Exception as e:
                    print(f"Error reading {path}: {e}")

    print("Missing packages identified:")
    for m in sorted(list(missing)):
        print(f"- {m}")

if __name__ == "__main__":
    audit()
