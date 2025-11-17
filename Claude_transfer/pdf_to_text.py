#!/usr/bin/env python3
"""
PDF to Text Converter with OCR capabilities.
Extracts text from PDF files using pdfplumber and optional OCR with pytesseract.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union
import pdfplumber
import pytesseract
from PIL import Image
import click
import io

def setup_logging(name: str, verbose: bool = False) -> logging.Logger:
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(name)

class PDFTextExtractor:
    """Handles PDF text extraction with optional OCR."""
    
    def __init__(self, output_dir: Optional[str] = None, overwrite: bool = False, 
                 dry_run: bool = False, use_ocr: bool = False):
        self.output_dir = Path(output_dir) if output_dir else None
        self.overwrite = overwrite
        self.dry_run = dry_run
        self.use_ocr = use_ocr
        self.errors = []
        
    def process_single_pdf(self, pdf_path: Path) -> bool:
        """Process a single PDF file."""
        if not pdf_path.exists():
            logger.error(f"PDF file does not exist: {pdf_path}")
            return False
            
        try:
            # Determine output path
            output_path = self._get_output_path(pdf_path)
            if output_path.exists() and not self.overwrite:
                logger.info(f"Output file exists (skipping): {output_path}")
                return True
                
            if self.dry_run:
                logger.info(f"Would process: {pdf_path} -> {output_path}")
                return True
                
            # Extract text
            text = self._extract_text(pdf_path)
            if not text:
                logger.error(f"No text extracted from {pdf_path}")
                return False
                
            # Write output
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
                
            logger.info(f"Successfully processed: {pdf_path} -> {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {str(e)}")
            self.errors.append(str(e))
            return False
            
    def process_directory(self, dir_path: Path, recursive: bool = False) -> Dict[str, int]:
        """Process all PDFs in a directory."""
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory does not exist: {dir_path}")
            
        pattern = '**/*.pdf' if recursive else '*.pdf'
        pdf_files = list(dir_path.glob(pattern))
        
        results = {
            'total': len(pdf_files),
            'processed': 0,
            'failed': 0,
            'errors': self.errors
        }
        
        for pdf_path in pdf_files:
            success = self.process_single_pdf(pdf_path)
            if success:
                results['processed'] += 1
            else:
                results['failed'] += 1
                
        return results
        
    def _get_output_path(self, pdf_path: Path) -> Path:
        """Determine output text file path."""
        if self.output_dir:
            return self.output_dir / f"{pdf_path.stem}.txt"
        return pdf_path.with_suffix('.txt')
        
    def _extract_text(self, pdf_path: Path) -> str:
        """Extract text from PDF using pdfplumber and optional OCR."""
        text_parts = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Try normal text extraction
                text = page.extract_text() or ""
                
                # If OCR is enabled and no text found, try OCR
                if self.use_ocr and not text.strip():
                    image = page.to_image()
                    text = pytesseract.image_to_string(
                        Image.open(io.BytesIO(image.original.encode()))
                    )
                    
                text_parts.append(f"--- PAGE {page.page_number} ---\n{text}")
                
        return "\n\n".join(text_parts)

@click.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('--output-dir', '-o', type=click.Path(),
              help='Output directory for text files')
@click.option('--recursive', '-r', is_flag=True,
              help='Process subdirectories recursively')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose logging')
@click.option('--dry-run', is_flag=True,
              help='Show what would be processed without converting')
@click.option('--overwrite', is_flag=True,
              help='Overwrite existing text files')
@click.option('--ocr', is_flag=True,
              help='Use OCR for image-based PDFs')
def main(input_path, output_dir, recursive, verbose, dry_run, overwrite, ocr):
    """Extract text from PDF files."""
    global logger
    logger = setup_logging('pdf_to_text', verbose=verbose)
    
    try:
        # Create extractor
        extractor = PDFTextExtractor(output_dir, overwrite=overwrite,
                                   dry_run=dry_run, use_ocr=ocr)
        
        input_path_obj = Path(input_path)
        if input_path_obj.is_file():
            success = extractor.process_single_pdf(input_path_obj)
            exit(0 if success else 1)
        elif input_path_obj.is_dir():
            results = extractor.process_directory(input_path_obj, recursive)
            logger.info(f"Processed {results['processed']} of {results['total']} files "
                       f"({results['failed']} failed)")
            exit(0 if results['failed'] == 0 else 1)
        else:
            logger.error(f"Input path does not exist: {input_path}")
            exit(1)
            
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        exit(1)

def process_pdf(input_path: str, output_dir: Optional[str] = None, recursive: bool = False, 
              verbose: bool = False, dry_run: bool = False, overwrite: bool = False, 
              ocr: bool = False) -> tuple[bool, Optional[str]]:
    """
    Process PDF files without using command line interface.
    
    Args:
        input_path: Path to PDF file or directory
        output_dir: Output directory for text files (default: same as input)
        recursive: Process subdirectories recursively
        verbose: Enable verbose logging
        dry_run: Show what would be processed without converting
        overwrite: Overwrite existing text files
        ocr: Use OCR for image-based PDFs
    
    Returns:
        tuple: (success: bool, error_message: Optional[str])
            - success: True if successful, False if any errors occurred
            - error_message: None if successful, error description if failed
    """
    try:
        # Validate input path
        if not input_path:
            return False, "Input path cannot be empty"
            
        input_path_obj = Path(input_path)
        if not input_path_obj.exists():
            return False, f"Input path does not exist: {input_path}"
            
        # Validate output directory if provided
        if output_dir:
            output_dir_obj = Path(output_dir)
            if not output_dir_obj.exists() and not dry_run:
                try:
                    output_dir_obj.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    return False, f"Failed to create output directory: {e}"
        
        # Setup logging
        global logger
        logger = setup_logging('pdf_to_text', verbose=verbose)
        
        # Create extractor
        try:
            extractor = PDFTextExtractor(output_dir, overwrite=overwrite, 
                                       dry_run=dry_run, use_ocr=ocr)
        except Exception as e:
            return False, f"Failed to initialize PDF extractor: {e}"
        
        # Process based on input type
        if input_path_obj.is_file():
            if input_path_obj.suffix.lower() != '.pdf':
                return False, f"Input file is not a PDF: {input_path}"
            
            success = extractor.process_single_pdf(input_path_obj)
            if not success:
                return False, f"Failed to process PDF file: {input_path}"
            return True, None
            
        elif input_path_obj.is_dir():
            results = extractor.process_directory(input_path_obj, recursive)
            if results['failed'] > 0:
                error_msg = f"Failed to process {results['failed']} out of {results['total']} files"
                if results['errors']:
                    error_msg += f"\nFirst error: {results['errors'][0]}"
                return False, error_msg
            return True, None
            
        else:
            return False, f"Input path is neither a file nor directory: {input_path}"
            
    except Exception as e:
        error_msg = f"Unexpected error processing PDF: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

if __name__ == '__main__':
    main()