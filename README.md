# 虚拟用户调研研究 (Virtual Users Survey Research)

> 用LLM构建虚拟用户替代传统问卷调研

**当前版本**: v3 (聚焦跨问题一致性)
**目标会议**: KDD 2026

---

## 项目结构

```
virtual-users/
├── README.md                    # 本文件
│
├── current/                     # 🚧 当前工作版本 (v3)
│   ├── README.md               # v3概述
│   ├── P1-问题定义.md          # (待创建)
│   ├── P2-差异化定位.md        # (待创建)
│   ├── P3-方法设计.md          # (待创建)
│   ├── P4-实验设计.md          # (待创建)
│   └── paper/                  # 论文草稿
│
├── versions/                    # 历史版本
│   ├── v1/                     # 第一版 (已完成)
│   │   ├── docs/               # P1-P11文档
│   │   └── papers/             # 论文PDF
│   │
│   └── v2/                     # 第二版 (KDD增强)
│       ├── docs/               # 设计文档
│       ├── papers/             # 论文PDF
│       └── plan/               # 迭代计划
│
├── literature/                  # 文献研究 (共享)
│   └── P2-文献清单.md          # 35+篇核心文献
│
├── code/                        # 代码实现
│   ├── README.md               # 代码说明
│   ├── models/                 # Persona生成
│   ├── data/                   # 数据加载
│   ├── evaluation/             # 评估指标
│   ├── baselines/              # 基线方法
│   └── experiments/            # 实验脚本 (待创建)
│
└── archive/                     # 归档文件
    └── kdd-paper/              # 旧版KDD论文
```

---

## 版本演进

| 版本 | 状态 | 核心创新 | 目标 |
|------|------|---------|------|
| **v1** | ✅ 完成 | Persona + RAG + 评估框架 | 完整流程 |
| **v2** | ✅ 完成 | 四模块架构 + 大规模实验 | KDD增强 |
| **v3** | 🚧 进行中 | **跨问题态度一致性** | 聚焦创新 |

---

## v3 核心洞察

> **"分布匹配 ≠ 行为真实。一个可靠的虚拟用户不仅需要匹配群体分布，还需要在个体层面保持态度一致性。"**

### 与现有工作差异

| 维度 | 现有方法 | 我们 |
|------|---------|------|
| 核心目标 | 分布匹配 (KL散度) | **态度一致性 (ACS)** |
| 一致性机制 | 隐式/无 | **显式约束解码** |
| 评估指标 | 分布层面 | **跨问题层面** |

### 核心贡献

1. **CQCB** - Cross-Question Consistency Benchmark
2. **ACS** - Attitude Consistency Score (新指标)
3. **ConsistAgent** - 一致性约束的虚拟用户生成方法

---

## 快速开始

### 数据集
- **ANES 2020**: 政治态度调研 (https://electionstudies.org/)
- **GSS**: 社会态度调研 (https://gss.norc.org/)

### 运行实验
```bash
cd code
pip install -r requirements.txt  # 待创建
python experiments/run_experiment.py --config config/default.yaml
```

---

## 关键文献

详见 [literature/P2-文献清单.md](literature/P2-文献清单.md)

核心参考：
- LLM-S³ (arXiv 2024): 分布匹配基准
- Polypersona (arXiv 2025): 人格条件化
- Abdulhai et al. (NeurIPS 2025): 对话一致性
- AlignSurvey (arXiv 2025): 偏好对齐基准

---

## 时间线

| 阶段 | 任务 | 状态 |
|------|------|------|
| Week 1 | 代码补全 + 基线实验 | 🔲 |
| Week 2 | ConsistAgent实现 + 实验 | 🔲 |
| Week 3 | 论文更新 + 投稿准备 | 🔲 |

---

**创建日期**: 2026-02-15
**最后更新**: 2026-02-23
