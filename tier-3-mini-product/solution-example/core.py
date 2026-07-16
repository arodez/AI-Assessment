import csv
import io
import datetime
from typing import List, Dict, Any, Tuple

REQUIRED_HEADERS = ["name", "email", "team", "course", "course_status", "deadline"]

def parse_and_validate_csv(csv_content: str) -> Tuple[List[Dict[str, str]], List[Dict[str, Any]]]:
    """
    Parses and validates CSV content.
    Returns:
        (valid_rows, rejected_rows)
        - valid_rows: List of dicts with keys normalized.
        - rejected_rows: List of dicts detailing validation errors (row_index, content, reason).
    """
    valid_rows = []
    rejected_rows = []
    
    # Read using StringIO to process line-by-line and handle errors
    f = io.StringIO(csv_content.strip())
    reader = csv.reader(f)
    
    try:
        headers = next(reader)
    except StopIteration:
        return [], [{"row_index": 1, "content": "", "reason": "Empty CSV file"}]
    
    # Normalize headers
    headers = [h.strip().lower() for h in headers]
    
    # Check for required headers
    missing_headers = [req for req in REQUIRED_HEADERS if req not in headers]
    if missing_headers:
        return [], [{"row_index": 1, "content": ",".join(headers), "reason": f"Missing required columns: {', '.join(missing_headers)}"}]
    
    # Create mapping of expected header to column index
    header_indices = {h: headers.index(h) for h in REQUIRED_HEADERS}
    
    for row_idx, row in enumerate(reader, start=2):
        # Handle empty lines
        if not row or all(cell.strip() == "" for cell in row):
            continue
            
        # Check column count matches headers
        if len(row) < len(headers):
            # Try to map columns but check if any required is missing
            rejected_rows.append({
                "row_index": row_idx,
                "content": ",".join(row),
                "reason": f"Row has {len(row)} columns, expected {len(headers)} columns"
            })
            continue

        # Extract values
        extracted = {}
        row_errors = []
        
        for field in REQUIRED_HEADERS:
            idx = header_indices[field]
            val = row[idx].strip() if idx < len(row) else ""
            extracted[field] = val
            
            if not val:
                row_errors.append(f"Missing required field: '{field}'")
        
        if row_errors:
            rejected_rows.append({
                "row_index": row_idx,
                "content": ",".join(row),
                "reason": "; ".join(row_errors)
            })
            continue
            
        # Email validation
        email = extracted["email"]
        if "@" not in email:
            rejected_rows.append({
                "row_index": row_idx,
                "content": ",".join(row),
                "reason": f"Invalid email format: '{email}'"
            })
            continue
            
        # Status normalization & validation
        status = extracted["course_status"].lower().replace("_", " ")
        if status in ["pending", "in progress", "completed"]:
            # Standardize status
            extracted["course_status"] = "in_progress" if status == "in progress" else status
        else:
            rejected_rows.append({
                "row_index": row_idx,
                "content": ",".join(row),
                "reason": f"Invalid course status: '{extracted['course_status']}'"
            })
            continue
            
        # Date validation
        deadline_str = extracted["deadline"]
        try:
            # Validate format and check if it's a real date
            datetime.datetime.strptime(deadline_str, "%Y-%m-%d").date()
        except ValueError:
            rejected_rows.append({
                "row_index": row_idx,
                "content": ",".join(row),
                "reason": f"Invalid date format for deadline: '{deadline_str}' (expected YYYY-MM-DD)"
            })
            continue
            
        valid_rows.append(extracted)
        
    return valid_rows, rejected_rows


def calculate_dashboard_metrics(engineers: List[Dict[str, Any]], system_date: datetime.date = None) -> Dict[str, Any]:
    """
    Calculates Training Compliance Dashboard statistics.
    """
    if system_date is None:
        system_date = datetime.date.today()
        
    team_stats = {}
    course_stats = {}
    overdue_engineers = []
    
    for eng in engineers:
        team = eng["team"]
        course = eng["course"]
        status = eng["course_status"]
        deadline_str = eng["deadline"]
        
        # Parse deadline
        deadline_date = datetime.datetime.strptime(deadline_str, "%Y-%m-%d").date()
        
        # Initialize stats if not present
        if team not in team_stats:
            team_stats[team] = {"total": 0, "completed": 0}
        if course not in course_stats:
            course_stats[course] = {"total": 0, "completed": 0}
            
        # Update counts
        team_stats[team]["total"] += 1
        course_stats[course]["total"] += 1
        
        if status == "completed":
            team_stats[team]["completed"] += 1
            course_stats[course]["completed"] += 1
            
        # Overdue logic: not completed AND deadline < system_date (strict inequality)
        is_overdue = (status != "completed") and (deadline_date < system_date)
        
        if is_overdue:
            overdue_engineers.append({
                "name": eng["name"],
                "email": eng["email"],
                "team": team,
                "course": course,
                "course_status": status,
                "deadline": deadline_str,
                "days_overdue": (system_date - deadline_date).days
            })
            
    # Calculate percentages
    team_percentages = {}
    for team, counts in team_stats.items():
        team_percentages[team] = round((counts["completed"] / counts["total"]) * 100, 1) if counts["total"] > 0 else 0.0
        
    course_percentages = {}
    for course, counts in course_stats.items():
        course_percentages[course] = round((counts["completed"] / counts["total"]) * 100, 1) if counts["total"] > 0 else 0.0
        
    return {
        "team_compliance": team_percentages,
        "course_compliance": course_percentages,
        "overdue_list": overdue_engineers,
        "total_count": len(engineers)
    }
