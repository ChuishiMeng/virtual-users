"""
评估指标模块

实现 KL 散度、JS 距离、准确率等评估指标
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from scipy import stats
from scipy.spatial.distance import jensenshannon
from scipy.stats import wasserstein_distance, entropy
from sklearn.metrics import accuracy_score, f1_score, cohen_kappa_score
import warnings


@dataclass
class EvaluationResult:
    """评估结果"""
    metric_name: str
    value: float
    std: Optional[float] = None
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None
    p_value: Optional[float] = None
    effect_size: Optional[float] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def __str__(self) -> str:
        parts = [f"{self.metric_name}: {self.value:.4f}"]
        if self.std is not None:
            parts.append(f"±{self.std:.4f}")
        if self.ci_lower is not None and self.ci_upper is not None:
            parts.append(f"[{self.ci_lower:.4f}, {self.ci_upper:.4f}]")
        if self.p_value is not None:
            parts.append(f"p={self.p_value:.4f}")
        return " ".join(parts)


class DistributionMetrics:
    """分布对齐指标"""
    
    @staticmethod
    def kl_divergence(p: np.ndarray, q: np.ndarray, epsilon: float = 1e-10) -> float:
        """
        计算 KL 散度 D_KL(P || Q)
        
        Args:
            p: 真实分布
            q: 预测分布
            epsilon: 平滑参数，避免 log(0)
        
        Returns:
            KL 散度值（越小越好）
        """
        p = np.asarray(p, dtype=float)
        q = np.asarray(q, dtype=float)
        
        # 归一化
        p = p / p.sum()
        q = q / q.sum()
        
        # 平滑
        p = np.clip(p, epsilon, 1)
        q = np.clip(q, epsilon, 1)
        
        # 重新归一化
        p = p / p.sum()
        q = q / q.sum()
        
        return float(entropy(p, q))
    
    @staticmethod
    def js_distance(p: np.ndarray, q: np.ndarray, epsilon: float = 1e-10) -> float:
        """
        计算 JS 距离
        
        Args:
            p: 真实分布
            q: 预测分布
            epsilon: 平滑参数
        
        Returns:
            JS 距离值 [0, 1]，越小越好
        """
        p = np.asarray(p, dtype=float)
        q = np.asarray(q, dtype=float)
        
        # 归一化
        p = p / p.sum()
        q = q / q.sum()
        
        return float(jensenshannon(p, q))
    
    @staticmethod
    def js_divergence(p: np.ndarray, q: np.ndarray) -> float:
        """计算 JS 散度（距离的平方）"""
        js_dist = DistributionMetrics.js_distance(p, q)
        return js_dist ** 2
    
    @staticmethod
    def wasserstein(p_values: np.ndarray, q_values: np.ndarray,
                   p_weights: Optional[np.ndarray] = None,
                   q_weights: Optional[np.ndarray] = None) -> float:
        """
        计算 Wasserstein 距离（推土机距离）
        
        Args:
            p_values: 真实分布的值
            q_values: 预测分布的值
            p_weights: 真实分布的权重
            q_weights: 预测分布的权重
        
        Returns:
            Wasserstein 距离，越小越好
        """
        if p_weights is None:
            p_weights = np.ones(len(p_values)) / len(p_values)
        if q_weights is None:
            q_weights = np.ones(len(q_values)) / len(q_values)
        
        return float(wasserstein_distance(p_values, q_values, p_weights, q_weights))
    
    @staticmethod
    def total_variation(p: np.ndarray, q: np.ndarray) -> float:
        """计算总变差距离"""
        p = np.asarray(p, dtype=float)
        q = np.asarray(q, dtype=float)
        
        p = p / p.sum()
        q = q / q.sum()
        
        return float(0.5 * np.abs(p - q).sum())


class AccuracyMetrics:
    """准确性指标"""
    
    @staticmethod
    def accuracy(y_true: List, y_pred: List) -> float:
        """计算准确率"""
        return float(accuracy_score(y_true, y_pred))
    
    @staticmethod
    def top_k_accuracy(y_true: List, y_pred_list: List[List], k: int = 3) -> float:
        """
        计算 Top-K 准确率
        
        Args:
            y_true: 真实标签
            y_pred_list: 预测的排序列表（每个元素是一个列表，按置信度排序）
            k: 考虑前 k 个预测
        
        Returns:
            Top-K 准确率
        """
        correct = 0
        for true, pred in zip(y_true, y_pred_list):
            if true in pred[:k]:
                correct += 1
        return correct / len(y_true) if y_true else 0.0
    
    @staticmethod
    def f1(y_true: List, y_pred: List, average: str = 'macro') -> float:
        """计算 F1 分数"""
        return float(f1_score(y_true, y_pred, average=average, zero_division=0))
    
    @staticmethod
    def balanced_accuracy(y_true: List, y_pred: List) -> float:
        """计算平衡准确率"""
        from sklearn.metrics import balanced_accuracy_score
        return float(balanced_accuracy_score(y_true, y_pred))


class ConsistencyMetrics:
    """一致性指标"""
    
    @staticmethod
    def cohen_kappa(y1: List, y2: List) -> float:
        """
        计算 Cohen's Kappa
        
        Args:
            y1: 第一次观测结果
            y2: 第二次观测结果
        
        Returns:
            Kappa 值 [-1, 1]，>0.7 为强一致
        """
        return float(cohen_kappa_score(y1, y2))
    
    @staticmethod
    def self_consistency(responses_t1: List, responses_t2: List) -> float:
        """
        计算自一致性
        
        Args:
            responses_t1: 第一次响应
            responses_t2: 第二次响应
        
        Returns:
            一致性比例 [0, 1]
        """
        if len(responses_t1) != len(responses_t2):
            warnings.warn("Response lists have different lengths")
            min_len = min(len(responses_t1), len(responses_t2))
            responses_t1 = responses_t1[:min_len]
            responses_t2 = responses_t2[:min_len]
        
        matches = sum(1 for r1, r2 in zip(responses_t1, responses_t2) if r1 == r2)
        return matches / len(responses_t1) if responses_t1 else 0.0
    
    @staticmethod
    def cronbach_alpha(items: np.ndarray) -> float:
        """
        计算 Cronbach's Alpha（内部一致性）
        
        Args:
            items: 二维数组，每行是一个被试，每列是一个题项
        
        Returns:
            Alpha 值 [0, 1]，>0.8 为优秀信度
        """
        items = np.asarray(items)
        n_items = items.shape[1]
        
        if n_items < 2:
            return 1.0
        
        # 计算方差
        item_variances = items.var(axis=0, ddof=1)
        total_variance = items.sum(axis=1).var(ddof=1)
        
        # Cronbach's Alpha
        alpha = (n_items / (n_items - 1)) * (1 - item_variances.sum() / total_variance)
        
        return float(alpha)


class DiversityMetrics:
    """多样性指标"""
    
    @staticmethod
    def entropy(dist: np.ndarray, base: int = 2, normalize: bool = True) -> float:
        """
        计算信息熵
        
        Args:
            dist: 分布
            base: 对数底数
            normalize: 是否归一化
        
        Returns:
            熵值
        """
        dist = np.asarray(dist, dtype=float)
        dist = dist / dist.sum()
        dist = dist[dist > 0]  # 移除零
        
        if base == 2:
            h = -np.sum(dist * np.log2(dist))
        elif base == 10:
            h = -np.sum(dist * np.log10(dist))
        else:
            h = -np.sum(dist * np.log(dist))
        
        if normalize:
            max_entropy = np.log(len(dist)) / np.log(base) if base != 2 else np.log2(len(dist))
            if max_entropy > 0:
                h = h / max_entropy
        
        return float(h)
    
    @staticmethod
    def gini_coefficient(values: np.ndarray) -> float:
        """
        计算 Gini 系数
        
        Args:
            values: 数值数组
        
        Returns:
            Gini 系数 [0, 1]，0 表示完全平等
        """
        values = np.asarray(values, dtype=float)
        values = values.flatten()
        
        if np.amin(values) < 0:
            values -= np.amin(values)
        
        values = np.sort(values)
        n = len(values)
        
        if n == 0:
            return 0.0
        
        index = np.arange(1, n + 1)
        return float((2 * np.sum(index * values) - (n + 1) * np.sum(values)) / (n * np.sum(values)))
    
    @staticmethod
    def simpson_index(dist: np.ndarray) -> float:
        """计算 Simpson 多样性指数"""
        dist = np.asarray(dist, dtype=float)
        dist = dist / dist.sum()
        return float(1 - np.sum(dist ** 2))


class StatisticalTests:
    """统计检验"""
    
    @staticmethod
    def paired_t_test(group1: np.ndarray, group2: np.ndarray) -> Tuple[float, float]:
        """
        配对 t 检验
        
        Returns:
            (t 统计量, p 值)
        """
        t_stat, p_value = stats.ttest_rel(group1, group2)
        return float(t_stat), float(p_value)
    
    @staticmethod
    def wilcoxon_test(group1: np.ndarray, group2: np.ndarray) -> Tuple[float, float]:
        """
        Wilcoxon 符号秩检验（非参数）
        
        Returns:
            (统计量, p 值)
        """
        try:
            stat, p_value = stats.wilcoxon(group1, group2)
            return float(stat), float(p_value)
        except ValueError:
            return 0.0, 1.0
    
    @staticmethod
    def cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
        """
        计算 Cohen's d（效应量）
        
        Returns:
            d 值，<0.2 小效应，0.5 中效应，>0.8 大效应
        """
        n1, n2 = len(group1), len(group2)
        var1, var2 = group1.var(ddof=1), group2.var(ddof=1)
        
        # 合并标准差
        pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        
        if pooled_std == 0:
            return 0.0
        
        d = (group1.mean() - group2.mean()) / pooled_std
        return float(d)
    
    @staticmethod
    def bootstrap_ci(data: np.ndarray, n_bootstrap: int = 1000, 
                    confidence: float = 0.95, statistic: str = 'mean') -> Tuple[float, float]:
        """
        Bootstrap 置信区间
        
        Args:
            data: 数据
            n_bootstrap: Bootstrap 次数
            confidence: 置信水平
            statistic: 统计量 ('mean', 'median', 'std')
        
        Returns:
            (下界, 上界)
        """
        data = np.asarray(data)
        bootstrap_stats = []
        
        for _ in range(n_bootstrap):
            sample = np.random.choice(data, size=len(data), replace=True)
            
            if statistic == 'mean':
                bootstrap_stats.append(sample.mean())
            elif statistic == 'median':
                bootstrap_stats.append(np.median(sample))
            elif statistic == 'std':
                bootstrap_stats.append(sample.std())
        
        alpha = 1 - confidence
        lower = np.percentile(bootstrap_stats, alpha / 2 * 100)
        upper = np.percentile(bootstrap_stats, (1 - alpha / 2) * 100)
        
        return float(lower), float(upper)


class Evaluator:
    """综合评估器"""
    
    def __init__(self, metrics: Optional[List[str]] = None):
        """
        初始化评估器
        
        Args:
            metrics: 要计算的指标列表
        """
        self.metrics = metrics or [
            'kl_divergence', 'js_distance', 'accuracy', 
            'cohen_kappa', 'entropy'
        ]
    
    def evaluate(
        self,
        real_distribution: Dict[str, float],
        predicted_distribution: Dict[str, float],
        real_responses: Optional[List] = None,
        predicted_responses: Optional[List] = None
    ) -> Dict[str, EvaluationResult]:
        """
        综合评估
        
        Args:
            real_distribution: 真实分布 {选项: 概率}
            predicted_distribution: 预测分布
            real_responses: 真实响应列表（可选）
            predicted_responses: 预测响应列表（可选）
        
        Returns:
            指标名 -> EvaluationResult 的字典
        """
        results = {}
        
        # 确保分布对齐
        all_keys = sorted(set(real_distribution.keys()) | set(predicted_distribution.keys()))
        p = np.array([real_distribution.get(k, 1e-10) for k in all_keys])
        q = np.array([predicted_distribution.get(k, 1e-10) for k in all_keys])
        
        # 分布指标
        if 'kl_divergence' in self.metrics:
            results['kl_divergence'] = EvaluationResult(
                metric_name='kl_divergence',
                value=DistributionMetrics.kl_divergence(p, q),
                metadata={'n_options': len(all_keys)}
            )
        
        if 'js_distance' in self.metrics:
            results['js_distance'] = EvaluationResult(
                metric_name='js_distance',
                value=DistributionMetrics.js_distance(p, q)
            )
        
        if 'wasserstein' in self.metrics:
            # 对于分类数据，使用索引作为值
            indices = np.arange(len(all_keys))
            results['wasserstein'] = EvaluationResult(
                metric_name='wasserstein',
                value=DistributionMetrics.wasserstein(indices, indices, p, q)
            )
        
        if 'total_variation' in self.metrics:
            results['total_variation'] = EvaluationResult(
                metric_name='total_variation',
                value=DistributionMetrics.total_variation(p, q)
            )
        
        # 准确性指标
        if real_responses and predicted_responses:
            if 'accuracy' in self.metrics:
                results['accuracy'] = EvaluationResult(
                    metric_name='accuracy',
                    value=AccuracyMetrics.accuracy(real_responses, predicted_responses),
                    metadata={'n_samples': len(real_responses)}
                )
            
            if 'f1' in self.metrics:
                results['f1'] = EvaluationResult(
                    metric_name='f1',
                    value=AccuracyMetrics.f1(real_responses, predicted_responses)
                )
            
            if 'cohen_kappa' in self.metrics:
                results['cohen_kappa'] = EvaluationResult(
                    metric_name='cohen_kappa',
                    value=ConsistencyMetrics.cohen_kappa(real_responses, predicted_responses)
                )
        
        # 多样性指标
        if 'entropy' in self.metrics:
            results['entropy'] = EvaluationResult(
                metric_name='entropy',
                value=DiversityMetrics.entropy(q, normalize=True)
            )
        
        return results
    
    def compare_methods(
        self,
        real_distribution: Dict[str, float],
        method_predictions: Dict[str, Dict[str, float]],
        real_responses: Optional[List] = None,
        method_response_lists: Optional[Dict[str, List]] = None
    ) -> Dict[str, Dict[str, EvaluationResult]]:
        """
        对比多个方法
        
        Args:
            real_distribution: 真实分布
            method_predictions: {方法名: 预测分布}
            real_responses: 真实响应
            method_response_lists: {方法名: 响应列表}
        
        Returns:
            {方法名: {指标名: EvaluationResult}}
        """
        all_results = {}
        
        for method_name, pred_dist in method_predictions.items():
            pred_responses = None
            if method_response_lists and method_name in method_response_lists:
                pred_responses = method_response_lists[method_name]
            
            all_results[method_name] = self.evaluate(
                real_distribution, pred_dist, real_responses, pred_responses
            )
        
        return all_results


if __name__ == "__main__":
    # 测试评估指标
    print("测试评估指标...")
    
    # 真实分布和预测分布
    real_dist = {'A': 0.4, 'B': 0.3, 'C': 0.2, 'D': 0.1}
    pred_dist = {'A': 0.35, 'B': 0.35, 'C': 0.2, 'D': 0.1}
    
    # 真实响应和预测响应
    real_responses = ['A', 'B', 'A', 'C', 'B', 'A', 'B', 'C', 'A', 'D']
    pred_responses = ['A', 'B', 'A', 'B', 'B', 'A', 'A', 'C', 'A', 'C']
    
    # 创建评估器
    evaluator = Evaluator()
    
    # 评估
    results = evaluator.evaluate(real_dist, pred_dist, real_responses, pred_responses)
    
    print("\n评估结果:")
    for name, result in results.items():
        print(f"  {result}")
    
    # 测试多方法对比
    print("\n多方法对比:")
    method_predictions = {
        'random': {'A': 0.25, 'B': 0.25, 'C': 0.25, 'D': 0.25},
        'llm_prompt': {'A': 0.38, 'B': 0.32, 'C': 0.18, 'D': 0.12},
        'ours': {'A': 0.39, 'B': 0.31, 'C': 0.2, 'D': 0.1}
    }
    
    comparison = evaluator.compare_methods(real_dist, method_predictions)
    
    for method, metrics in comparison.items():
        print(f"\n  {method}:")
        for metric_name, result in metrics.items():
            print(f"    {result}")
    
    # 测试统计检验
    print("\n统计检验:")
    group1 = np.array([0.4, 0.42, 0.38, 0.41, 0.39])
    group2 = np.array([0.5, 0.52, 0.48, 0.51, 0.49])
    
    t_stat, p_value = StatisticalTests.paired_t_test(group1, group2)
    d = StatisticalTests.cohens_d(group1, group2)
    ci = StatisticalTests.bootstrap_ci(group1)
    
    print(f"  t-test: t={t_stat:.3f}, p={p_value:.4f}")
    print(f"  Cohen's d: {d:.3f}")
    print(f"  95% CI: [{ci[0]:.3f}, {ci[1]:.3f}]")
