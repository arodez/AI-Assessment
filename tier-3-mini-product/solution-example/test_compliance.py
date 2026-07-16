import datetime
import pytest
from core import parse_and_validate_csv, calculate_dashboard_metrics

def test_parse_valid_csv():
    csv_data = """name,email,team,course,course_status,deadline
Ana Torres,ana.torres@example.com,Platform,Intro to AI Agents,completed,2026-06-30
Luis Mendoza,luis.mendoza@example.com,Platform,Intro to AI Agents,Pending,2026-06-15
Sofia Reyes,sofia.reyes@example.com,Data,LLM Concepts,in_progress,2026-07-14
"""
    valid, rejected = parse_and_validate_csv(csv_data)
    assert len(valid) == 3
    assert len(rejected) == 0
    
    # Assert normalization of Pending to pending
    assert valid[1]["course_status"] == "pending"
    assert valid[0]["name"] == "Ana Torres"

def test_parse_missing_headers():
    csv_data = """name,email,team,course,course_status
Ana Torres,ana.torres@example.com,Platform,Intro to AI Agents,completed
"""
    valid, rejected = parse_and_validate_csv(csv_data)
    assert len(valid) == 0
    assert len(rejected) == 1
    assert "Missing required columns" in rejected[0]["reason"]

def test_parse_validation_failures():
    csv_data = """name,email,team,course,course_status,deadline
Diego Fuentes,diego.fuentes@example.com,Data,LLM Concepts,pending
Camila Ortiz,camila.ortiz@example.com,Mobile,AI-Assisted Coding,completed,not-a-date
Jorge Salinas,,Mobile,AI-Assisted Coding,pending,2026-06-20
Renata Vega,renata.vega.example.com,Mobile,LLM Concepts,pending,2026-08-15
"""
    valid, rejected = parse_and_validate_csv(csv_data)
    assert len(valid) == 0
    assert len(rejected) == 4
    
    # Assert specific reasons
    reasons = [r["reason"] for r in rejected]
    assert any("Row has 5 columns, expected 6 columns" in r for r in reasons)
    assert any("Invalid date format for deadline" in r for r in reasons)
    assert any("Missing required field" in r for r in reasons)
    assert any("Invalid email format" in r for r in reasons)

def test_overdue_logic():
    # Set system date to 2026-07-14 for testing
    system_date = datetime.date(2026, 7, 14)
    
    engineers = [
        # Completed, deadline in past -> Not overdue
        {"name": "Ana Torres", "email": "ana@example.com", "team": "Platform", "course": "Intro to AI Agents", "course_status": "completed", "deadline": "2026-06-30"},
        # Pending, deadline in past -> Genuinely overdue
        {"name": "Luis Mendoza", "email": "luis@example.com", "team": "Platform", "course": "Intro to AI Agents", "course_status": "pending", "deadline": "2026-06-15"},
        # In progress, deadline is exactly today -> NOT overdue (boundary condition)
        {"name": "Sofia Reyes", "email": "sofia@example.com", "team": "Data", "course": "LLM Concepts", "course_status": "in_progress", "deadline": "2026-07-14"},
        # Pending, deadline in future -> Not overdue
        {"name": "Jorge Salinas", "email": "jorge@example.com", "team": "Mobile", "course": "AI-Assisted Coding", "course_status": "pending", "deadline": "2026-07-15"}
    ]
    
    metrics = calculate_dashboard_metrics(engineers, system_date=system_date)
    overdue_list = metrics["overdue_list"]
    
    # Only Luis Mendoza should be overdue (deadline 2026-06-15 is in past relative to 2026-07-14)
    assert len(overdue_list) == 1
    assert overdue_list[0]["name"] == "Luis Mendoza"
    
    # Sofia Reyes (deadline 2026-07-14) must not be in the overdue list
    overdue_names = [eng["name"] for eng in overdue_list]
    assert "Sofia Reyes" not in overdue_names
    
    # Verify percentages
    assert metrics["team_compliance"]["Platform"] == 50.0  # 1 completed, 1 pending
    assert metrics["team_compliance"]["Data"] == 0.0      # 0 completed, 1 in_progress
    assert metrics["course_compliance"]["Intro to AI Agents"] == 50.0
