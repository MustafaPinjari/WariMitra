"""Custom exception handlers for WariMitra backend."""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def custom_exception_handler(exc, context):
    """Custom DRF exception handler with enhanced error responses."""
    
    response = drf_exception_handler(exc, context)
    
    if response is not None:
        response.data = {
            'error': True,
            'message': response.data.get('detail') or str(exc),
            'status_code': response.status_code,
            'errors': response.data,
        }
    
    return response
