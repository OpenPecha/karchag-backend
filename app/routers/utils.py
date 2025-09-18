from fastapi import APIRouter
import logging

router = APIRouter(prefix="/utils", tags=["Utils"])
logger = logging.getLogger(__name__)

# This file is reserved for utility endpoints that don't fit other categories
# Currently empty - stats moved to dashboard.py for better organization