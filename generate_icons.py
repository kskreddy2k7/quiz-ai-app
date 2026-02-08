#!/usr/bin/env python3
"""
Generate PNG icons from SVG for PWA/Android app
Requires: pip install cairosvg pillow
"""
import os

try:
    import cairosvg
    from PIL import Image
    import io
    
    SIZES = [144, 192, 512, 1024]
    SVG_PATH = 'static/icon.svg'
    OUTPUT_DIR = 'static'
    
    print("Generating app icons from SVG...")
    
    with open(SVG_PATH, 'r') as f:
        svg_data = f.read()
    
    for size in SIZES:
        # Generate PNG using cairosvg
        png_data = cairosvg.svg2png(
            bytestring=svg_data.encode('utf-8'),
            output_width=size,
            output_height=size
        )
        
        # Save the PNG
        output_path = os.path.join(OUTPUT_DIR, f'icon-{size}.png')
        with open(output_path, 'wb') as f:
            f.write(png_data)
        
        print(f"✓ Generated {output_path} ({size}x{size})")
    
    print("\n✅ All icons generated successfully!")
    print("\nGenerated files:")
    for size in SIZES:
        print(f"  - static/icon-{size}.png")
    
except ImportError as e:
    print("⚠️  Required libraries not installed.")
    print("To generate icons, install: pip install cairosvg pillow")
    print("\nFallback: Using SVG icon directly in manifest.")
    print("For production, please generate PNG icons manually or use an online tool.")
    print("Recommended tool: https://realfavicongenerator.net/")
    
except Exception as e:
    print(f"❌ Error generating icons: {e}")
    print("\nFallback: Using SVG icon directly in manifest.")
    print("For production, please generate PNG icons manually.")

if __name__ == '__main__':
    pass
