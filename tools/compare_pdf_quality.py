#!/usr/bin/env python3
"""
Compare PDF quality between two sources (e.g., PrimeGov vs Laserfiche)

Usage:
    python3 compare_pdf_quality.py <pdf1> <pdf2>
    python3 compare_pdf_quality.py primegov_minutes.pdf laserfiche_minutes.pdf

Requirements:
    - poppler-utils: brew install poppler (provides pdfinfo, pdfimages, pdftotext)
    - PyMuPDF (optional): pip install pymupdf (for additional metrics)

Output:
    Detailed comparison report showing which source has better quality
"""

import argparse
import subprocess
import sys
from pathlib import Path


def check_dependencies():
    """Check if required tools are installed"""
    tools = ['pdfinfo', 'pdftotext', 'pdfimages']
    missing = []

    for tool in tools:
        try:
            subprocess.run([tool, '--version'], capture_output=True, timeout=5)
        except FileNotFoundError:
            missing.append(tool)
        except subprocess.TimeoutExpired:
            pass  # Tool exists but timed out

    if missing:
        print(f"⚠️  Missing tools: {', '.join(missing)}")
        print("   Install with: brew install poppler")
        return False
    return True


def get_pdf_info(pdf_path):
    """Extract comprehensive PDF metadata and quality indicators"""
    path = Path(pdf_path)

    if not path.exists():
        print(f"❌ File not found: {pdf_path}")
        return None

    info = {
        'path': str(path),
        'filename': path.name,
        'file_size_bytes': path.stat().st_size,
        'file_size_kb': path.stat().st_size / 1024,
        'file_size_mb': path.stat().st_size / (1024 * 1024),
    }

    # Get PDF metadata using pdfinfo
    try:
        result = subprocess.run(
            ['pdfinfo', str(path)],
            capture_output=True, text=True, timeout=30
        )
        for line in result.stdout.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                info[key] = value

                # Parse numeric values
                if key == 'pages':
                    try:
                        info['page_count'] = int(value)
                    except ValueError:
                        pass
                elif key == 'page_size':
                    # Parse "612 x 792 pts (letter)"
                    try:
                        parts = value.split()
                        info['page_width_pts'] = float(parts[0])
                        info['page_height_pts'] = float(parts[2])
                    except (ValueError, IndexError):
                        pass

    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"   ⚠️  pdfinfo error: {e}")

    # Analyze images using pdfimages
    try:
        result = subprocess.run(
            ['pdfimages', '-list', str(path)],
            capture_output=True, text=True, timeout=60
        )

        lines = [l for l in result.stdout.split('\n') if l.strip()]
        # Skip header lines
        data_lines = [l for l in lines if not l.startswith('page') and not l.startswith('-')]

        info['image_count'] = len(data_lines)

        # Parse image details
        resolutions_x = []
        resolutions_y = []
        image_sizes = []

        for line in data_lines:
            parts = line.split()
            if len(parts) >= 8:
                try:
                    width = int(parts[3])
                    height = int(parts[4])
                    x_ppi = int(parts[5])
                    y_ppi = int(parts[6])

                    resolutions_x.append(x_ppi)
                    resolutions_y.append(y_ppi)
                    image_sizes.append(width * height)
                except (ValueError, IndexError):
                    pass

        if resolutions_x:
            info['avg_image_dpi_x'] = sum(resolutions_x) / len(resolutions_x)
            info['avg_image_dpi_y'] = sum(resolutions_y) / len(resolutions_y)
            info['avg_image_dpi'] = (info['avg_image_dpi_x'] + info['avg_image_dpi_y']) / 2
            info['max_image_dpi'] = max(max(resolutions_x), max(resolutions_y))
            info['min_image_dpi'] = min(min(resolutions_x), min(resolutions_y))
            info['total_image_pixels'] = sum(image_sizes)
            info['avg_image_pixels'] = sum(image_sizes) / len(image_sizes)

    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"   ⚠️  pdfimages error: {e}")

    # Extract and analyze text
    try:
        result = subprocess.run(
            ['pdftotext', '-layout', str(path), '-'],
            capture_output=True, text=True, timeout=120
        )
        text = result.stdout

        info['text_length'] = len(text)
        info['text_lines'] = len(text.split('\n'))
        info['text_words'] = len(text.split())
        info['text_chars_no_space'] = len(text.replace(' ', '').replace('\n', ''))

        # Quality indicators
        # Count Unicode replacement characters (indicates encoding issues)
        info['unicode_errors'] = text.count('�')

        # Count excessive spacing (indicates poor OCR)
        double_spaces = text.count('  ')
        single_spaces = text.count(' ') - double_spaces
        info['double_space_ratio'] = double_spaces / max(single_spaces, 1)

        # Count likely OCR artifacts
        ocr_artifacts = sum([
            text.count('|'),  # Often misread 'l' or 'I'
            text.count('~'),  # Often misread '-'
            text.count('`'),  # Often misread apostrophe
        ])
        info['ocr_artifacts'] = ocr_artifacts

        # Estimate text quality score (0-100)
        quality_penalties = 0
        quality_penalties += min(info['unicode_errors'] * 2, 30)
        quality_penalties += min(info['double_space_ratio'] * 50, 20)
        quality_penalties += min(info['ocr_artifacts'] / 10, 20)
        info['text_quality_score'] = max(0, 100 - quality_penalties)

        # Check for searchable text vs scanned
        info['is_searchable'] = info['text_words'] > 100

        # Sample text (first 500 chars for inspection)
        info['text_sample'] = text[:500].replace('\n', ' ')[:200]

    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"   ⚠️  pdftotext error: {e}")

    return info


def compare_pdfs(pdf1_path, pdf2_path, label1="Source 1", label2="Source 2"):
    """Compare two PDFs and determine which has better quality"""

    print("\n" + "=" * 80)
    print("PDF QUALITY COMPARISON")
    print("=" * 80)

    # Get info for both PDFs
    print(f"\n📄 Analyzing {label1}: {Path(pdf1_path).name}")
    info1 = get_pdf_info(pdf1_path)

    print(f"📄 Analyzing {label2}: {Path(pdf2_path).name}")
    info2 = get_pdf_info(pdf2_path)

    if not info1 or not info2:
        print("\n❌ Cannot compare - one or both files could not be analyzed")
        return None

    # Define comparison metrics
    # (label, key, preference: 'higher'|'lower'|'equal', weight)
    metrics = [
        ("File Size (MB)", 'file_size_mb', 'higher', 1),
        ("Page Count", 'page_count', 'equal', 0),
        ("Image Count", 'image_count', 'info', 0),
        ("Avg Image DPI", 'avg_image_dpi', 'higher', 3),
        ("Max Image DPI", 'max_image_dpi', 'higher', 2),
        ("Min Image DPI", 'min_image_dpi', 'higher', 1),
        ("Total Image Pixels", 'total_image_pixels', 'higher', 2),
        ("Text Words", 'text_words', 'higher', 2),
        ("Text Quality Score", 'text_quality_score', 'higher', 3),
        ("Unicode Errors", 'unicode_errors', 'lower', 2),
        ("OCR Artifacts", 'ocr_artifacts', 'lower', 1),
        ("Double Space Ratio", 'double_space_ratio', 'lower', 1),
    ]

    # Print comparison table
    print(f"\n{'Metric':<25} {label1:<20} {label2:<20} {'Winner':<15}")
    print("-" * 80)

    scores = {label1: 0, label2: 0}
    details = []

    for label, key, preference, weight in metrics:
        val1 = info1.get(key, 'N/A')
        val2 = info2.get(key, 'N/A')

        winner = '-'
        winner_label = None

        if val1 != 'N/A' and val2 != 'N/A' and preference != 'info':
            try:
                num1 = float(val1) if not isinstance(val1, bool) else (1 if val1 else 0)
                num2 = float(val2) if not isinstance(val2, bool) else (1 if val2 else 0)

                if preference == 'higher':
                    if num1 > num2 * 1.05:  # 5% threshold
                        winner = f"← {label1}"
                        winner_label = label1
                    elif num2 > num1 * 1.05:
                        winner = f"→ {label2}"
                        winner_label = label2
                    else:
                        winner = "≈ Equal"
                elif preference == 'lower':
                    if num1 < num2 * 0.95:
                        winner = f"← {label1}"
                        winner_label = label1
                    elif num2 < num1 * 0.95:
                        winner = f"→ {label2}"
                        winner_label = label2
                    else:
                        winner = "≈ Equal"
                elif preference == 'equal':
                    if abs(num1 - num2) < 0.01:
                        winner = "✓ Match"
                    else:
                        winner = "✗ Mismatch"

                if winner_label:
                    scores[winner_label] += weight

            except (ValueError, TypeError):
                pass

        # Format values for display
        if isinstance(val1, float):
            val1_str = f"{val1:.2f}"
        else:
            val1_str = str(val1)

        if isinstance(val2, float):
            val2_str = f"{val2:.2f}"
        else:
            val2_str = str(val2)

        print(f"{label:<25} {val1_str:<20} {val2_str:<20} {winner:<15}")

        details.append({
            'metric': label,
            'source1_value': val1,
            'source2_value': val2,
            'winner': winner_label,
            'weight': weight
        })

    # Print summary
    print("-" * 80)
    print(f"\n{'WEIGHTED SCORE:':<25} {scores[label1]:<20} {scores[label2]:<20}")

    # Determine overall winner
    print("\n" + "=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)

    if scores[label2] > scores[label1] * 1.2:
        print(f"\n✅ {label2} is SIGNIFICANTLY BETTER")
        print(f"   Use {label2} as your primary document source.")
        winner = label2
    elif scores[label1] > scores[label2] * 1.2:
        print(f"\n✅ {label1} is SIGNIFICANTLY BETTER")
        print(f"   Use {label1} as your primary document source.")
        winner = label1
    elif scores[label2] > scores[label1]:
        print(f"\n✅ {label2} is SLIGHTLY BETTER")
        print(f"   {label2} has marginally better quality.")
        winner = label2
    elif scores[label1] > scores[label2]:
        print(f"\n✅ {label1} is SLIGHTLY BETTER")
        print(f"   {label1} has marginally better quality.")
        winner = label1
    else:
        print(f"\n⚖️  SOURCES ARE COMPARABLE")
        print(f"   Choose based on convenience or availability.")
        winner = "tie"

    # Key insights
    print("\n📊 Key Insights:")

    # DPI comparison
    dpi1 = info1.get('avg_image_dpi', 0)
    dpi2 = info2.get('avg_image_dpi', 0)
    if dpi1 and dpi2:
        if dpi1 > dpi2:
            print(f"   • {label1} has {dpi1:.0f} DPI vs {dpi2:.0f} DPI ({(dpi1/dpi2-1)*100:.0f}% higher resolution)")
        elif dpi2 > dpi1:
            print(f"   • {label2} has {dpi2:.0f} DPI vs {dpi1:.0f} DPI ({(dpi2/dpi1-1)*100:.0f}% higher resolution)")

    # Text quality
    tq1 = info1.get('text_quality_score', 0)
    tq2 = info2.get('text_quality_score', 0)
    if tq1 and tq2:
        print(f"   • Text quality scores: {label1}={tq1:.0f}/100, {label2}={tq2:.0f}/100")

    # File size
    size1 = info1.get('file_size_mb', 0)
    size2 = info2.get('file_size_mb', 0)
    if size1 and size2:
        print(f"   • File sizes: {label1}={size1:.2f}MB, {label2}={size2:.2f}MB")

    print()

    return {
        'winner': winner,
        'scores': scores,
        'details': details,
        'info1': info1,
        'info2': info2
    }


def main():
    parser = argparse.ArgumentParser(
        description='Compare PDF quality between two sources'
    )

    parser.add_argument(
        'pdf1',
        help='First PDF file (e.g., from PrimeGov)'
    )

    parser.add_argument(
        'pdf2',
        help='Second PDF file (e.g., from Laserfiche)'
    )

    parser.add_argument(
        '--label1',
        default='PrimeGov',
        help='Label for first PDF source (default: PrimeGov)'
    )

    parser.add_argument(
        '--label2',
        default='Laserfiche',
        help='Label for second PDF source (default: Laserfiche)'
    )

    parser.add_argument(
        '--output',
        help='Save comparison results to JSON file'
    )

    args = parser.parse_args()

    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install required dependencies first")
        sys.exit(1)

    # Run comparison
    result = compare_pdfs(
        args.pdf1,
        args.pdf2,
        label1=args.label1,
        label2=args.label2
    )

    # Save results if requested
    if args.output and result:
        import json
        # Remove non-serializable items
        output_result = {
            'winner': result['winner'],
            'scores': result['scores'],
            'source1': {
                'label': args.label1,
                'path': args.pdf1,
                'metrics': {k: v for k, v in result['info1'].items()
                          if k != 'text_sample'}
            },
            'source2': {
                'label': args.label2,
                'path': args.pdf2,
                'metrics': {k: v for k, v in result['info2'].items()
                          if k != 'text_sample'}
            }
        }

        with open(args.output, 'w') as f:
            json.dump(output_result, f, indent=2)
        print(f"📄 Results saved to: {args.output}")


if __name__ == '__main__':
    main()
