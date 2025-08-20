#!/usr/bin/env python3
"""
Setup script for Margin Report Automation System
Helps users install dependencies and configure the system
"""

import os
import sys
import subprocess
import shutil

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_pip():
    """Check if pip is available"""
    try:
        import pip
        print("✅ pip is available")
        return True
    except ImportError:
        print("❌ pip is not available")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        # Install from requirements.txt
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create .env file from template"""
    print("\n🔧 Setting up environment configuration...")
    
    if os.path.exists(".env"):
        print("✅ .env file already exists")
        return True
    
    if os.path.exists("env_example.txt"):
        try:
            shutil.copy("env_example.txt", ".env")
            print("✅ Created .env file from template")
            print("   Please edit .env with your NetSuite credentials")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("⚠️  env_example.txt not found")
        return False

def test_imports():
    """Test if all modules can be imported"""
    print("\n🧪 Testing module imports...")
    
    modules = [
        "date_parser",
        "email_processor", 
        "netsuite_client",
        "config"
    ]
    
    all_good = True
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module} imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import {module}: {e}")
            all_good = False
    
    return all_good

def run_basic_test():
    """Run a basic test to verify functionality"""
    print("\n🧪 Running basic functionality test...")
    
    try:
        from date_parser import DateParser
        
        # Test basic date parsing
        parser = DateParser()
        result = parser.parse_date_string("2025/08")
        
        if result and result.get('fiscal_year') == 'FY 2025':
            print("✅ Basic date parsing test passed")
            return True
        else:
            print("❌ Basic date parsing test failed")
            return False
            
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Margin Report Automation System - Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_pip():
        print("Please install pip and try again")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("Failed to install dependencies")
        sys.exit(1)
    
    # Create environment file
    if not create_env_file():
        print("Failed to create environment file")
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("Some modules failed to import")
        sys.exit(1)
    
    # Run basic test
    if not run_basic_test():
        print("Basic functionality test failed")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your NetSuite credentials")
    print("2. Run 'python3 demo.py' to see the system in action")
    print("3. Run 'python3 test_system.py' to run comprehensive tests")
    print("4. Run 'python3 main.py' to use the full system")
    
    print("\nFor help, see README.md")

if __name__ == "__main__":
    main()
