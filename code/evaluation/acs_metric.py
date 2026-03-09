#!/usr/bin/env python3
"""
ACS (Attitude Consistency Score) Metric
态度一致性分数评估指标

This module implements the Attitude Consistency Score (ACS) metric for evaluating
cross-question consistency in virtual user responses.
"""

from typing import Dict, List, Any, Tuple, Optional
import numpy as np
from dataclasses import dataclass
import json
from pathlib import Path

from data.cqcb_benchmark import ConsistencyConstraint, CQCBInstance
from eval import Evaluator


@dataclass
class ACSResult:
    """ACS评估结果"""

    overall_score: float
    domain_scores: Dict[str, float]
    constraint_scores: Dict[str, float]
    detailed_results: Dict[str, Any]


class ACSMetric:
    """Attitude Consistency Score 评估指标"""

    def __init__(self, epsilon: float = 1e-8):
        self.epsilon = epsilon

    def evaluate_consistency(
        self, responses: List[Dict[str, Any]], constraints: List[ConsistencyConstraint]
    ) -> ACSResult:
        """
        评估响应的一致性

        Args:
            responses: 虚拟用户响应列表
            constraints: 一致性约束列表

        Returns:
            ACSResult: 评估结果
        """
        # 计算每个约束的一致性得分
        constraint_scores = {}
        domain_scores = {}
        domain_counts = {}

        for constraint in constraints:
            score = self._evaluate_constraint(responses, constraint)
            constraint_scores[constraint.constraint_id] = score

            # 累积领域得分
            domain = constraint.domain
            if domain not in domain_scores:
                domain_scores[domain] = 0.0
                domain_counts[domain] = 0
            domain_scores[domain] += score
            domain_counts[domain] += 1

        # 计算平均领域得分
        for domain in domain_scores:
            domain_scores[domain] /= domain_counts[domain]

        # 计算总体得分
        overall_score = np.mean(list(constraint_scores.values()))

        return ACSResult(
            overall_score=float(overall_score),
            domain_scores=domain_scores,
            constraint_scores=constraint_scores,
            detailed_results={
                "constraint_count": len(constraints),
                "response_count": len(responses),
                "domains": list(domain_scores.keys()),
            },
        )

    def _evaluate_constraint(
        self, responses: List[Dict[str, Any]], constraint: ConsistencyConstraint
    ) -> float:
        """
        评估单个约束的一致性

        Args:
            responses: 响应列表
            constraint: 一致性约束

        Returns:
            一致性得分 (0-1)
        """
        q1, q2 = constraint.question_pair
        consistent_count = 0
        total_count = 0

        for response in responses:
            if q1 in response and q2 in response:
                r1, r2 = response[q1], response[q2]
                if self._check_consistency(r1, r2, constraint):
                    consistent_count += 1
                total_count += 1

        if total_count == 0:
            return 0.0

        return consistent_count / total_count

    def _check_consistency(
        self, response1: Any, response2: Any, constraint: ConsistencyConstraint
    ) -> bool:
        """
        检查两个响应是否一致

        Args:
            response1: 第一个问题的响应
            response2: 第二个问题的响应
            constraint: 一致性约束

        Returns:
            是否一致
        """
        # 根据约束类型进行一致性检查
        if constraint.constraint_type == "logical":
            return self._check_logical_consistency(response1, response2, constraint)
        elif constraint.constraint_type == "semantic":
            return self._check_semantic_consistency(response1, response2, constraint)
        elif constraint.constraint_type == "value-based":
            return self._check_value_consistency(response1, response2, constraint)
        else:
            # 默认使用语义一致性
            return self._check_semantic_consistency(response1, response2, constraint)

    def _check_logical_consistency(
        self, response1: Any, response2: Any, constraint: ConsistencyConstraint
    ) -> bool:
        """检查逻辑一致性"""
        # Party ID and Presidential Vote consistency
        if (
            "party_id" in constraint.question_pair
            and "presidential_vote" in constraint.question_pair
        ):
            party_to_candidate = {
                "Democrat": "Biden",
                "Republican": "Trump",
                "Independent": None,  # Independent can vote for anyone
                "Other": None,
            }

            if response1 in party_to_candidate and response2 in ["Biden", "Trump"]:
                expected = party_to_candidate[response1]
                if expected is None:
                    return True  # Independent/Other can vote for anyone
                return response2 == expected

        # Economy rating and Country direction consistency
        if (
            "economy_rating" in constraint.question_pair
            and "country_direction" in constraint.question_pair
        ):
            # Better economy should correlate with "Right" direction
            if response1 == "Better" and response2 == "Right":
                return True
            if response1 == "Worse" and response2 == "Wrong":
                return True
            if response1 == "Same":
                return True  # Neutral on economy can have any view on direction

        # Party ID and Country direction consistency
        if (
            "party_id" in constraint.question_pair
            and "country_direction" in constraint.question_pair
        ):
            party_to_direction = {
                "Democrat": "Right",  # Assuming current political context
                "Republican": "Wrong",
                "Independent": None,
                "Other": None,
            }

            if response1 in party_to_direction and response2 in ["Right", "Wrong"]:
                expected = party_to_direction[response1]
                if expected is None:
                    return True
                return response2 == expected

        # Default: assume consistent
        return True

    def _check_semantic_consistency(
        self, response1: Any, response2: Any, constraint: ConsistencyConstraint
    ) -> bool:
        """检查语义一致性（基于预定义的关联）"""
        # Age group and Party ID correlation
        if (
            "age_group" in constraint.question_pair
            and "party_id" in constraint.question_pair
        ):
            age_party_correlation = {
                "18-29": ["Democrat", "Independent"],
                "30-44": ["Democrat", "Republican", "Independent"],
                "45-59": ["Democrat", "Republican", "Independent"],
                "60+": ["Republican", "Independent"],
            }

            age = response1 if "age_group" in constraint.question_pair[0] else response2
            party = (
                response2 if "age_group" in constraint.question_pair[0] else response1
            )

            if age in age_party_correlation:
                return party in age_party_correlation[age]

        # Education and Income correlation
        if (
            "education" in constraint.question_pair
            and "income" in constraint.question_pair
        ):
            education_income_mapping = {
                "HS": ["<30k", "30k-60k"],
                "Some College": ["30k-60k", "60k-100k"],
                "Bachelor": ["60k-100k", ">100k"],
                "Graduate": [">100k"],
            }

            education = (
                response1 if "education" in constraint.question_pair[0] else response2
            )
            income = (
                response2 if "education" in constraint.question_pair[0] else response1
            )

            if education in education_income_mapping:
                return income in education_income_mapping[education]

        # Party ID and Government Trust correlation
        if (
            "party_id" in constraint.question_pair
            and "trust_government" in constraint.question_pair
        ):
            party_trust_mapping = {
                "Democrat": ["Trust", "Neutral"],
                "Republican": ["Distrust", "Neutral"],
                "Independent": ["Trust", "Distrust", "Neutral"],
                "Other": ["Trust", "Distrust", "Neutral"],
            }

            party = (
                response1 if "party_id" in constraint.question_pair[0] else response2
            )
            trust = (
                response2 if "party_id" in constraint.question_pair[0] else response1
            )

            if party in party_trust_mapping:
                return trust in party_trust_mapping[party]

        # Default: assume consistent
        return True

    def _check_value_consistency(
        self, response1: Any, response2: Any, constraint: ConsistencyConstraint
    ) -> bool:
        """检查基于价值观的一致性"""
        # For now, use semantic consistency as fallback
        return self._check_semantic_consistency(response1, response2, constraint)


def calculate_acs_score(
    virtual_responses: List[Dict[str, Any]],
    benchmark_path: str = "data/cache/cqcb_anes_2020.json",
) -> ACSResult:
    """
    计算ACS分数的便捷函数

    Args:
        virtual_responses: 虚拟用户响应
        benchmark_path: CQCB基准路径

    Returns:
        ACSResult: 评估结果
    """
    # Load benchmark
    with open(benchmark_path, "r", encoding="utf-8") as f:
        benchmark_data = json.load(f)

    # Reconstruct constraints
    constraints = []
    for c_data in benchmark_data["constraints"]:
        constraints.append(ConsistencyConstraint(**c_data))

    # Calculate ACS
    acs_metric = ACSMetric()
    return acs_metric.evaluate_consistency(virtual_responses, constraints)


if __name__ == "__main__":
    # Test ACS calculation
    test_responses = [
        {
            "party_id": "Democrat",
            "presidential_vote": "Biden",
            "country_direction": "Right",
        },
        {
            "party_id": "Republican",
            "presidential_vote": "Trump",
            "country_direction": "Wrong",
        },
        {
            "party_id": "Independent",
            "presidential_vote": "Biden",
            "country_direction": "Right",
        },
    ]

    # Create test constraints
    test_constraints = [
        ConsistencyConstraint(
            constraint_id="test_001",
            question_pair=("party_id", "presidential_vote"),
            constraint_type="logical",
            constraint_rule="Party should match vote",
            expected_consistency=0.9,
            domain="political",
        )
    ]

    acs_metric = ACSMetric()
    result = acs_metric.evaluate_consistency(test_responses, test_constraints)

    print(f"ACS Overall Score: {result.overall_score:.4f}")
    print(f"Domain Scores: {result.domain_scores}")
    print(f"Constraint Scores: {result.constraint_scores}")
