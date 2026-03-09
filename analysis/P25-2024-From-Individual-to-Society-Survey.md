# P25-2024-From-Individual-to-Society-Survey

## 基本信息

| 项目 | 内容 |
|------|------|
| **标题** | From Individual to Society: A Survey on Social Simulation Driven by Large Language Model-based Agents |
| **作者** | Xinyi Mou et al. (Fudan University) |
| **发表** | arXiv 2024.12 |
| **页数** | 35页 |
| **相关性** | ⭐⭐⭐⭐ 高相关性（综述论文，涵盖三个层次模拟） |
| **评分** | 9/10 |

---

## 核心贡献

### 三层模拟分类框架

```
Individual Simulation（个体模拟）
    ↓
Scenario Simulation（场景模拟）
    ↓
Society Simulation（社会模拟）
```

---

## 1. Individual Simulation（个体模拟）

**目标**: 模拟特定个体或人口统计群体

### 核心组件

| 组件 | 功能 |
|------|------|
| **Profile** | 人口统计、性格、价值观 |
| **Memory** | 短期/长期记忆 |
| **Planning** | 目标规划 |
| **Action** | 行为执行 |

### 评估方法

- **算法保真度**（Algorithmic Fidelity）
- 分布对齐（KL Divergence）
- 行为一致性

---

## 2. Scenario Simulation（场景模拟）

**目标**: 多Agent协作完成特定任务

### 任务分类

| 类别 | 示例 |
|------|------|
| **对话驱动** | Sotopia, Elicitron |
| **问答** | ICL-AIF, FORD, MAD |
| **游戏** | AvalonBench, AmongAgents |
| **任务驱动** | VIDS, MedAgents, AI Hospital |
| **软件开发** | ChatDev, MetaGPT |
| **其他行业** | SimuCourt, TradingGPT |

### Agent角色

**Participants（参与者）**:
- Communicators（沟通者）
- Workers（执行者）

**Directors（管理者）**:
- Planners（规划者）
- Coordinators（协调者）
- Integrators（整合者）

### 工具

- Python, SQL
- API调用
- 计算器
- 知识图谱查询

---

## 3. Society Simulation（社会模拟）

**目标**: 模拟大规模社会动态

### 核心要素

| 要素 | 描述 |
|------|------|
| **Composition** | Agent组成（人口统计分布） |
| **Network** | 社交网络结构 |
| **Social Influence** | 社会影响机制 |
| **Outcomes** | 涌现现象（舆论、经济） |

### 应用场景

- 舆论动力学（Opinion Dynamics）
- 流行病建模（Epidemic Modeling）
- 宏观经济（Macroeconomics）
- 社会运动（Social Movement）

---

## 评估方法汇总

### Individual Simulation

| 指标 | 描述 |
|------|------|
| KL Divergence | 分布对齐 |
| Accuracy | 行为预测准确率 |
| Consistency | 一致性度量 |

### Scenario Simulation

| 指标 | 描述 |
|------|------|
| Task Success Rate | 任务完成率 |
| Quality Score | 输出质量 |
| Efficiency | 效率指标 |

### Society Simulation

| 指标 | 描述 |
|------|------|
| Emergent Patterns | 涌现模式匹配 |
| Macro-level Metrics | 宏观指标 |
| Network Properties | 网络属性 |

---

## 数据集与基准

### Individual Simulation

- OpinionQA
- ANES
- Pew Research ATP
- GSS

### Scenario Simulation

- Sotopia
- AvalonBench
- AI Hospital
- ChatDev

### Society Simulation

- OASIS（100万Agent）
- Generative Agents

---

## 与本研究的关系

### 可借鉴点

| 方面 | 借鉴内容 |
|------|---------|
| **三层框架** | Individual → Scenario → Society |
| **Profile设计** | 人口统计+性格+价值观 |
| **Memory机制** | 短期/长期记忆用于一致性维护 |
| **评估指标** | KL Divergence + Consistency |

### 本研究定位

```
本研究（ConsistAgent）属于：
- Individual Simulation层
- 问卷响应生成场景
- 跨问题态度一致性评估
```

---

## 开源资源

- **GitHub**: https://github.com/FudanDISC/SocialAgent

---

## 关键趋势

1. **规模扩大**: 从个体到百万Agent
2. **动态交互**: 静态→动态场景
3. **涌现行为**: 从规则驱动到涌现驱动
4. **评估挑战**: 需要更全面的评估框架

---

**解读时间**: 2026-03-08
**状态**: 完成