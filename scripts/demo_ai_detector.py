#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 味检测器 - 测试演示脚本
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.ai_detector import AIDetector, format_report


# 测试用例
TEST_CASES = [
    {
        "name": "高AI味文本",
        "text": """
        首先，我们要明确项目目标。其次，需要制定详细的计划。
        第三，要分配足够的资源。除此之外，还要考虑潜在的风险。
        
        # 第一章
        
        # 第二章
        
        # 第三章
        
        人工智能的优势在于效率高、成本低。为了实现目标，我们需要不断努力。
        通过持续改进，可以提升产品质量。数据分析的重要性在于支持决策。
        
        首先收集数据，然后进行分析，最后得出结论。
        第一明确目标，第二制定计划，第三执行任务。
        第四总结经验，第五持续改进。
        
        总体来说，这些都是关键因素。整体来看，任务很重要。
        """
    },
    {
        "name": "低AI味文本（人类写作）",
        "text": """
        今天天气真好，阳光明媚。我和家人一起去公园野餐。
        孩子们在草地上奔跑玩耍，笑声回荡在空气中。
        我们带来了美味的三明治和新鲜的水果，大家吃得很开心。
        野餐垫铺在草坪上，我们一边享受美食，一边欣赏周围的风景。
        这是一个美好的周末，我感到幸福满足。
        """
    }
]


def main():
    detector = AIDetector()
    
    for case in TEST_CASES:
        print(f"\n{'='*50}")
        print(f"测试: {case['name']}")
        print('='*50)
        
        report = detector.detect(case["text"])
        
        # 使用 Python 输出避免编码问题
        print(f"总体AI味: {report.total_score:.1f}/100")
        print(f"  词汇AI化: {report.vocabulary_score:.1f}/100 (权重25%)")
        print(f"  句式AI化: {report.structure_score:.1f}/100 (权重25%)")
        print(f"  结构AI化: {report.hierarchy_score:.1f}/100 (权重20%)")
        print(f"  表达AI化: {report.expression_score:.1f}/100 (权重20%)")
        print(f"  内容原创度: {report.originality_score:.1f}/100 (权重10%)")


if __name__ == "__main__":
    main()
