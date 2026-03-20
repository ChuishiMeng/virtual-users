# P31-2025-OPeRA-Dataset

## 基本信息

| 项目 | 内容 |
|------|------|
| **标题** | OPeRA: A Dataset of Observation, Persona, Rationale, and Action for Evaluating LLMs on Human Online Shopping Behavior Simulation |
| **作者** | Ziyi Wang et al. (Northeastern University等) |
| **发表** | 2025年 |
| **页数** | 18页 |
| **相关性** | ⭐⭐⭐ 高相关性（数据集+用户行为模拟） |
| **评分** | 8/10 |

---

## 核心问题

能否准确模拟特定用户的下一个网页动作？缺乏高质量公开数据集来捕获可观察动作和内部推理。

---

## 核心贡献

### 1. OPeRA数据集

**首个综合捕获以下元素的公开数据集**：

| 元素 | 描述 |
|------|------|
| **Persona** | 用户画像（人口统计、偏好） |
| **Observation** | 浏览器观察（HTML、截图） |
| **Action** | 细粒度网页动作（点击、输入、终止） |
| **Rationale** | 自报告即时理由（为什么做这个动作） |

### 2. 数据集规模

| 版本 | Sessions | Users | <Action, Obs> Pairs | Rationales |
|------|----------|-------|---------------------|------------|
| OPeRA-full | 692 | 51 | 28,904 | 604 |
| OPeRA-filtered | 527 | - | 5,856 | 207 |

### 3. 数据收集方法

- **在线问卷**：收集用户画像
- **自定义浏览器插件**：ShoppingFlow Plugin
- **收集周期**：4周

---

## 评估任务

### Next Action Prediction

**输入**：Persona + <Observation, Action, Rationale> history
**输出**：Predicted Action + Generated Rationale

### 评估指标

| 指标 | 描述 |
|------|------|
| Action Generation Accuracy | 精确匹配准确率 |
| Action Type Macro F1 | 高层动作类别预测（input/click/terminate） |
| Click Type Weighted F1 | 具体点击动作类型预测 |
| Session Outcome Weighted F1 | 会话最终结果预测（purchase/terminate） |

---

## 实验结果

### 主实验

| Model | Action Acc. | Action Type F1 | Click Type F1 | Outcome F1 |
|-------|-------------|----------------|---------------|------------|
| GPT-4.1 | **21.51%** | **48.78%** | **44.47%** | 47.54% |
| DeepSeek-R1 | 14.75% | 27.37% | 35.12% | 46.36% |
| Claude-3.7 | 10.75% | 31.58% | 27.27% | 43.52% |
| LLaMA-3.3 | 8.31% | 24.29% | 19.99% | 36.64% |

### 消融研究

| 消融 | 对Action Acc影响 | 对Action Type影响 |
|------|-----------------|------------------|
| w/o persona | 混合（有时提升） | 普遍下降 |
| w/o rationale | 普遍下降 | 普遍下降 |

---

## 关键发现

### 1. LLM能力有限

- ✅ GPT-4.1最佳：21.51%动作预测准确率
- ⚠️ 所有模型表现远低于人类

### 2. Persona作用不一致

- ✅ 对动作类型预测有帮助
- ⚠️ 对精确动作预测有时引入噪音
- ⚠️ 当前模型难以深度整合persona到决策中

### 3. Rationale重要

- ✅ 移除rationale导致性能普遍下降
- ✅ 提供有价值的中间监督信号

### 4. 上下文长度影响

- ✅ GPT-4.1（200k context）表现最好
- ⚠️ DeepSeek-R1、Claude-3.7（128k context）受限

---

## 与本研究的关系

### 可借鉴点

| 方面 | 借鉴内容 |
|------|---------|
| **数据集设计** | Persona + Rationale + Action三元组 |
| **评估框架** | Next Action Prediction任务 |
| **消融方法** | w/o persona、w/o rationale消融研究 |

### 差异

| 维度 | OPeRA | 本研究 |
|------|-------|--------|
| 任务 | 网页行为预测 | 问卷响应生成 |
| 输入 | 观察序列 | 问题+选项 |
| 输出 | 动作 | 封闭式回答 |
| 一致性 | 时序一致性 | 跨问题态度一致性 |

---

## 数据集获取

- **HuggingFace**: https://huggingface.co/datasets/NEU-HAI/OPeRA

---

## 局限性

1. 简化动作空间（省略滚动、页面导航）
2. 未使用视觉信号（截图）
3. 用户数量有限（51人）

---

**解读时间**: 2026-03-08
**状态**: 完成