# 论文深度阅读：Exploring LLMs for Automated Generation and Adaptation of Questionnaires

> 论文ID: arXiv:2501.05985
> 作者: Divya Mani Adhikari, Alexander Hartland, Ingmar Weber, Vikram Kamath Cannanure (Saarland University)
> 发表时间: 2025年1月（CUI '25）
> 页数: 23页
> 阅读时间: 2026-02-28

---

## 📋 基本信息

**研究主题**: 用 LLM 自动生成和适应问卷

**核心问题**: 
- LLM 能否自动生成新问卷？
- LLM 能否预测试问卷并发现问题？
- LLM 能否将现有问卷适应到不同文化？

**核心贡献**:
1. **完整流水线**：生成 + 预测试 + 适应
2. **双研究验证**：美国（238人）+ 南非（118人）
3. **专家评估**：13名专家对比评估

---

## 🎯 研究动机

### 问卷设计的挑战

**新问卷创建**：
- 需要逻辑结构化的顺序
- 必须清晰、相关、精确
- 避免混淆和误解

**预测试困难**：
- 资源限制（成本、时间）
- 参与者可用性
- 专家访问有限

**跨文化适应**：
- 问题措辞和解释因地区而异
- 需要本地化验证
- 敏感问题需特别处理

### LLM 的机会

**自动预测试**：
- 采用不同 Persona 模拟试点研究
- 评估问卷有效性
- 检测潜在问题（歧义、偏见）

**问卷适应**：
- 跨文化适应
- 语言本地化
- 上下文调整

---

## 💡 核心方法

### 1. 完整流水线

```
┌─────────────────────────────────────┐
│   RQ1: Creation（新问卷创建）        │
│   研究问题 → LLM 生成问卷 → 预测试   │
└──────────┬──────────────────────────┘
           │
┌──────────┴──────────────────────────┐
│   RQ2: Adaptation（问卷适应）        │
│   现有问卷 → Persona生成 → 文化适应  │
└─────────────────────────────────────┘
```

### 2. RQ1: Creation（创建新问卷）

**步骤**：

**Step 1: Persona 生成**
```python
prompt = """
You are a researcher working on Survey research.
Generate 10 personas for the following research question:
<question>{research_question}</question>

Persona should contain:
- Name (fictional, common in intended demographic)
- Age, Gender, Race, Location
- Occupation, Education
- Preferences (based on research question)
"""
```

**示例 Persona**（南非环境科学家）：
```
Name: Thabo Dlamini
Age: 35
Gender: Male
Race: Black
Location: Johannesburg, South Africa
Occupation: Environmental Scientist
Education: Masters in Environmental Science
Beliefs: Strong believer in climate change
Perceptions of Risk: High concern about air pollution
Policy Preferences: Supports carbon emission regulations
Behaviors: Recycles and uses public transportation
```

**Step 2: 问卷生成**
```python
prompt = """
Based on the research question and personas, generate a questionnaire.

Research Question: {research_question}
Target Personas: {personas}

Generate {num_questions} questions that:
- Are clear and unambiguous
- Cover all aspects of the research question
- Are appropriate for the target personas
"""
```

**Step 3: LLM 预测试**
```python
# 用 Persona 模拟参与者
participant_prompt = """
You are a participant in a survey interview.
Your details:
{persona}

You will be asked a series of questions.
Answer strictly following your details and chat history.
"""

# 用 LLM 模拟访谈
for question in questionnaire:
    response = llm.chat(participant_prompt, question)
    
# 用 Reviewer Prompt 分析问题
reviewer_prompt = """
As a reviewer, evaluate the survey questionnaire based on:
- Clarity, Comprehension, Sensitivity
- Double questions, Ambiguous questions
- Loaded/Leading questions
- Missing response categories
- Contradictions in responses
"""
```

### 3. RQ2: Adaptation（问卷适应）

**步骤**：

**Step 1: 提取标准化问卷**
- 来源：美国气候变化调查（2008-2020）
- 30个问题：全球变暖信念、原因、危害、政策支持

**Step 2: 文化适应**
```python
prompt = """
Adapt the following US-specific questionnaire for South African audience.

Original Question: {us_question}

Consider:
- Cultural context differences
- Local terminology
- Relevant local examples
- Sensitive topics in South Africa
"""
```

**Step 3: Persona 驱动预测试**
- 生成南非 Persona
- 用 Persona 评估适应后的问卷
- 识别需要修改的问题

---

## 🧪 实验设计

### 1. RQ1: Creation Study

**研究主题**：政治信任（Political Trust）

**参与者**：
- **Prolific 参与者**：238人（美国）
- **专家**：13人（政治学、社会学等领域）

**对比条件**：
1. **LLM-generated**：LLM 直接生成的问卷
2. **LLM-pretested**：生成后经 LLM 预测试并修改

**评估维度**：
1. Clarity（清晰度）
2. Relevance（相关性）
3. Specificity（特异性）
4. Bias（偏见）

### 2. RQ2: Adaptation Study

**研究主题**：气候变化（Climate Change）

**参与者**：
- **Prolific 参与者**：118人（南非）
- 75%女性，31%中左翼
- 99%有调查经验
- 专业背景：地球/环境科学、政治、心理学、社工、社会学

**对比条件**：
1. **Traditional**：原始美国问卷
2. **LLM-adapted**：LLM 适应后的南非问卷

**评估维度**：
- 同上（Clarity, Relevance, Specificity, Bias）

---

## 📊 实验结果

### 1. RQ1: Creation 结果

**Prolific 参与者评估**（N=238）：

| 维度 | LLM-generated | LLM-pretested | 差异 |
|------|--------------|---------------|------|
| **Clarity** | 3.90 | **4.09** | **+4.9%** ✅ |
| **Relevance** | 4.17 | 3.94 | -5.5% ⚠️ |
| **Specificity** | 2.98 | **2.72** | **-8.7%** ✅ |
| **Bias** | 2.55 | **2.88** | **+13%** ⚠️ |

**关键发现**：
- ✅ **预测试提升清晰度**（+4.9%，p < 0.1）
- ✅ **预测试提升特异性**（-8.7%，更低=更具体）
- ⚠️ **预测试增加感知偏见**（+13%，p < 0.05）

**专家评估**（N=13）：

| 维度 | LLM-generated | LLM-pretested | 差异 |
|------|--------------|---------------|------|
| **Clarity** | **4.46** | 4.00 | **-10.3%** ⚠️ |
| **Relevance** | **4.17** | 3.94 | -5.5% ⚠️ |
| **Specificity** | **2.98** | 2.72 | -8.7% ⚠️ |
| **Bias** | 2.55 | **2.88** | **+13%** ⚠️ |

**关键发现**：
- ⚠️ **专家偏好 LLM-generated**（更清晰、更相关、更具体）
- ⚠️ **专家认为 pretested 更有偏见**

**参与者 vs 专家对比**：
- 参与者：偏好 pretested（更清晰、更具体）
- 专家：偏好 generated（更简洁、更直接）

**定性反馈**：

*参与者*：
> "LLM-generated 更好，因为它更简洁。虽然 LLM pre-tested 是更好的问题，但它不够清晰，太多类似问题会导致参与者疲劳。"

> "LLM-generated 问题远不如 LLM pre-tested 具体。"

*专家*：
> "更短的句子 → 更易理解"

> "Group 2 (LLM pre-tested) 的阅读年龄太高。所有 Group 2 的问题都同时问两件事，所以不够清晰。"

> "虽然 Group 2 的陈述似乎更精确，但对普通公众来说更难回答，因为它们太具体了（例如，'公共福利和政策结果'而不是'公众利益'）。"

### 2. RQ2: Adaptation 结果

**南非参与者评估**（N=118）：

| 维度 | Traditional（美国版）| LLM-adapted（南非版）| 差异 |
|------|---------------------|---------------------|------|
| **Clarity** | 3.85 | **3.99** | **+3.6%** ✅ |
| **Relevance** | 3.95 | **4.03** | +2.0% |
| **Specificity** | 3.55 | 3.52 | -0.8% |
| **Bias** | 3.34 | **3.06** | **-8.4%** ✅ |

**关键发现**：
- ✅ **适应后更清晰**（+3.6%，p < 0.1）
- ✅ **适应后偏见更低**（-8.4%，p < 0.1）
- ⚠️ **差异边际显著**（p < 0.1）

**LLM 建议修改的5个问题示例**：

| 原问题（美国版）| 适应后（南非版）| 修改原因 |
|----------------|----------------|---------|
| "Do you think global warming is happening?" | "Do you think climate change is affecting South Africa?" | 本地化表述 |
| "How much do you trust the US government..." | "How much do you trust the South African government..." | 上下文适应 |
| ... | ... | ... |

**关键发现**：
- LLM 建议修改 **5/30（16.7%）** 问题
- 主要是本地化和文化适应
- 大部分问题无需修改（适用性良好）

### 3. 偏好分布

**RQ1（Creation）**：

*参与者偏好*（N=238）：
- 偏好相对平衡
- 无强烈偏好（generated vs pretested）

*专家偏好*（N=13）：
- **明显偏好 LLM-generated**
- 所有3个问题都选择 generated

**RQ2（Adaptation）**：
- 南非参与者偏好 LLM-adapted
- 但差异不大

---

## 🔍 关键洞察

### 1. 对虚拟用户研究的启示 ⭐⭐⭐⭐

**直接相关！**

**核心价值**：
1. ✅ **Persona 驱动预测试**：可用虚拟用户预测试问卷
2. ✅ **跨文化适应**：LLM 可适应问卷到不同文化
3. ✅ **完整流水线**：生成 + 预测试 + 适应

**可借鉴的组件**：
- **Persona 生成 Prompt**：可生成虚拟受访者
- **Participant Prompt**：Persona 扮演受访者
- **Reviewer Prompt**：自动检测问卷问题

**与 P05 Polypersona 的对比**：
| 维度 | P16 Automated Questionnaires | P05 Polypersona |
|------|----------------------------|----------------|
| **目标** | 问卷生成 + 预测试 | 问卷回答生成 |
| **Persona** | 用于预测试 | 用于回答生成 |
| **流程** | 生成 → 预测试 → 修改 | Persona → 问卷 → 回答 |
| **验证** | 真实参与者 + 专家 | ANES 数据集 |

**可结合方案**：
- P16 的预测试流水线 + P05 的问卷生成方法
- P16 的 Persona 扮演 + P13 的评估框架

### 2. 技术要点

**Persona 生成**：
```python
def generate_personas(research_question, num=10):
    """生成 Persona"""
    prompt = f"""
    Generate {num} personas for:
    {research_question}
    
    Include: Name, Age, Gender, Race, Location,
    Occupation, Education, Preferences
    """
    
    personas = llm.generate(prompt)
    return parse_personas(personas)
```

**Persona 扮演受访者**：
```python
def persona_respond(persona, question):
    """Persona 回答问卷"""
    prompt = f"""
    You are: {persona}
    
    Question: {question}
    
    Answer strictly following your details.
    For multiple choice, pick just one option.
    For open-ended, answer in 2-3 sentences.
    """
    
    response = llm.generate(prompt)
    return response
```

**Reviewer 自动检测问题**：
```python
def review_questionnaire(transcripts):
    """自动检测问卷问题"""
    prompt = f"""
    Review the interview transcripts:
    {transcripts}
    
    Check for:
    - Double questions
    - Ambiguous questions
    - Loaded/Leading questions
    - Missing response categories
    - Contradictions
    
    Provide detailed review and suggested changes.
    """
    
    review = llm.generate(prompt)
    return review
```

### 3. 专家 vs 参与者的差异 ⚠️

**关键发现**：
- **专家偏好简洁**：LLM-generated（更清晰、更直接）
- **参与者偏好具体**：LLM-pretested（更清晰、更具体）

**原因**：
- 专家关注可读性和简洁性
- 参与者关注具体性和清晰度

**启示**：
- 问卷设计需平衡简洁 vs 具体
- 不同利益相关者有不同偏好
- 需要多视角评估

### 4. 局限性

**评估规模**：
- 专家数量少（N=13）
- 单一研究主题（政治信任、气候变化）

**文化范围**：
- 只测试美国 → 南非
- 其他文化未验证

**LLM 限制**：
- 可能引入 LLM 偏见
- Persona 生成可能不具代表性
- 预测试结果需人工验证

---

## 📊 数据描述

### 实验数据

| 数据集 | 参与者 | 国家 | 主题 |
|--------|--------|------|------|
| **RQ1 Creation** | 238（Prolific）+ 13（专家）| 美国 | 政治信任 |
| **RQ2 Adaptation** | 118（Prolific）| 南非 | 气候变化 |

**Persona 数据**：
- 每个研究生成10个 Persona
- Persona 包含8+属性

**问卷数据**：
- RQ1：30个问题（政治信任）
- RQ2：30个问题（气候变化），5个需要适应

---

## 🎯 相关性评分

**评分**: **9/10 (P0)** ⭐⭐⭐

**理由**:

| 维度 | 评分 | 说明 |
|------|------|------|
| **研究领域** | 10/10 | CS + 社会科学，直接相关 |
| **核心问题** | 10/10 | 问卷生成 + 预测试 + 适应，完全匹配 |
| **方法论** | 9/10 | 完整流水线 + 真实参与者验证 |
| **技术实现** | 9/10 | 开源代码 + 详细 Prompt |

**关键价值**:
1. ✅ **完整流水线**：生成 + 预测试 + 适应
2. ✅ **Persona 驱动**：虚拟用户预测试
3. ✅ **真实验证**：238 + 118 + 13 专家
4. ✅ **开源资源**：代码和 Prompt 公开

---

## 📚 关键引用

**核心方法**：
- LLM-based Persona 模拟
- 自动问卷预测试
- 跨文化适应

**相关工作**：
- Survey Methodology
- Cross-cultural Adaptation
- LLM for Social Science

---

## 🔗 与其他论文的关联

### 在研究框架中的位置

```
虚拟用户 = Persona + Memory + 问卷生成

P05 Polypersona:  Persona + 问卷生成框架  ✅
P09 Generative Agents: Memory + 行为模拟  ✅
P13 LLM-S3: ✅ 评估框架 + 真实数据验证  ⭐
P14 Questioning Survey: ⚠️ 警告：调查回答不可靠  ⭐
P15 Guided Persona: ✅ Persona-based 引导式方法  ⭐
P16 Automated Questionnaires: ✅ 问卷生成 + 预测试 + 适应  ⭐⭐（本论文）
```

**核心组合**：
- P16 的预测试流水线 + P05 的问卷生成 + P13 的评估框架

---

## 🚀 可直接应用的技术

### 1. 完整预测试流水线

```python
def pretest_questionnaire(questionnaire, research_question):
    """完整预测试流水线"""
    # 1. 生成 Persona
    personas = generate_personas(research_question, num=10)
    
    # 2. Persona 扮演受访者
    transcripts = []
    for persona in personas:
        responses = []
        for question in questionnaire:
            response = persona_respond(persona, question)
            responses.append(response)
        transcripts.append({
            'persona': persona,
            'responses': responses
        })
    
    # 3. Reviewer 自动检测问题
    review = review_questionnaire(transcripts)
    
    # 4. 修改问卷
    modified_questionnaire = modify_based_on_review(
        questionnaire, review
    )
    
    return modified_questionnaire, review
```

### 2. 跨文化适应

```python
def adapt_questionnaire(original_questionnaire, target_country):
    """跨文化适应问卷"""
    adapted = []
    for question in original_questionnaire:
        prompt = f"""
        Adapt this question for {target_country}:
        {question}
        
        Consider:
        - Cultural context
        - Local terminology
        - Sensitive topics
        """
        adapted_question = llm.generate(prompt)
        adapted.append(adapted_question)
    
    return adapted
```

---

## 📝 总结

### 优点

1. ✅ **完整流水线**：生成 + 预测试 + 适应
2. ✅ **Persona 驱动**：虚拟用户预测试
3. ✅ **真实验证**：238 + 118 + 13 专家
4. ✅ **开源资源**：代码和 Prompt
5. ✅ **专家 vs 参与者对比**：揭示偏好差异

### 局限

1. ⚠️ **专家数量少**：N=13
2. ⚠️ **文化范围有限**：美国 → 南非
3. ⚠️ **LLM 偏见**：可能引入新偏见
4. ⚠️ **需人工验证**：预测试结果需人工确认

### 对本研究的价值

**核心借鉴**（⭐⭐⭐）:
1. **Persona 驱动预测试**：虚拟用户预测试问卷
2. **完整流水线**：生成 + 预测试 + 修改
3. **跨文化适应**：LLM 可适应问卷到不同文化
4. **Reviewer Prompt**：自动检测问卷问题

**必须采取的措施**:
1. ✅ **使用 Persona 预测试**：验证问卷质量
2. ✅ **平衡简洁 vs 具体**：考虑专家和参与者偏好
3. ✅ **真实数据验证**：对照 P11+P12+P14 警告
4. ✅ **多视角评估**：专家 + 参与者

---

## 🎯 下一步行动

1. ✅ 已完成：理解完整预测试流水线
2. ⏳ 待做：实现 Persona 生成和扮演
3. ⏳ 待做：结合 P05 问卷生成方法
4. ⏳ 待做：用 P13 框架评估

---

*阅读完成时间: 2026-02-28*
*阅读用时: 约20分钟*
*笔记字数: 约7000字*
