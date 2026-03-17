#!/usr/bin/env python3
"""
DA-Agent CLI - Command line interface for data analysis

Usage:
    python cli.py analyze
"""

import sys
import os
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent))

from lib.security_wrapper import SecureFileAccess, SecurityError
from lib.complexity_scorer import ComplexityScorer
from lib.knowledge_store import KnowledgeStore
from lib.code_generator import CodeGenerator, ValidationError
from lib.executor import Executor, ExecutionError


def analyze_request():
    """Interactive analysis request workflow"""
    print("\n" + "="*60)
    print("🎯 DA-Agent: Data Analysis Session")
    print("="*60 + "\n")

    # Step 1: Get business question
    print("📊 Step 1: Business Question")
    print("-" * 60)
    question = input("\nWhat business question are you trying to answer?\n> ")

    if not question.strip():
        print("❌ Please provide a valid question")
        return

    print(f"\n✓ Question: {question}")

    # Step 2: Get data source
    print("\n📁 Step 2: Data Source")
    print("-" * 60)
    data_file = input("\nWhere is your data file? (e.g., users.csv)\n> ")

    # Validate file access
    workspace = Path(os.getcwd())
    security = SecureFileAccess(workspace)

    try:
        safe_path = security.validate_path(data_file)
        print(f"✓ File validated: {safe_path}")
    except SecurityError as e:
        print(f"❌ Security error: {e}")
        return

    if not safe_path.exists():
        print(f"❌ File not found: {safe_path}")
        return

    # Step 3: Get analysis type
    print("\n🔍 Step 3: Analysis Type")
    print("-" * 60)
    print("\nChoose analysis type:")
    print("1) Top N records by column")
    print("2) Group by and aggregate")

    choice = input("\nYour choice (1-2): ")

    # Build task specification
    task = {
        "analysis_type": "aggregation",
        "data_source": str(safe_path.name)
    }

    if choice == "1":
        sort_col = input("Sort by which column? ")
        limit = input("How many top records? (default: 10) ") or "10"

        task.update({
            "operation": "top_n",
            "sort_by": sort_col,
            "limit": int(limit)
        })

        # Build structured request for complexity scoring
        structured_req = {
            "question": question,
            "data_sources": [data_file],
            "analysis_type": "aggregation",
            "requires_join": False,
            "statistical_methods": []
        }

    elif choice == "2":
        group_col = input("Group by which column? ")
        agg_col = input("Aggregate which column? ")
        agg_func = input("Aggregation function (sum/mean/count/min/max/std/median)? ") or "sum"

        task.update({
            "operation": "groupby",
            "group_by": group_col,
            "agg_column": agg_col,
            "agg_function": agg_func
        })

        structured_req = {
            "question": question,
            "data_sources": [data_file],
            "analysis_type": "groupby",
            "requires_join": False,
            "statistical_methods": []
        }
    else:
        print("❌ Invalid choice")
        return

    # Step 4: Score complexity
    print("\n📈 Step 4: Complexity Scoring")
    print("-" * 60)

    scorer = ComplexityScorer()
    result = scorer.score_with_rules(structured_req)

    print(f"\n  Score: {result.score}/10")
    print(f"  Mode: {result.mode.upper()}")
    print(f"  Reasoning: {result.reasoning}")

    # Step 5: Generate code
    print("\n💻 Step 5: Code Generation")
    print("-" * 60)

    templates_dir = Path(__file__).parent / "assets" / "sql_templates"
    generator = CodeGenerator(templates_dir)

    try:
        code = generator.generate(task)
        print(f"\n✓ Generated {len(code)} characters of code\n")
        print("Generated code preview:")
        print("-" * 60)
        for i, line in enumerate(code.split('\n')[:20], 1):
            print(f"{i:3d} | {line}")
        if len(code.split('\n')) > 20:
            print("    | ... (truncated)")
        print("-" * 60)
    except ValidationError as e:
        print(f"❌ Validation error: {e}")
        return

    # Step 6: User approval
    print("\n✅ Step 6: Execution")
    print("-" * 60)
    approval = input("\nExecute this code? (y/n): ")

    if approval.lower() != 'y':
        print("❌ Execution cancelled")
        return

    # Step 7: Execute
    print("\n⚙️  Executing...")
    executor = Executor(workspace)

    try:
        output = executor.execute(code, timeout=30)
        print("\n" + "="*60)
        print("📊 RESULTS")
        print("="*60)
        print(output)
    except ExecutionError as e:
        print(f"❌ Execution failed: {e}")
        return

    # Step 8: Save to knowledge base
    print("\n💾 Step 8: Save to Knowledge Base")
    print("-" * 60)

    kb_dir = Path.home() / ".da-agent" / "knowledge"
    kb_dir.mkdir(parents=True, exist_ok=True)
    kb = KnowledgeStore(str(kb_dir / "kb.db"))

    task_id = kb.save_task(
        description=question,
        structured_req=structured_req,
        complexity_score=result.score,
        execution_mode=result.mode
    )

    print(f"✓ Task saved to knowledge base (ID: {task_id})")

    print("\n" + "="*60)
    print("✅ Analysis complete!")
    print("="*60 + "\n")


def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python cli.py analyze")
        sys.exit(1)

    command = sys.argv[1]

    if command == "analyze":
        analyze_request()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: analyze")
        sys.exit(1)


if __name__ == "__main__":
    main()
