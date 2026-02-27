# -*- coding: utf-8 -*-
"""AI Detection Accuracy Test Script"""

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
print(f"Total Score: {result1['total_score']}")
print(f"Expected: >= 60 (High AI Flavor)")
print(f"Status: {'PASS' if result1['total_score'] >= 60 else 'FAIL'}")
print(f"Details: {result1['scores']}")

# Test 2: Low AI Flavor Sample
print("\n[Test 2] Low AI Flavor Sample")
print("-" * 50)
text2 = "今天天气真好。我约了几个朋友去公园野餐。我们带了水果、三明治和饮料。大家坐在草地上聊天，非常开心。"
report2 = detector.detect(text2)
result2 = report2.to_dict()
print(f"Total Score: {result2['total_score']}")
print(f"Expected: < 30 (Low AI Flavor)")
print(f"Status: {'PASS' if result2['total_score'] < 30 else 'FAIL'}")
print(f"Details: {result2['scores']}")

# Test 3: Production Content Sample (TK-006)
print("\n[Test 3] Production Content Sample (TK-006)")
print("-" * 50)
# Read the content file
with open("E:/workspaces_2026_python/OPC-CEO/docs/内容/科技篇/TK-006-用AI做内容营销.md", "r", encoding="utf-8") as f:
    text3 = f.read()

# Remove markdown metadata for cleaner test
import re
text3_clean = re.sub(r'^>.*$', '', text3, flags=re.MULTILINE)
text3_clean = re.sub(r'^---.*$', '', text3_clean, flags=re.MULTILINE)
text3_clean = re.sub(r'^#+\s*', '', text3_clean)

report3 = detector.detect(text3_clean)
result3 = report3.to_dict()
print(f"Total Score: {result3['total_score']}")
print(f"Expected: < 40 (Human-edited AI content)")
print(f"Status: {'PASS' if result3['total_score'] < 40 else 'FAIL'}")
print(f"Details: {result3['scores']}")

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
