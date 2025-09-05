import os
import pandas as pd
import logging
from datetime import datetime
from typing import List, Dict, Optional
from config import Config

logger = logging.getLogger(__name__)

class ReportMerger:
    def __init__(self, start_date: str, end_date: str):
        self.start_date = start_date
        self.end_date = end_date
        self.temp_dir = os.path.join(os.getcwd(), "temp_downloads")
        self.merge_dir = os.path.join(os.getcwd(), "merge")
        self.ensure_directories()

    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.merge_dir, exist_ok=True)

    def get_raw_files(self) -> List[str]:
        """Get list of raw report files from temp directory"""
        files = []
        for file in os.listdir(self.temp_dir):
            if file.startswith("margin_") and file.endswith(".xlsx"):
                files.append(os.path.join(self.temp_dir, file))
        return sorted(files)

    def merge_reports(self) -> Optional[str]:
        """Merge all raw report files and perform calculations"""
        try:
            raw_files = self.get_raw_files()
            if not raw_files:
                logger.error("No raw files found to merge")
                return None

            # Read and combine all raw files
            dfs = []
            for file in raw_files:
                df = pd.read_excel(file)
                dfs.append(df)

            # Combine all data
            combined_df = pd.concat(dfs, ignore_index=True)

            # Group by unique identifiers and perform calculations
            grouped = combined_df.groupby(['No.', 'Customer No.']).agg({
                'Invoiced Quantity': 'sum',
                'Gross Sales Amount': 'sum',
                'Net Sales Amount': 'sum',
                'Cost': 'sum',
                'Profit': 'sum'
            }).reset_index()

            # Calculate derived metrics
            grouped['Gross Unit Price'] = grouped['Gross Sales Amount'] / grouped['Invoiced Quantity']
            grouped['Net Unit Price'] = grouped['Net Sales Amount'] / grouped['Invoiced Quantity']
            grouped['Unit Cost'] = grouped['Cost'] / grouped['Invoiced Quantity']
            grouped['Unit Profit'] = grouped['Net Unit Price'] - grouped['Unit Cost']
            grouped['Profit Percent'] = grouped['Profit'] / grouped['Net Sales Amount']
            grouped['Off-Invoice Allowance %'] = (grouped['Gross Sales Amount'] - grouped['Net Sales Amount']) / grouped['Gross Sales Amount']

            # Create output filename
            output_filename = f"Margin_Report_{self.start_date}_{self.end_date}.xlsx"
            output_path = os.path.join(self.merge_dir, output_filename)

            # Save with formatting
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                grouped.to_excel(writer, index=False, sheet_name='Margin Report')
                
                # Get the worksheet
                worksheet = writer.sheets['Margin Report']
                
                # Apply formatting
                for idx, col in enumerate(grouped.columns, 1):
                    cell = worksheet.cell(row=1, column=idx)
                    cell.font = cell.font.copy(bold=True)
                
                # Add autofilter
                worksheet.auto_filter.ref = worksheet.dimensions

            logger.info(f"Successfully created merged report: {output_filename}")
            return output_path

        except Exception as e:
            logger.error(f"Error merging reports: {str(e)}")
            return None

    def cleanup_temp_files(self):
        """Remove temporary raw files after successful merge"""
        try:
            for file in self.get_raw_files():
                os.remove(file)
            logger.info("Successfully cleaned up temporary files")
        except Exception as e:
            logger.error(f"Error cleaning up temporary files: {str(e)}")
