#!/usr/bin/env python3
"""
评估脚本 - LLM-S³ Virtual Users Experiment

功能：
- KL散度计算（分布相似度）
- 准确率计算（Top-1/Top-3）
- Cohen's Kappa系数（一致性）
- 统计显著性检验

使用：
    from eval import Evaluator
    evaluator = Evaluator()
    metrics = evaluator.evaluate_all(real_responses, virtual_responses)
"""

import numpy as np
from scipy import stats
from scipy.special import kl_div
from sklearn.metrics import cohen_kappa_score, accuracy_score
from collections import Counter
from typing import List, Dict, Any, Tuple
import warnings
warnings.filterwarnings('ignore')


class Evaluator:
    """虚拟用户评估器"""
    
    def __init__(self, epsilon: float = 1e-10):
        """
        初始化评估器
        
        Args:
            epsilon: 避免除零的小常数
        """
        self.epsilon = epsilon
    
    # ==================== 分布相似度指标 ====================
    
    def kl_divergence(self, p: np.ndarray, q: np.ndarray) -> float:
        """
        计算KL散度 (Kullback-Leibler Divergence)
        
        KL(P || Q) = Σ P(x) * log(P(x) / Q(x))
        
        Args:
            p: 真实分布
            q: 预测分布
            
        Returns:
            KL散度值（越小越好，0表示完全一致）
        """
        # 确保是概率分布
        p = np.array(p, dtype=float)
        q = np.array(q, dtype=float)
        
        # 归一化
        p = p / (p.sum() + self.epsilon)
        q = q / (q.sum() + self.epsilon)
        
        # 避免零值
        p = np.clip(p, self.epsilon, 1.0)
        q = np.clip(q, self.epsilon, 1.0)
        
        # 计算KL散度
        kl = np.sum(p * np.log(p / q))
        
        return float(kl)
    
    def js_divergence(self, p: np.ndarray, q: np.ndarray) -> float:
        """
        计算JS散度 (Jensen-Shannon Divergence)
        JS散度是KL散度的对称版本，范围[0, 1]
        
        Args:
            p: 真实分布
            q: 预测分布
            
        Returns:
            JS散度值（越小越好）
        """
        p = np.array(p, dtype=float)
        q = np.array(q, dtype=float)
        
        p = p / (p.sum() + self.epsilon)
        q = q / (q.sum() + self.epsilon)
        
        m = 0.5 * (p + q)
        
        js = 0.5 * self.kl_divergence(p, m) + 0.5 * self.kl_divergence(q, m)
        
        return float(js)
    
    def distribution_similarity(self, p: np.ndarray, q: np.ndarray) -> float:
        """
        计算分布相似度（基于JS散度）
        
        Args:
            p: 真实分布
            q: 预测分布
            
        Returns:
            相似度 [0, 1]（越大越好）
        """
        js = self.js_divergence(p, q)
        return 1.0 - js
    
    # ==================== 准确率指标 ====================
    
    def top_k_accuracy(self, real: List[Any], pred: List[Any], k: int = 1) -> float:
        """
        计算Top-K准确率
        
        Args:
            real: 真实标签列表
            pred: 预测标签列表
            k: Top-K中的K值
            
        Returns:
            Top-K准确率
        """
        if len(real) != len(pred):
            raise ValueError("真实和预测列表长度必须相同")
        
        # 统计真实分布的Top-K
        real_counter = Counter(real)
        real_top_k = set([item for item, _ in real_counter.most_common(k)])
        
        # 统计预测分布的Top-K
        pred_counter = Counter(pred)
        pred_top_k = set([item for item, _ in pred_counter.most_common(k)])
        
        # 计算重叠度
        overlap = len(real_top_k & pred_top_k)
        
        return overlap / k
    
    def mode_match_accuracy(self, real: List[Any], pred: List[Any]) -> float:
        """
        计算众数匹配准确率
        
        Args:
            real: 真实标签列表
            pred: 预测标签列表
            
        Returns:
            1.0 如果众数匹配，否则 0.0
        """
        real_mode = Counter(real).most_common(1)[0][0]
        pred_mode = Counter(pred).most_common(1)[0][0]
        
        return 1.0 if real_mode == pred_mode else 0.0
    
    def exact_match_accuracy(self, real: List[Any], pred: List[Any]) -> float:
        """
        计算精确匹配准确率
        
        Args:
            real: 真实标签列表
            pred: 预测标签列表
            
        Returns:
            精确匹配比例
        """
        if len(real) != len(pred):
            raise ValueError("真实和预测列表长度必须相同")
        
        matches = sum(1 for r, p in zip(real, pred) if r == p)
        return matches / len(real)
    
    def jaccard_similarity(self, real: List[Any], pred: List[Any]) -> float:
        """
        计算Jaccard相似度（适用于多选题）
        
        Args:
            real: 真实选项集合
            pred: 预测选项集合
            
        Returns:
            Jaccard相似度 [0, 1]
        """
        real_set = set(real)
        pred_set = set(pred)
        
        if len(real_set | pred_set) == 0:
            return 1.0
        
        return len(real_set & pred_set) / len(real_set | pred_set)
    
    # ==================== 一致性指标 ====================
    
    def cohens_kappa(self, real: List[Any], pred: List[Any]) -> float:
        """
        计算Cohen's Kappa系数
        
        解释：
        - < 0: 不一致
        - 0-0.2: 轻微一致
        - 0.2-0.4: 一般一致
        - 0.4-0.6: 中等一致
        - 0.6-0.8: 强一致
        - 0.8-1.0: 几乎完全一致
        
        Args:
            real: 真实标签列表
            pred: 预测标签列表
            
        Returns:
            Kappa系数 [-1, 1]
        """
        if len(real) != len(pred):
            raise ValueError("真实和预测列表长度必须相同")
        
        return cohen_kappa_score(real, pred)
    
    def internal_consistency(self, responses_list: List[List[Any]]) -> float:
        """
        计算内部一致性（多次生成的一致度）
        
        Args:
            responses_list: 多次生成的响应列表，每个元素是一次生成的响应
            
        Returns:
            平均Kappa系数
        """
        if len(responses_list) < 2:
            return 1.0
        
        kappas = []
        for i in range(len(responses_list)):
            for j in range(i+1, len(responses_list)):
                try:
                    kappa = self.cohens_kappa(responses_list[i], responses_list[j])
                    kappas.append(kappa)
                except:
                    continue
        
        return np.mean(kappas) if kappas else 0.0
    
    # ==================== 统计检验 ====================
    
    def chi_square_test(self, real: List[Any], pred: List[Any]) -> Dict[str, float]:
        """
        卡方检验（检验分布差异）
        
        Args:
            real: 真实标签列表
            pred: 预测标签列表
            
        Returns:
            包含统计量和p值的字典
        """
        # 构建列联表
        real_counter = Counter(real)
        pred_counter = Counter(pred)
        
        all_labels = sorted(set(real) | set(pred))
        
        observed = np.array([
            [real_counter.get(label, 0), pred_counter.get(label, 0)]
            for label in all_labels
        ])
        
        # 执行卡方检验
        chi2, p_value, dof, expected = stats.chi2_contingency(observed)
        
        return {
            'statistic': float(chi2),
            'p_value': float(p_value),
            'dof': int(dof),
            'significant': p_value < 0.05
        }
    
    def t_test(self, real: List[float], pred: List[float]) -> Dict[str, float]:
        """
        独立样本t检验
        
        Args:
            real: 真实数值列表
            pred: 预测数值列表
            
        Returns:
            包含统计量、p值和效应量的字典
        """
        t_stat, p_value = stats.ttest_ind(real, pred)
        
        # Cohen's d 效应量
        mean_diff = np.mean(real) - np.mean(pred)
        pooled_std = np.sqrt((np.std(real)**2 + np.std(pred)**2) / 2)
        cohens_d = mean_diff / (pooled_std + self.epsilon)
        
        return {
            'statistic': float(t_stat),
            'p_value': float(p_value),
            'cohens_d': float(cohens_d),
            'significant': p_value < 0.05
        }
    
    def ks_test(self, real: List[float], pred: List[float]) -> Dict[str, float]:
        """
        Kolmogorov-Smirnov检验（分布差异）
        
        Args:
            real: 真实数值列表
            pred: 预测数值列表
            
        Returns:
            包含统计量和p值的字典
        """
        ks_stat, p_value = stats.ks_2samp(real, pred)
        
        return {
            'statistic': float(ks_stat),
            'p_value': float(p_value),
            'significant': p_value < 0.05
        }
    
    # ==================== 综合评估 ====================
    
    def evaluate_single_question(
        self,
        real_answers: List[Any],
        virtual_answers: List[Any],
        question_type: str = "single_choice"
    ) -> Dict[str, float]:
        """
        评估单个问题
        
        Args:
            real_answers: 真实用户答案列表
            virtual_answers: 虚拟用户答案列表
            question_type: 问题类型 (single_choice/multiple_choice/likert_scale/open_ended)
            
        Returns:
            评估指标字典
        """
        metrics = {}
        
        if question_type == "single_choice":
            # 单选题
            metrics['mode_match'] = self.mode_match_accuracy(real_answers, virtual_answers)
            metrics['top3_accuracy'] = self.top_k_accuracy(real_answers, virtual_answers, k=3)
            
            # 分布相似度
            real_dist = self._get_distribution(real_answers)
            virtual_dist = self._get_distribution(virtual_answers, len(real_dist))
            metrics['distribution_similarity'] = self.distribution_similarity(real_dist, virtual_dist)
            metrics['kl_divergence'] = self.kl_divergence(real_dist, virtual_dist)
            
            # Kappa
            try:
                metrics['kappa'] = self.cohens_kappa(real_answers, virtual_answers)
            except:
                metrics['kappa'] = 0.0
            
            # 统计检验
            chi2_result = self.chi_square_test(real_answers, virtual_answers)
            metrics['chi_square_p'] = chi2_result['p_value']
        
        elif question_type == "multiple_choice":
            # 多选题（假设每个答案是选项列表）
            jaccard_scores = [
                self.jaccard_similarity(r, v)
                for r, v in zip(real_answers, virtual_answers)
            ]
            metrics['jaccard_similarity'] = np.mean(jaccard_scores)
        
        elif question_type == "likert_scale":
            # 李克特量表
            real_numeric = [float(x) for x in real_answers]
            virtual_numeric = [float(x) for x in virtual_answers]
            
            metrics['mean_error'] = abs(np.mean(real_numeric) - np.mean(virtual_numeric))
            
            # 分布相似度
            real_dist = self._get_distribution(real_answers)
            virtual_dist = self._get_distribution(virtual_answers, len(real_dist))
            metrics['distribution_similarity'] = self.distribution_similarity(real_dist, virtual_dist)
            metrics['kl_divergence'] = self.kl_divergence(real_dist, virtual_dist)
            
            # 统计检验
            t_result = self.t_test(real_numeric, virtual_numeric)
            metrics['t_test_p'] = t_result['p_value']
            metrics['cohens_d'] = t_result['cohens_d']
            
            ks_result = self.ks_test(real_numeric, virtual_numeric)
            metrics['ks_test_p'] = ks_result['p_value']
        
        return metrics
    
    def evaluate_all(
        self,
        real_responses: List[Dict[str, Any]],
        virtual_responses: List[Dict[str, Any]],
        questions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        全面评估所有问题
        
        Args:
            real_responses: 真实用户响应列表 [{'q1': 'A', 'q2': 5, ...}, ...]
            virtual_responses: 虚拟用户响应列表
            questions: 问题定义列表 [{'id': 'q1', 'type': 'single_choice', ...}, ...]
            
        Returns:
            综合评估结果
        """
        results = {
            'per_question': {},
            'aggregate': {}
        }
        
        # 逐题评估
        for question in questions:
            q_id = question['id']
            q_type = question['type']
            
            real_answers = [r[q_id] for r in real_responses if q_id in r]
            virtual_answers = [v[q_id] for v in virtual_responses if q_id in v]
            
            if len(real_answers) > 0 and len(virtual_answers) > 0:
                results['per_question'][q_id] = self.evaluate_single_question(
                    real_answers, virtual_answers, q_type
                )
        
        # 聚合指标
        if results['per_question']:
            # 平均分布相似度
            dist_sims = [
                m['distribution_similarity']
                for m in results['per_question'].values()
                if 'distribution_similarity' in m
            ]
            results['aggregate']['avg_distribution_similarity'] = np.mean(dist_sims) if dist_sims else 0.0
            
            # 平均KL散度
            kl_divs = [
                m['kl_divergence']
                for m in results['per_question'].values()
                if 'kl_divergence' in m
            ]
            results['aggregate']['avg_kl_divergence'] = np.mean(kl_divs) if kl_divs else 0.0
            
            # 平均Kappa
            kappas = [
                m['kappa']
                for m in results['per_question'].values()
                if 'kappa' in m
            ]
            results['aggregate']['avg_kappa'] = np.mean(kappas) if kappas else 0.0
            
            # 统计显著问题数
            sig_count = sum(
                1 for m in results['per_question'].values()
                if m.get('chi_square_p', 1.0) < 0.05 or m.get('t_test_p', 1.0) < 0.05
            )
            results['aggregate']['significant_questions'] = sig_count
            results['aggregate']['total_questions'] = len(results['per_question'])
        
        return results
    
    # ==================== 辅助函数 ====================
    
    def _get_distribution(self, answers: List[Any], num_bins: int = None) -> np.ndarray:
        """
        将答案转换为分布
        
        Args:
            answers: 答案列表
            num_bins: 分箱数（用于连续变量）
            
        Returns:
            概率分布数组
        """
        counter = Counter(answers)
        
        if num_bins is not None:
            # 确保分布长度一致
            all_labels = sorted(counter.keys())
            if len(all_labels) < num_bins:
                # 补齐
                distribution = np.zeros(num_bins)
                for label, count in counter.items():
                    idx = all_labels.index(label) if label in all_labels else 0
                    if idx < num_bins:
                        distribution[idx] = count
            else:
                distribution = np.array([counter.get(label, 0) for label in all_labels[:num_bins]])
        else:
            all_labels = sorted(counter.keys())
            distribution = np.array([counter[label] for label in all_labels])
        
        return distribution


def print_evaluation_results(results: Dict[str, Any]):
    """打印评估结果"""
    print("\n" + "="*60)
    print("评估结果")
    print("="*60)
    
    print("\n【聚合指标】")
    agg = results.get('aggregate', {})
    print(f"  平均分布相似度: {agg.get('avg_distribution_similarity', 0):.4f}")
    print(f"  平均KL散度: {agg.get('avg_kl_divergence', 0):.4f}")
    print(f"  平均Kappa系数: {agg.get('avg_kappa', 0):.4f}")
    print(f"  统计显著问题: {agg.get('significant_questions', 0)}/{agg.get('total_questions', 0)}")
    
    print("\n【逐题详情】")
    for q_id, metrics in results.get('per_question', {}).items():
        print(f"\n  {q_id}:")
        for metric, value in metrics.items():
            if isinstance(value, float):
                print(f"    {metric}: {value:.4f}")
            else:
                print(f"    {metric}: {value}")


# ==================== 示例使用 ====================

if __name__ == "__main__":
    # 模拟数据
    real_responses = [
        {'q1': 'A', 'q2': 5, 'q3': ['price', 'quality']},
        {'q1': 'A', 'q2': 4, 'q3': ['price']},
        {'q1': 'B', 'q2': 5, 'q3': ['quality', 'brand']},
        {'q1': 'A', 'q2': 3, 'q3': ['price']},
        {'q1': 'B', 'q2': 4, 'q3': ['brand']},
    ]
    
    virtual_responses = [
        {'q1': 'A', 'q2': 4, 'q3': ['price', 'quality']},
        {'q1': 'A', 'q2': 5, 'q3': ['price']},
        {'q1': 'B', 'q2': 5, 'q3': ['quality']},
        {'q1': 'A', 'q2': 4, 'q3': ['price', 'brand']},
        {'q1': 'B', 'q2': 4, 'q3': ['brand']},
    ]
    
    questions = [
        {'id': 'q1', 'type': 'single_choice'},
        {'id': 'q2', 'type': 'likert_scale'},
        {'id': 'q3', 'type': 'multiple_choice'},
    ]
    
    # 评估
    evaluator = Evaluator()
    results = evaluator.evaluate_all(real_responses, virtual_responses, questions)
    
    # 打印结果
    print_evaluation_results(results)
