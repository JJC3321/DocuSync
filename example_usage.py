"""Example usage of the Live Document Editor (Python API).

Note: For MCP usage in Cursor, use the MCP tools directly.
This example shows programmatic usage of the orchestrator.
"""
from src.orchestrator import MCPOrchestrator
from src.git_handler import GitHandler

# Example Git diff content
example_diff = """
diff --git a/src/example.py b/src/example.py
index 1234567..abcdefg 100644
--- a/src/example.py
+++ b/src/example.py
@@ -1,3 +1,5 @@
 def hello_world():
-    print("Hello")
+    """Print a greeting message."""
+    print("Hello, World!")
+    return True
"""


def main():
    """Example usage."""
    print("Initializing Live Document Editor...")
    
    # Initialize orchestrator
    orchestrator = MCPOrchestrator()
    
    # Process code changes
    print("\nProcessing code changes...")
    update = orchestrator.process_code_changes(example_diff)
    
    print(f"\nDocumentation generated:")
    print(f"File: {update.file_path}")
    print(f"Quality Score: {update.evaluation_score:.2f}")
    print(f"Ready to Commit: {update.ready_to_commit}")
    print(f"\nContent Preview:\n{update.content[:500]}...")
    
    # Initialize Git handler
    git_handler = GitHandler()
    
    # Commit documentation (optional)
    if update.ready_to_commit:
        print("\nCommitting documentation...")
        success = git_handler.commit_documentation(
            update.file_path,
            update.content,
            "docs: Auto-generated documentation update"
        )
        if success:
            print("Documentation committed successfully!")
        else:
            print("Failed to commit documentation")
    
    # Cleanup
    orchestrator.cleanup()
    print("\nDone!")


if __name__ == "__main__":
    main()

