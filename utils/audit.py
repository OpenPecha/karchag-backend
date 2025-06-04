import json
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from models import AuditLog

def log_activity(
    db: Session,
    user_id: int,
    table_name: str,
    record_id: int,
    action: str,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
) -> bool:
    """
    Log user activity to audit table
    
    Args:
        db: Database session
        user_id: ID of user performing action
        table_name: Name of table being modified
        record_id: ID of record being modified
        action: Action being performed (CREATE, UPDATE, DELETE, LOGIN, LOGOUT)
        old_values: Previous values (for UPDATE/DELETE)
        new_values: New values (for CREATE/UPDATE)
        ip_address: IP address of user
    
    Returns:
        bool: True if logged successfully, False otherwise
    """
    try:
        # Serialize values to JSON
        old_values_json = json.dumps(old_values, default=str) if old_values else None
        new_values_json = json.dumps(new_values, default=str) if new_values else None
        
        audit_log = AuditLog(
            user_id=user_id,
            table_name=table_name,
            record_id=record_id,
            action=action,
            old_values=old_values_json,
            new_values=new_values_json,
            timestamp=datetime.utcnow(),
            ip_address=ip_address
        )
        
        db.add(audit_log)
        db.commit()
        return True
        
    except Exception as e:
        print(f"Audit log error: {e}")
        db.rollback()
        return False

def get_audit_logs(
    db: Session,
    user_id: Optional[int] = None,
    table_name: Optional[str] = None,
    record_id: Optional[int] = None,
    action: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> list:
    """
    Retrieve audit logs with optional filters
    
    Args:
        db: Database session
        user_id: Filter by user ID
        table_name: Filter by table name
        record_id: Filter by record ID
        action: Filter by action type
        limit: Maximum number of records to return
        offset: Number of records to skip
    
    Returns:
        list: List of audit log records
    """
    query = db.query(AuditLog)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if table_name:
        query = query.filter(AuditLog.table_name == table_name)
    if record_id:
        query = query.filter(AuditLog.record_id == record_id)
    if action:
        query = query.filter(AuditLog.action == action)
    
    return query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()