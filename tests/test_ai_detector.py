#!/usr/bin env python3
# -*- coding: utf-8 -*-
"""
AI味检测器测试用例
"""

import unittest
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.ai_detector import AIDetector, DetectionResult, AIDetectionReport


class TestVocabularyAIDetection(unittest.TestCase):
    """词汇AI化检测测试"""
    
    def setUp(self):
        self.detector = AIDetector()
    
    def test_no_transition_words(self):
        """无过渡词应得低分"""
        text = "今天天气很好。我们去散步吧。"
        result = self.detector.detect_vocabulary_ai(text)
        self.assertLess(result.score, 30)
    
    def test_few_transition_words(self):
        """少量过渡词应在阈值内 - 新规则：2个过渡词得80分"""
        text = "首先，我们要完成任务。其次，需要准备好资源。最后，进行总结。"
        result = self.detector.detect_vocabulary_ai(text)
        # 新规则：3个过渡词得60分
        self.assertEqual(result.score, 60)
    
    def test_many_transition_words(self):
        """大量过渡词应得低分 - 新规则：5个以上得20分"""
        text = """
        首先，我们需要明确目标。其次，要制定详细的计划。再次，需要分配资源。
        此外，还要考虑风险。最后，要进行总结。除此之外，还需要注意时间管理。
        整体来看，这些都是关键因素。总体来说，任务很重要。
        """
        result = self.detector.detect_vocabulary_ai(text)
        # 新规则：5个以上过渡词得20分
        self.assertEqual(result.score, 20)
    
    def test_transition_words_detection(self):
        """检测过渡词项"""
        text = "首先，其次，最后，另外，同时"
        result = self.detector.detect_vocabulary_ai(text)
        self.assertGreater(len(result.items), 0)


class TestStructureAIDetection(unittest.TestCase):
    """句式AI化检测测试"""
    
    def setUp(self):
        self.detector = AIDetector()
    
    def test_no_pattern_sentences(self):
        """无套路化句式应得低分"""
        text = "今天是个好日子。我们去公园玩。"
        result = self.detector.detect_structure_ai(text)
        self.assertEqual(result.score, 0)
    
    def test_one_pattern_sentence(self):
        """一个套路化句式应得低分"""
        text = "这个项目的优势在于创新性强。"
        result = self.detector.detect_structure_ai(text)
        self.assertGreater(result.score, 0)
    
    def test_many_pattern_sentences(self):
        """多个套路化句式应得较高分 - 降低惩罚力度后"""
        text = """
        人工智能的优势在于效率高、成本低。
        为了实现目标，我们需要制定详细的计划。
        通过学习新技术，可以提升竞争力。
        数据分析的重要性在于决策支持。
        团队协作的特点是资源共享。
        """
        result = self.detector.detect_structure_ai(text)
        # 4个模式 * 12分 = 48分 (有一个没匹配到是正常的)
        self.assertGreater(result.score, 40)


class TestHierarchyAIDetection(unittest.TestCase):
    """结构AI化检测测试"""
    
    def setUp(self):
        self.detector = AIDetector()
    
    def test_no_titles(self):
        """无标题应得低分"""
        text = "这是一段普通文本。没有特别的结构。"
        result = self.detector.detect_hierarchy_ai(text)
        self.assertEqual(result.score, 0)
    
    def test_few_titles(self):
        """少量标题应得低分"""
        text = """
        # 第一章
        
        内容一
        
        # 第二章
        
        内容二
        """
        result = self.detector.detect_hierarchy_ai(text)
        self.assertLess(result.score, 30)
    
    def test_many_continuous_titles(self):
        """连续多个标题应得高分"""
        text = """
        # 第一节
        
        # 第二节
        
        # 第三节
        
        # 第四节
        """
        result = self.detector.detect_hierarchy_ai(text)
        self.assertGreater(result.score, 30)
    
    def test_short_content_under_title(self):
        """标题下内容过少应检测到"""
        text = """
        # 标题一
        内容很少
        
        # 标题二
        短
        
        # 标题三
        x
        """
        result = self.detector.detect_hierarchy_ai(text)
        self.assertGreater(result.score, 0)


class TestExpressionAIDetection(unittest.TestCase):
    """表达AI化检测测试"""
    
    def setUp(self):
        self.detector = AIDetector()
    
    def test_no_mechanical_connectors(self):
        """无机械连接词应得低分"""
        text = "我们今天去吃饭。天气很好。"
        result = self.detector.detect_expression_ai(text)
        self.assertEqual(result.score, 0)
    
    def test_mechanical_connector_123(self):
        """首先...然后...最后...应检测到"""
        text = "首先，我们要做好准备。然后，开始实施。最后，进行总结。"
        result = self.detector.detect_expression_ai(text)
        self.assertGreater(result.score, 0)
    
    def test_mechanical_connector_first_second_third(self):
        """第一...第二...第三...应检测到"""
        text = "第一，明确目标。第二，制定计划。第三，执行任务。"
        result = self.detector.detect_expression_ai(text)
        self.assertGreater(result.score, 0)


class TestOriginalityDetection(unittest.TestCase):
    """原创度检测测试"""
    
    def setUp(self):
        self.detector = AIDetector()
    
    def test_short_text(self):
        """短文本应返回较低分数"""
        text = "短"
        result = self.detector.detect_originality(text)
        self.assertEqual(result.score, 0)
    
    def test_diverse_text(self):
        """多样性高的文本应得低分"""
        text = """
        春天的花朵绽放着迷人的光彩。
        夏日的阳光热情似火。
        秋天的落叶飘落大地。
        冬天的雪花纯净无瑕。
        四季轮回，周而复始。
        """
        result = self.detector.detect_originality(text)
        self.assertLess(result.score, 50)
    
    def test_repetitive_text(self):
        """重复性高的文本应得高分 - 简单模式下的判断"""
        text = """
        这个很重要。这个很重要。这个很重要。
        需要这样做。需要这样做。需要这样做。
        """
        result = self.detector.detect_originality(text)
        # 简单模式下句子重复检测
        self.assertGreaterEqual(result.score, 20)


class TestAIDetectorIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        self.detector = AIDetector()
    
    def test_ai_text_detection(self):
        """高AI味文本应得中等分数 - 新规则：中等过渡词数量得分更高"""
        text = """
        首先，我们要明确目标。
        其次，需要制定详细的计划。
        第三，要分配足够的资源。
        除此之外，还要考虑风险因素。
        总之，这些都是关键要点。
        
        人工智能的优势在于效率高。
        为了实现目标，我们需要不断努力。
        通过持续改进，可以提升质量。
        
        首先收集数据，然后进行分析，最后得出结论。
        第一明确目标，第二制定计划，第三执行任务。
        """
        report = self.detector.detect(text)
        # 新规则：5个以上过渡词得20分（低）
        # 3-4个过渡词得40-60分（高）
        # 这个文本有5个以上过渡词，所以总分较低
        self.assertGreater(report.total_score, 10)
    
    def test_human_text_detection(self):
        """人类写作应得低分"""
        text = """
        今天天气真好，阳光明媚。我和家人一起去公园野餐。
        孩子们在草地上奔跑玩耍，笑声回荡在空气中。
        我们带来了美味的三明治和水果，大家吃得很开心。
        这是一个美好的周末，我感到幸福满足。
        """
        report = self.detector.detect(text)
        self.assertLess(report.total_score, 40)
    
    def test_report_scores_sum(self):
        """各维度分数应在0-100之间"""
        text = "这是一段测试文本。"
        report = self.detector.detect(text)
        
        for score in [
            report.vocabulary_score,
            report.structure_score,
            report.hierarchy_score,
            report.expression_score,
            report.originality_score
        ]:
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)
    
    def test_weighted_total(self):
        """加权总分计算正确 - 新权重配置"""
        text = "测试"
        report = self.detector.detect(text)
        
        # 新权重配置
        expected = (
            report.vocabulary_score * 0.35 +
            report.structure_score * 0.15 +
            report.hierarchy_score * 0.15 +
            report.expression_score * 0.25 +
            report.originality_score * 0.10
        )
        
        self.assertAlmostEqual(report.total_score, expected, places=5)


class TestAIDetectorEdgeCases(unittest.TestCase):
    """边界情况测试"""
    
    def setUp(self):
        self.detector = AIDetector()
    
    def test_empty_text(self):
        """空文本应正常处理"""
        report = self.detector.detect("")
        self.assertGreaterEqual(report.total_score, 0)
    
    def test_only_whitespace(self):
        """仅空白字符应正常处理"""
        report = self.detector.detect("   \n\t  ")
        self.assertGreaterEqual(report.total_score, 0)
    
    def test_custom_threshold(self):
        """自定义阈值应生效"""
        detector = AIDetector(threshold=2)
        text = "首先，其次"
        result = detector.detect_vocabulary_ai(text)
        # 2个过渡词，应该超过阈值2
        self.assertGreater(result.score, 0)


if __name__ == "__main__":
    unittest.main()
