---
tags: [科研, 文献, 虚拟用户, Persona, 问卷调查, 可靠性评估]
paper_id: P39
arxiv: "2602.18462"
date: 2026-04-14
---

# P39 - Assessing the Reliability of Persona-Conditioned LLMs as Synthetic Survey Respondents

## 基本信息
- **作者**: Erika Elizabeth Taday Morocho 等（意大利 IIT-CNR / 比萨大学 / 佛罗伦萨大学）
- **时间**: 2026年2月
- **arXiv**: 2602.18462
- **发表**: WWW 2026 (Companion)

## 核心问题
多属性 Persona Prompting 真的能提升 LLM 虚拟调查受访者的可靠性吗？还是反而引入扭曲？

## 实验设计
- **数据**: WVS-7（世界价值观调查第7波），美国 2,596 名受访者 × 31 道题
- **模型**: Llama-2-13B + Qwen3-4B
- **Persona**: 8 个社会人口属性（性别、年龄、教育、就业、职业、收入、宗教、种族）
- **三组对照**: Persona-based (PB) vs Vanilla (V) vs Random (R)
- **规模**: 31 万+ 次推理

## 核心发现：Persona Prompting 效果不一致！

| 条件 | Llama-2 HS | Qwen3 HS |
|------|-----------|----------|
| Random | 0.273 | 0.273 |
| Vanilla（无 Persona） | **0.370** | 0.391 |
| Persona（有 Persona） | 0.366 | **0.398** |

- 两个模型都远超随机猜测
- **Persona vs Vanilla 差异统计上不显著**
- Llama-2 加了 Persona 反而略差
- 题目级效果高度异质：大部分题目 PB≈V，少数大幅波动
- **小群体受冲击最大**：少数群体（如 farm owner 4人、hindu 14人）被 Persona 扭曲最严重
- 更强的模型 ≠ 更可靠的 Persona 模拟

## 评估指标
- **Hard Similarity (HS)**: 精确匹配率
- **Soft Similarity (SS)**: 有序距离（差一格 vs 差五格区别对待）
- **子群体保真度**: 按人口属性分层的 HS/SS
- 仅看精确匹配率可能误导：HS 提升可能被有序距离增大抵消

## 对 virtual-users 的价值
1. ⚠️ **核心警示**: Persona 不是万能药，必须设 Vanilla 基线对照
2. ⚠️ 小群体误差被聚合指标"稀释" → 必须做子群体级分析
3. ✅ HS + SS 双重指标值得采用
4. ✅ 温度 0.3、单次生成、严格解析流程可参考
5. ⚠️ 需验证每个属性的独立贡献（消融实验）
6. **局限**: 仅用 Llama-2-13B 和 Qwen3-4B，未测更大模型；仅限美国数据

## 关键引用
- "Persona effects are highly heterogeneous as most items exhibit minimal change, while a small subset of questions and underrepresented subgroups experience disproportionate distortions."
- "Multi-attribute persona prompting does not deliver a consistent aggregate gain over a matched vanilla control across models."
