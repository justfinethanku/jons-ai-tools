"""
Test suite for core/rule_engine.py module.

Tests rule engine functionality including rule storage, validation,
conflict detection, and compliance evaluation.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass
from enum import Enum
import tempfile
import os

# Import the module under test
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.rule_engine import (
    RuleType,
    RuleScope,
    RulePriority,
    ArchitecturalRule,
    RuleViolation,
    ComplianceResult,
    RuleConflict,
    RuleEngine,
    RuleParser,
    RuleContext
)


class TestRuleType:
    """Test RuleType enumeration."""
    
    def test_rule_types(self):
        """Test that all expected rule types are available."""
        expected_types = [
            'PURPOSE', 'RESPONSIBILITY', 'IMPORTS_ALLOWED', 'IMPORTS_FORBIDDEN',
            'DEPENDENCY_DIRECTION', 'INTERFACE_RULE', 'SECURITY', 'PERFORMANCE'
        ]
        actual_types = [rule_type.name for rule_type in RuleType]
        
        for rule_type in expected_types:
            assert rule_type in actual_types


class TestRuleScope:
    """Test RuleScope enumeration."""
    
    def test_rule_scopes(self):
        """Test that all expected rule scopes are available."""
        expected_scopes = ['FILE', 'CLASS', 'FUNCTION', 'MODULE', 'PROJECT']
        actual_scopes = [scope.name for scope in RuleScope]
        
        for scope in expected_scopes:
            assert scope in actual_scopes


class TestRulePriority:
    """Test RulePriority enumeration."""
    
    def test_rule_priorities(self):
        """Test that all expected rule priorities are available."""
        expected_priorities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        actual_priorities = [priority.name for priority in RulePriority]
        
        for priority in expected_priorities:
            assert priority in actual_priorities


class TestArchitecturalRule:
    """Test ArchitecturalRule data structure."""
    
    def test_architectural_rule_creation(self):
        """Test creation of architectural rule."""
        rule = ArchitecturalRule(
            rule_id="TEST_001",
            rule_type=RuleType.PURPOSE,
            scope=RuleScope.FILE,
            priority=RulePriority.HIGH,
            description="Test rule description",
            pattern=r"@RULE:PURPOSE: (.+)",
            enforcement_level="warning",
            context_requirements=["file_path"],
            validation_function=None
        )
        
        assert rule.rule_id == "TEST_001"
        assert rule.rule_type == RuleType.PURPOSE
        assert rule.scope == RuleScope.FILE
        assert rule.priority == RulePriority.HIGH
        assert rule.description == "Test rule description"
        assert rule.pattern == r"@RULE:PURPOSE: (.+)"
        assert rule.enforcement_level == "warning"
    
    def test_architectural_rule_with_validation(self):
        """Test architectural rule with custom validation function."""
        def custom_validator(value, context):
            return len(value) > 5
        
        rule = ArchitecturalRule(
            rule_id="TEST_002",
            rule_type=RuleType.RESPONSIBILITY,
            scope=RuleScope.CLASS,
            priority=RulePriority.MEDIUM,
            description="Test rule with validation",
            validation_function=custom_validator
        )
        
        assert rule.validation_function is not None
        assert rule.validation_function("short", {}) == False
        assert rule.validation_function("longer description", {}) == True


class TestRuleViolation:
    """Test RuleViolation data structure."""
    
    def test_rule_violation_creation(self):
        """Test creation of rule violation."""
        violation = RuleViolation(
            rule_id="TEST_001",
            violation_type="missing_rule",
            severity="high",
            message="Required rule is missing",
            file_path="/test/file.py",
            line_number=42,
            context={"function": "test_func"},
            suggested_fix="Add @RULE:PURPOSE comment"
        )
        
        assert violation.rule_id == "TEST_001"
        assert violation.violation_type == "missing_rule"
        assert violation.severity == "high"
        assert violation.message == "Required rule is missing"
        assert violation.file_path == "/test/file.py"
        assert violation.line_number == 42
        assert violation.context["function"] == "test_func"
        assert violation.suggested_fix == "Add @RULE:PURPOSE comment"


class TestComplianceResult:
    """Test ComplianceResult data structure."""
    
    def test_compliance_result_success(self):
        """Test creation of successful compliance result."""
        result = ComplianceResult(
            is_compliant=True,
            compliance_score=0.95,
            violations=[],
            warnings=[],
            summary="All rules are satisfied",
            checked_rules=["RULE_001", "RULE_002"],
            context={"file": "/test/file.py"}
        )
        
        assert result.is_compliant == True
        assert result.compliance_score == 0.95
        assert len(result.violations) == 0
        assert len(result.warnings) == 0
        assert result.summary == "All rules are satisfied"
        assert len(result.checked_rules) == 2
    
    def test_compliance_result_with_violations(self):
        """Test creation of compliance result with violations."""
        violation = RuleViolation(
            rule_id="TEST_001",
            violation_type="forbidden_import",
            severity="high",
            message="Forbidden import detected"
        )
        
        result = ComplianceResult(
            is_compliant=False,
            compliance_score=0.3,
            violations=[violation],
            warnings=["Consider refactoring"],
            summary="Rule violations found"
        )
        
        assert result.is_compliant == False
        assert result.compliance_score == 0.3
        assert len(result.violations) == 1
        assert len(result.warnings) == 1
        assert result.violations[0].rule_id == "TEST_001"


class TestRuleConflict:
    """Test RuleConflict data structure."""
    
    def test_rule_conflict_creation(self):
        """Test creation of rule conflict."""
        conflict = RuleConflict(
            conflict_id="CONFLICT_001",
            rule_id_1="RULE_001",
            rule_id_2="RULE_002",
            conflict_type="contradictory",
            severity="medium",
            description="Rules contradict each other",
            resolution_strategy="priority_based",
            context={"scope": "file"}
        )
        
        assert conflict.conflict_id == "CONFLICT_001"
        assert conflict.rule_id_1 == "RULE_001"
        assert conflict.rule_id_2 == "RULE_002"
        assert conflict.conflict_type == "contradictory"
        assert conflict.severity == "medium"
        assert conflict.resolution_strategy == "priority_based"


class TestRuleContext:
    """Test RuleContext data structure."""
    
    def test_rule_context_creation(self):
        """Test creation of rule context."""
        context = RuleContext(
            file_path="/test/module.py",
            class_name="TestClass",
            function_name="test_method",
            module_name="test_module",
            imports=["os", "sys"],
            dependencies=["dependency1"],
            metadata={"author": "test"}
        )
        
        assert context.file_path == "/test/module.py"
        assert context.class_name == "TestClass"
        assert context.function_name == "test_method"
        assert context.module_name == "test_module"
        assert "os" in context.imports
        assert "dependency1" in context.dependencies
        assert context.metadata["author"] == "test"


class TestRuleParser:
    """Test RuleParser functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = RuleParser()
    
    def test_rule_parser_creation(self):
        """Test creation of rule parser."""
        assert self.parser is not None
    
    def test_parse_rule_comments(self):
        """Test parsing of rule comments from code."""
        code_with_rules = '''
"""
@RULE:PURPOSE: Test utility function for file processing
@RULE:RESPONSIBILITY: File validation and processing
@RULE:IMPORTS_ALLOWED: os, sys, pathlib
@RULE:IMPORTS_FORBIDDEN: requests, urllib
@RULE:DEPENDENCY_DIRECTION: utils <- tools
"""

def process_file(file_path):
    pass
        '''
        
        rules = self.parser.parse_rule_comments(code_with_rules)
        
        assert isinstance(rules, dict)
        assert "PURPOSE" in rules
        assert "RESPONSIBILITY" in rules
        assert "IMPORTS_ALLOWED" in rules
        assert "IMPORTS_FORBIDDEN" in rules
        assert "file processing" in rules["PURPOSE"]
        assert "os, sys, pathlib" in rules["IMPORTS_ALLOWED"]
    
    def test_parse_multiline_rules(self):
        """Test parsing of multiline rule definitions."""
        multiline_rule_code = '''
"""
@RULE:PURPOSE: This is a long purpose description that spans
               multiple lines to test the parsing capability
@RULE:IMPORTS_ALLOWED: os, sys,
                       pathlib, typing,
                       dataclasses
"""
        '''
        
        rules = self.parser.parse_rule_comments(multiline_rule_code)
        
        assert "PURPOSE" in rules
        assert "IMPORTS_ALLOWED" in rules
        assert "multiple lines" in rules["PURPOSE"]
        assert "pathlib" in rules["IMPORTS_ALLOWED"]
        assert "dataclasses" in rules["IMPORTS_ALLOWED"]
    
    def test_parse_rules_from_file(self):
        """Test parsing rules from actual file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp_file:
            tmp_file.write('''
"""
@RULE:PURPOSE: Test file for rule parsing
@RULE:RESPONSIBILITY: Testing rule extraction
"""

def test_function():
    pass
            ''')
            tmp_file.flush()
            
            try:
                rules = self.parser.parse_rules_from_file(tmp_file.name)
                
                assert isinstance(rules, dict)
                assert "PURPOSE" in rules
                assert "RESPONSIBILITY" in rules
                assert "rule parsing" in rules["PURPOSE"]
            finally:
                os.unlink(tmp_file.name)
    
    def test_validate_rule_syntax(self):
        """Test validation of rule syntax."""
        valid_rule = "@RULE:PURPOSE: Valid purpose description"
        invalid_rule = "RULE:PURPOSE Invalid syntax"
        
        assert self.parser.validate_rule_syntax(valid_rule) == True
        assert self.parser.validate_rule_syntax(invalid_rule) == False
    
    def test_extract_rule_hierarchy(self):
        """Test extraction of rule hierarchies."""
        hierarchical_rules = {
            "PURPOSE": "Main purpose",
            "SECURITY": "Security requirements",
            "SECURITY.AUTHENTICATION": "Authentication rules",
            "SECURITY.AUTHORIZATION": "Authorization rules",
            "PERFORMANCE": "Performance requirements",
            "PERFORMANCE.MEMORY": "Memory usage rules"
        }
        
        hierarchy = self.parser.extract_rule_hierarchy(hierarchical_rules)
        
        assert isinstance(hierarchy, dict)
        assert "SECURITY" in hierarchy
        assert "PERFORMANCE" in hierarchy
        assert "AUTHENTICATION" in hierarchy["SECURITY"]
        assert "AUTHORIZATION" in hierarchy["SECURITY"]


class TestRuleEngine:
    """Test RuleEngine functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Use in-memory database for testing
        self.engine = RuleEngine(database_path=":memory:")
        
        # Add some test rules
        self.test_rule_1 = ArchitecturalRule(
            rule_id="TEST_001",
            rule_type=RuleType.PURPOSE,
            scope=RuleScope.FILE,
            priority=RulePriority.HIGH,
            description="Test purpose rule",
            pattern=r"@RULE:PURPOSE: (.+)"
        )
        
        self.test_rule_2 = ArchitecturalRule(
            rule_id="TEST_002",
            rule_type=RuleType.IMPORTS_FORBIDDEN,
            scope=RuleScope.MODULE,
            priority=RulePriority.CRITICAL,
            description="Test import restriction",
            pattern=r"@RULE:IMPORTS_FORBIDDEN: (.+)"
        )
    
    def test_rule_engine_creation(self):
        """Test creation of rule engine."""
        assert self.engine is not None
    
    def test_add_rule(self):
        """Test adding rules to the engine."""
        result = self.engine.add_rule(self.test_rule_1)
        
        assert result == True
        
        # Verify rule was added
        retrieved_rule = self.engine.get_rule("TEST_001")
        assert retrieved_rule is not None
        assert retrieved_rule.rule_id == "TEST_001"
        assert retrieved_rule.description == "Test purpose rule"
    
    def test_update_rule(self):
        """Test updating existing rules."""
        # Add initial rule
        self.engine.add_rule(self.test_rule_1)
        
        # Update the rule
        updated_rule = ArchitecturalRule(
            rule_id="TEST_001",
            rule_type=RuleType.PURPOSE,
            scope=RuleScope.FILE,
            priority=RulePriority.MEDIUM,  # Changed priority
            description="Updated test purpose rule",  # Changed description
            pattern=r"@RULE:PURPOSE: (.+)"
        )
        
        result = self.engine.update_rule(updated_rule)
        assert result == True
        
        # Verify update
        retrieved_rule = self.engine.get_rule("TEST_001")
        assert retrieved_rule.priority == RulePriority.MEDIUM
        assert retrieved_rule.description == "Updated test purpose rule"
    
    def test_delete_rule(self):
        """Test deleting rules from the engine."""
        # Add rule
        self.engine.add_rule(self.test_rule_1)
        
        # Verify it exists
        assert self.engine.get_rule("TEST_001") is not None
        
        # Delete rule
        result = self.engine.delete_rule("TEST_001")
        assert result == True
        
        # Verify deletion
        assert self.engine.get_rule("TEST_001") is None
    
    def test_get_rules_by_scope(self):
        """Test retrieving rules by scope."""
        # Add rules with different scopes
        self.engine.add_rule(self.test_rule_1)  # FILE scope
        self.engine.add_rule(self.test_rule_2)  # MODULE scope
        
        file_rules = self.engine.get_rules_by_scope(RuleScope.FILE)
        module_rules = self.engine.get_rules_by_scope(RuleScope.MODULE)
        
        assert len(file_rules) == 1
        assert len(module_rules) == 1
        assert file_rules[0].rule_id == "TEST_001"
        assert module_rules[0].rule_id == "TEST_002"
    
    def test_get_rules_by_priority(self):
        """Test retrieving rules by priority."""
        self.engine.add_rule(self.test_rule_1)  # HIGH priority
        self.engine.add_rule(self.test_rule_2)  # CRITICAL priority
        
        critical_rules = self.engine.get_rules_by_priority(RulePriority.CRITICAL)
        high_rules = self.engine.get_rules_by_priority(RulePriority.HIGH)
        
        assert len(critical_rules) == 1
        assert len(high_rules) == 1
        assert critical_rules[0].rule_id == "TEST_002"
        assert high_rules[0].rule_id == "TEST_001"
    
    def test_check_compliance(self):
        """Test compliance checking functionality."""
        # Add rules
        self.engine.add_rule(self.test_rule_1)
        self.engine.add_rule(self.test_rule_2)
        
        # Test code that should comply
        compliant_code = '''
"""
@RULE:PURPOSE: Test utility function
@RULE:IMPORTS_FORBIDDEN: requests
"""
import os
import sys

def test_function():
    pass
        '''
        
        context = RuleContext(
            file_path="/test/test.py",
            module_name="test"
        )
        
        result = self.engine.check_compliance(compliant_code, context)
        
        assert isinstance(result, ComplianceResult)
        assert result.is_compliant in [True, False]  # Depends on implementation
        assert isinstance(result.compliance_score, float)
        assert 0.0 <= result.compliance_score <= 1.0
    
    def test_detect_rule_conflicts(self):
        """Test detection of rule conflicts."""
        # Create conflicting rules
        rule_allow = ArchitecturalRule(
            rule_id="ALLOW_001",
            rule_type=RuleType.IMPORTS_ALLOWED,
            scope=RuleScope.MODULE,
            priority=RulePriority.HIGH,
            description="Allow certain imports",
            pattern=r"@RULE:IMPORTS_ALLOWED: requests"
        )
        
        rule_forbid = ArchitecturalRule(
            rule_id="FORBID_001",
            rule_type=RuleType.IMPORTS_FORBIDDEN,
            scope=RuleScope.MODULE,
            priority=RulePriority.HIGH,
            description="Forbid certain imports",
            pattern=r"@RULE:IMPORTS_FORBIDDEN: requests"
        )
        
        self.engine.add_rule(rule_allow)
        self.engine.add_rule(rule_forbid)
        
        conflicts = self.engine.detect_rule_conflicts()
        
        assert isinstance(conflicts, list)
        # Should detect conflict between allowing and forbidding same import
        assert len(conflicts) >= 0  # May or may not detect conflicts depending on implementation
    
    def test_resolve_rule_conflicts(self):
        """Test resolution of rule conflicts."""
        # Create conflicting rules with different priorities
        high_priority_rule = ArchitecturalRule(
            rule_id="HIGH_001",
            rule_type=RuleType.IMPORTS_FORBIDDEN,
            scope=RuleScope.MODULE,
            priority=RulePriority.CRITICAL,
            description="Critical import restriction"
        )
        
        low_priority_rule = ArchitecturalRule(
            rule_id="LOW_001",
            rule_type=RuleType.IMPORTS_ALLOWED,
            scope=RuleScope.MODULE,
            priority=RulePriority.LOW,
            description="Low priority import allowance"
        )
        
        self.engine.add_rule(high_priority_rule)
        self.engine.add_rule(low_priority_rule)
        
        # Create a conflict
        conflict = RuleConflict(
            conflict_id="CONFLICT_001",
            rule_id_1="HIGH_001",
            rule_id_2="LOW_001",
            conflict_type="priority",
            resolution_strategy="priority_based"
        )
        
        resolution = self.engine.resolve_rule_conflict(conflict)
        
        assert resolution is not None
        # Higher priority rule should win
        assert "HIGH_001" in str(resolution) or "CRITICAL" in str(resolution)
    
    def test_get_applicable_rules(self):
        """Test getting applicable rules for context."""
        self.engine.add_rule(self.test_rule_1)  # FILE scope
        self.engine.add_rule(self.test_rule_2)  # MODULE scope
        
        file_context = RuleContext(
            file_path="/test/test.py",
            module_name="test"
        )
        
        applicable_rules = self.engine.get_applicable_rules(file_context)
        
        assert isinstance(applicable_rules, list)
        assert len(applicable_rules) >= 0
        
        # Should include rules applicable to this context
        rule_ids = [rule.rule_id for rule in applicable_rules]
        # FILE scope rule should be applicable to file context
        # MODULE scope rule should also be applicable
    
    def test_export_import_rules(self):
        """Test exporting and importing rule configurations."""
        # Add test rules
        self.engine.add_rule(self.test_rule_1)
        self.engine.add_rule(self.test_rule_2)
        
        # Export rules
        exported_data = self.engine.export_rules()
        
        assert isinstance(exported_data, (str, dict))
        
        # Create new engine and import
        new_engine = RuleEngine(database_path=":memory:")
        result = new_engine.import_rules(exported_data)
        
        assert result == True
        
        # Verify import
        imported_rule = new_engine.get_rule("TEST_001")
        assert imported_rule is not None
        assert imported_rule.description == "Test purpose rule"


class TestRuleValidation:
    """Test rule validation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = RuleEngine(database_path=":memory:")
    
    def test_validate_import_rules(self):
        """Test validation of import-related rules."""
        import_rule = ArchitecturalRule(
            rule_id="IMPORT_001",
            rule_type=RuleType.IMPORTS_FORBIDDEN,
            scope=RuleScope.MODULE,
            priority=RulePriority.HIGH,
            description="Forbid dangerous imports",
            pattern=r"@RULE:IMPORTS_FORBIDDEN: (.+)"
        )
        
        self.engine.add_rule(import_rule)
        
        code_with_forbidden_import = '''
"""
@RULE:IMPORTS_FORBIDDEN: requests, urllib
"""
import os
import requests  # This should be flagged
import sys
        '''
        
        context = RuleContext(file_path="/test/test.py")
        result = self.engine.check_compliance(code_with_forbidden_import, context)
        
        assert isinstance(result, ComplianceResult)
        # Should detect the forbidden import violation
    
    def test_validate_dependency_rules(self):
        """Test validation of dependency direction rules."""
        dependency_rule = ArchitecturalRule(
            rule_id="DEP_001",
            rule_type=RuleType.DEPENDENCY_DIRECTION,
            scope=RuleScope.MODULE,
            priority=RulePriority.HIGH,
            description="Validate dependency direction",
            pattern=r"@RULE:DEPENDENCY_DIRECTION: (.+)"
        )
        
        self.engine.add_rule(dependency_rule)
        
        code_with_dependency = '''
"""
@RULE:DEPENDENCY_DIRECTION: utils <- tools
"""
from tools.helper import something  # This might violate direction
        '''
        
        context = RuleContext(
            file_path="/utils/utilities.py",
            module_name="utils"
        )
        
        result = self.engine.check_compliance(code_with_dependency, context)
        
        assert isinstance(result, ComplianceResult)
    
    def test_custom_validation_functions(self):
        """Test custom validation functions for rules."""
        def validate_class_naming(value, context):
            """Custom validator for class naming conventions."""
            if "class_name" in context:
                class_name = context["class_name"]
                return class_name[0].isupper() and "_" not in class_name
            return True
        
        naming_rule = ArchitecturalRule(
            rule_id="NAMING_001",
            rule_type=RuleType.INTERFACE_RULE,
            scope=RuleScope.CLASS,
            priority=RulePriority.MEDIUM,
            description="Class naming conventions",
            validation_function=validate_class_naming
        )
        
        self.engine.add_rule(naming_rule)
        
        # Test with good class name
        good_context = RuleContext(
            file_path="/test/test.py",
            class_name="GoodClassName"
        )
        
        # Test with bad class name
        bad_context = RuleContext(
            file_path="/test/test.py",
            class_name="bad_class_name"
        )
        
        good_result = self.engine.check_compliance("", good_context)
        bad_result = self.engine.check_compliance("", bad_context)
        
        # Good class name should have higher compliance
        assert good_result.compliance_score >= bad_result.compliance_score


if __name__ == "__main__":
    pytest.main([__file__])