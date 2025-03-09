#!/usr/bin/env python3
"""
TRIZ Tool Builder
----------------
A Python script to build the TRIZ tool website from separate components.
Makes it easier to maintain and edit the content.
"""

import json
import os
from pathlib import Path
import shutil
import re
from datetime import datetime
import sys

# Ensure directories exist
def ensure_dirs():
    """Create necessary directories if they don't exist."""
    directories = [
        'data', 
        'static/css', 
        'static/js', 
        'static/img/flags', 
        'templates', 
        'templates/components'
    ]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

# Load JSON data
def load_data(filename):
    """Load data from a JSON file."""
    try:
        with open(f'data/{filename}', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {filename} not found. Using empty data.")
        return {}

# Render template with data
def render_template(template_path, data=None):
    """Render a template with provided data."""
    if data is None:
        data = {}
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
            
        # Simple template variable replacement
        for key, value in data.items():
            placeholder = f"{{{{ {key} }}}}"
            template = template.replace(placeholder, str(value))
            
        return template
    except FileNotFoundError:
        print(f"Warning: Template {template_path} not found.")
        return ""

# Build the site with optional matrix size
def build_site(matrix_size=None):
    """Build the complete TRIZ tool site."""
    print("Building TRIZ Tool site...")
    
    # Determine available matrix sizes
    matrix_sizes = [39]  # Default size
    
    # Check for additional matrix sizes
    for filename in os.listdir('data'):
        if filename.startswith('matrix_') and filename.endswith('.json'):
            try:
                size = int(filename.replace('matrix_', '').replace('.json', ''))
                matrix_sizes.append(size)
            except ValueError:
                continue
    
    matrix_sizes.sort()
    print(f"Available matrix sizes: {matrix_sizes}")
    
    # Prepare data for templates
    data = {
        'year': datetime.now().year,
        'matrix_sizes': matrix_sizes
    }
    
    # Render components
    header = render_template('templates/components/header.html', data)
    footer = render_template('templates/components/footer.html', data)
    
    # Render main content
    content = render_template('templates/index.html', data)
    
    # Render complete page
    complete_data = data.copy()
    complete_data.update({
        'header': header,
        'content': content,
        'footer': footer
    })
    
    complete_page = render_template('templates/base.html', complete_data)
    
    # Write output
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(complete_page)
    
    # Copy static files and ensure data files are available
    copy_static_files()
    
    print("Build complete!")

# Copy static files to output directory
def copy_static_files():
    """Copy CSS, JS and image files to output directory."""
    # Simple implementation - just ensures the files exist
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/img/flags', exist_ok=True)
    
    # Create sample flag images if they don't exist
    for lang in ['en', 'fr', 'de']:
        flag_path = f'static/img/flags/{lang}.png'
        if not os.path.exists(flag_path):
            print(f"Creating sample flag image: {flag_path}")
            with open(flag_path, 'wb') as f:
                # Create an empty PNG file as a placeholder
                f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x00\x00\x02\x00\x01\xe5\'\xde\xfc\x00\x00\x00\x00IEND\xaeB`\x82')

# Extract data from an existing HTML file
def extract_data_from_html(html_path):
    """Extract data from an existing HTML file into separate JSON and component files."""
    print(f"Extracting data from {html_path}...")
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Extract CSS
    css_match = re.search(r'<style>(.*?)</style>', html_content, re.DOTALL)
    if css_match:
        with open('static/css/styles.css', 'w', encoding='utf-8') as f:
            f.write(css_match.group(1).strip())
        print("✓ Extracted CSS to static/css/styles.css")
    
    # Extract features
    features_match = re.search(r'const trizFeatures = \[(.*?)\];', html_content, re.DOTALL)
    if features_match:
        features_text = features_match.group(1)
        # Convert JS array to Python list
        features = []
        for line in features_text.split(',\n'):
            # Remove quotes and whitespace
            line = line.strip().strip('"').strip("'")
            if line:
                features.append(line)
        
        with open('data/features.json', 'w', encoding='utf-8') as f:
            json.dump(features, f, indent=2)
        print("✓ Extracted features to data/features.json")
    
    # Extract principles
    principles_match = re.search(r'const trizPrinciples = \[(.*?)\];', html_content, re.DOTALL)
    if principles_match:
        # This is complex to parse directly
        # Save as JavaScript that we can process
        principles_js = f"const trizPrinciples = [{principles_match.group(1)}];"
        with open('temp_principles.js', 'w', encoding='utf-8') as f:
            f.write(principles_js)
            f.write("""
// Now convert to JSON format
const output = trizPrinciples.map((principle, index) => {
    return {
        id: index + 1,
        name: principle[0],
        descriptions: principle[1].map(desc => {
            return {
                text: desc[0],
                examples: desc.slice(1)
            };
        })
    };
});
console.log(JSON.stringify(output, null, 2));
""")
        
        print("Created temporary principles.js - run with Node.js to extract")
        print("✓ Run: node temp_principles.js > data/principles.json")
    
    # Extract matrix - this is complex to parse directly from the HTML
    matrix_match = re.search(r'const trizMatrix = \[(.*?)\];', html_content, re.DOTALL)
    if matrix_match:
        # Save as JavaScript that we can process
        matrix_js = f"const trizMatrix = [{matrix_match.group(1)}];"
        with open('temp_matrix.js', 'w', encoding='utf-8') as f:
            f.write(matrix_js)
            f.write("""
// Now convert to a cleaner JSON format
const output = trizMatrix.map(row => {
    return row.map(cell => {
        // Filter out trailing zeros and -1 values
        return cell.filter(value => value > 0);
    });
});
console.log(JSON.stringify(output, null, 2));
""")
        
        print("Created temporary matrix.js - run with Node.js to extract")
        print("✓ Run: node temp_matrix.js > data/matrix.json")
    
    # Extract HTML structure - header, content, footer
    header_match = re.search(r'<div class="banner">(.*?)<div class="container">', html_content, re.DOTALL)
    if header_match:
        header_html = '<div class="banner">' + header_match.group(1)
        os.makedirs('templates/components', exist_ok=True)
        with open('templates/components/header.html', 'w', encoding='utf-8') as f:
            f.write(header_html)
        print("✓ Extracted header to templates/components/header.html")
    
    footer_match = re.search(r'<footer class="footer">(.*?)</footer>', html_content, re.DOTALL)
    if footer_match:
        footer_html = '<footer class="footer">' + footer_match.group(1) + '</footer>'
        os.makedirs('templates/components', exist_ok=True)
        with open('templates/components/footer.html', 'w', encoding='utf-8') as f:
            f.write(footer_html)
        print("✓ Extracted footer to templates/components/footer.html")
    
    # Extract the main content
    content_match = re.search(r'<div class="container">(.*?)<footer class="footer">', html_content, re.DOTALL)
    if content_match:
        content_html = content_match.group(1).strip()
        os.makedirs('templates', exist_ok=True)
        with open('templates/index.html', 'w', encoding='utf-8') as f:
            f.write(content_html)
        print("✓ Extracted main content to templates/index.html")
    
    # Create base template
    base_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TRIZ40: Solving Technical Problems with TRIZ Methodology</title>
    <meta name="description" content="TRIZ Interactive Matrix, illustrated TRIZ 40 principles and 39 feature contradiction table">
    <meta name="keywords" content="TRIZ, matrix, contradiction, principles, interactive, table, 40, forty, overcome, TRIZ40">
    
    <!-- Bootstrap 5 -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    
    <!-- Custom styles -->
    <link href="static/css/styles.css" rel="stylesheet">
</head>
<body>
    {{ header }}
    
    <!-- Main Content -->
    <div class="container">
        {{ content }}
    </div>
    
    {{ footer }}

    <!-- JavaScript -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/js/bootstrap.bundle.min.js"></script>
    
    <!-- App Logic -->
    <script src="static/js/app.js"></script>
</body>
</html>"""
    
    with open('templates/base.html', 'w', encoding='utf-8') as f:
        f.write(base_html)
    print("✓ Created base template in templates/base.html")
    
    # Extract JavaScript (minus the data arrays)
    js_match = re.search(r'<script>\s*// TRIZ Principles(.*?)</script>', html_content, re.DOTALL)
    if js_match:
        js_content = js_match.group(1).strip()
        
        # Remove the data arrays
        js_content = re.sub(r'const trizPrinciples = \[.*?\];', '// Principles loaded from JSON', js_content, flags=re.DOTALL)
        js_content = re.sub(r'const trizFeatures = \[.*?\];', '// Features loaded from JSON', js_content, flags=re.DOTALL)
        js_content = re.sub(r'const trizMatrix = \[.*?\];', '// Matrix loaded from JSON', js_content, flags=re.DOTALL)
        
        # Add data loading
        app_js = """/**
 * TRIZ Tool Application Logic
 * 
 * This file contains the main functionality for the TRIZ40 tool.
 * Data is loaded from separate JSON files for easier maintenance.
 */

// Global data variables
let trizFeatures = [];
let trizPrinciples = [];
let trizMatrix = [];

// Load data when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Load data from JSON files
    Promise.all([
        fetch('data/features.json').then(response => response.json()),
        fetch('data/principles.json').then(response => response.json()),
        fetch('data/matrix.json').then(response => response.json())
    ]).then(([features, principles, matrix]) => {
        trizFeatures = features;
        trizPrinciples = principles;
        trizMatrix = matrix;
        
        // Initialize the app
        populateFeatureDropdowns();
        setupEventListeners();
    }).catch(error => {
        console.error('Error loading data:', error);
        alert('Error loading data. Please try refreshing the page.');
    });
});

"""
        
        # Add the rest of the JS content
        app_js += js_content
        
        with open('static/js/app.js', 'w', encoding='utf-8') as f:
            f.write(app_js)
        print("✓ Created app.js in static/js/")
    
    print("Data extraction complete!")
    print("Now run 'python build.py' to build the site.")

# Create default matrix size conversion file
def create_matrix_conversion(source_size, target_size, output_filename):
    """Create a matrix size conversion file from one size to another."""
    print(f"Creating matrix conversion from {source_size} to {target_size}...")
    
    # Load source matrix
    source_suffix = "" if source_size == 39 else f"_{source_size}"
    source_matrix = load_data(f"matrix{source_suffix}.json")
    
    if not source_matrix:
        print(f"Error: Source matrix not found (matrix{source_suffix}.json)")
        return False
    
    # Create target matrix (extended with empty arrays)
    target_matrix = []
    for i in range(target_size):
        if i < len(source_matrix):
            # Copy existing row
            row = source_matrix[i].copy()
            # Extend row if needed
            while len(row) < target_size:
                row.append([])
            target_matrix.append(row)
        else:
            # Add new empty row
            target_matrix.append([[] for _ in range(target_size)])
    
    # Save the target matrix
    with open(f'data/{output_filename}', 'w', encoding='utf-8') as f:
        json.dump(target_matrix, f, indent=2)
    
    print(f"✓ Created {output_filename}")
    return True

# Create features file with extended features
def create_extended_features(source_size, target_size, output_filename):
    """Create an extended features file."""
    print(f"Creating extended features from {source_size} to {target_size}...")
    
    # Load source features
    source_suffix = "" if source_size == 39 else f"_{source_size}"
    source_features = load_data(f"features{source_suffix}.json")
    
    if not source_features:
        print(f"Error: Source features not found (features{source_suffix}.json)")
        return False
    
    # Create target features
    target_features = source_features.copy()
    
    # Add placeholder features for the extended ones
    while len(target_features) < target_size:
        feature_num = len(target_features) + 1
        target_features.append(f"{feature_num}: Extended feature {feature_num}")
    
    # Save the target features
    with open(f'data/{output_filename}', 'w', encoding='utf-8') as f:
        json.dump(target_features, f, indent=2)
    
    print(f"✓ Created {output_filename}")
    return True

# Main function
def main():
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'extract' and len(sys.argv) > 2:
            # Extract data from HTML
            ensure_dirs()
            extract_data_from_html(sys.argv[2])
        elif command == 'init':
            # Initialize the project structure
            ensure_dirs()
            print("Project structure initialized. Add your files and run 'python build.py'.")
        elif command == 'create-matrix' and len(sys.argv) > 3:
            # Create a new matrix size from an existing one
            ensure_dirs()
            try:
                source_size = int(sys.argv[2])
                target_size = int(sys.argv[3])
                if source_size >= target_size:
                    print("Error: Target size must be larger than source size.")
                    return
                
                # Create matrix and features files
                matrix_success = create_matrix_conversion(source_size, target_size, f"matrix_{target_size}.json")
                features_success = create_extended_features(source_size, target_size, f"features_{target_size}.json")
                
                if matrix_success and features_success:
                    print(f"Successfully created {target_size}×{target_size} matrix and features files.")
                    print("You can now edit these files to add your custom data.")
            except ValueError:
                print("Error: Size parameters must be integers.")
                print("Usage: python build.py create-matrix <source_size> <target_size>")
        else:
            print("Unknown command. Available commands:")
            print("  python build.py - Build the site")
            print("  python build.py extract <html_file> - Extract data from HTML")
            print("  python build.py init - Initialize project structure")
            print("  python build.py create-matrix <source_size> <target_size> - Create a new matrix size")
    else:
        # Build the site
        ensure_dirs()
        build_site()

if __name__ == "__main__":
    main()