# 研究上下文 - 2026-02-23

## 当前状态

**项目**: 虚拟用户调研研究
**位置**: `~/.openclaw/workspace/research/virtual-users/`
**版本**: v3 (聚焦跨问题一致性)

---

## 已完成的工作

### 1. 文件夹整理 ✅
- 按版本归档：`versions/v1/`, `versions/v2/`
- 新建 `current/` 目录用于 v3 工作
- 文献清单放在 `literature/`
- 旧文件归档到 `archive/`

### 2. 文献调研 ✅
- 35+篇核心文献已整理
- 关键发现：
  - Abdulhai et al. (NeurIPS 2025): 对话一致性度量
  - 现有工作关注分布匹配，忽视跨问题态度一致性
  - 差异化点：聚焦 "跨问题态度一致性"

### 3. 研究定位确定 ✅
- **核心洞察**: "分布匹配 ≠ 行为真实"
- **核心贡献**:
  1. CQCB (Cross-Question Consistency Benchmark)
  2. ACS (Attitude Consistency Score)
  3. ConsistAgent 方法

---

## 下一步计划

### Week 1: 代码补全 + 基线
- [ ] 创建 `requirements.txt`
- [ ] 创建 `config/default.yaml`
- [ ] 实现 `experiments/run_experiment.py`
- [ ] 下载 ANES 数据
- [ ] 运行 5 个基线

### Week 2: 核心方法 + 实验
- [ ] 实现 ConsistAgent
- [ ] 实现 ACS 指标
- [ ] 运行主实验
- [ ] 消融实验

### Week 3: 论文 + 投稿
- [ ] 结果分析
- [ ] 论文更新
- [ ] 图表制作

---

## 关键文件位置

```
~/.openclaw/workspace/research/virtual-users/
├── current/          # v3 工作目录
├── literature/       # 文献清单
├── code/             # 代码实现
└── versions/         # 历史版本
```

---

## 重要决策

1. **研究定位**: 聚焦"一致性"，不做大而全的框架
2. **实验规模**: MVP (2领域/5基线)
3. **资源**: 无GPU，使用coding plan的LLM
4. **数据**: 使用开源数据集 (ANES, GSS)
