#!/usr/bin/env python3
"""
Check for potential undefined variables in Python code
"""
import os
import re
import ast
from pathlib import Path

class UndefinedVariableChecker(ast.NodeVisitor):
    def __init__(self, filename):
        self.filename = filename
        self.defined_names = set()
        self.used_names = set()
        self.issues = []
        self.current_scope = [set()]  # Stack of scopes
        self.imports = set()
        
    def visit_Import(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.defined_names.add(name)
            self.imports.add(name)
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node):
        for alias in node.names:
            if alias.name == '*':
                # Can't track star imports
                pass
            else:
                name = alias.asname if alias.asname else alias.name
                self.defined_names.add(name)
                self.imports.add(name)
        self.generic_visit(node)
        
    def visit_FunctionDef(self, node):
        self.defined_names.add(node.name)
        # New scope for function
        self.current_scope.append(set())
        
        # Add function parameters to scope
        for arg in node.args.args:
            self.current_scope[-1].add(arg.arg)
            
        self.generic_visit(node)
        self.current_scope.pop()
        
    def visit_ClassDef(self, node):
        self.defined_names.add(node.name)
        self.current_scope.append(set())
        self.generic_visit(node)
        self.current_scope.pop()
        
    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.defined_names.add(target.id)
                self.current_scope[-1].add(target.id)
        self.generic_visit(node)
        
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            # This is a variable being used
            name = node.id
            # Check if it's defined in any scope or is a builtin
            all_defined = self.defined_names | set().union(*self.current_scope)
            if (name not in all_defined and 
                name not in __builtins__ and
                name not in ['self', 'cls', '__name__', '__file__', '__doc__'] and
                not name.startswith('__')):
                self.issues.append((node.lineno, name))
        elif isinstance(node.ctx, ast.Store):
            # This is a variable being defined
            self.defined_names.add(node.id)
            self.current_scope[-1].add(node.id)
        self.generic_visit(node)

def check_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        tree = ast.parse(content)
        checker = UndefinedVariableChecker(filepath)
        checker.visit(tree)
        
        if checker.issues:
            return filepath, checker.issues
    except Exception as e:
        # Skip files that can't be parsed
        pass
    return None, []

def main():
    src_dir = Path('src')
    all_issues = []
    
    for py_file in src_dir.rglob('*.py'):
        filepath, issues = check_file(py_file)
        if issues:
            all_issues.append((filepath, issues))
    
    if all_issues:
        print("🔍 Potential undefined variables found:\n")
        for filepath, issues in all_issues:
            print(f"📄 {filepath}")
            for line_no, var_name in issues:
                print(f"   Line {line_no}: '{var_name}' may be undefined")
            print()
    else:
        print("✅ No obvious undefined variable issues found!")

if __name__ == '__main__':
    main()