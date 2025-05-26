"""
logging_manager 
Structured Logging Framework for AI Tools Project.
Provides consistent, structured logging across all components.
"""
import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""
    
    def format(self, record):
        """Format log record as structured JSON"""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add custom fields if present
        if hasattr(record, 'client_id'):
            log_entry['client_id'] = record.client_id
        if hasattr(record, 'step_name'):
            log_entry['step_name'] = record.step_name
        if hasattr(record, 'operation'):
            log_entry['operation'] = record.operation
        if hasattr(record, 'duration_ms'):
            log_entry['duration_ms'] = record.duration_ms
        if hasattr(record, 'error_code'):
            log_entry['error_code'] = record.error_code
        if hasattr(record, 'metadata'):
            log_entry['metadata'] = record.metadata
            
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry, default=str)

class AIToolsLogger:
    """
    Centralized logger for AI Tools project with structured logging capabilities.
    """
    
    def __init__(self, name: str = "ai_tools", log_level: str = "INFO", 
                 log_file: Optional[str] = None, enable_console: bool = True):
        """
        Initialize the structured logger.
        
        Args:
            name: Logger name
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional log file path
            enable_console: Whether to enable console logging
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Add console handler if enabled
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(StructuredFormatter())
            self.logger.addHandler(console_handler)
        
        # Add file handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(StructuredFormatter())
            self.logger.addHandler(file_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message with optional structured data"""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with optional structured data"""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with optional structured data"""
        self._log(logging.ERROR, message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with optional structured data"""
        self._log(logging.DEBUG, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with optional structured data"""
        self._log(logging.CRITICAL, message, **kwargs)
    
    def _log(self, level: int, message: str, **kwargs):
        """Internal logging method that adds structured data"""
        extra = {}
        for key, value in kwargs.items():
            extra[key] = value
        
        self.logger.log(level, message, extra=extra)
    
    def log_operation_start(self, operation: str, **metadata):
        """Log the start of an operation"""
        self.info(f"Operation started: {operation}", 
                 operation=operation, 
                 operation_status="started",
                 metadata=metadata)
    
    def log_operation_success(self, operation: str, duration_ms: Optional[float] = None, **metadata):
        """Log successful completion of an operation"""
        log_data = {
            "operation": operation,
            "operation_status": "completed",
            "metadata": metadata
        }
        if duration_ms is not None:
            log_data["duration_ms"] = duration_ms
            
        self.info(f"Operation completed successfully: {operation}", **log_data)
    
    def log_operation_failure(self, operation: str, error: str, error_code: Optional[str] = None, 
                            duration_ms: Optional[float] = None, **metadata):
        """Log failed operation"""
        log_data = {
            "operation": operation,
            "operation_status": "failed",
            "error_message": error,
            "metadata": metadata
        }
        if error_code:
            log_data["error_code"] = error_code
        if duration_ms is not None:
            log_data["duration_ms"] = duration_ms
            
        self.error(f"Operation failed: {operation} - {error}", **log_data)
    
    def log_api_call(self, api_name: str, endpoint: str, status_code: Optional[int] = None,
                    duration_ms: Optional[float] = None, **metadata):
        """Log API call details"""
        log_data = {
            "operation": "api_call",
            "api_name": api_name,
            "endpoint": endpoint,
            "metadata": metadata
        }
        if status_code is not None:
            log_data["status_code"] = status_code
        if duration_ms is not None:
            log_data["duration_ms"] = duration_ms
            
        level = logging.INFO if status_code and 200 <= status_code < 300 else logging.WARNING
        self.logger.log(level, f"API call to {api_name}: {endpoint}", extra=log_data)
    
    def log_database_operation(self, operation: str, database: str, table: Optional[str] = None,
                             record_count: Optional[int] = None, duration_ms: Optional[float] = None,
                             **metadata):
        """Log database operation"""
        log_data = {
            "operation": "database_operation",
            "db_operation": operation,
            "database": database,
            "metadata": metadata
        }
        if table:
            log_data["table"] = table
        if record_count is not None:
            log_data["record_count"] = record_count
        if duration_ms is not None:
            log_data["duration_ms"] = duration_ms
            
        self.info(f"Database {operation}: {database}.{table or 'N/A'}", **log_data)
    
    def log_workflow_step(self, step_name: str, status: str, client_id: Optional[str] = None,
                         duration_ms: Optional[float] = None, **metadata):
        """Log workflow step execution"""
        log_data = {
            "operation": "workflow_step",
            "step_name": step_name,
            "step_status": status,
            "metadata": metadata
        }
        if client_id:
            log_data["client_id"] = client_id
        if duration_ms is not None:
            log_data["duration_ms"] = duration_ms
            
        level = logging.INFO if status == "completed" else logging.WARNING
        self.logger.log(level, f"Workflow step {step_name}: {status}", extra=log_data)

# Global logger instance
_global_logger = None

def get_logger(name: str = "ai_tools", **kwargs) -> AIToolsLogger:
    """
    Get or create a global logger instance.
    
    Args:
        name: Logger name
        **kwargs: Additional arguments for logger initialization
        
    Returns:
        AIToolsLogger instance
    """
    global _global_logger
    
    if _global_logger is None:
        _global_logger = AIToolsLogger(name, **kwargs)
    
    return _global_logger

def configure_logging(log_level: str = "INFO", log_file: Optional[str] = None,
                     enable_console: bool = True):
    """
    Configure global logging settings.
    
    Args:
        log_level: Logging level
        log_file: Optional log file path
        enable_console: Whether to enable console logging
    """
    global _global_logger
    _global_logger = AIToolsLogger("ai_tools", log_level, log_file, enable_console)

def log_performance_metrics(metrics: Dict[str, Any]):
    """Log performance metrics"""
    logger = get_logger()
    logger.info("Performance metrics", operation="performance_metrics", metadata=metrics)

def log_user_action(action: str, user_id: Optional[str] = None, **metadata):
    """Log user action"""
    logger = get_logger()
    log_data = {"operation": "user_action", "action": action, "metadata": metadata}
    if user_id:
        log_data["user_id"] = user_id
    logger.info(f"User action: {action}", **log_data)

# Context manager for operation logging
class LoggedOperation:
    """Context manager for logging operations with timing"""
    
    def __init__(self, operation: str, logger: Optional[AIToolsLogger] = None, **metadata):
        self.operation = operation
        self.logger = logger or get_logger()
        self.metadata = metadata
        self.start_time = None
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        self.logger.log_operation_start(self.operation, **self.metadata)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        duration_ms = (time.time() - self.start_time) * 1000
        
        if exc_type is None:
            self.logger.log_operation_success(self.operation, duration_ms=duration_ms, **self.metadata)
        else:
            error_msg = str(exc_val) if exc_val else "Unknown error"
            self.logger.log_operation_failure(
                self.operation, 
                error_msg, 
                error_code=exc_type.__name__ if exc_type else None,
                duration_ms=duration_ms, 
                **self.metadata
            )
        
        return False  # Don't suppress exceptions

# Initialize default logger
configure_logging()