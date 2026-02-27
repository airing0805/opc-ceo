# -*- coding: utf-8 -*-
"""AI Detection Accuracy Test Script - Detailed Report"""

import sys
import json
sys.path.insert(0, 'E:/workspaces_2026_python/OPC-CEO/scripts')
from ai_detector import AIDetector

detector = AIDetector()

print("=" * 70)
print("AI Detection Accuracy Test Report")
print("=" * 70)

# Test 1: High AI Flavor Sample
print("\n[Test 1] High AI Flavor Sample")
print("-" * 50)
text1 = "首先，我们要了解AI的基本概念。其次，AI在各个领域都有广泛应用。最后，AI的发展前景非常广阔。总之，掌握AI技术对我们的未来至关重要。"
report1 = detector.detect(text1)
result1 = report1.to_dict()
print(f"Text: {text1}")
print(f"\nTotal Score: {result1['total_score']}")
print(f"Expected: >= 60 (High AI Flavor)")
print(f"Status: {'PASS' if result1['total_score'] >= 60 else 'FAIL'}")
print("\nDimension Scores:")
for dim, score in result1['scores'].items():
    print(f"  {dim}: {score}")
print("\nDetection Details:")
for detail in result1['details']:
    print(f"  [{detail['dimension']}] {detail['details']}")
    if detail['items']:
        print(f"    Items: {detail['items']}")

# Analysis
print("\n>>> Analysis for Test 1:")
print(f"  - Detected transition words: {result1['details'][0]['items']}")
print(f"  - Vocabulary score: {result1['details'][0]['score']} -> contributes {result1['details'][0]['score'] * 0.35:.1f} to total")
print(f"  - Expression score: {result1['details'][3]['score']} -> contributes {result1['details'][3]['score'] * 0.25:.1f} to total")
print(f"  - Issue: Missing '然后' prevents mechanical connector detection")

# Test 2: Low AI Flavor Sample
print("\n" + "=" * 70)
print("\n[Test 2] Low AI Flavor Sample")
print("-" * 50)
text2 = "今天天气真好。我约了几个朋友去公园野餐。我们带了水果、三明治和饮料。大家坐在草地上聊天，非常开心。"
report2 = detector.detect(text2)
result2 = report2.to_dict()
print(f"Text: {text2}")
print(f"\nTotal Score: {result2['total_score']}")
print(f"Expected: < 30 (Low AI Flavor)")
print(f"Status: {'PASS' if result2['total_score'] < 30 else 'FAIL'}")
print("\nDimension Scores:")
for dim, score in result2['scores'].items():
    print(f"  {dim}: {score}")

# Test 3: Production Content Sample (TK-006)
print("\n" + "=" * 70)
print("\n[Test 3] Production Content Sample (TK-006)")
print("-" * 50)

# Read the content file
with open("E:/workspaces_2026_python/OPC-CEO/docs/内容/科技篇/TK-006-用AI做内容营销.md", "r", encoding="utf-8") as f:
    text3 = f.read()

# Remove markdown metadata
import re
text3_clean = re.sub(r'^>.*$', '', text3, flags=re.MULTILINE)
text3_clean = re.sub(r'^---.*$', '', text3_clean, flags=re.MULTILINE)

# Get first 2000 chars for testing
text3_sample = text3_clean[:2000]

report3 = detector.detect(text3_sample)
result3 = report3.to_dict()
print(f"Content: First 2000 chars of TK-006")
print(f"\nTotal Score: {result3['total_score']}")
print(f"Expected: < 40 (Human-edited AI content)")
print(f"Status: {'PASS' if result3['total_score'] < 40 else 'FAIL'}")
print("\nDimension Scores:")
for dim, score in result3['scores'].items():
    print(f"  {dim}: {score}")
print("\nDetection Details:")
for detail in result3['details']:
    print(f"  [{detail['dimension']}] {detail['details']}")
    if detail['items']:
        print(f"    Items: {detail['items'][:5]}")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
test1_pass = result1['total_score'] >= 60
test2_pass = result2['total_score'] < 30
test3_pass = result3['total_score'] < 40
print(f"Test 1 (High AI >=60): {'PASS' if test1_pass else 'FAIL'} - Score: {result1['total_score']}")
print(f"Test 2 (Low AI <30):  {'PASS' if test2_pass else 'FAIL'} - Score: {result2['total_score']}")
print(f"Test 3 (Production <40): {'PASS' if test3_pass else 'FAIL'} - Score: {result3['total_score']}")
print(f"\nOverall: {'ALL TESTS PASSED' if (test1_pass and test2_pass and test3_pass) else 'SOME TESTS FAILED'}")

# Improvement suggestions
print("\n" + "=" * 70)
print("IMPROVEMENT SUGGESTIONS")
print("=" * 70)
print("""
Issue 1: High AI flavor sample (Test 1) scored only 16 points
Root cause:
  - The text has 4 transition words (首先,其次,最后,总之) -> vocabulary score 40
  - But missing "然后" so mechanical connector "首先...然后...最后" not matched
  - Expression score: 0 (should detect sequential transition words)

Suggested fix:
  - Add new pattern to detect "首先...其次...最后/总之" sequence
  - Or increase vocabulary weight contribution

Current detection:
  - Vocabulary (35%): 40 * 0.35 = 14
  - Expression (25%): 0 * 0.25 = 0
  - Originality (10%): 20 * 0.10 = 2
  - Total = 16
""")
