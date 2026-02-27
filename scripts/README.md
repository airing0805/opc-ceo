# AI味检测器

基于内容发布规范中的验证检查清单实现的自动化AI味检测脚本。

## 安装依赖

```bash
pip install jieba
```

## 使用方法

### 命令行

```bash
# 检测文本
python scripts/ai_detector.py --text "要检测的文本..."

# 检测文件
python scripts/ai_detector.py --file article.md

# 详细输出
python scripts/ai_detector.py --file article.md --verbose

# JSON格式输出
python scripts/ai_detector.py --text "..." --json

# 自定义过渡词阈值
python scripts/ai_detector.py --text "..." --threshold 3
```

### Python API

```python
from scripts.ai_detector import AIDetector

detector = AIDetector()
report = detector.detect("要检测的文本...")

print(f"总体AI味: {report.total_score}/100")
print(f"词汇AI化: {report.vocabulary_score}/100")
print(f"句式AI化: {report.structure_score}/100")
print(f"结构AI化: {report.hierarchy_score}/100")
print(f"表达AI化: {report.expression_score}/100")
print(f"内容原创度: {report.originality_score}/100")
```

## 检测维度

| 维度 | 权重 | 说明 |
|------|------|------|
| 词汇AI化 | 25% | 过渡词出现频率（阈值5个） |
| 句式AI化 | 25% | 套路化句式检测 |
| 结构AI化 | 20% | 过度层级化检测 |
| 表达AI化 | 20% | 机械连接词检测 |
| 内容原创度 | 10% | 语义重复度 |

## 检测规则

### 1. 词汇AI化
- 检测过渡词黑名单： 首先、其次、最后、总之、需要注意的是、值得注意的是、总的来说、整体来看、除此之外、另外
- 阈值：过渡词数量<=5个

### 2. 句式AI化
- 检测套路化句式：
  - "xxx的优势在于"
  - "为了xxx，我们需要"
  - "通过xxx，可以实现"

### 3. 结构AI化
- 检测连续3个以上同级标题
- 检测标题下内容过少

### 4. 表达AI化
- 检测机械连接词：
  - "首先...然后...最后..."
  - "第一...第二...第三..."

### 5. 原创度
- 使用jieba分词+集合比较（需要安装jieba）

## 运行测试

```bash
# 安装测试依赖
pip install pytest

# 运行所有测试
python -m pytest tests/test_ai_detector.py -v

# 运行演示
python scripts/demo_ai_detector.py
```

## 输出说明

- **总分 >= 60**: 高AI味，建议修改
- **总分 40-60**: 中AI味，可适当优化
- **总分 < 40**: 低AI味，较为自然
