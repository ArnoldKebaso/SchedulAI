#!/usr/bin/env python3
"""
Test script to debug SchedulAI application startup
"""
import os
import sys

print("=== SchedulAI Debug Test ===")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

try:
    print("\n1. Testing imports...")
    from flask import Flask
    print("✓ Flask import successful")
    
    from database import db, register_db
    print("✓ Database import successful")
    
    from calendar_module.calendar_service import list_events, create_event
    print("✓ Calendar service import successful")
    
    from ai.scheduler_ai import schedule_event
    print("✓ AI scheduler import successful")
    
    print("\n2. Testing config...")
    import config
    print("✓ Config import successful")
    
    print("\n3. Testing app creation...")
    from app import create_app
    print("✓ create_app import successful")
    
    app = create_app()
    print("✓ Flask app created successfully")
    
    print("\n4. Testing database initialization...")
    with app.app_context():
        db.create_all()
        print("✓ Database tables created successfully")
    
    print("\n5. Testing Ollama connection...")
    from ai.scheduler_ai import chat
    response = chat("Hello, just testing!", "You are a test assistant.")
    print(f"✓ Ollama response: {response[:50]}...")
    
    print("\n6. Testing calendar service...")
    events = list_events()
    print(f"✓ Calendar events fetched: {len(events)} events")
    
    print("\n=== All tests passed! Starting Flask app ===")
    app.run(debug=True, host='127.0.0.1', port=5000)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
