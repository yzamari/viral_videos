"""
API Documentation Generator for AI Video Generator
Automatically generates comprehensive documentation for the system
"""

import os
import ast
import inspect
import json
from typing import Dict, List, Any, Optional, Type, get_type_hints
from dataclasses  import dataclass, field
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class ParameterDoc:
    """Documentation for a parameter"""
    name: str
    type_hint: str
    description: str
    required: bool = True
    default_value: Any = None

@dataclass
class MethodDoc:
    """Documentation for a method"""
    name: str
    description: str
    parameters: List[ParameterDoc] = field(default_factory=list)
    return_type: str = ""
    return_description: str = ""
    examples: List[str] = field(default_factory=list)
    raises: List[str] = field(default_factory=list)

@dataclass
class ClassDoc:
    """Documentation for a class"""
    name: str
    description: str
    module: str
    methods: List[MethodDoc] = field(default_factory=list)
    attributes: List[ParameterDoc] = field(default_factory=list)
    inheritance: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)

@dataclass
class ModuleDoc:
    """Documentation for a module"""
    name: str
    description: str
    file_path: str
    classes: List[ClassDoc] = field(default_factory=list)
    functions: List[MethodDoc] = field(default_factory=list)
    constants: List[ParameterDoc] = field(default_factory=list)

class APIDocumentationGenerator:
    """
    Comprehensive API documentation generator

    Automatically generates documentation for the AI Video Generator system
    by analyzing source code, docstrings, and type hints.
    """

    def __init(self, project_root: str, output_dir: str = "docs/api"):
        """
        Initialize API documentation generator

        Args:
            project_root: Root directory of the project
            output_dir: Directory to output documentation
        """
        self.project_root = Path(project_root)
        self.output_dir = Path(output_dir)
        self.src_dir = self.project_root / "src"

        # Documentation data
        self.modules: Dict[str, ModuleDoc] = {}
        self.classes: Dict[str, ClassDoc] = {}
        self.functions: Dict[str, MethodDoc] = {}

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("📚 API documentation generator initialized")
        logger.info(f"   Project root: {self.project_root}")
        logger.info(f"   Output directory: {self.output_dir}")

    def generate_documentation(self) -> Dict[str, Any]:
        """
        Generate comprehensive API documentation

        Returns:
            Dictionary with documentation data
        """
        logger.info("🔍 Analyzing source code for documentation...")

        # Analyze all Python files in src directory
        for py_file in self.src_dir.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue

            try:
                self._analyze_file(py_file)
            except Exception as e:
                logger.error(f"❌ Error analyzing {py_file}: {e}")

        # Generate documentation files
        self._generate_markdown_docs()
        self._generate_json_docs()
        self._generate_index()

        logger.info(f"✅ Generated API documentation in {self.output_dir}")

        return {
            "modules": len(self.modules),
            "classes": len(self.classes),
            "functions": len(self.functions),
            "output_dir": str(self.output_dir)
        }

    def _analyze_file(self, file_path: Path):
        """Analyze a Python file for documentation"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content)

            # Get module info
            module_name = self._get_module_name(file_path)
            module_doc = self._extract_module_doc(tree, module_name, str(file_path))

            # Analyze classes and functions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_doc = self._extract_class_doc(node, module_name)
                    self.classes[f"{module_name}.{class_doc.name}"] = class_doc
                    module_doc.classes.append(class_doc)

                elif isinstance(node, ast.FunctionDef) and not self._is_method(node, tree):
                    func_doc = self._extract_function_doc(node)
                    self.functions[f"{module_name}.{func_doc.name}"] = func_doc
                    module_doc.functions.append(func_doc)

            self.modules[module_name] = module_doc

        except Exception as e:
            logger.error(f"❌ Error analyzing file {file_path}: {e}")

    def _get_module_name(self, file_path: Path) -> str:
        """Get module name from file path"""
        relative_path = file_path.relative_to(self.src_dir)
        module_parts = list(relative_path.parts[:-1]) + [relative_path.stem]
        return ".".join(module_parts)

    def _extract_module_doc(
        self,
        tree: ast.AST,
        module_name: str,
        file_path: str) -> ModuleDoc:
        """Extract module documentation"""
        description = ""

        # Get module docstring
        if (tree.body and
            isinstance(tree.body[0], ast.Expr) and
            isinstance(tree.body[0].value, ast.Constant) and
            isinstance(tree.body[0].value.value, str)):
            description = tree.body[0].value.value.strip()

        return ModuleDoc(
            name=module_name,
            description=description,
            file_path=file_path
        )

    def _extract_class_doc(self, node: ast.ClassDef, module_name: str) -> ClassDoc:
        """Extract class documentation"""
        description = ast.get_docstring(node) or ""

        # Get inheritance
        inheritance = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                inheritance.append(base.id)
            elif isinstance(base, ast.Attribute):
                inheritance.append(f"{base.attr}")

        class_doc = ClassDoc(
            name=node.name,
            description=description,
            module=module_name,
            inheritance=inheritance
        )

        # Extract methods
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_doc = self._extract_function_doc(item)
                class_doc.methods.append(method_doc)

        return class_doc

    def _extract_function_doc(self, node: ast.FunctionDef) -> MethodDoc:
        """Extract function/method documentation"""
        description = ast.get_docstring(node) or ""

        # Parse docstring for parameters and return info
        params, return_desc, examples, raises = self._parse_docstring(description)

        # Extract parameters from function signature
        parameters = []
        for arg in node.args.args:
            param_doc = ParameterDoc(
                name=arg.arg,
                type_hint=self._get_type_hint(arg),
                description=params.get(arg.arg, ""),
                required=arg.arg not in [d.arg for d in node.args.defaults] if node.args.defaults else True
            )
            parameters.append(param_doc)

        # Get return type
        return_type = ""
        if node.returns:
            return_type = self._ast_to_string(node.returns)

        return MethodDoc(
            name=node.name,
            description=description.split('\n')[0] if description else "",
            parameters=parameters,
            return_type=return_type,
            return_description=return_desc,
            examples=examples,
            raises=raises
        )

    def _parse_docstring(self, docstring: str) -> tuple:
        """Parse docstring for structured information"""
        params = {}
        return_desc = ""
        examples = []
        raises = []

        if not docstring:
            return params, return_desc, examples, raises

        lines = docstring.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()

            if line.startswith('Args:'):
                current_section = 'args'
                continue
            elif line.startswith('Returns:'):
                current_section = 'returns'
                continue
            elif line.startswith('Raises:'):
                current_section = 'raises'
                continue
            elif line.startswith('Example'):
                current_section = 'examples'
                continue

            if current_section == 'args' and ':' in line:
                param_name = line.split(':')[0].strip()
                param_desc = ':'.join(line.split(':')[1:]).strip()
                params[param_name] = param_desc

            elif current_section == 'returns' and line:
                return_desc = line

            elif current_section == 'raises' and line:
                raises.append(line)

            elif current_section == 'examples' and line:
                examples.append(line)

        return params, return_desc, examples, raises

    def _get_type_hint(self, arg: ast.arg) -> str:
        """Get type hint for argument"""
        if arg.annotation:
            return self._ast_to_string(arg.annotation)
        return "Any"

    def _ast_to_string(self, node: ast.AST) -> str:
        """Convert AST node to string"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return str(node.value)
        elif isinstance(node, ast.Attribute):
            return f"{self._ast_to_string(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return f"{self._ast_to_string(node.value)}[{self._ast_to_string(node.slice)}]"
        else:
            return "Unknown"

    def _is_method(self, node: ast.FunctionDef, tree: ast.AST) -> bool:
        """Check if function is a method (inside a class)"""
        for parent in ast.walk(tree):
            if isinstance(parent, ast.ClassDef):
                if node in parent.body:
                    return True
        return False

    def _generate_markdown_docs(self):
        """Generate Markdown documentation files"""
        logger.info("📝 Generating Markdown documentation...")

        # Generate module documentation
        for module_name, module_doc in self.modules.items():
            self._generate_module_markdown(module_doc)

        # Generate class documentation
        for class_name, class_doc in self.classes.items():
            self._generate_class_markdown(class_doc)

    def _generate_module_markdown(self, module_doc: ModuleDoc):
        """Generate Markdown for a module"""
        content = f"# {module_doc.name}\n\n"

        if module_doc.description:
            content += f"{module_doc.description}\n\n"

        content += f"**File:** `{module_doc.file_path}`\n\n"

        # Classes
        if module_doc.classes:
            content += "## Classes\n\n"
            for class_doc in module_doc.classes:
                content += f"### {class_doc.name}\n\n"
                if class_doc.description:
                    content += f"{class_doc.description}\n\n"

                if class_doc.inheritance:
                    content += f"**Inherits from:** {', '.join(class_doc.inheritance)}\n\n"

                # Methods
                if class_doc.methods:
                    content += "#### Methods\n\n"
                    for method in class_doc.methods:
                        content += f"##### {method.name}\n\n"
                        if method.description:
                            content += f"{method.description}\n\n"

                        # Parameters
                        if method.parameters:
                            content += "**Parameters:**\n\n"
                            for param in method.parameters:
                                required = "required" if param.required else "optional"
                                content += f"- `{param.name}` ({param.type_hint}, {required}): {param.description}\n"
                            content += "\n"

                        # Return
                        if method.return_type:
                            content += f"**Returns:** {method.return_type}"
                            if method.return_description:
                                content += f" - {method.return_description}"
                            content += "\n\n"

        # Functions
        if module_doc.functions:
            content += "## Functions\n\n"
            for func_doc in module_doc.functions:
                content += f"### {func_doc.name}\n\n"
                if func_doc.description:
                    content += f"{func_doc.description}\n\n"

                # Parameters
                if func_doc.parameters:
                    content += "**Parameters:**\n\n"
                    for param in func_doc.parameters:
                        required = "required" if param.required else "optional"
                        content += f"- `{param.name}` ({param.type_hint}, {required}): {param.description}\n"
                    content += "\n"

                # Return
                if func_doc.return_type:
                    content += f"**Returns:** {func_doc.return_type}"
                    if func_doc.return_description:
                        content += f" - {func_doc.return_description}"
                    content += "\n\n"

        # Save to file
        filename = module_doc.name.replace('.', '_') + '.md'
        filepath = self.output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    def _generate_class_markdown(self, class_doc: ClassDoc):
        """Generate detailed Markdown for a class"""
        content = f"# {class_doc.name}\n\n"

        if class_doc.description:
            content += f"{class_doc.description}\n\n"

        content += f"**Module:** `{class_doc.module}`\n\n"

        if class_doc.inheritance:
            content += f"**Inherits from:** {', '.join(class_doc.inheritance)}\n\n"

        # Methods
        if class_doc.methods:
            content += "## Methods\n\n"
            for method in class_doc.methods:
                content += f"### {method.name}\n\n"
                if method.description:
                    content += f"{method.description}\n\n"

                # Parameters
                if method.parameters:
                    content += "**Parameters:**\n\n"
                    for param in method.parameters:
                        required = "required" if param.required else "optional"
                        content += f"- `{param.name}` ({param.type_hint}, {required}): {param.description}\n"
                    content += "\n"

                # Return
                if method.return_type:
                    content += f"**Returns:** {method.return_type}"
                    if method.return_description:
                        content += f" - {method.return_description}"
                    content += "\n\n"

                # Examples
                if method.examples:
                    content += "**Examples:**\n\n"
                    for example in method.examples:
                        content += f"```python\n{example}\n```\n\n"

                # Raises
                if method.raises:
                    content += "**Raises:**\n\n"
                    for exception in method.raises:
                        content += f"- {exception}\n"
                    content += "\n"

        # Save to file
        filename = f"class_{class_doc.name.lower()}.md"
        filepath = self.output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    def _generate_json_docs(self):
        """Generate JSON documentation"""
        logger.info("📄 Generating JSON documentation...")

        # Convert to serializable format
        docs_data = {
            "generated_at": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "modules": {
                name: {
                    "name": doc.name,
                    "description": doc.description,
                    "file_path": doc.file_path,
                    "classes": [
                        {
                            "name": cls.name,
                            "description": cls.description,
                            "methods": [
                                {
                                    "name": method.name,
                                    "description": method.description,
                                    "parameters": [
                                        {
                                            "name": param.name,
                                            "type_hint": param.type_hint,
                                            "description": param.description,
                                            "required": param.required
                                        } for param in method.parameters
                                    ],
                                    "return_type": method.return_type,
                                    "return_description": method.return_description
                                } for method in cls.methods
                            ]
                        } for cls in doc.classes
                    ],
                    "functions": [
                        {
                            "name": func.name,
                            "description": func.description,
                            "parameters": [
                                {
                                    "name": param.name,
                                    "type_hint": param.type_hint,
                                    "description": param.description,
                                    "required": param.required
                                } for param in func.parameters
                            ],
                            "return_type": func.return_type,
                            "return_description": func.return_description
                        } for func in doc.functions
                    ]
                } for name, doc in self.modules.items()
            }
        }

        # Save JSON documentation
        json_path = self.output_dir / "api_documentation.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(docs_data, f, indent=2, ensure_ascii=False)

    def _generate_index(self):
        """Generate index/overview documentation"""
        logger.info("📋 Generating documentation index...")

        content = "# AI Video Generator API Documentation\n\n"
        content += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # Overview
        content += "## Overview\n\n"
        content += f"- **Modules:** {len(self.modules)}\n"
        content += f"- **Classes:** {len(self.classes)}\n"
        content += f"- **Functions:** {len(self.functions)}\n\n"

        # Modules
        content += "## Modules\n\n"
        for module_name, module_doc in sorted(self.modules.items()):
            filename = module_name.replace('.', '_') + '.md'
            content += f"- [{module_name}](filename)"
            if module_doc.description:
                first_line = module_doc.description.split('\n')[0]
                content += f" - {first_line}"
            content += "\n"

        content += "\n"

        # Classes
        content += "## Classes\n\n"
        for class_name, class_doc in sorted(self.classes.items()):
            filename = f"class_{class_doc.name.lower()}.md"
            content += f"- [{class_name}](filename)"
            if class_doc.description:
                first_line = class_doc.description.split('\n')[0]
                content += f" - {first_line}"
            content += "\n"

        # Save index
        index_path = self.output_dir / "README.md"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"📚 Documentation index saved to: {index_path}")

def generate_api_documentation(
    project_root: str = ".",
    output_dir: str = "docs/api") -> Dict[str, Any]:
    """
    Generate comprehensive API documentation

    Args:
        project_root: Root directory of the project
        output_dir: Directory to output documentation

    Returns:
        Dictionary with generation results
    """
    generator = APIDocumentationGenerator(project_root, output_dir)
    return generator.generate_documentation()

if __name__ == "__main__":
    # Generate documentation when run directly
    result = generate_api_documentation()
    print(f"✅ Generated documentation: {result}")
