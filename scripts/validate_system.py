#!/usr/bin/env python3
"""
AURORA SYSTEM VALIDATION
========================

Pre-demo validation checklist to ensure all components are working.
Run this before demonstrating to judges.

Usage:
    python scripts/validate_system.py
"""

from __future__ import annotations

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
CHECKBOX_PASS = f'{GREEN}✓{RESET}'
CHECKBOX_FAIL = f'{RED}✗{RESET}'
CHECKBOX_WARN = f'{YELLOW}⚠{RESET}'


class SystemValidator:
    """Validates AURORA system readiness for judge demonstration."""
    
    def __init__(self):
        self.checks = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0
    
    def add_check(self, name: str, passed: bool, message: str = "") -> None:
        """Record a check result."""
        symbol = CHECKBOX_PASS if passed else CHECKBOX_FAIL
        print(f"  {symbol} {name}")
        if message:
            print(f"      {message}")
        
        self.checks.append((name, passed, message))
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def add_warning(self, name: str, message: str = "") -> None:
        """Record a warning."""
        print(f"  {CHECKBOX_WARN} {name}")
        if message:
            print(f"      {message}")
        self.warnings += 1
    
    def validate_files(self) -> None:
        """Check that all required files exist."""
        print("\n1. FILE STRUCTURE")
        print("─" * 60)
        
        required_files = {
            "Model": "models/model.pkl",
            "Feature Schema": "models/feature_schema.json",
            "Training Report": "models/training_report.json",
            "Agent Memory": "backend/ml/agent_memory.py",
            "Live Loop": "backend/services/live_trading_loop.py",
            "Dashboard": "frontend/dashboard_live.py",
            "Master Demo": "scripts/demo_complete.py",
            "Exchange Manager": "backend/execution/exchange_manager.py",
            "Failover Service": "backend/execution/exchange_failover_service.py",
        }
        
        for name, filepath in required_files.items():
            full_path = project_root / filepath
            exists = full_path.exists()
            message = f"{filepath}" if not exists else ""
            self.add_check(f"{name}", exists, message)
    
    def validate_imports(self) -> None:
        """Check that key modules can be imported."""
        print("\n2. PYTHON IMPORTS")
        print("─" * 60)
        
        imports = {
            "pandas": "Data processing",
            "numpy": "Numerical operations",
            "xgboost": "ML model",
            "streamlit": "Dashboard UI",
            "plotly": "Interactive charts",
            "ccxt": "Exchange connectivity",
        }
        
        for module, purpose in imports.items():
            try:
                __import__(module)
                self.add_check(f"{module}", True, purpose)
            except ImportError as e:
                self.add_check(f"{module}", False, f"Missing: {purpose}")
    
    def validate_model(self) -> None:
        """Check that trained model exists and is loadable."""
        print("\n3. ML MODEL")
        print("─" * 60)
        
        import pickle
        
        model_path = project_root / "models" / "model.pkl"
        
        if not model_path.exists():
            self.add_check("Model File", False, "models/model.pkl not found")
            return
        
        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            self.add_check("Model Loadable", True, "XGBoost model loaded successfully")
            self.add_check("Model Type", hasattr(model, 'predict'), f"Type: {type(model).__name__}")
        except Exception as e:
            self.add_check("Model Loadable", False, f"Error: {str(e)}")
    
    def validate_feature_schema(self) -> None:
        """Check feature schema."""
        print("\n4. FEATURE SCHEMA")
        print("─" * 60)
        
        import json
        
        schema_path = project_root / "models" / "feature_schema.json"
        
        if not schema_path.exists():
            self.add_check("Schema File", False, "models/feature_schema.json not found")
            return
        
        try:
            with open(schema_path, 'r') as f:
                schema = json.load(f)
            feature_count = len(schema.get('features', []))
            self.add_check("Schema Loadable", True, f"{feature_count} features defined")
        except Exception as e:
            self.add_check("Schema Loadable", False, f"Error: {str(e)}")
    
    def validate_classes(self) -> None:
        """Check that key classes can be instantiated."""
        print("\n5. CORE CLASSES")
        print("─" * 60)
        
        # Test AgentMemory
        try:
            from backend.ml.agent_memory import AgentMemory
            memory = AgentMemory(max_history=50)
            self.add_check("AgentMemory", True, "Instantiated successfully")
        except Exception as e:
            self.add_check("AgentMemory", False, f"Error: {str(e)}")
        
        # Test ExchangeManager
        try:
            from backend.execution.exchange_manager import ExchangeManager
            self.add_check("ExchangeManager", True, "Import successful")
        except Exception as e:
            self.add_check("ExchangeManager", False, f"Error: {str(e)}")
        
        # Test LiveTradingLoop
        try:
            from backend.services.live_trading_loop import LiveTradingLoop
            self.add_check("LiveTradingLoop", True, "Import successful")
        except Exception as e:
            self.add_check("LiveTradingLoop", False, f"Error: {str(e)}")
    
    def validate_exchange_connectivity(self) -> None:
        """Test exchange connectivity."""
        print("\n6. EXCHANGE CONNECTIVITY")
        print("─" * 60)
        
        try:
            from backend.execution.exchange_failover_service import (
                initialize_exchange_system,
                get_exchange_service
            )
            
            # Initialize system
            if not initialize_exchange_system(region="india"):
                self.add_check("Exchange Init", False, "Failed to initialize exchange system")
                return
            
            self.add_check("Exchange Init", True, "India region initialized")
            
            # Get service
            service = get_exchange_service()
            if service is None:
                self.add_check("Exchange Service", False, "Could not get exchange service")
                return
            
            self.add_check("Exchange Service", True, "Service retrieved")
            
            # Test ticker fetch
            try:
                ticker = service.get_ticker("BTC/USDT")
                if ticker:
                    price = ticker.get('last', 'N/A')
                    self.add_check("Ticker Fetch", True, f"BTC/USDT: ${price}")
                else:
                    self.add_check("Ticker Fetch", False, "No ticker data returned")
            except Exception as e:
                self.add_warning("Ticker Fetch", f"Network issue (expected if no internet)")
        
        except Exception as e:
            self.add_check("Exchange System", False, f"Error: {str(e)}")
    
    def validate_documentation(self) -> None:
        """Check that documentation exists."""
        print("\n7. DOCUMENTATION")
        print("─" * 60)
        
        docs = {
            "WINNER_GUIDE.md": "Competition strategy guide",
            "LIVE_TRADING_GUIDE.md": "Operation instructions",
            "COMPETITION_SUBMISSION.md": "Demo protocol",
            "EXCHANGE_FAILOVER_GUIDE.md": "Failover system docs",
        }
        
        for doc, purpose in docs.items():
            path = project_root / doc
            self.add_check(doc, path.exists(), purpose)
    
    def validate_scripts(self) -> None:
        """Check demo scripts."""
        print("\n8. DEMO SCRIPTS")
        print("─" * 60)
        
        scripts = {
            "scripts/demo_complete.py": "Complete system demo",
            "scripts/demo_exchange_failover.py": "Failover demonstration",
        }
        
        for script, purpose in scripts.items():
            path = project_root / script
            self.add_check(script, path.exists(), purpose)
    
    def print_summary(self) -> None:
        """Print validation summary."""
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        
        total = self.passed + self.failed + self.warnings
        
        print(f"\n{CHECKBOX_PASS} Passed:  {self.passed}/{total}")
        print(f"{CHECKBOX_FAIL} Failed:  {self.failed}/{total}")
        if self.warnings:
            print(f"{CHECKBOX_WARN} Warnings: {self.warnings}")
        
        if self.failed == 0:
            print(f"\n{GREEN}✓ SYSTEM READY FOR DEMO{RESET}")
            return True
        else:
            print(f"\n{RED}✗ SYSTEM NOT READY - Fix errors above{RESET}")
            return False
    
    def run(self) -> bool:
        """Run all validations."""
        print("\n" + "=" * 60)
        print("AURORA SYSTEM VALIDATION")
        print("=" * 60)
        print("Pre-demo checklist - ensuring all components ready\n")
        
        self.validate_files()
        self.validate_imports()
        self.validate_model()
        self.validate_feature_schema()
        self.validate_classes()
        self.validate_exchange_connectivity()
        self.validate_documentation()
        self.validate_scripts()
        
        return self.print_summary()


def main() -> None:
    """Run validation."""
    validator = SystemValidator()
    success = validator.run()
    
    if not success:
        print(f"\n{YELLOW}⚠ To fix issues:{RESET}")
        print("  1. Train model: python backend/ml/train.py")
        print("  2. Install missing packages: pip install -r requirements.txt")
        print("  3. Check file paths in workspace")
        sys.exit(1)
    
    print(f"\n{GREEN}Ready to run demo:{RESET}")
    print("  python scripts/demo_complete.py --duration 10")
    print("\nIn another terminal:")
    print("  streamlit run frontend/dashboard_live.py")
    print("\nGood luck! 🚀")


if __name__ == "__main__":
    main()
