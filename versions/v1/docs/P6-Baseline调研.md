# P6-1: Baseline Persona 生成方法调研

> 调研时间: 2026-02-17
> 调研目的: 评估 3 个主流 Persona 生成方法，为 Virtual Users 项目选择 Baseline

---

## 1. Generative Agents (Stanford)

**论文**: arXiv:2304.03442 - "Generative Agents: Interactive Simulacra of Human Behavior"

### 核心思想

斯坦福大学提出的生成式代理架构，使用大语言模型模拟可信人类行为。代理能够存储完整经验记录（自然语言形式），合成高层反思，并动态检索记忆规划行为。在类 Sims 的沙盒环境中，25 个代理展现出可信的个体和社会行为（如自主组织派对）。

### 代码/模型链接

- **GitHub**: https://github.com/joonspk-research/generative_agents
- **PDF**: https://arxiv.org/pdf/2304.03442

### 优点

1. **完整架构**: 包含观察→反思→规划的完整认知循环
2. **涌现行为**: 代理间可产生复杂的社交互动（邀请、约会、协调）
3. **开源可复现**: 代码完全开源，社区活跃

### 缺点

1. **计算成本高**: 每个代理需要频繁 LLM 调用
2. **记忆效率**: 自然语言存储记忆，检索效率较低
3. **短期一致性**: 长时间跨度的行为一致性难保证

---

## 2. Polypersona

**论文**: arXiv:2512.14562 - "Polypersona: Persona-Grounded LLM for Synthetic Survey Responses"

### 核心思想

面向调查问卷的 persona 条件生成框架，使用 LoRA 适配器和 4-bit 量化对小型模型（TinyLlama 1.1B, Phi-2）进行指令微调。构建了 3,568 条跨 10 个领域、433 个 persona 的调查回复数据集，证明小模型经微调可达 7B-8B 基线性能。

### 代码/模型链接

- **匿名仓库**: https://anonymous.4open.science/r/Polypersona-1D70/
- **PDF**: https://arxiv.org/pdf/2512.14562
- **基础数据集**: PersonaHub (Tencent AI Lab)

### 优点

1. **参数高效**: LoRA+4-bit 量化，消费级 GPU 可训练
2. **多领域覆盖**: 10 个领域（医疗、教育、金融等）的系统化评估
3. **可复现**: 多指标评估栈（BLEU, ROUGE, BERTScore + 调查指标）

### 缺点

1. **领域限制**: 仅针对调查问卷回复，交互能力有限
2. **静态 persona**: Persona 在生成时固定，无法动态演化
3. **缺乏验证**: 未与真实用户回复进行大规模对比验证

---

## 3. PersonaCite

**论文**: arXiv:2601.22288 - "PersonaCite: VoC-Grounded Interviewable Agentic Synthetic AI Personas"

### 核心思想

将 AI persona 重构为证据约束的研究工具。每次对话时，系统从 VoC（Voice of Customer）数据中检索真实用户评论，约束 LLM 只基于检索证据生成回复；证据不足时显式拒绝回答，并提供响应级来源归属。

### 代码/模型链接

- **论文 HTML**: https://arxiv.org/html/2601.22288v1
- **PDF**: https://arxiv.org/pdf/2601.22288
- **代码**: 论文未提及公开代码（研究原型）

### 优点

1. **证据可追溯**: 每个回复都有 VoC 来源引用
2. **显式弃权**: 证据不足时不乱答，提高可信度
3. **专家验证**: 14 位行业专家的访谈研究

### 缺点

1. **依赖 VoC 数据**: 需要高质量的原始用户评论数据
2. **代码未公开**: 当前仅作为研究原型
3. **领域受限**: 知识边界受限于已收集的 VoC 数据范围

---

## 对比总结

| 方法 | 核心创新 | 开源程度 | 计算成本 | 证据基础 |
|------|----------|----------|----------|----------|
| Generative Agents | 认知架构 (观察→反思→规划) | 完全开源 | 高 | 无特定数据要求 |
| Polypersona | 参数高效微调 (LoRA+4bit) | 代码开源 | 低 | PersonaHub 数据集 |
| PersonaCite | 检索增强+来源归属 | 原型阶段 | 中 | VoC 数据依赖 |

## Baseline 选择建议

1. **首选**: Generative Agents - 架构完整、开源可复现、学术影响力大
2. **补充**: Polypersona - 如果需要轻量化方案或调查场景
3. **参考**: PersonaCite - 检索增强思路值得借鉴，但需自建实现

---

*调研完成于 2026-02-17*

---

# P6-2: Baseline 问卷模拟方法调研

> 调研时间: 2026-02-17
> 调研目的: 评估 3 个问卷模拟方法，为 Virtual Users 项目选择 Baseline

---

## 4. LLM-S³ PAS/FAS

**论文**: arXiv:2509.06337 - "Large Language Models as Virtual Survey Respondents: Evaluating Sociodemographic Response Generation"

### 核心思想

提出两种创新模拟范式：Partial Attribute Simulation (PAS) 基于部分人口统计属性预测缺失属性，Full Attribute Simulation (FAS) 在零上下文和增强上下文条件下生成完整合成数据集。构建 LLM-S³ 基准，覆盖 11 个公共数据集、4 个社会学领域，系统评估 GPT-3.5/4、LLaMA 3.0/3.1 的模拟保真度。

### 代码/模型链接

- **GitHub**: https://github.com/dart-lab-research/LLM-S-Cube-Benchmark
- **PDF**: https://arxiv.org/pdf/2509.06337
- **HTML**: https://arxiv.org/html/2509.06337

### 优点

1. **系统化基准**: 覆盖 11 个数据集、4 个领域、多模型对比
2. **实用范式**: PAS 对应数据填补，FAS 对应合成人口生成
3. **提示工程洞察**: 上下文增强和提示设计对模拟保真度影响显著

### 缺点

1. **结构化输出瓶颈**: FAS 场景中结构化输出生成存在失败模式
2. **依赖真实数据**: 需要高质量的真实调查数据作为基准
3. **领域局限**: 仅覆盖社会学相关领域，其他场景待验证

---

## 5. Specializing LLMs for Survey

**论文**: NAACL 2025 - "Specializing Large Language Models to Simulate Survey Response Distributions for Global Populations"

### 核心思想

首个专门针对调查响应分布模拟的 LLM 微调方法。基于 first-token probabilities 设计微调目标，最小化预测分布与真实国家级响应分布的差异。使用 World Values Survey (66 国、80,000+ 响应者) 作为测试平台，证明专业化模型显著优于 zero-shot。

### 代码/模型链接

- **GitHub**: https://github.com/yongcaoplus/SimLLMCultureDist
- **PDF**: https://aclanthology.org/2025.naacl-long.162.pdf
- **ACL Anthology**: https://aclanthology.org/2025.naacl-long.162/

### 优点

1. **跨数据集泛化**: 在未见国家、未见问题、完全未见问卷 (Pew) 上均有提升
2. **多语言支持**: 提供 English 和 Chinese 数据集
3. **开源复现**: 代码、数据集、微调方法完全公开

### 缺点

1. **未见问题差距**: 即使最佳微调模型在未见问题上仍远非完美
2. **多样性不足**: 所有测试 LLM 的预测跨国家多样性低于真实人类数据
3. **计算成本**: 需要针对每个国家/群体进行专业化训练

---

## 6. Random Silicon Sampling

**论文**: arXiv:2402.18144 - "Random Silicon Sampling: Simulating Human Sub-Population Opinion Using a Large Language Model Based on Group-Level Demographic Information"

### 核心思想

利用 LLM 内嵌的社会偏见（与人口统计信息相关），仅基于群体级人口统计分布生成调查响应。通过"随机硅采样"方法，模拟美国公共民意调查的响应分布，发现生成分布与真实民调高度相似，且相似度因人口群体和主题而异。

### 代码/模型链接

- **PDF**: https://arxiv.org/pdf/2402.18144
- **arXiv**: https://arxiv.org/abs/2402.18144
- **代码**: 论文未提及公开代码

### 优点

1. **仅需群体级信息**: 不需要个体级详细画像，仅需人口统计分布
2. **高度相似**: 生成的响应分布与美国真实民调高度一致
3. **方法简单**: 无需微调，直接通过提示工程实现

### 缺点

1. **依赖社会偏见**: 方法有效性直接依赖于模型内嵌的社会偏见
2. **可复现性差异**: 不同人口群体和主题的复现性存在差异
3. **代码未公开**: 当前仅作为研究论文，未提供开源实现

---

## 对比总结

| 方法 | 核心创新 | 开源程度 | 计算成本 | 数据需求 |
|------|----------|----------|----------|----------|
| LLM-S³ PAS/FAS | 双范式系统化基准 (PAS+FAS) | 完全开源 | 中-高 | 需真实调查数据 |
| Specializing LLMs for Survey | First-token 微调方法 | 完全开源 | 中 (需微调) | WVS/Pew 数据集 |
| Random Silicon Sampling | 仅用群体级人口统计信息 | 未开源 | 低 | 仅需分布信息 |

## 方法选择建议

1. **系统化研究**: LLM-S³ - 提供完整基准测试框架，适合深入评估
2. **生产级应用**: Specializing LLMs for Survey - 微调后性能最优，开源可复现
3. **快速原型**: Random Silicon Sampling - 无需微调，但需自行实现

---

*P6-2 调研追加于 2026-02-17*
