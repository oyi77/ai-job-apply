#!/usr/bin/env python3
"""
Technical Debt Monitor for AI Job Application Assistant

This script analyzes the codebase for technical debt indicators and generates
a comprehensive report with actionable insights for debt reduction.
"""

import os
import sys
import subprocess
import json
import ast
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import argparse

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from utils.logger import get_logger
except ImportError:
    # Fallback if logger not available
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = logging.getLogger

logger = get_logger(__name__)

@dataclass
class CodeMetrics:
    """Code quality metrics for a file or module."""
    file_path: str
    lines_of_code: int
    function_count: int
    class_count: int
    max_function_length: int
    max_class_length: int
    complexity_score: int
    docstring_coverage: float
    type_hint_coverage: float
    import_count: int
    unused_imports: int
    magic_numbers: int
    todo_comments: int
    fixme_comments: int

@dataclass
class TechnicalDebtReport:
    """Complete technical debt analysis report."""
    timestamp: datetime
    total_files: int
    total_lines: int
    overall_score: float
    debt_indicators: List[str]
    critical_issues: List[str]
    recommendations: List[str]
    file_metrics: List[CodeMetrics]
    summary: Dict[str, Any]

class TechnicalDebtAnalyzer:
    """Analyzes codebase for technical debt indicators."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.python_files = []
        self.typescript_files = []
        self.analysis_results = []
        
    def discover_files(self) -> None:
        """Discover all code files in the project."""
        logger.info("Discovering code files...")
        
        # Python files
        for py_file in self.project_root.rglob("*.py"):
            if not self._is_excluded(py_file):
                self.python_files.append(py_file)
        
        # TypeScript/JavaScript files
        for ts_file in self.project_root.rglob("*.ts"):
            if not self._is_excluded(ts_file):
                self.typescript_files.append(ts_file)
        
        for tsx_file in self.project_root.rglob("*.tsx"):
            if not self._is_excluded(tsx_file):
                self.typescript_files.append(tsx_file)
        
        logger.info(f"Found {len(self.python_files)} Python files and {len(self.typescript_files)} TypeScript files")
    
    def _is_excluded(self, file_path: Path) -> bool:
        """Check if file should be excluded from analysis."""
        exclude_patterns = [
            "venv/", "__pycache__/", ".git/", "node_modules/",
            "build/", "dist/", ".pytest_cache/", ".mypy_cache/",
            "*.pyc", "*.pyo", "*.pyd", "*.so", "*.dll", "*.dylib"
        ]
        
        return any(pattern in str(file_path) for pattern in exclude_patterns)
    
    def analyze_python_file(self, file_path: Path) -> CodeMetrics:
        """Analyze a single Python file for code quality metrics."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Parse AST for detailed analysis
            try:
                tree = ast.parse(content)
            except SyntaxError:
                logger.warning(f"Syntax error in {file_path}")
                return self._create_empty_metrics(str(file_path))
            
            # Count functions and classes
            function_count = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
            class_count = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
            
            # Analyze function lengths
            function_lengths = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    function_lengths.append(node.end_lineno - node.lineno)
            
            max_function_length = max(function_lengths) if function_lengths else 0
            
            # Analyze class lengths
            class_lengths = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_lengths.append(node.end_lineno - node.lineno)
            
            max_class_length = max(class_lengths) if class_lengths else 0
            
            # Count imports
            import_count = len([node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))])
            
            # Count TODO/FIXME comments
            todo_comments = sum(1 for line in lines if 'TODO' in line.upper())
            fixme_comments = sum(1 for line in lines if 'FIXME' in line.upper())
            
            # Count magic numbers (simplified)
            magic_numbers = sum(1 for line in lines if any(char.isdigit() for char in line) and '=' in line)
            
            # Calculate complexity score (simplified)
            complexity_score = sum(1 for node in ast.walk(tree) if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)))
            
            # Calculate docstring coverage (simplified)
            docstring_count = sum(1 for line in lines if '"""' in line or "'''" in line)
            docstring_coverage = min(100.0, (docstring_count / max(1, function_count + class_count)) * 100)
            
            # Calculate type hint coverage (simplified)
            type_hint_lines = sum(1 for line in lines if ':' in line and '->' in line)
            type_hint_coverage = min(100.0, (type_hint_lines / max(1, function_count)) * 100)
            
            return CodeMetrics(
                file_path=str(file_path),
                lines_of_code=len(lines),
                function_count=function_count,
                class_count=class_count,
                max_function_length=max_function_length,
                max_class_length=max_class_length,
                complexity_score=complexity_score,
                docstring_coverage=docstring_coverage,
                type_hint_coverage=type_hint_coverage,
                import_count=import_count,
                unused_imports=0,  # Would need more sophisticated analysis
                magic_numbers=magic_numbers,
                todo_comments=todo_comments,
                fixme_comments=fixme_comments
            )
            
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return self._create_empty_metrics(str(file_path))
    
    def _create_empty_metrics(self, file_path: str) -> CodeMetrics:
        """Create empty metrics for files that can't be analyzed."""
        return CodeMetrics(
            file_path=file_path,
            lines_of_code=0,
            function_count=0,
            class_count=0,
            max_function_length=0,
            max_class_length=0,
            complexity_score=0,
            docstring_coverage=0.0,
            type_hint_coverage=0.0,
            import_count=0,
            unused_imports=0,
            magic_numbers=0,
            todo_comments=0,
            fixme_comments=0
        )
    
    def analyze_typescript_file(self, file_path: Path) -> CodeMetrics:
        """Analyze a single TypeScript file for code quality metrics."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Simplified TypeScript analysis
            function_count = sum(1 for line in lines if 'function ' in line or '=>' in line)
            class_count = sum(1 for line in lines if 'class ' in line)
            interface_count = sum(1 for line in lines if 'interface ' in line)
            
            # Count TODO/FIXME comments
            todo_comments = sum(1 for line in lines if 'TODO' in line.upper())
            fixme_comments = sum(1 for line in lines if 'FIXME' in line.upper())
            
            # Count imports
            import_count = sum(1 for line in lines if 'import ' in line)
            
            # Calculate complexity score (simplified)
            complexity_score = sum(1 for line in lines if any(keyword in line for keyword in ['if', 'while', 'for', 'catch']))
            
            return CodeMetrics(
                file_path=str(file_path),
                lines_of_code=len(lines),
                function_count=function_count,
                class_count=class_count + interface_count,
                max_function_length=0,  # Would need more sophisticated analysis
                max_class_length=0,     # Would need more sophisticated analysis
                complexity_score=complexity_score,
                docstring_coverage=0.0,  # TypeScript doesn't use docstrings
                type_hint_coverage=100.0,  # TypeScript is typed by default
                import_count=import_count,
                unused_imports=0,
                magic_numbers=0,
                todo_comments=todo_comments,
                fixme_comments=fixme_comments
            )
            
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return self._create_empty_metrics(str(file_path))
    
    def analyze_codebase(self) -> None:
        """Analyze all discovered files for technical debt indicators."""
        logger.info("Analyzing codebase for technical debt...")
        
        # Analyze Python files
        for py_file in self.python_files:
            metrics = self.analyze_python_file(py_file)
            self.analysis_results.append(metrics)
        
        # Analyze TypeScript files
        for ts_file in self.typescript_files:
            metrics = self.analyze_typescript_file(ts_file)
            self.analysis_results.append(metrics)
        
        logger.info(f"Analysis complete. Analyzed {len(self.analysis_results)} files.")
    
    def generate_report(self) -> TechnicalDebtReport:
        """Generate a comprehensive technical debt report."""
        logger.info("Generating technical debt report...")
        
        if not self.analysis_results:
            return self._create_empty_report()
        
        # Calculate overall metrics
        total_files = len(self.analysis_results)
        total_lines = sum(m.lines_of_code for m in self.analysis_results)
        
        # Identify debt indicators
        debt_indicators = []
        critical_issues = []
        
        # Check for violations of technical debt rules
        for metrics in self.analysis_results:
            if metrics.max_function_length > 20:
                debt_indicators.append(f"{metrics.file_path}: Function too long ({metrics.max_function_length} lines)")
            
            if metrics.max_class_length > 200:
                debt_indicators.append(f"{metrics.file_path}: Class too long ({metrics.max_class_length} lines)")
            
            if metrics.lines_of_code > 500:
                debt_indicators.append(f"{metrics.file_path}: Module too long ({metrics.lines_of_code} lines)")
            
            if metrics.complexity_score > 10:
                critical_issues.append(f"{metrics.file_path}: High complexity ({metrics.complexity_score})")
            
            if metrics.todo_comments > 0:
                debt_indicators.append(f"{metrics.file_path}: {metrics.todo_comments} TODO comments")
            
            if metrics.fixme_comments > 0:
                critical_issues.append(f"{metrics.file_path}: {metrics.fixme_comments} FIXME comments")
            
            if metrics.docstring_coverage < 80:
                debt_indicators.append(f"{metrics.file_path}: Low docstring coverage ({metrics.docstring_coverage:.1f}%)")
            
            if metrics.type_hint_coverage < 80:
                debt_indicators.append(f"{metrics.file_path}: Low type hint coverage ({metrics.type_hint_coverage:.1f}%)")
        
        # Calculate overall score (0-100, higher is better)
        overall_score = 100.0
        
        # Deduct points for violations
        overall_score -= len(debt_indicators) * 2
        overall_score -= len(critical_issues) * 5
        overall_score = max(0.0, overall_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(debt_indicators, critical_issues)
        
        # Create summary
        summary = {
            "total_files": total_files,
            "total_lines": total_lines,
            "average_file_size": total_lines / total_files if total_files > 0 else 0,
            "files_with_violations": len([m for m in self.analysis_results if any([
                m.max_function_length > 20,
                m.max_class_length > 200,
                m.lines_of_code > 500,
                m.complexity_score > 10,
                m.todo_comments > 0,
                m.fixme_comments > 0
            ])]),
            "debt_indicators_count": len(debt_indicators),
            "critical_issues_count": len(critical_issues)
        }
        
        return TechnicalDebtReport(
            timestamp=datetime.now(),
            total_files=total_files,
            total_lines=total_lines,
            overall_score=overall_score,
            debt_indicators=debt_indicators,
            critical_issues=critical_issues,
            recommendations=recommendations,
            file_metrics=self.analysis_results,
            summary=summary
        )
    
    def _generate_recommendations(self, debt_indicators: List[str], critical_issues: List[str]) -> List[str]:
        """Generate actionable recommendations based on debt indicators."""
        recommendations = []
        
        if any("Function too long" in indicator for indicator in debt_indicators):
            recommendations.append("Refactor long functions to be under 20 lines")
        
        if any("Class too long" in indicator for indicator in debt_indicators):
            recommendations.append("Break down large classes into smaller, focused classes")
        
        if any("Module too long" in indicator for indicator in debt_indicators):
            recommendations.append("Split large modules into smaller, focused modules")
        
        if any("High complexity" in issue for issue in critical_issues):
            recommendations.append("Reduce cyclomatic complexity by simplifying conditional logic")
        
        if any("TODO comments" in indicator for indicator in debt_indicators):
            recommendations.append("Address all TODO comments within the current sprint")
        
        if any("FIXME comments" in issue for issue in critical_issues):
            recommendations.append("Immediately address all FIXME comments as they indicate broken code")
        
        if any("Low docstring coverage" in indicator for indicator in debt_indicators):
            recommendations.append("Add comprehensive docstrings to all public functions and classes")
        
        if any("Low type hint coverage" in indicator for indicator in debt_indicators):
            recommendations.append("Add type hints to all function parameters and return values")
        
        if not recommendations:
            recommendations.append("Code quality is excellent! Keep up the good work.")
        
        return recommendations
    
    def _create_empty_report(self) -> TechnicalDebtReport:
        """Create an empty report when no files are analyzed."""
        return TechnicalDebtReport(
            timestamp=datetime.now(),
            total_files=0,
            total_lines=0,
            overall_score=0.0,
            debt_indicators=[],
            critical_issues=[],
            recommendations=["No files found to analyze"],
            file_metrics=[],
            summary={}
        )
    
    def save_report(self, report: TechnicalDebtReport, output_file: str) -> None:
        """Save the technical debt report to a file."""
        try:
            # Convert dataclass to dict for JSON serialization
            report_dict = {
                "timestamp": report.timestamp.isoformat(),
                "total_files": report.total_files,
                "total_lines": report.total_lines,
                "overall_score": report.overall_score,
                "debt_indicators": report.debt_indicators,
                "critical_issues": report.critical_issues,
                "recommendations": report.recommendations,
                "summary": report.summary,
                "file_metrics": [
                    {
                        "file_path": m.file_path,
                        "lines_of_code": m.lines_of_code,
                        "function_count": m.function_count,
                        "class_count": m.class_count,
                        "max_function_length": m.max_function_length,
                        "max_class_length": m.max_class_length,
                        "complexity_score": m.complexity_score,
                        "docstring_coverage": m.docstring_coverage,
                        "type_hint_coverage": m.type_hint_coverage,
                        "import_count": m.import_count,
                        "unused_imports": m.unused_imports,
                        "magic_numbers": m.magic_numbers,
                        "todo_comments": m.todo_comments,
                        "fixme_comments": m.fixme_comments
                    }
                    for m in report.file_metrics
                ]
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Technical debt report saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving report: {e}")
    
    def print_report(self, report: TechnicalDebtReport) -> None:
        """Print the technical debt report to console."""
        print("\n" + "="*80)
        print("🔍 TECHNICAL DEBT ANALYSIS REPORT")
        print("="*80)
        print(f"📅 Generated: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Overall Score: {report.overall_score:.1f}/100")
        print(f"📁 Total Files: {report.total_files}")
        print(f"📝 Total Lines: {report.total_lines:,}")
        print()
        
        # Summary
        print("📋 SUMMARY")
        print("-" * 40)
        print(f"Files with violations: {report.summary.get('files_with_violations', 0)}")
        print(f"Debt indicators: {len(report.debt_indicators)}")
        print(f"Critical issues: {len(report.critical_issues)}")
        print()
        
        # Critical Issues
        if report.critical_issues:
            print("🚨 CRITICAL ISSUES (Fix Immediately)")
            print("-" * 40)
            for issue in report.critical_issues:
                print(f"  ❌ {issue}")
            print()
        
        # Debt Indicators
        if report.debt_indicators:
            print("⚠️  DEBT INDICATORS (Address Soon)")
            print("-" * 40)
            for indicator in report.debt_indicators:
                print(f"  ⚠️  {indicator}")
            print()
        
        # Recommendations
        if report.recommendations:
            print("💡 RECOMMENDATIONS")
            print("-" * 40)
            for i, rec in enumerate(report.recommendations, 1):
                print(f"  {i}. {rec}")
            print()
        
        # File-level metrics (top 10 worst offenders)
        if report.file_metrics:
            print("📊 TOP 10 FILES BY DEBT SCORE")
            print("-" * 40)
            
            # Calculate debt score for each file
            file_scores = []
            for metrics in report.file_metrics:
                score = 0
                if metrics.max_function_length > 20:
                    score += (metrics.max_function_length - 20) * 0.5
                if metrics.max_class_length > 200:
                    score += (metrics.max_class_length - 200) * 0.1
                if metrics.complexity_score > 10:
                    score += (metrics.complexity_score - 10) * 2
                if metrics.todo_comments > 0:
                    score += metrics.todo_comments * 1
                if metrics.fixme_comments > 0:
                    score += metrics.fixme_comments * 5
                
                file_scores.append((metrics.file_path, score))
            
            # Sort by score (highest first)
            file_scores.sort(key=lambda x: x[1], reverse=True)
            
            for i, (file_path, score) in enumerate(file_scores[:10], 1):
                if score > 0:
                    print(f"  {i:2d}. {file_path} (Score: {score:.1f})")
        
        print("="*80)
        print("🎯 Remember: Technical debt is a choice, not a necessity!")
        print("Every line of code should improve the system, not burden it.")
        print("="*80)

def main():
    """Main entry point for the technical debt monitor."""
    parser = argparse.ArgumentParser(description="Technical Debt Monitor for AI Job Application Assistant")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--output", default="technical-debt-report.json", help="Output JSON file")
    parser.add_argument("--quiet", action="store_true", help="Suppress console output")
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = TechnicalDebtAnalyzer(args.project_root)
    
    try:
        # Discover and analyze files
        analyzer.discover_files()
        analyzer.analyze_codebase()
        
        # Generate and save report
        report = analyzer.generate_report()
        analyzer.save_report(report, args.output)
        
        # Print report unless quiet mode
        if not args.quiet:
            analyzer.print_report(report)
        
        # Exit with error code if critical issues found
        if report.critical_issues:
            logger.error(f"Found {len(report.critical_issues)} critical issues")
            sys.exit(1)
        elif report.debt_indicators:
            logger.warning(f"Found {len(report.debt_indicators)} debt indicators")
            sys.exit(0)
        else:
            logger.info("No technical debt found! 🎉")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
