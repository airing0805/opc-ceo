#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 味自动检测脚本

检测维度：
- 词汇AI化：过渡词出现频率
- 句式AI化：套路化句式检测
- 结构AI化：过度层级化检测
- 表达AI化：机械连接词检测
- 内容原创度：语义重复度
"""

import re
import argparse
import sys
from dataclasses import dataclass
from typing import List, Dict, Tuple
from collections import Counter

# 可选依赖：jieba 用于中文分词
try:
    import jieba
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False


@dataclass
class DetectionResult:
    """检测结果"""
    dimension: str
    score: float  # 0-100, 分数越高AI味越重
    details: str
    items: List[str]


@dataclass
class AIDetectionReport:
    """AI检测报告"""
    total_score: float  # 总AI味分数
    vocabulary_score: float    # 词汇AI化 25%
    structure_score: float    # 句式AI化 25%
    hierarchy_score: float     # 结构AI化 20%
    expression_score: float    # 表达AI化 20%
    originality_score: float   # 原创度 10%
    results: List[DetectionResult]
    
    def to_dict(self) -> Dict:
        return {
            "total_score": round(self.total_score, 2),
            "scores": {
                "词汇AI化": round(self.vocabulary_score, 2),
                "句式AI化": round(self.structure_score, 2),
                "结构AI化": round(self.hierarchy_score, 2),
                "表达AI化": round(self.expression_score, 2),
                "内容原创度": round(self.originality_score, 2),
            },
            "weights": {
                "词汇AI化": "20%",
                "句式AI化": "10%",
                "结构AI化": "10%",
                "表达AI化": "50%",
                "内容原创度": "10%",
            },
            "details": [
                {
                    "dimension": r.dimension,
                    "score": round(r.score, 2),
                    "details": r.details,
                    "items": r.items
                }
                for r in self.results
            ]
        }


class AIDetector:
    """AI味检测器"""
    
    # 过渡词黑名单
    TRANSITION_WORDS = [
        "首先", "其次", "最后", "总之",
        "需要注意的是", "值得注意的是",
        "总的来说", "整体来看",
        "除此之外", "另外", "同时",
        "一方面", "另一方面", "总的来看",
        "由此可见", "总之可见",
        # 新增：结论性过渡词
        "综上所述", "总而言之", "综上",
        # 新增：强调性过渡词
        "需要指出的是", "必须说明的是", "必须指出的是",
    ]
    
    # 套路化句式模式
    PATTERN_SENTENCES = [
        (r"[\u4e00-\u9fa5]+的优势在于", "xxx的优势在于"),
        (r"为了[\u4e00-\u9fa5]+，我们需要", "为了xxx，我们需要"),
        (r"通过[\u4e00-\u9fa5]+，可以实现", "通过xxx，可以实现"),
        (r"[\u4e00-\u9fa5]+的重要性", "xxx的重要性"),
        (r"[\u4e00-\u9fa5]+的特点是", "xxx的特点是"),
        (r"[\u4e00-\u9fa5]+的关键是", "xxx的关键是"),
        (r"[\u4e00-\u9fa5]+能够", "xxx能够"),
        (r"[\u4e00-\u9fa5]+可以", "xxx可以"),
    ]
    
    # 机械连接词模式
    MECHANICAL_CONNECTORS = [
        r"首先[\s，,]+.*?然后[\s，,]+.*?最后",
        r"第一[\s，,]+.*?第二[\s，,]+.*?第三",
        r"第一[\s，,]+.*?第二[\s，,]+.*?第三[\s，,]+.*?第四",
        r"一是[\s，,]+.*?二是[\s，,]+.*?三是",
        r"一方面[\s，,]+.*?另一方面",
        # 新增：第一...第二...第三...模式
        r"第一[\u4e00-\u9fa5]{1,20}[，,\s]{0,3}第二[\u4e00-\u9fa5]{1,20}[，,\s]{0,3}第三[\u4e00-\u9fa5]{1,20}",
        # 新增：连续过渡词序列模式（首先+其次+最后/总之）
        r"首先.*?其次.*?(?:最后|总之)",
    ]
    
    # 标题模式
    TITLE_PATTERNS = [
        r"^#{1,6}\s+",  # Markdown 标题
        r"^[\u4e00-\u9fa5]{1,10}[\u3000\s]{1,5}[一二三四五六七八九十]+[\u3000\s]?",  # 中文标题编号
        r"^[\u4e00-\u9fa5]{1,10}[\.、]\s*",  # 中文点号标题
    ]
    
    def __init__(self, threshold: int = 5):
        """
        初始化检测器
        
        Args:
            threshold: 过渡词数量阈值，默认5个
        """
        self.threshold = threshold
        self._init_patterns()
    
    def _init_patterns(self):
        """编译正则表达式"""
        self._pattern_cache = {}
        for pattern, desc in self.PATTERN_SENTENCES:
            self._pattern_cache[desc] = re.compile(pattern)
        
        self._mechanical_patterns = [
            re.compile(p, re.MULTILINE | re.DOTALL) for p in self.MECHANICAL_CONNECTORS
        ]
        
        self._title_patterns = [
            re.compile(p, re.MULTILINE) for p in self.TITLE_PATTERNS
        ]
    
    def detect_vocabulary_ai(self, text: str) -> DetectionResult:
        """
        检测词汇AI化
        权重：35%
        阈值：过渡词数量
          2个过渡词得80分
          3个过渡词得60分
          4个过渡词得40分
          5个以上过渡词得20分
        """
        found_words = []
        for word in self.TRANSITION_WORDS:
            count = len(re.findall(word, text))
            if count > 0:
                found_words.append((word, count))
        
        total_count = sum(count for _, count in found_words)
        
        # 计算分数：按照新阈值规则
        if total_count <= 1:
            # 0-1个，无AI味
            score = total_count * 30  # 0分或30分
        elif total_count == 2:
            score = 80
        elif total_count == 3:
            score = 60
        elif total_count == 4:
            score = 40
        else:  # 5个及以上
            score = 20
        
        details = f"检测到过渡词 {total_count} 个"
        items = [f"{word}x{count}" for word, count in found_words]
        
        return DetectionResult(
            dimension="词汇AI化",
            score=score,
            details=details,
            items=items
        )
    
    def detect_structure_ai(self, text: str) -> DetectionResult:
        """
        检测句式AI化
        权重：15%
        检测套路化句式 - 改为累积计分方式，降低单一模式惩罚力度
        """
        found_patterns = []
        
        for desc, pattern in self._pattern_cache.items():
            matches = pattern.findall(text)
            if matches:
                found_patterns.append((desc, len(matches)))
        
        # 计算分数：累积计分方式，每个模式扣分减少
        total_patterns = sum(count for _, count in found_patterns)
        # 降低惩罚力度：从20分改为12分
        score = min(total_patterns * 12, 100)
        
        details = f"检测到套路化句式 {total_patterns} 处"
        items = [f"{desc}x{count}" for desc, count in found_patterns]
        
        return DetectionResult(
            dimension="句式AI化",
            score=score,
            details=details,
            items=items
        )
    
    def detect_hierarchy_ai(self, text: str) -> DetectionResult:
        """
        检测结构AI化
        权重：15%
        检测过度层级化
        """
        lines = text.split('\n')
        
        # 查找所有标题行
        titles = []
        for i, line in enumerate(lines):
            for pattern in self._title_patterns:
                if pattern.match(line.strip()):
                    titles.append((i, line.strip()))
                    break
        
        # 检测连续3个以上同级标题
        continuous_count = 1
        max_continuous = 1
        
        for i in range(1, len(titles)):
            prev_line_num = titles[i-1][0]
            curr_line_num = titles[i][0]
            # 如果标题行连续或间隔1行
            if curr_line_num - prev_line_num <= 2:
                continuous_count += 1
                max_continuous = max(max_continuous, continuous_count)
            else:
                continuous_count = 1
        
        # 检测标题下内容过少
        short_content_count = 0
        for i, (line_num, title) in enumerate(titles):
            # 获取标题下的内容行数
            next_title_line = titles[i+1][0] if i+1 < len(titles) else len(lines)
            content_lines = next_title_line - line_num - 1
            
            # 统计非空内容行
            non_empty = sum(1 for j in range(line_num+1, next_title_line) 
                          if lines[j].strip())
            
            if non_empty <= 1:
                short_content_count += 1
        
        # 计算分数
        hierarchy_score = 0
        if max_continuous >= 3:
            hierarchy_score += (max_continuous - 2) * 20
        hierarchy_score += short_content_count * 10
        score = min(hierarchy_score, 100)
        
        details = f"连续标题: {max_continuous}个, 短内容标题: {short_content_count}个"
        items = [f"标题行: {title[:30]}..." if len(title) > 30 else title 
                 for _, title in titles[:10]]
        
        return DetectionResult(
            dimension="结构AI化",
            score=score,
            details=details,
            items=items
        )
    
    def detect_expression_ai(self, text: str) -> DetectionResult:
        """
        检测表达AI化
        权重：25%
        检测机械连接词 + 连续过渡词序列
        """
        found_patterns = []

        # 1. 检测机械连接词
        for i, pattern in enumerate(self._mechanical_patterns):
            matches = pattern.findall(text)
            if matches:
                found_patterns.append((self.MECHANICAL_CONNECTORS[i], len(matches)))

        # 2. 连续过渡词序列检测（直接满分）
        # 检测"首先"+"其次"+"最后/总之"连续出现
        continuous_transition_pattern = re.compile(r"首先.*?其次.*?(?:最后|总之)", re.DOTALL)
        continuous_match = continuous_transition_pattern.search(text)

        # 计算分数
        mechanical_total = sum(count for _, count in found_patterns)

        if continuous_match:
            # 连续过渡词序列检测到，直接判定为高AI味（满分100分）
            # 这是因为连续使用多个过渡词是典型的人类模仿AI写作的特征
            score = 100
            details = f"检测到连续过渡词序列（首先+其次+最后/总之），直接判定为高AI味（满分）"
            items = ["连续过渡词序列x1（满分）"] + [f"机械连接{idx+1}" for idx in range(mechanical_total)]
        else:
            # 没有连续过渡词序列，使用累积计分
            # 降低惩罚力度：从25分改为15分
            score = min(mechanical_total * 15, 100)
            details = f"检测到机械连接词 {mechanical_total} 处"
            items = [f"模式{idx+1}" for idx in range(len(found_patterns))]

        return DetectionResult(
            dimension="表达AI化",
            score=score,
            details=details,
            items=items
        )
    
    def detect_originality(self, text: str) -> DetectionResult:
        """
        检测内容原创度
        权重：10%
        使用jieba分词+集合比较
        """
        if not JIEBA_AVAILABLE:
            # 如果没有jieba，使用简单字符级检测
            return self._detect_originality_simple(text)
        
        return self._detect_originality_jieba(text)
    
    def _detect_originality_jieba(self, text: str) -> DetectionResult:
        """使用jieba分词检测原创度"""
        # 分词
        words = list(jieba.cut(text))
        
        # 过滤停用词和短词
        words = [w.strip() for w in words if len(w.strip()) >= 2]
        
        if not words:
            return DetectionResult(
                dimension="内容原创度",
                score=0,
                details="内容过短，无法检测",
                items=[]
            )
        
        # 计算词频
        word_counts = Counter(words)
        total_words = len(words)
        unique_words = len(word_counts)
        
        # 计算词汇多样性（独特词/总词数）
        diversity = unique_words / total_words if total_words > 0 else 0
        
        # 检测重复词
        repeated_words = [(w, c) for w, c in word_counts.items() if c >= 2]
        
        # 计算AI味分数：重复度越高，AI味越重
        if diversity >= 0.6:
            # 词汇多样性高，AI味低
            score = (1 - diversity) * 80
        else:
            # 词汇多样性低，AI味高
            score = 50 + (0.6 - diversity) * 100
        
        score = min(max(score, 0), 100)
        
        details = f"总词数: {total_words}, 独特词: {unique_words}, 多样性: {diversity:.2f}"
        items = [f"{w}x{c}" for w, c in repeated_words[:10]]
        
        return DetectionResult(
            dimension="内容原创度",
            score=score,
            details=details,
            items=items
        )
    
    def _detect_originality_simple(self, text: str) -> DetectionResult:
        """简单字符级原创度检测"""
        # 移除空白字符
        text_clean = re.sub(r'\s+', '', text)
        
        if len(text_clean) < 10:
            return DetectionResult(
                dimension="内容原创度",
                score=0,
                details="内容过短，无法检测",
                items=[]
            )
        
        # 计算句子数
        sentences = re.split(r'[。！？\n]', text_clean)
        sentences = [s for s in sentences if len(s) >= 5]
        
        if not sentences:
            return DetectionResult(
                dimension="内容原创度",
                score=20,
                details="内容过短",
                items=[]
            )
        
        # 简单相似度：取前3句和后3句比较
        sample_size = min(3, len(sentences) // 2)
        if sample_size > 0:
            front = set(sentences[:sample_size])
            back = set(sentences[-sample_size:])
            overlap = len(front & back)
            
            # 高重复度 = AI味重
            if overlap > 0:
                score = min(overlap * 30, 80)
            else:
                score = 20
        else:
            score = 20
        
        details = f"句子数: {len(sentences)}"
        items = []
        
        return DetectionResult(
            dimension="内容原创度",
            score=score,
            details=details,
            items=items
        )
    
    def detect(self, text: str) -> AIDetectionReport:
        """
        执行完整检测
        
        Args:
            text: 待检测文本
            
        Returns:
            AIDetectionReport: 检测报告
        """
        # 执行各项检测
        vocab_result = self.detect_vocabulary_ai(text)
        struct_result = self.detect_structure_ai(text)
        hier_result = self.detect_hierarchy_ai(text)
        expr_result = self.detect_expression_ai(text)
        orig_result = self.detect_originality(text)
        
        results = [vocab_result, struct_result, hier_result, expr_result, orig_result]
        
        # 计算加权总分 - 新权重配置
        # 当检测到连续过渡词序列时，表达AI化为满分100分，总分需达到60+
        weights = {
            "vocabulary": 0.20,   # 词汇AI化 20%
            "structure": 0.10,   # 句式AI化 10%
            "hierarchy": 0.10,   # 结构AI化 10%
            "expression": 0.50,   # 表达AI化 50%（提高权重以检测AI写作特征）
            "originality": 0.10,  # 原创度 10%
        }
        
        total_score = (
            vocab_result.score * weights["vocabulary"] +
            struct_result.score * weights["structure"] +
            hier_result.score * weights["hierarchy"] +
            expr_result.score * weights["expression"] +
            orig_result.score * weights["originality"]
        )
        
        return AIDetectionReport(
            total_score=total_score,
            vocabulary_score=vocab_result.score,
            structure_score=struct_result.score,
            hierarchy_score=hier_result.score,
            expression_score=expr_result.score,
            originality_score=orig_result.score,
            results=results
        )
    
    def detect_file(self, file_path: str) -> AIDetectionReport:
        """
        检测文件内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            AIDetectionReport: 检测报告
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        return self.detect(text)


def format_report(report: AIDetectionReport, verbose: bool = False) -> str:
    """格式化检测报告"""
    lines = []
    
    # 总体评分
    level = "低"
    if report.total_score >= 60:
        level = "高"
    elif report.total_score >= 40:
        level = "中"
    
    lines.append("=" * 50)
    lines.append(f"AI味检测报告")
    lines.append("=" * 50)
    lines.append(f"总体AI味: {report.total_score:.1f}/100 ({level}AI味)")
    lines.append("")
    
    # 各维度分数
    lines.append("各维度得分:")
    lines.append(f"  词汇AI化: {report.vocabulary_score:.1f}/100 (权重35%)")
    lines.append(f"  句式AI化: {report.structure_score:.1f}/100 (权重15%)")
    lines.append(f"  结构AI化: {report.hierarchy_score:.1f}/100 (权重15%)")
    lines.append(f"  表达AI化: {report.expression_score:.1f}/100 (权重25%)")
    lines.append(f"  内容原创度: {report.originality_score:.1f}/100 (权重10%)")
    
    # 详细结果
    if verbose:
        lines.append("")
        lines.append("详细检测结果:")
        for result in report.results:
            lines.append(f"\n[{result.dimension}] 得分: {result.score:.1f}")
            lines.append(f"  说明: {result.details}")
            if result.items:
                items_str = ", ".join(result.items[:5])
                if len(result.items) > 5:
                    items_str += f" ... (+{len(result.items)-5}项)"
                lines.append(f"  项目: {items_str}")
    
    lines.append("=" * 50)
    
    return "\n".join(lines)


def detect_ai_score(text: str) -> float:
    """
    便捷函数：检测文本的AI味分数

    Args:
        text: 待检测文本

    Returns:
        float: AI味分数 (0-100)，分数越高AI味越重
    """
    detector = AIDetector()
    report = detector.detect(text)
    return report.total_score


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="AI味自动检测脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python ai_detector.py --text "这是一段测试文本..."
  python ai_detector.py --file article.md
  python ai_detector.py --file article.md --verbose
        """
    )
    
    parser.add_argument(
        "--text", "-t",
        type=str,
        help="待检测文本"
    )
    
    parser.add_argument(
        "--file", "-f",
        type=str,
        help="待检测文件路径"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细检测结果"
    )
    
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="JSON格式输出"
    )
    
    parser.add_argument(
        "--threshold", "-th",
        type=int,
        default=5,
        help="过渡词阈值 (默认5)"
    )
    
    args = parser.parse_args()
    
    # 检查输入
    if not args.text and not args.file:
        parser.print_help()
        sys.exit(1)
    
    # 获取待检测文本
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        except FileNotFoundError:
            print(f"错误: 文件不存在: {args.file}")
            sys.exit(1)
        except Exception as e:
            print(f"错误: 读取文件失败: {e}")
            sys.exit(1)
    else:
        text = args.text
    
    # 执行检测
    detector = AIDetector(threshold=args.threshold)
    report = detector.detect(text)
    
    # 输出结果
    if args.json:
        import json
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(format_report(report, verbose=args.verbose))
    
    # 返回退出码
    sys.exit(0 if report.total_score < 60 else 1)


if __name__ == "__main__":
    main()
