#!/usr/bin/env python3
"""
Setup script for ReAct AI Search Agent
"""

import os
import sys
import subprocess
from pathlib import Path

def print_step(step_num, title, description=""):
    """Print setup step with formatting"""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {title}")
    if description:
        print(f"{description}")
    print('='*60)

def check_python_version():
    """Check if Python version is compatible"""
    print_step(1, "CHECKING PYTHON VERSION")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. Current: {version.major}.{version.minor}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def setup_virtual_environment():
    """Setup virtual environment"""
    print_step(2, "SETTING UP VIRTUAL ENVIRONMENT")
    
    if os.path.exists("venv"):
        print("⚠️  Virtual environment already exists")
        response = input("Do you want to recreate it? (y/N): ").lower()
        if response == 'y':
            import shutil
            shutil.rmtree("venv")
        else:
            print("✅ Using existing virtual environment")
            return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def install_dependencies():
    """Install required dependencies"""
    print_step(3, "INSTALLING DEPENDENCIES")
    
    # Determine pip path based on OS
    if os.name == 'nt':  # Windows
        pip_path = os.path.join("venv", "Scripts", "pip")
    else:  # Linux/Mac
        pip_path = os.path.join("venv", "bin", "pip")
    
    if not os.path.exists(pip_path):
        print(f"❌ Pip not found at: {pip_path}")
        return False
    
    try:
        # Upgrade pip first
        subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
        print("✅ Pip upgraded successfully")
        
        # Install requirements
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment_file():
    """Setup environment configuration"""
    print_step(4, "SETTING UP ENVIRONMENT CONFIGURATION")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("⚠️  .env file already exists")
        response = input("Do you want to recreate it? (y/N): ").lower()
        if response != 'y':
            print("✅ Using existing .env file")
            return True
    
    if not env_example.exists():
        print("❌ .env.example file not found")
        return False
    
    try:
        # Copy example to .env
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        
        print("✅ .env file created from template")
        print("\n📝 IMPORTANT: Please edit .env file and add your API keys:")
        print("   - GEMINI_API_KEY: Get from https://makersuite.google.com/")
        print("   - SERPAPI_KEY: Get from https://serpapi.com/")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def verify_installation():
    """Verify installation by running a simple test"""
    print_step(5, "VERIFYING INSTALLATION")
    
    # Check if we can import required modules
    test_imports = [
        "google.generativeai",
        "serpapi", 
        "transformers",
        "torch"
    ]
    
    # Determine python path
    if os.name == 'nt':  # Windows
        python_path = os.path.join("venv", "Scripts", "python")
    else:  # Linux/Mac
        python_path = os.path.join("venv", "bin", "python")
    
    print("Testing imports...")
    for module in test_imports:
        try:
            result = subprocess.run([
                python_path, "-c", f"import {module}; print('✅ {module}')"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(result.stdout.strip())
            else:
                print(f"❌ {module}: {result.stderr.strip()}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⚠️  {module}: Import test timed out (this is normal for some modules)")
        except Exception as e:
            print(f"❌ {module}: {e}")
            return False
    
    print("\n✅ Installation verification completed")
    return True

def print_next_steps():
    """Print next steps for the user"""
    print_step(6, "NEXT STEPS")
    
    activation_cmd = ""
    if os.name == 'nt':  # Windows
        activation_cmd = "venv\\Scripts\\activate"
    else:  # Linux/Mac
        activation_cmd = "source venv/bin/activate"
    
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print(f"   1. Activate virtual environment: {activation_cmd}")
    print("   2. Edit .env file and add your API keys")
    print("   3. Test the installation:")
    print("      python run_agent.py quick")
    print("   4. Start using the agent:")
    print("      python main.py interactive")
    
    print("\n📚 Documentation:")
    print("   - README.md: Complete documentation")
    print("   - main.py: Full-featured interface")
    print("   - run_agent.py: Quick testing")
    
    print("\n🔗 Get API Keys:")
    print("   - Gemini API: https://makersuite.google.com/")
    print("   - SerpAPI: https://serpapi.com/ (free tier available)")

def main():
    """Main setup function"""
    print("🚀 REACT AI SEARCH AGENT - SETUP")
    print("This script will set up your development environment")
    
    # Confirm setup
    response = input("\nDo you want to continue with setup? (Y/n): ").lower()
    if response == 'n':
        print("Setup cancelled.")
        return
    
    # Run setup steps
    steps = [
        check_python_version,
        setup_virtual_environment, 
        install_dependencies,
        setup_environment_file,
        verify_installation
    ]
    
    for step_func in steps:
        if not step_func():
            print(f"\n❌ Setup failed at step: {step_func.__name__}")
            print("Please fix the issues above and run setup again.")
            return
    
    print_next_steps()

if __name__ == "__main__":
    main()