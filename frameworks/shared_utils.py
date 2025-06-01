"""
Shared utility functions for AI Tools frameworks
"""
import json
import re
from typing import Dict, Any, Tuple, Optional

def safe_json_parse(json_string: str, fallback: Optional[Dict] = None) -> Tuple[bool, Dict[str, Any]]:
    """Safely parse JSON string with fallback handling."""
    if fallback is None:
        fallback = {}
    
    try:
        cleaned = json_string.strip()
        if cleaned.startswith('```json'):
            cleaned = cleaned.replace('```json', '').replace('```', '').strip()
        elif cleaned.startswith('```'):
            cleaned = cleaned.replace('```', '').strip()
        parsed = json.loads(cleaned)
        return True, parsed
    except (json.JSONDecodeError, Exception) as e:
        print(f"⚠️ JSON parsing failed: {str(e)}")
        return False, fallback

def sanitize_text_for_notion(text: str, max_length: int = 2000) -> str:
    """Sanitize text for Notion rich text fields."""
    if not text:
        return ""
    
    sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', str(text))
    
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length-3] + "..."
    
    return sanitized

def format_list_for_display(items_list):
    """Format a list for display (converts list to comma-separated string)"""
    if not items_list:
        return ""
    
    if isinstance(items_list, list):
        return ", ".join(items_list)
    
    return str(items_list)

def parse_markdown_table(markdown_table):
    """Parse a markdown table into a list of dictionaries"""
    import re
    result = []
    
    lines = markdown_table.strip().split('\n')
    
    header_row = None
    for i, line in enumerate(lines):
        if line.startswith('|') and i < len(lines) - 1 and re.match(r'^\|\s*[-:]+\s*\|', lines[i+1]):
            header_row = line
            break
    
    if not header_row:
        return result
    
    headers = [h.strip() for h in header_row.split('|')[1:-1]]
    
    for line in lines:
        if line == header_row or re.match(r'^\|\s*[-:]+\s*\|', line):
            continue
        
        if line.startswith('|') and line.endswith('|'):
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            
            if len(cells) != len(headers):
                continue
            
            row_dict = {headers[i]: cells[i] for i in range(len(headers))}
            result.append(row_dict)
    
    return result

def extract_comment_rules(file_path: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Extract @RULE directives from file comments.
    
    Args:
        file_path: Path to the file to parse
        
    Returns:
        Tuple of (success, rules_dict)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to match @RULE: directives in comments
        rule_pattern = r'@RULE:(\w+):\s*(.+?)(?=\n|$)'
        matches = re.findall(rule_pattern, content, re.IGNORECASE | re.MULTILINE)
        
        rules = {}
        for rule_name, rule_value in matches:
            rule_name = rule_name.upper()
            
            # Parse different rule value types
            rule_value = rule_value.strip()
            
            # Handle numeric values
            if rule_value.isdigit():
                rules[rule_name] = int(rule_value)
            # Handle ranges (e.g., "3-5", "40-80")
            elif re.match(r'^\d+-\d+$', rule_value):
                min_val, max_val = map(int, rule_value.split('-'))
                rules[rule_name] = {'min': min_val, 'max': max_val}
            # Handle comma-separated lists
            elif ',' in rule_value:
                rules[rule_name] = [item.strip() for item in rule_value.split(',')]
            # Handle boolean values
            elif rule_value.lower() in ['true', 'false']:
                rules[rule_name] = rule_value.lower() == 'true'
            # Handle decimal values
            elif re.match(r'^\d+\.\d+$', rule_value):
                rules[rule_name] = float(rule_value)
            # Default to string
            else:
                rules[rule_name] = rule_value
        
        return True, rules
        
    except Exception as e:
        print(f"⚠️ Rule extraction failed for {file_path}: {str(e)}")
        return False, {}

def extract_string_rules(content: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Extract @RULE directives from string content.
    
    Args:
        content: String content to parse
        
    Returns:
        Tuple of (success, rules_dict)
    """
    try:
        # Pattern to match @RULE: directives in comments
        rule_pattern = r'@RULE:(\w+):\s*(.+?)(?=\n|$)'
        matches = re.findall(rule_pattern, content, re.IGNORECASE | re.MULTILINE)
        
        rules = {}
        for rule_name, rule_value in matches:
            rule_name = rule_name.upper()
            
            # Parse different rule value types
            rule_value = rule_value.strip()
            
            # Handle numeric values
            if rule_value.isdigit():
                rules[rule_name] = int(rule_value)
            # Handle ranges (e.g., "3-5", "40-80")
            elif re.match(r'^\d+-\d+$', rule_value):
                min_val, max_val = map(int, rule_value.split('-'))
                rules[rule_name] = {'min': min_val, 'max': max_val}
            # Handle comma-separated lists
            elif ',' in rule_value:
                rules[rule_name] = [item.strip() for item in rule_value.split(',')]
            # Handle boolean values
            elif rule_value.lower() in ['true', 'false']:
                rules[rule_name] = rule_value.lower() == 'true'
            # Handle decimal values
            elif re.match(r'^\d+\.\d+$', rule_value):
                rules[rule_name] = float(rule_value)
            # Default to string
            else:
                rules[rule_name] = rule_value
        
        return True, rules
        
    except Exception as e:
        print(f"⚠️ Rule extraction failed from string content: {str(e)}")
        return False, {}