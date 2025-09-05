#!/usr/bin/env python3
import logging
from report_merger import ReportMerger
from report_delivery import ReportDelivery
from config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_report_merger():
    """Test report merging functionality"""
    try:
        # Initialize merger with test dates
        merger = ReportMerger("2024-08", "2025-08")
        
        # Test merge process
        output_path = merger.merge_reports()
        
        if output_path:
            logger.info(f"Successfully created merged report: {output_path}")
            
            # Test delivery
            delivery = ReportDelivery("test@example.com")
            
            # Test email delivery
            logger.info("Testing email delivery...")
            delivery.send_success_notification(output_path)
            
            # Test shared folder delivery
            logger.info("Testing shared folder delivery...")
            delivery.copy_to_shared_folder(output_path)
            
            # Cleanup
            merger.cleanup_temp_files()
            
        else:
            logger.error("Failed to merge reports")
            
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")

def main():
    print("=== Testing Report Merger and Delivery ===")
    print("\nThis test will:")
    print("1. Merge any existing report files in temp_downloads")
    print("2. Perform calculations")
    print("3. Test email delivery")
    print("4. Test shared folder delivery")
    print("\nPress Enter to start the test (Ctrl+C to cancel)")
    
    try:
        input()
        test_report_merger()
    except KeyboardInterrupt:
        print("\nTest cancelled by user")
    except Exception as e:
        print(f"\nTest failed: {str(e)}")

if __name__ == "__main__":
    main()
