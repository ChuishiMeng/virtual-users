# P11: KDD论文扩充计划

**目标**：将 5 页论文扩充到 8+ 页（KDD 2026 标准）
**时间**：2-3 天
**负责人**：科研小新

---

## 一、现状分析

### 1.1 页数差距
- **当前**：5 页
- **要求**：8 页正文（+ 无限参考文献/附录）
- **差距**：3 页

### 1.2 KDD 2026 官方要求
- Research Track: 8 content pages
- ADS Track: 8 content pages  
- 前 8 页必须自洽（reviewer 不强制读附录）
- 附录无页数限制

### 1.3 当前论文结构分析
```
main.tex (513行) 结构:
├─ Abstract (185 words) ✅
├─ Introduction (完整) ✅
├─ Related Work (待扩充) ⚠️
├─ Method (待形式化) ⚠️
├─ Experiments (待扩充) ❌
├─ Discussion (简短) ⚠️
└─ Conclusion ✅
```

---

## 二、学习阶段（第1天）

### 2.1 学习目标
理解 KDD 顶级论文的写作标准和结构

### 2.2 学习材料

#### 必读论文（3篇，每篇1小时）
1. **Agent4Rec** (SIGIR 2024) - 用户模拟器标杆
   - 重点：方法论形式化、实验设计
   - 学习：4模块架构如何形式化描述

2. **LLM-S³** (arXiv 2024) - LLM调研基准
   - 重点：评估指标设计、多数据集实验
   - 学习：11个数据集如何系统评估

3. **Generative Agents** (UIST 2023) - Persona 系统
   - 重点：记忆架构、行为一致性
   - 学习：如何证明虚拟用户可信

#### 必读指南
- `论文学习方法/KDD-研究方法指南.md` (已总结)
- P10 差距分析报告（已分析）

### 2.3 学习产出
- 总结 KDD 论文 8 页标准结构模板
- 对比当前论文与标准的差距清单

---

## 三、扩充阶段（第2天）

### 3.1 页数分配目标

| 章节 | 当前 | 目标 | 增加 | 内容 |
|------|------|------|------|------|
| Abstract | 0.3页 | 0.3页 | - | 保持 |
| Introduction | 1.2页 | 1.5页 | +0.3 | 补充研究空白、贡献点细化 |
| Related Work | 0.5页 | **1.5页** | **+1.0** | 分类细化、Gap分析 |
| Method | 1.0页 | **1.8页** | **+0.8** | 形式化、伪代码、理论依据 |
| Experiments | 1.2页 | **2.0页** | **+0.8** | 增加实验细节、误差分析 |
| Discussion | 0.3页 | 0.5页 | +0.2 | Limitations、Future Work |
| Conclusion | 0.3页 | 0.4页 | +0.1 | 保持简洁 |
| **总计** | **5页** | **8页** | **+3页** | |

### 3.2 扩充策略

#### 策略1：Related Work 扩充 (+1页)

**当前问题**：只有分类标题，缺少具体分析

**扩充内容**：
```markdown
2. Related Work
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2.1 LLM-Based User Simulation (0.4页)
    - Agent4Rec [详细分析]
    - Generative Agents [详细分析]
    - Gap: 缺少调研场景专用框架
    
2.2 Survey Automation (0.3页)
    - LLM-S³ [详细分析]
    - AlignSurvey [详细分析]
    - Gap: 缺少端到端系统
    
2.3 Persona-Based Systems (0.3页)
    - PersonaCite [详细分析]
    - Polypersona [详细分析]
    - Gap: 缺少可靠性评估机制
    
2.4 Retrieval-Augmented Generation (0.3页)
    - RAG [详细分析]
    - DPR [详细分析]
    - Gap: 缺少 Persona-aware 检索
```

**模板**（每个子节）：
```latex
\subsection{XXX}

Existing works on XXX include A~\cite{}, B~\cite{}, and C~\cite{}.
A proposes... [1-2句概述]
B demonstrates... [1-2句概述]
However, these approaches share limitations:
\begin{itemize}
    \item Limitation 1
    \item Limitation 2
\end{itemize}
Our work addresses these gaps by...
```

#### 策略2：Method 形式化 (+0.8页)

**当前问题**：文字描述为主，缺少数学形式化

**扩充内容**：
```markdown
3. Method
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3.1 Problem Formulation (新增 0.2页)
    - 形式化定义调研任务
    - 输入输出空间定义
    - 优化目标
    
3.2 Framework Overview (0.2页)
    - 系统架构图（TikZ）
    - 模块交互说明
    
3.3 Persona Generation (扩充 0.2页)
    - 数学公式：P = f(D; θ)
    - 算法伪代码（Algorithm 1）
    
3.4 Retrieval Augmentation (扩充 0.1页)
    - 检索公式：R = Top-k(Q, K)
    - Reranking 策略
    
3.5 Response Generation (扩充 0.1页)
    - 生成公式：P(y|x,p,R)
    - 置信度校准
    
3.6 Reliability Assessment (0.1页)
    - 多层评估指标
```

**形式化模板**：
```latex
\subsection{Problem Formulation}

Let $\mathcal{D}$ denote the target demographic distribution, 
$\mathcal{Q}$ the survey questions, and $\mathcal{Y}$ the response space.
Our goal is to learn a mapping function:
$$f: \mathcal{D} \times \mathcal{Q} \rightarrow \mathcal{Y}$$
such that the generated responses $\hat{Y}$ align with real human responses $Y$ 
in distribution: $P(\hat{Y}) \approx P(Y)$.

\begin{algorithm}
\caption{Persona Generation}
\begin{algorithmic}
\REQUIRE Target distribution $\mathcal{D}$, sample size $N$
\ENSURE Persona pool $\mathcal{P} = \{p_1, ..., p_N\}$
\FOR{$i = 1$ to $N$}
    \STATE Sample demographics $d_i \sim \mathcal{D}$
    \STATE Generate psychographics via LLM: $g_i = \text{LLM}(d_i)$
    \IF{consistency\_check($p_i = (d_i, g_i)$)}
        \STATE $\mathcal{P} \leftarrow \mathcal{P} \cup \{p_i\}$
    \ENDIF
\ENDFOR
\RETURN $\mathcal{P}$
\end{algorithmic}
\end{algorithm}
```

#### 策略3：Experiments 细化 (+0.8页)

**当前问题**：实验描述简略，缺少细节

**扩充内容**：
```markdown
4. Experiments
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4.1 Experimental Setup (0.3页)
    - 数据集详细描述（表格）
    - Baseline 详细说明
    - 超参数设置
    
4.2 Main Results (0.5页)
    - 主实验结果表（详细）
    - 统计显著性标注
    - 置信区间
    
4.3 Ablation Studies (0.3页)
    - 模块级消融
    - 参数敏感性分析
    
4.4 Analysis (0.3页)
    - 误差分析
    - Case Study
    - 专家评估详情
```

**表格模板**：
```latex
\begin{table}[t]
\centering
\caption{Main results on LLM-S³ benchmark. 
Best results in \textbf{bold}. 
$\dagger$ indicates statistically significant improvement (p < 0.05).}
\label{tab:main}
\begin{tabular}{lcccc}
\toprule
Method & KL $\downarrow$ & JS $\downarrow$ & Acc $\uparrow$ & Sim $\uparrow$ \\
\midrule
Random & 1.23 & 0.45 & 0.31 & 0.42 \\
LLM-Direct & 0.78 & 0.35 & 0.52 & 0.65 \\
LLM-Prompt & 0.65 & 0.30 & 0.58 & 0.72 \\
\midrule
\textbf{Ours} & \textbf{0.42}$\dagger$ & \textbf{0.21}$\dagger$ & \textbf{0.71}$\dagger$ & \textbf{0.85}$\dagger$ \\
\bottomrule
\end{tabular}
\end{table}
```

---

## 四、执行计划

### Day 1: 学习 + 规划（今天）

| 任务 | 时间 | 产出 |
|------|------|------|
| 学习 Agent4Rec 论文 | 1h | 方法论形式化笔记 |
| 学习 LLM-S³ 论文 | 1h | 实验设计笔记 |
| 对比差距清单 | 0.5h | 详细差距表 |
| 确定扩充内容 | 0.5h | 本文档 |

### Day 2: 扩充 Related Work + Method

| 任务 | 时间 | 产出 |
|------|------|------|
| 扩充 Related Work | 2h | +1页 |
| 增加 Problem Formulation | 0.5h | +0.2页 |
| 添加算法伪代码 | 1h | 2个Algorithm |
| 添加数学公式 | 1h | 5+公式 |
| 编译验证 | 0.5h | 6-7页PDF |

### Day 3: 扩充 Experiments + 润色

| 任务 | 时间 | 产出 |
|------|------|------|
| 扩充实验细节 | 1.5h | +0.5页 |
| 添加统计标注 | 0.5h | 显著性 |
| 添加消融实验 | 1h | +0.3页 |
| 添加图表 | 1h | 2图2表 |
| 最终编译 | 0.5h | 8页PDF |
| 审校润色 | 0.5h | 最终版 |

---

## 五、质量检查清单

### 5.1 内容检查
- [ ] 页数达到 8 页
- [ ] 所有章节内容完整
- [ ] 所有表格有 caption
- [ ] 所有公式有编号
- [ ] 所有算法有伪代码

### 5.2 格式检查
- [ ] 引用格式统一（ACM format）
- [ ] 图表清晰可读
- [ ] 统计显著性标注
- [ ] 无编译错误/警告

### 5.3 学术检查
- [ ] 所有 claim 有引用/实验支持
- [ ] 贡献点明确具体
- [ ] 与 SOTA 对比清晰
- [ ] Limitations 讨论诚实

---

## 六、预期产出

### 6.1 最终论文结构
```
VirtualSurvey: A Persona-Based LLM Framework
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Abstract (0.3页)
1. Introduction (1.5页)
   - Background & Motivation
   - Challenges
   - Contributions
   
2. Related Work (1.5页) ← 新增
   - LLM-Based User Simulation
   - Survey Automation
   - Persona-Based Systems
   - Retrieval-Augmented Generation
   
3. Method (1.8页) ← 扩充
   - Problem Formulation (新)
   - Framework Overview
   - Persona Generation (+伪代码)
   - Retrieval Augmentation (+公式)
   - Response Generation (+公式)
   - Reliability Assessment
   
4. Experiments (2.0页) ← 扩充
   - Setup (+详细表格)
   - Main Results (+统计)
   - Ablation Studies (+参数)
   - Analysis (+Case Study)
   
5. Discussion (0.5页)
   - Limitations
   - Future Work
   
6. Conclusion (0.4页)

References (无限制)
Appendix (无限制)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
总计: ~8 页正文
```

### 6.2 新增元素
- **算法**：2 个伪代码（Persona Generation, Response Generation）
- **公式**：8+ 数学公式
- **表格**：3 个详细表格（数据集、主结果、消融）
- **图表**：2 个可视化（系统架构、分布对比）

---

## 七、风险与应对

| 风险 | 概率 | 应对 |
|------|------|------|
| 扩充后仍不足8页 | 中 | 准备 Appendix 素材 |
| 公式格式错误 | 低 | 参考已发表论文 |
| 统计数据不足 | 中 | 增加 bootstrap 采样 |
| 编译问题 | 低 | 分步编译调试 |

---

**计划状态**：待启动
**预计完成**：3天
**下一步**：启动学习阶段（Day 1）

