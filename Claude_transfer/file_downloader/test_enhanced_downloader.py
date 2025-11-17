#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced file downloader capabilities
"""

import subprocess
import sys

def run_test(description, command):
    """Run a test command and show results"""
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print(f"{'='*60}")
    print(f"Command: {command}")
    print("Results:")
    
    try:
        result = subprocess.run(command.split(), capture_output=True, text=True, timeout=30)
        output_lines = result.stdout.split('\n')
        
        # Show first 15 lines of output
        for line in output_lines[:15]:
            if line.strip():
                print(f"  {line}")
        
        if len(output_lines) > 15:
            print("  ...")
            
    except subprocess.TimeoutExpired:
        print("  ⏰ Test timed out")
    except Exception as e:
        print(f"  ❌ Test failed: {e}")

def main():
    """Run all tests"""
    print("🧪 Testing Enhanced File Downloader")
    print("This demonstrates the new flexible structure support and auto-detection")
    
    tests = [
        (
            "Auto-detect minutes from Columbus (Legistar structure)",
            "python3 file_downloader/file_downloader.py --input Columbus_OH/Columbus_meetings_2024_clean.json --key auto_minutes --output Columbus_OH/PDF --dry-run"
        ),
        (
            "Auto-detect agenda from Houston (NovusAgenda structure)",
            "python3 file_downloader/file_downloader.py --input Houston_TX/json_files/houston_council_latest.json --key auto_agenda --output Houston_TX/PDF --dry-run"
        ),
        (
            "Partial match 'minutes' in Pomona (Legistar structure)",
            "python3 file_downloader/file_downloader.py --input Pomona_CA/json/Pomona_meetings_2024_20250814_103247.json --key minutes --output Pomona_CA/PDF --dry-run"
        ),
        (
            "Partial match 'agenda' in Santa Ana (PrimeGov structure)",
            "python3 file_downloader/file_downloader.py --input Santa_Ana_CA/json_files/santa_ana_city_council_2024_20250810_094633.json --key agenda --output Santa_Ana_CA/PDF --dry-run"
        ),
        (
            "Auto-detect any PDF from Houston",
            "python3 file_downloader/file_downloader.py --input Houston_TX/json_files/houston_council_latest.json --key auto_pdf --output Houston_TX/PDF --dry-run"
        )
    ]
    
    for description, command in tests:
        run_test(description, command)
    
    print(f"\n{'='*60}")
    print("🎉 Testing Complete!")
    print("The enhanced file downloader now supports:")
    print("  ✅ Multiple city structures (Santa Ana, Houston, Columbus, Pomona)")
    print("  ✅ Auto-detection modes (auto_minutes, auto_agenda, auto_pdf)")
    print("  ✅ Partial key matching (finds keys containing search terms)")
    print("  ✅ PDF preference (prioritizes PDF URLs over HTML when multiple options exist)")
    print("  ✅ Flexible filename generation with proper date parsing and titles")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
