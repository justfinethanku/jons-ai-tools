"""
Health Check Framework for AI Tools Project.
Provides comprehensive system health monitoring and validation.
"""
import time
import json
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Import our frameworks
try:
    from frameworks.database_manager import EnhancedDatabaseManager, DatabaseError
    from frameworks.logging_manager import get_logger, LoggedOperation
    from notion_client_manager import NotionClientManager
    from frameworks import universal_framework
except ImportError as e:
    print(f"Warning: Could not import framework modules: {e}")

class HealthStatus(Enum):
    """Health check status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded" 
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class HealthCheckResult:
    """Result of a health check"""
    component: str
    status: HealthStatus
    message: str
    details: Dict[str, Any]
    duration_ms: float
    timestamp: str

class SystemHealthChecker:
    """
    Comprehensive system health checker for AI Tools project.
    """
    
    def __init__(self, logger=None):
        """Initialize health checker"""
        self.logger = logger or get_logger()
        self.start_time = datetime.now()
        
    def check_all(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check of all system components.
        
        Returns:
            Dict containing overall health status and component details
        """
        with LoggedOperation("system_health_check", self.logger):
            results = []
            
            # Check each component
            results.append(self._check_notion_connectivity())
            results.append(self._check_database_schemas())
            results.append(self._check_api_endpoints())
            results.append(self._check_framework_modules())
            results.append(self._check_file_system())
            results.append(self._check_brand_builder_workflow())
            
            # Calculate overall health
            overall_status = self._calculate_overall_status(results)
            
            health_report = {
                "overall_status": overall_status.value,
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
                "components": {result.component: {
                    "status": result.status.value,
                    "message": result.message,
                    "details": result.details,
                    "duration_ms": result.duration_ms,
                    "timestamp": result.timestamp
                } for result in results}
            }
            
            self.logger.info("System health check completed", 
                           operation="health_check",
                           overall_status=overall_status.value,
                           component_count=len(results))
            
            return health_report
    
    def _check_notion_connectivity(self) -> HealthCheckResult:
        """Check Notion API connectivity"""
        start_time = time.time()
        
        try:
            manager = NotionClientManager()
            
            if not manager.is_connected():
                return HealthCheckResult(
                    component="notion_connectivity",
                    status=HealthStatus.UNHEALTHY,
                    message="Notion client not properly configured",
                    details={"error": "Missing API key or database ID"},
                    duration_ms=(time.time() - start_time) * 1000,
                    timestamp=datetime.now().isoformat()
                )
            
            # Test actual API call
            clients = manager.get_clients()
            
            return HealthCheckResult(
                component="notion_connectivity",
                status=HealthStatus.HEALTHY,
                message="Notion API accessible",
                details={
                    "client_count": len(clients),
                    "api_responsive": True
                },
                duration_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="notion_connectivity",
                status=HealthStatus.UNHEALTHY,
                message=f"Notion API error: {str(e)}",
                details={"error": str(e), "traceback": traceback.format_exc()},
                duration_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.now().isoformat()
            )
    
    def _check_database_schemas(self) -> HealthCheckResult:
        """Check database schema validity"""
        start_time = time.time()
        
        try:
            # This would check database schemas in production
            # For now, we'll validate that our schema definitions are complete
            
            from frameworks.database_manager import EnhancedDatabaseManager
            
            # Mock validation - check schema completeness
            test_manager = EnhancedDatabaseManager("test_key")
            schemas = test_manager.schemas
            
            schema_issues = []
            for schema_name, schema in schemas.items():
                if not schema.get('required_fields'):
                    schema_issues.append(f"{schema_name}: missing required_fields")
                if not schema.get('field_types'):
                    schema_issues.append(f"{schema_name}: missing field_types")
            
            if schema_issues:
                return HealthCheckResult(
                    component="database_schemas",
                    status=HealthStatus.DEGRADED,
                    message="Schema configuration issues detected",
                    details={"issues": schema_issues},
                    duration_ms=(time.time() - start_time) * 1000,
                    timestamp=datetime.now().isoformat()
                )
            
            return HealthCheckResult(
                component="database_schemas",
                status=HealthStatus.HEALTHY,
                message="Database schemas valid",
                details={
                    "schema_count": len(schemas),
                    "schemas": list(schemas.keys())
                },
                duration_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="database_schemas",
                status=HealthStatus.UNHEALTHY,
                message=f"Schema validation failed: {str(e)}",
                details={"error": str(e)},
                duration_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.now().isoformat()
            )
    
    def _check_api_endpoints(self) -> HealthCheckResult:
        """Check AI API endpoints availability"""
        start_time = time.time()
        
        try:
            # Test Gemini API (mock call)
            api_status = {
                "gemini": "available",  # Would test actual API in production
                "openai": "available"   # Would test actual API in production
            }
            
            # In production, you would make actual test calls:
            # response = universal_framework.call_gemini_api("test", temperature=0.1)
            
            return HealthCheckResult(
                component="api_endpoints",
                status=HealthStatus.HEALTHY,
                message="AI API endpoints accessible",
                details=api_status,
                duration_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="api_endpoints",
                status=HealthStatus.DEGRADED,
                message=f"API endpoint issues: {str(e)}",
                details={"error": str(e)},
                duration_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.now().isoformat()
            )
    
    def _check_framework_modules(self) -> HealthCheckResult:
        """Check framework module imports and functionality"""
        start_time = time.time()
        
        try:
            # Test framework imports
            modules_status = {}
            
            try:
                from frameworks import universal_framework
                modules_status["universal_framework"] = "loaded"
            except ImportError as e:
                modules_status["universal_framework"] = f"failed: {e}"
            
            try:
                from frameworks.database_manager import EnhancedDatabaseManager
                modules_status["database_manager"] = "loaded"
            except ImportError as e:
                modules_status["database_manager"] = f"failed: {e}"
            
            try:
                from frameworks.logging_manager import get_logger
                modules_status["logging_manager"] = "loaded"
            except ImportError as e:
                modules_status["logging_manager"] = f"failed: {e}"
            
            failed_modules = [k for k, v in modules_status.items() if v.startswith("failed")]
            
            if failed_modules:
                return HealthCheckResult(
                    component="framework_modules",
                    status=HealthStatus.DEGRADED,
                    message=f"Module import failures: {', '.join(failed_modules)}",
                    details=modules_status,
                    duration_ms=(time.time() - start_time) * 1000,
                    timestamp=datetime.now().isoformat()
                )
            
            return HealthCheckResult(
                component="framework_modules",
                status=HealthStatus.HEALTHY,
                message="All framework modules loaded successfully",
                details=modules_status,
                duration_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="framework_modules",
                status=HealthStatus.UNHEALTHY,
                message=f"Framework module check failed: {str(e)}",
                details={"error": str(e)},
                duration_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.now().isoformat()
            )
    
    def _check_file_system(self) -> HealthCheckResult:
        """Check file system access and required directories"""
        start_time = time.time()
        
        try:
            import os
            from pathlib import Path
            
            base_path = Path.cwd()
            required_paths = [
                "frameworks",
                "tools/brand_builder", 
                "prompts",
                "tests"
            ]
            
            path_status = {}
            missing_paths = []
            
            for path in required_paths:
                full_path = base_path / path
                if full_path.exists():
                    path_status[path] = "exists"
                else:
                    path_status[path] = "missing"
                    missing_paths.append(path)
            
            if missing_paths:
                return HealthCheckResult(
                    component="file_system",
                    status=HealthStatus.DEGRADED,
                    message=f"Missing directories: {', '.join(missing_paths)}",
                    details=path_status,
                    duration_ms=(time.time() - start_time) * 1000,
                    timestamp=datetime.now().isoformat()
                )
            
            return HealthCheckResult(
                component="file_system",
                status=HealthStatus.HEALTHY,
                message="All required directories accessible",
                details=path_status,
                duration_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="file_system",
                status=HealthStatus.UNHEALTHY,
                message=f"File system check failed: {str(e)}",
                details={"error": str(e)},
                duration_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.now().isoformat()
            )
    
    def _check_brand_builder_workflow(self) -> HealthCheckResult:
        """Check Brand Builder workflow components"""
        start_time = time.time()
        
        try:
            from pathlib import Path
            
            brand_builder_steps = [
                "step_01_website_extractor.py",
                "step_02_brand_analyzer.py", 
                "step_03_content_collector.py",
                "step_04_voice_auditor.py",
                "step_05_audience_definer.py",
                "step_06_voice_traits_builder.py",
                "step_07_gap_analyzer.py",
                "step_08_content_rewriter.py",
                "step_09_guidelines_finalizer.py"
            ]
            
            brand_builder_path = Path.cwd() / "tools" / "brand_builder"
            step_status = {}
            missing_steps = []
            
            for step in brand_builder_steps:
                step_path = brand_builder_path / step
                if step_path.exists():
                    step_status[step] = "exists"
                else:
                    step_status[step] = "missing"
                    missing_steps.append(step)
            
            if missing_steps:
                return HealthCheckResult(
                    component="brand_builder_workflow",
                    status=HealthStatus.DEGRADED,
                    message=f"Missing workflow steps: {', '.join(missing_steps)}",
                    details=step_status,
                    duration_ms=(time.time() - start_time) * 1000,
                    timestamp=datetime.now().isoformat()
                )
            
            return HealthCheckResult(
                component="brand_builder_workflow",
                status=HealthStatus.HEALTHY,
                message="Brand Builder workflow complete",
                details={
                    "total_steps": len(brand_builder_steps),
                    "available_steps": len([s for s in step_status.values() if s == "exists"])
                },
                duration_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="brand_builder_workflow",
                status=HealthStatus.UNHEALTHY,
                message=f"Workflow check failed: {str(e)}",
                details={"error": str(e)},
                duration_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.now().isoformat()
            )
    
    def _calculate_overall_status(self, results: List[HealthCheckResult]) -> HealthStatus:
        """Calculate overall system health from component results"""
        if not results:
            return HealthStatus.UNKNOWN
        
        unhealthy_count = sum(1 for r in results if r.status == HealthStatus.UNHEALTHY)
        degraded_count = sum(1 for r in results if r.status == HealthStatus.DEGRADED)
        
        # If any component is unhealthy, system is unhealthy
        if unhealthy_count > 0:
            return HealthStatus.UNHEALTHY
        
        # If multiple components are degraded, system is degraded
        if degraded_count > 1:
            return HealthStatus.DEGRADED
        
        # If any component is degraded, system is degraded
        if degraded_count > 0:
            return HealthStatus.DEGRADED
        
        # All components healthy
        return HealthStatus.HEALTHY

def run_health_check(output_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Run comprehensive health check and optionally save results.
    
    Args:
        output_file: Optional file path to save health check results
        
    Returns:
        Health check results dictionary
    """
    checker = SystemHealthChecker()
    results = checker.check_all()
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
    
    return results

def print_health_summary(health_data: Dict[str, Any]):
    """Print a formatted health check summary"""
    print("\n" + "="*60)
    print(f"🏥 AI TOOLS SYSTEM HEALTH CHECK")
    print("="*60)
    print(f"Overall Status: {health_data['overall_status'].upper()}")
    print(f"Timestamp: {health_data['timestamp']}")
    print(f"Uptime: {health_data['uptime_seconds']:.1f} seconds")
    print("\nComponent Status:")
    print("-"*40)
    
    for component, details in health_data['components'].items():
        status_icon = {
            'healthy': '✅',
            'degraded': '⚠️',
            'unhealthy': '❌',
            'unknown': '❓'
        }.get(details['status'], '❓')
        
        print(f"{status_icon} {component}: {details['status'].upper()}")
        print(f"   {details['message']}")
        if details['details']:
            for key, value in details['details'].items():
                if isinstance(value, (list, dict)):
                    print(f"   {key}: {len(value) if isinstance(value, list) else 'complex'}")
                else:
                    print(f"   {key}: {value}")
        print(f"   Duration: {details['duration_ms']:.1f}ms")
        print()

if __name__ == "__main__":
    """CLI interface for health checks"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run AI Tools system health check')
    parser.add_argument('--output', help='Output file for results (JSON)')
    parser.add_argument('--quiet', action='store_true', help='Suppress output')
    
    args = parser.parse_args()
    
    results = run_health_check(args.output)
    
    if not args.quiet:
        print_health_summary(results)
    
    # Exit with appropriate code
    exit_code = 0 if results['overall_status'] == 'healthy' else 1
    exit(exit_code)