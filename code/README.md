# VirtualSurvey: LLM-Based Virtual User Survey System

基于大语言模型的虚拟用户问卷调研系统

---

## 📖 项目简介

VirtualSurvey 是一个端到端的虚拟用户调研框架，利用大语言模型（LLM）生成符合真实用户分布的问卷响应。系统通过 Persona 生成、检索增强知识注入、响应生成和可靠性评估四个模块，实现高质量、低成本的自动化调研。

**核心特性**:
- 🎭 **Persona 生成**: 基于人口统计分布生成多样化虚拟用户画像
- 🔍 **知识检索**: RAG 增强领域知识注入，提升响应真实性
- 📊 **多类型支持**: 支持单选、多选、李克特量表、开放题等多种问题类型
- ✅ **可靠性评估**: KL 散度、Cohen's Kappa、统计显著性检验等多维评估

---

## 🚀 快速开始

### 环境要求

- Python 3.9+
- 依赖库: numpy, scipy, scikit-learn, pyyaml

### 安装

```bash
cd code
pip install -r requirements.txt
```

### 基本使用

#### 1. 生成 Persona 池

```python
from models.persona import PersonaGenerator, PersonaPool

# 初始化生成器
generator = PersonaGenerator(seed=42)

# 生成 100 个 Persona
personas = generator.generate_personas(100)

# 创建 Persona 池
pool = PersonaPool(personas)

# 保存
pool.save("data/cache/persona_pool.json")
```

#### 2. 评估虚拟用户响应

```python
from eval import Evaluator, print_evaluation_results

# 真实用户响应
real_responses = [
    {'q1': 'A', 'q2': 5},
    {'q1': 'A', 'q2': 4},
    {'q1': 'B', 'q2': 5},
]

# 虚拟用户响应
virtual_responses = [
    {'q1': 'A', 'q2': 4},
    {'q1': 'A', 'q2': 5},
    {'q1': 'B', 'q2': 5},
]

# 问题定义
questions = [
    {'id': 'q1', 'type': 'single_choice'},
    {'id': 'q2', 'type': 'likert_scale'},
]

# 评估
evaluator = Evaluator()
results = evaluator.evaluate_all(real_responses, virtual_responses, questions)

# 打印结果
print_evaluation_results(results)
```

#### 3. 完整实验流程

```bash
# 运行主实验
python experiments/run_experiment.py --config config/default.yaml

# 运行消融实验
python experiments/run_ablation.py --config config/ablation.yaml
```

---

## 📁 项目结构

```
code/
├── README.md                 # 本文档
├── requirements.txt          # 依赖列表
│
├── models/                   # 模型模块
│   └── persona.py           # Persona 生成器
│
├── data/                     # 数据模块
│   └── loader.py            # 数据加载器
│
├── evaluation/               # 评估模块
│   └── metrics.py           # 评估指标
│
├── baselines/                # 基线方法
│   └── base.py              # 基线基类
│
├── utils/                    # 工具模块
│   └── config.py            # 配置管理
│
├── eval.py                   # 评估入口
│
├── experiments/              # 实验脚本
│   ├── run_experiment.py    # 主实验
│   └── run_ablation.py      # 消融实验
│
├── config/                   # 配置文件
│   └── default.yaml         # 默认配置
│
└── results/                  # 实验结果（自动生成）
```

---

## 🧪 实验配置

### 配置文件示例 (config/default.yaml)

```yaml
name: virtual_survey_experiment
output_dir: results
log_dir: logs
n_repeats: 5

model:
  name: glm-5
  temperature: 0.7
  max_tokens: 2048

data:
  name: anes_2020
  data_dir: data/raw
  sample_size: null

persona:
  pool_size: 300
  diversity_weight: 0.5

retrieval:
  enabled: true
  top_k: 5
  rerank: true

evaluation:
  metrics:
    - kl_divergence
    - js_distance
    - accuracy
    - cohen_kappa
  n_bootstrap: 1000
  significance_level: 0.05
```

### 运行参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--config` | `config/default.yaml` | 配置文件路径 |
| `--dataset` | `anes_2020` | 数据集名称 |
| `--n_personas` | `300` | Persona 池大小 |
| `--temperature` | `0.7` | LLM 温度参数 |
| `--n_repeats` | `5` | 重复次数 |

---

## 📊 评估指标

### 分布相似度指标

| 指标 | 公式 | 目标值 | 说明 |
|------|------|--------|------|
| **KL Divergence** | KL(P \|\| Q) = Σ P(x) log(P(x)/Q(x)) | < 0.5 | 越小越好 |
| **JS Distance** | JS = √[(1/2)KL(P \|\| M) + (1/2)KL(Q \|\| M)] | < 0.3 | [0,1]，越小越好 |
| **Wasserstein** | W₁(P, Q) = ∫ \|CDF_P - CDF_Q\| dx | < 0.3 | 连续变量分布距离 |

### 准确性指标

| 指标 | 说明 | 目标值 |
|------|------|--------|
| **Mode Match** | 众数匹配准确率 | 100% |
| **Top-3 Accuracy** | 前三选项重叠率 | > 80% |
| **Jaccard Similarity** | 多选题集合相似度 | > 0.7 |

### 一致性指标

| 指标 | 说明 | 目标值 |
|------|------|--------|
| **Cohen's Kappa** | Persona-Response 一致性 | > 0.7 |
| **Self-consistency** | 重复测试稳定性 | > 0.8 |

### 统计检验

- **Chi-Square Test**: 分布差异显著性检验
- **T-Test**: 均值差异检验（含 Cohen's d 效应量）
- **KS Test**: 分布形状差异检验

---

## 🔧 模块详解

### 1. Persona 生成器 (models/persona.py)

**功能**: 生成多样化、一致的虚拟用户画像

**Persona 结构**:
```python
Persona:
  - id: 唯一标识
  - demographics: 人口统计（年龄、性别、教育、收入等）
  - psychographics: 心理特征（性格、风险偏好等）
  - values: 价值观（自由、平等、创新等）
  - decision_style: 决策风格（理性、感性、直觉等）
  - knowledge_domains: 知识领域
  - confidence_threshold: 置信度阈值
```

**使用示例**:
```python
# 从人口统计分布生成
distributions = {
    'age_group': {'18-29': 0.2, '30-44': 0.3, '45-59': 0.3, '60+': 0.2},
    'gender': {'Male': 0.48, 'Female': 0.50, 'Other': 0.02}
}
personas = generator.generate_personas(100, demographic_distributions=distributions)

# 生成提示词
prompt = persona.to_prompt(format_type="detailed")
```

### 2. 评估器 (eval.py)

**功能**: 多维度评估虚拟用户响应质量

**支持的评估场景**:
- 单选题: 众数匹配、Top-K 准确率、分布相似度
- 多选题: Jaccard 相似度、选项覆盖率
- 李克特量表: 均值误差、分布距离、统计检验
- 开放题: 文本相似度（待实现）

**使用示例**:
```python
# 单题评估
metrics = evaluator.evaluate_single_question(
    real_answers=['A', 'A', 'B', 'A', 'B'],
    virtual_answers=['A', 'B', 'B', 'A', 'B'],
    question_type='single_choice'
)

# 全问卷评估
results = evaluator.evaluate_all(real_responses, virtual_responses, questions)
```

### 3. 配置管理 (utils/config.py)

**功能**: 统一管理实验配置

**配置层级**:
```python
ExperimentConfig:
  - model: ModelConfig       # LLM 模型配置
  - data: DataConfig         # 数据集配置
  - persona: PersonaConfig   # Persona 生成配置
  - retrieval: RetrievalConfig # 检索配置
  - evaluation: EvaluationConfig # 评估配置
```

**使用示例**:
```python
from utils.config import ExperimentConfig

# 从 YAML 加载
config = ExperimentConfig.from_yaml("config/default.yaml")

# 修改配置
config.persona.pool_size = 500
config.evaluation.significance_level = 0.01

# 保存配置
config.save_yaml("config/custom.yaml")
```

---

## 📈 预期性能

基于 P7 实验方案的设计目标：

| 方法 | KL Divergence | Accuracy | Cohen's Kappa |
|------|---------------|----------|---------------|
| Random | 1.50 | 0.25 | 0.00 |
| LLM-Direct | 0.80 | 0.55 | 0.45 |
| LLM-Prompt | 0.65 | 0.62 | 0.58 |
| **VirtualSurvey (Ours)** | **0.42** | **0.72** | **0.71** |

**改进幅度**:
- vs LLM-Prompt: KL 降低 35%, 准确率提升 16%
- vs Random: KL 降低 72%, 准确率提升 188%

---

## 🛠️ 开发指南

### 添加新的基线方法

```python
# baselines/custom_baseline.py
from baselines.base import BaseBaseline

class CustomBaseline(BaseBaseline):
    def __init__(self, config):
        super().__init__(config)
        self.name = "Custom Baseline"
    
    def generate_response(self, question, persona=None):
        # 实现你的方法
        return response
```

### 添加新的评估指标

```python
# evaluation/custom_metrics.py
def custom_metric(real, pred):
    """
    自定义评估指标
    
    Args:
        real: 真实标签
        pred: 预测标签
    
    Returns:
        float: 指标值
    """
    # 实现你的指标
    return score
```

---

## 📚 参考文献

1. **Agent4Rec** (SIGIR 2024): LLM 用户模拟框架
2. **LLM-S³** (arXiv 2024): 合成调研基准
3. **AlignSurvey** (arXiv 2024): 调研对齐数据集
4. **RAG** (NeurIPS 2020): 检索增强生成

详见: `../P2-文献清单.md`

---

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目仅供学术研究使用。

---

## 📧 联系方式

- 项目主页: [GitHub Repository]
- 问题反馈: [Issues]
- 邮箱: [Research Email]

---

**最后更新**: 2026-02-17
**版本**: v1.0
