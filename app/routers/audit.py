from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import AuditLog, User
from app.dependencies.auth import require_admin
import logging

router = APIRouter(prefix="/audit", tags=["Audit"])
logger = logging.getLogger(__name__)

@router.get("/logs")
async def get_audit_logs(
    current_user: User = Depends(require_admin),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    table_name: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get audit logs with filtering and pagination.
    
    Admin only endpoint for reviewing system activities.
    """
    try:
        # Build query
        query = db.query(AuditLog)
        
        # Apply filters
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        if action:
            query = query.filter(AuditLog.action.ilike(f"%{action}%"))
            
        if table_name:
            query = query.filter(AuditLog.table_name.ilike(f"%{table_name}%"))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        audit_logs = query.order_by(AuditLog.timestamp.desc())\
                         .offset(offset)\
                         .limit(limit)\
                         .all()
        
        # Format response
        logs = []
        for log in audit_logs:
            logs.append({
                "id": log.id,
                "user_id": log.user_id,
                "table_name": log.table_name,
                "record_id": log.record_id,
                "action": log.action,
                "old_values": log.old_values,
                "new_values": log.new_values,
                "timestamp": log.timestamp,
                "ip_address": log.ip_address
            })
        
        logger.info(f"Admin {current_user.username} retrieved audit logs")
        return {
            "audit_logs": logs,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
        
    except Exception as e:
        logger.error(f"Error in get_audit_logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Audit logs error: {str(e)}")
