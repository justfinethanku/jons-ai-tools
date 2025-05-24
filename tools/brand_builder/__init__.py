"""
Brand Builder Modular Workflow System

This module provides a plugin-based architecture for the Brand Builder workflow.
Each step is implemented as an independent tool that can be tested and executed
in isolation while maintaining the ability to run as a complete workflow.

Architecture:
- Each step inherits from WorkflowStep base class
- Steps are auto-discovered using importlib
- Context is passed between steps as JSON
- Each step can be tested independently
- Workflow can resume from any step
"""

import importlib
import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class StepResult:
    """Result of executing a workflow step"""
    success: bool
    data: Dict[str, Any]
    errors: List[str]
    warnings: List[str]
    step_name: str
    
    def can_continue(self) -> bool:
        """Determine if workflow can proceed to next step"""
        return self.success and not any("FATAL" in error for error in self.errors)


class WorkflowContext:
    """Manages data flow between workflow steps"""
    
    def __init__(self, initial_data: Dict = None):
        self.data = initial_data or {}
        self.step_results = {}
    
    def get(self, key: str, default=None):
        """Get data from context"""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set data in context"""
        self.data[key] = value
    
    def update(self, data: Dict):
        """Update context with new data"""
        self.data.update(data)
    
    def add_step_result(self, result: StepResult):
        """Add result from a completed step"""
        self.step_results[result.step_name] = result
        if result.success:
            self.data.update(result.data)
    
    def get_step_result(self, step_name: str) -> Optional[StepResult]:
        """Get result from a specific step"""
        return self.step_results.get(step_name)
    
    def to_json(self) -> str:
        """Serialize context to JSON"""
        return json.dumps({
            'data': self.data,
            'step_results': {k: {
                'success': v.success,
                'data': v.data,
                'errors': v.errors,
                'warnings': v.warnings,
                'step_name': v.step_name
            } for k, v in self.step_results.items()}
        }, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'WorkflowContext':
        """Deserialize context from JSON"""
        data = json.loads(json_str)
        context = cls(data['data'])
        
        for step_name, result_data in data.get('step_results', {}).items():
            result = StepResult(
                success=result_data['success'],
                data=result_data['data'],
                errors=result_data['errors'],
                warnings=result_data['warnings'],
                step_name=result_data['step_name']
            )
            context.step_results[step_name] = result
        
        return context


class WorkflowStep(ABC):
    """Base class for all Brand Builder workflow steps"""
    
    def __init__(self):
        self.name = self.__class__.__name__.lower().replace('tool', '').replace('step', '')
        self.description = self.__doc__ or f"Brand Builder step: {self.name}"
    
    @abstractmethod
    def execute(self, context: WorkflowContext) -> StepResult:
        """Execute this step with the given context"""
        pass
    
    def validate_inputs(self, context: WorkflowContext) -> List[str]:
        """Validate required inputs exist in context. Return list of missing fields."""
        required = self.get_required_inputs()
        missing = []
        for field in required:
            if field not in context.data:
                missing.append(field)
        return missing
    
    def get_required_inputs(self) -> List[str]:
        """Return list of required input fields for this step"""
        return []
    
    def get_dependencies(self) -> List[str]:
        """Return list of step names this step depends on"""
        return []
    
    def get_output_fields(self) -> List[str]:
        """Return list of fields this step adds to context"""
        return []


class BrandBuilderWorkflow:
    """Main orchestrator for Brand Builder workflow"""
    
    def __init__(self):
        self.steps = {}
        self.step_order = []
        self._discover_steps()
    
    def _discover_steps(self):
        """Discover all available workflow steps"""
        # Import all step modules to register them
        step_modules = [
            'step_01_website_extractor',
            'step_02_brand_analyzer', 
            'step_03_content_collector',
            'step_04_voice_auditor',
            'step_05_audience_definer',
            'step_06_voice_traits_builder',
            'step_07_gap_analyzer',
            'step_08_content_rewriter',
            'step_09_guidelines_finalizer'
        ]
        
        for module_name in step_modules:
            try:
                module = importlib.import_module(f'tools.brand_builder.{module_name}')
                # Find the step class in the module
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, WorkflowStep) and 
                        attr != WorkflowStep):
                        
                        step_instance = attr()
                        step_num = int(module_name.split('_')[1])  # Extract step number
                        self.steps[step_num] = step_instance
                        
            except ImportError as e:
                print(f"Warning: Could not import {module_name}: {e}")
        
        # Order steps by number
        self.step_order = sorted(self.steps.keys())
    
    def run_step(self, step_number: int, context: WorkflowContext) -> StepResult:
        """Run a specific step"""
        if step_number not in self.steps:
            return StepResult(
                success=False,
                data={},
                errors=[f"Step {step_number} not found"],
                warnings=[],
                step_name=f"step_{step_number:02d}"
            )
        
        step = self.steps[step_number]
        
        # Validate inputs
        missing_inputs = step.validate_inputs(context)
        if missing_inputs:
            return StepResult(
                success=False,
                data={},
                errors=[f"Missing required inputs: {', '.join(missing_inputs)}"],
                warnings=[],
                step_name=step.name
            )
        
        # Execute step
        try:
            result = step.execute(context)
            context.add_step_result(result)
            return result
        except Exception as e:
            return StepResult(
                success=False,
                data={},
                errors=[f"Step execution failed: {str(e)}"],
                warnings=[],
                step_name=step.name
            )
    
    def run_workflow(self, context: WorkflowContext, start_from: int = 1, end_at: int = None) -> List[StepResult]:
        """Run the complete workflow or a subset"""
        results = []
        end_step = end_at or max(self.step_order)
        
        for step_num in self.step_order:
            if step_num < start_from:
                continue
            if step_num > end_step:
                break
                
            result = self.run_step(step_num, context)
            results.append(result)
            
            if not result.can_continue():
                print(f"Workflow stopped at step {step_num} due to errors")
                break
        
        return results
    
    def get_step_status(self, context: WorkflowContext) -> Dict[int, str]:
        """Get status of all steps"""
        status = {}
        for step_num in self.step_order:
            step = self.steps[step_num]
            if step.name in context.step_results:
                result = context.step_results[step.name]
                status[step_num] = "completed" if result.success else "failed"
            else:
                missing_inputs = step.validate_inputs(context)
                status[step_num] = "ready" if not missing_inputs else "blocked"
        return status
    
    def list_steps(self) -> Dict[int, str]:
        """List all available steps"""
        return {num: self.steps[num].description for num in self.step_order}


# Export main classes and backward compatibility functions
__all__ = ['WorkflowStep', 'WorkflowContext', 'StepResult', 'BrandBuilderWorkflow']

# Import backward compatibility functions from the main module
def _import_compat_functions():
    """Import compatibility functions from the main brand_builder.py"""
    import sys
    import os
    
    # Add the tools directory to path to import brand_builder.py directly
    tools_dir = os.path.dirname(os.path.dirname(__file__))
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    
    try:
        # Import from brand_builder.py file directly
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "brand_builder_main", 
            os.path.join(tools_dir, "brand_builder.py")
        )
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    except Exception:
        return None

# Try to import and expose compatibility functions
_compat_module = _import_compat_functions()
if _compat_module:
    extract_website_data = getattr(_compat_module, 'extract_website_data', None)
    analyze_brand_voice = getattr(_compat_module, 'analyze_brand_voice', None)
    comprehensive_client_analysis = getattr(_compat_module, 'comprehensive_client_analysis', None)
    
    if extract_website_data:
        __all__.append('extract_website_data')
    if analyze_brand_voice:
        __all__.append('analyze_brand_voice')
    if comprehensive_client_analysis:
        __all__.append('comprehensive_client_analysis')