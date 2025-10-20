"""
Quick test script to verify AI integration with minimal token usage
"""

import os
from pathlib import Path
from src.crengine.ai_reviewer import review_file

# Create a simple test file
test_code = '''
def calculate_total(items):
    total = 0
    for item in items:
        total = total + item['price']
    return total

def get_user_by_id(user_id):
    query = "SELECT * FROM users WHERE id = " + str(user_id)
    return db.execute(query)
'''

# Write test file
test_file = Path("test_sample.py")
test_file.write_text(test_code)

print("Testing AI integration with OpenAI GPT-4o-mini...")
print("=" * 60)

# Get API key from environment
api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    print("❌ Error: OPENAI_API_KEY not found in environment variables")
    print("\nTo test, run:")
    print('  export OPENAI_API_KEY="sk-your-key-here"')
    print('  python test_ai_integration.py')
    exit(1)

try:
    # Run AI review on test file
    findings = review_file(
        file_path=test_file,
        repo_root=Path("."),
        ai_provider="openai",
        api_key=api_key,
        language="python"
    )

    print(f"✅ Success! Found {len(findings)} issues\n")

    # Display findings
    for i, finding in enumerate(findings, 1):
        print(f"\n{i}. {finding.title}")
        print(f"   Severity: {finding.severity}")
        print(f"   Category: {finding.category}")
        print(f"   Lines: {finding.line_start}-{finding.line_end}")
        print(f"   Description: {finding.description[:100]}...")
        print(f"   Confidence: {finding.confidence:.0%}")

    print("\n" + "=" * 60)
    print("✅ AI integration test passed!")

except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

finally:
    # Cleanup
    if test_file.exists():
        test_file.unlink()
