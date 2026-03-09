# P31-2025-OPeRA-Dataset 详细解读

## 基本信息

| 项目 | 内容 |
|------|------|
| **标题** | OPeRA: A Dataset of Observation, Persona, Rationale, and Action for Evaluating LLMs on Human Online Shopping Behavior Simulation |
| **作者** | Ziyi Wang, Yuxuan Lu, Wenbo Li et al. (Northeastern University, USC等) |
| **发表** | arXiv 2025.07 |
| **页数** | 18页 |
| **数据集** | https://huggingface.co/datasets/NEU-HAI/OPeRA |
| **相关性** | ⭐⭐⭐⭐ 高相关性（用户行为数据集+评估基准） |
| **评分** | 8/10 |

---

## 1. 核心问题

### 问题定义

能否准确模拟特定用户的下一个网页动作？

### 现有数据集局限

| 数据集类型 | 问题 |
|------------|------|
| **推荐数据集** | 仅记录稀疏、去语境化的用户动作，缺乏上下文 |
| **任务完成数据集** | 标注者生成或合成数据，缺乏真实性和个性化 |
| **共同缺陷** | 缺乏步骤级推理和persona信息 |

---

## 2. 核心贡献

### 2.1 OPeRA数据集

**首个综合捕获以下元素的公开数据集**：

| 元素 | 描述 | 表示 |
|------|------|------|
| **Observation** | 浏览器观察 | HTML + Screenshot |
| **Persona** | 用户画像 | Survey + Interview |
| **Rationale** | 动作理由 | 自然语言解释 |
| **Action** | 用户动作 | Click/Input/Terminate |

### 2.2 数据集规模

| 版本 | Sessions | Users | <Action, Obs> Pairs | Rationales |
|------|----------|-------|---------------------|------------|
| **OPeRA-full** | 692 | 51 | 28,904 | 604 |
| **OPeRA-filtered** | 527 | 51 | 5,856 | 207 |
| **OPeRA-test** | 90 | 15 | 992 actions | - |

---

## 3. 数据收集方法

### 3.1 参与者招募

**方法**: 雪球采样 (Snowball Sampling)

**筛选标准**:
- Amazon常客
- 计划未来几周在Amazon购物

**最终**: 84名候选 → 51名有效贡献者

### 3.2 Persona信息收集

**两部分**:

#### (1) 在线问卷 (Survey)

**三大板块**:

| 板块 | 内容 |
|------|------|
| **人口统计** | 年龄、性别、教育、职业、收入、居住地 |
| **购物偏好** | 购物频率、会员状态、购物习惯、季节性、广告信任、评论参与、配送影响、CSI量表(8项) |
| **性格特征** | Big-Five Inventory、MBTI |

#### (2) 半结构化访谈 (Interview, 可选)

**时长**: 20分钟

**内容**:
- 人口统计和个人背景
- 在线购物偏好

### 3.3 购物行为收集

**工具**: ShoppingFlow Chrome插件

**架构**:

```
Content Script (页面内)
├── Click Listener (点击监听)
├── Scroll Listener (滚动监听)
├── Input Listener (输入监听)
└── New Page Listener (页面监听)

Background Script (后台)
├── Page事件跟踪
├── 数据上传 (Amazon S3)
└── Rationale弹窗触发 (8%概率)
```

**Rationale收集**:
- 随机触发弹窗（8%概率）
- 问题: "You clicked on [button]. What made you decide to [action]?"

### 3.4 后处理

**隐私保护**:
1. 不记录PII页面（登录页、账户页、结账详情）
2. 规则自动检测和掩码PII（用户名、邮编、地址、支付信息）
3. 人工检查确保无PII

**会话分割**:
1. 时间阈值分割
2. 购买意图事件进一步分割（checkout/buy now/add to cart）

**动作过滤**:
- 丢弃少于5个动作的会话
- 移除非常见页面动作
- 过滤非交互区域点击
- 过滤Amazon Rufus相关动作

---

## 4. 数据集结构

### 4.1 User Persona

```
Pi = {Survey, Interview}

Survey:
- Demographics: Age, Gender, Income, Employment...
- Shopping Preferences: Monthly Spending, Brand Consciousness, Impulsiveness...
- Personality: MBTI, Big Five (Extraversion, Agreeableness...)

Interview (可选):
- 自由文本描述
- "I am a PhD student at xxx University..."
```

### 4.2 Action Traces

```
Aj = {a1, ..., aT}

动作空间:
- Click (带CSS selector和semantic_id)
- Input (带输入内容)
- Scroll (带起止位置)
- Navigate
- Tab Activate
- Terminate

语义标识示例:
- search_result.product_name
- product_detail.add_to_cart
- checkout.proceed
```

### 4.3 Web Observation

```
Oj = {o0, ..., oT}

每个ot包含:
- Full HTML (带clickable元素标注)
- Simplified HTML (关键元素)
- Screenshot
- Page Metadata (产品名、价格等)
- Purchase Info (如适用): Price, Title, ASIN
```

### 4.4 Rationale

```
Rj = {r1, ..., rT}

rk: 自然语言解释，可为null

示例:
"I clicked the button because it is cheaper with subscription."
"I've done a lot searching. This one has nice reviews and reasonable price."
```

---

## 5. 动作类型分布

### 5.1 OPeRA-full

| 动作类型 | 数量 | 百分比 |
|----------|------|--------|
| Scroll | 19,217 | 66.5% |
| Click | 5,253 | 18.1% |
| Tab Activate | 1,945 | 6.7% |
| Navigate | 1,901 | 6.6% |
| Text Input | 606 | 2.1% |
| **Total** | **28,904** | 100% |

### 5.2 OPeRA-filtered

| 动作类型 | 数量 | 百分比 |
|----------|------|--------|
| Click | 5,051 | 86.3% |
| Text Input | 597 | 10.2% |
| Terminate | 208 | 3.6% |
| **Total** | **5,856** | 100% |

### 5.3 Click子类型分布

| Click类型 | 数量 | 百分比 |
|-----------|------|--------|
| review | 1,052 | 20.8% |
| search | 763 | 15.1% |
| product_option | 700 | 13.9% |
| product_link | 537 | 10.6% |
| other | 449 | 8.9% |
| purchase | 321 | 6.4% |
| nav_bar | 283 | 5.6% |
| page_related | 198 | 3.9% |
| quantity | 191 | 3.8% |
| suggested_term | 182 | 3.6% |
| cart_side_bar | 145 | 2.9% |
| cart_page_select | 139 | 2.8% |
| filter | 91 | 1.8% |

---

## 6. 评估任务

### 6.1 Next Action Prediction

**任务定义**:

```
Input:
- History: {a1, ..., at-1}
- Web Context: {o1, ..., ot}
- Rationale: {r1, ..., rt-1}
- Persona: Pi

Output:
- Predicted Action: at

Function:
at = F(a1:t-1, r1:t-1, o1:t, Pi)
```

### 6.2 评估指标

| 指标 | 描述 |
|------|------|
| **Action Gen. Accuracy** | 精确匹配准确率（所有组件必须匹配） |
| **Action Type Macro F1** | 高层动作类别预测（click/input/terminate） |
| **Click Type Weighted F1** | 具体点击类型预测 |
| **Session Outcome Weighted F1** | 会话最终结果预测（purchase/terminate） |

---

## 7. 实验结果

### 7.1 主实验结果

**Table 6: Next Action Prediction性能**

| Model | Action Acc. | Action Type F1 | Click Type F1 | Outcome F1 |
|-------|-------------|----------------|---------------|------------|
| **GPT-4.1** | **21.51%** | **48.78%** | **44.47%** | 47.54% |
| DeepSeek-R1 | 14.75% | 27.37% | 35.12% | 46.36% |
| Claude-3.7 | 10.75% | 31.58% | 27.27% | 43.52% |
| LLaMA-3.3 | 8.31% | 24.29% | 19.99% | 36.64% |

### 7.2 消融研究

**w/o persona (移除persona信息)**:

| Model | Action Acc. | Action Type F1 | Click Type F1 | Outcome F1 |
|-------|-------------|----------------|---------------|------------|
| GPT-4.1 | 22.06% ↑ | 45.55% ↓ | 43.45% ↓ | **58.47%** ↑ |
| DeepSeek-R1 | 15.52% ↑ | 27.43% ↑ | 33.86% ↓ | 48.86% ↑ |
| Claude-3.7 | 10.75% → | 25.33% ↓ | 22.76% ↓ | 43.10% → |
| LLaMA-3.3 | 8.31% → | 23.69% ↓ | 18.59% ↓ | 33.21% ↓ |

**w/o rationale (移除rationale历史)**:

| Model | Action Acc. | Action Type F1 | Click Type F1 | Outcome F1 |
|-------|-------------|----------------|---------------|------------|
| GPT-4.1 | 21.28% ↓ | 34.93% ↓ | 42.63% ↓ | 51.17% ↓ |
| DeepSeek-R1 | 15.74% ↑ | 27.16% ↓ | 32.65% ↓ | 47.92% ↑ |
| Claude-3.7 | 10.08% ↓ | 26.06% ↓ | 20.29% ↓ | 43.10% → |
| LLaMA-3.3 | 8.76% ↑ | 23.60% ↓ | 19.22% ↓ | 34.19% ↑ |

### 7.3 关键发现

#### (1) LLM能力有限

- 最佳模型GPT-4.1: 仅21.51%动作预测准确率
- 所有模型表现远低于人类

#### (2) Persona作用不一致

- ✅ 对动作类型预测有帮助（提供用户偏好先验）
- ⚠️ 对精确动作预测有时引入噪音
- ⚠️ 当前模型难以深度整合persona到步骤级决策

#### (3) Rationale重要

- ✅ 移除rationale导致性能普遍下降
- ✅ 提供有价值的中间监督信号
- ✅ 帮助模型与合理用户意图对齐

#### (4) 上下文长度影响

- ✅ GPT-4.1（大context window）表现最好
- ⚠️ 其他模型受128k context限制

---

## 8. 与本研究的关系

### 8.1 可借鉴点

| 方面 | 借鉴内容 |
|------|---------|
| **数据集设计** | Persona + Rationale + Action三元组 |
| **Persona收集** | Survey + Interview双重收集方式 |
| **评估框架** | Next Action Prediction任务 |
| **消融方法** | w/o persona、w/o rationale消融研究 |

### 8.2 差异分析

| 维度 | OPeRA | 本研究 |
|------|-------|--------|
| **任务** | 网页行为预测 | 问卷响应生成 |
| **输入** | 观察序列（HTML） | 问题+选项 |
| **输出** | 动作（click/input） | 封闭式回答 |
| **一致性** | 时序一致性 | 跨问题态度一致性 |
| **数据集** | 购物行为 | 政治态度（ANES/GSS） |

### 8.3 整合建议

```
本研究可借鉴:
1. Persona收集方法: Survey + Interview
2. Rationale收集: 即时询问"为什么这样回答"
3. 评估框架: Next Response Prediction
4. 消融研究: w/o persona, w/o rationale
```

---

## 9. 局限性

1. **简化动作空间**: 省略滚动、页面导航
2. **未使用视觉信号**: 截图数据未在实验中使用
3. **用户数量有限**: 51名用户
4. **领域局限**: 仅在线购物场景

---

## 10. 未来方向

1. **多模态推理**: 整合截图视觉信息
2. **购买预测**: 基于用户行为的推荐
3. **意图推理**: 深度理解用户决策过程
4. **合成数据生成**: 可扩展的交互数据框架

---

## 11. 数据集获取

- **HuggingFace**: https://huggingface.co/datasets/NEU-HAI/OPeRA

---

## 12. 关键引用

```
@article{wang2025opera,
  title={OPeRA: A Dataset of Observation, Persona, Rationale, and Action for Evaluating LLMs on Human Online Shopping Behavior Simulation},
  author={Wang, Ziyi and Lu, Yuxuan and Li, Wenbo and others},
  journal={arXiv preprint arXiv:2506.05606},
  year={2025}
}
```

---

**解读时间**: 2026-03-08
**状态**: 详细解读完成
**字数**: ~11KB