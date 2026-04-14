---
tags: [科研, 文献, 虚拟用户, Mobile-Agent, 评估基准]
paper_id: P37
arxiv: "2604.08455"
date: 2026-04-14
---

# P37 - KnowU-Bench: Towards Interactive, Proactive, and Personalized Mobile Agent Evaluation

## 基本信息
- **作者**: 浙大 ZJU-REAL + Apple + Tencent
- **时间**: 2026年4月
- **arXiv**: 2604.08455
- **GitHub**: github.com/ZJU-REAL/KnowU-Bench

## 核心贡献
1. 首个将个性化推理与可复现 Android 模拟器结合的评测框架
2. 构建了交互式偏好获取和完整主动服务决策链的评测场景
3. 系统评测 11 个主流模型，揭示偏好推断和干预校准的关键缺陷

## 架构设计（POMDP）
- 192 个任务（23 个 App）= 42 通用 + 86 个性化 + 64 主动式
- Profile 对 Agent 隐藏，只暴露行为日志 → 强制偏好推断
- 14 种 GUI 操作，包括关键的 `ask_user` 用于交互

## Structured Profiles（7 维 YAML）
| 维度 | 用途 | 示例 |
|------|------|------|
| identity | 基本身份 | Aiden Lin, 34岁, 副教授 |
| locations | 物理/数字位置 | 家-海淀, 工作-北大 |
| digital_context | 设备环境 | MacBook Pro, 深色模式 |
| habits | 行为模式（trigger-action） | 每早查 AlphaXiv |
| preferences | 稳定偏好 | 不吃花生, 偏好美团 |
| decision_criteria | 决策逻辑 | 时间>金钱, 性能>稳定 |
| social_graph | 社交关系 | 院长-立即通知, 学生-委派 |

## LLM-driven User Simulator
- 用 GPT-4o 做角色扮演
- Prompt: Context → Profile → Current Context → Instruction → Preference Profile
- 两种模式：个性化任务（回答偏好澄清）/ 主动性任务（接受/拒绝决定）

## 评估方法
- 混合策略：Rule-based + LLM-as-a-Judge
- 融合公式：S_i = λ_i × S_rule + (1-λ_i) × S_llm
- 三层指标：SR + Efficiency（通用）/ Average Score + IE（个性化）/ Act/Silent/Stop Rate（主动性）

## 核心实验发现
- GUI 操作已不是瓶颈（General Easy 最高 100%）
- 个性化性能暴跌 ~30%（Claude Sonnet 4.6: 60.4% → 44.2%）
- 交互质量 > 交互数量（Sonnet 每任务仅问 0.4 题，却最优）
- 角色敏感：Grandma 最难，Student 差异最大
- 主动性是校准问题：60% 失败是过度干预

## 对 virtual-users 的借鉴价值
1. **Profile Schema**: 7 维结构可直接迁移为虚拟用户画像模板
2. **Simulator Prompt**: 复用 Context+Profile+Instruction 模板
3. **偏好注入机制**: Preference Profile 子块注入当前场景态度
4. **混合评估**: Rule-based + LLM-as-Judge
5. **决策逻辑建模**: decision_criteria 优先级-权衡-痛点三元组
6. **IE 指标**: 可改造为"虚拟用户回答信息量/问题数"
