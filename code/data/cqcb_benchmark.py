#!/usr/bin/env python3
"""
CQCB (Cross-Question Consistency Benchmark)
跨问题一致性基准

This module provides the CQCB benchmark dataset and evaluation framework
for measuring cross-question attitude consistency in virtual user responses.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import json
import numpy as np
from .loader import SurveyDataset, SurveyQuestion, SurveyResponse


@dataclass
class ConsistencyConstraint:
    """一致性约束定义"""

    constraint_id: str
    question_pair: Tuple[str, str]  # (question1_id, question2_id)
    constraint_type: str  # "logical", "semantic", "value-based"
    constraint_rule: str  # Rule description in natural language
    expected_consistency: float  # Expected consistency score (0-1)
    domain: str  # Domain of the constraint (e.g., "political", "social")


@dataclass
class CQCBInstance:
    """CQCB基准实例"""

    instance_id: str
    respondent_id: str
    questions: List[SurveyQuestion]
    responses: Dict[str, Any]
    constraints: List[ConsistencyConstraint]
    metadata: Dict[str, Any]


class CQCBBenchmark:
    """CQCB基准类"""

    def __init__(self, dataset_name: str = "anes_2020"):
        self.dataset_name = dataset_name
        self.constraints = self._load_constraints()
        self.instances = self._build_instances()

    def _load_constraints(self) -> List[ConsistencyConstraint]:
        """加载一致性约束"""
        # 基于ANES 2020的逻辑一致性约束
        constraints = [
            # Political consistency constraints
            ConsistencyConstraint(
                constraint_id="pol_001",
                question_pair=("party_id", "presidential_vote"),
                constraint_type="logical",
                constraint_rule="Party identification should be consistent with presidential vote choice",
                expected_consistency=0.85,
                domain="political",
            ),
            ConsistencyConstraint(
                constraint_id="pol_002",
                question_pair=("party_id", "country_direction"),
                constraint_type="semantic",
                constraint_rule="Party identification should correlate with country direction assessment",
                expected_consistency=0.75,
                domain="political",
            ),
            ConsistencyConstraint(
                constraint_id="pol_003",
                question_pair=("economy_rating", "country_direction"),
                constraint_type="logical",
                constraint_rule="Economic rating should be consistent with country direction assessment",
                expected_consistency=0.80,
                domain="political",
            ),
            # Social consistency constraints
            ConsistencyConstraint(
                constraint_id="soc_001",
                question_pair=("education", "income"),
                constraint_type="value-based",
                constraint_rule="Education level should correlate with income level",
                expected_consistency=0.70,
                domain="social",
            ),
            ConsistencyConstraint(
                constraint_id="soc_002",
                question_pair=("age_group", "party_id"),
                constraint_type="semantic",
                constraint_rule="Age group should show expected correlation with party identification",
                expected_consistency=0.65,
                domain="social",
            ),
            # Trust consistency constraints
            ConsistencyConstraint(
                constraint_id="trust_001",
                question_pair=("party_id", "trust_government"),
                constraint_type="logical",
                constraint_rule="Party identification should correlate with government trust",
                expected_consistency=0.75,
                domain="political",
            ),
        ]
        return constraints

    def _build_instances(self) -> List[CQCBInstance]:
        """构建CQCB实例"""
        from .loader import load_dataset

        # Load base dataset
        base_dataset = load_dataset(self.dataset_name, sample_size=100)

        instances = []
        for i, response in enumerate(base_dataset.responses):
            # Create CQCB instance
            instance = CQCBInstance(
                instance_id=f"CQCB_{i:04d}",
                respondent_id=response.respondent_id,
                questions=base_dataset.questions,
                responses=response.responses,
                constraints=self.constraints,
                metadata={
                    "source_dataset": self.dataset_name,
                    "original_index": i,
                    "constraint_count": len(self.constraints),
                },
            )
            instances.append(instance)

        return instances

    def get_constraints_by_domain(self, domain: str) -> List[ConsistencyConstraint]:
        """获取特定领域的一致性约束"""
        return [c for c in self.constraints if c.domain == domain]

    def get_all_domains(self) -> List[str]:
        """获取所有领域"""
        domains = set()
        for constraint in self.constraints:
            domains.add(constraint.domain)
        return list(domains)

    def save_benchmark(self, path: str):
        """保存基准到文件"""
        data = {
            "benchmark_name": "CQCB",
            "dataset_name": self.dataset_name,
            "constraints": [c.__dict__ for c in self.constraints],
            "instances": [
                {
                    "instance_id": inst.instance_id,
                    "respondent_id": inst.respondent_id,
                    "responses": inst.responses,
                    "metadata": inst.metadata,
                }
                for inst in self.instances
            ],
        }

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load_benchmark(cls, path: str) -> "CQCBBenchmark":
        """从文件加载基准"""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        benchmark = cls(data["dataset_name"])
        # Reconstruct constraints
        benchmark.constraints = [
            ConsistencyConstraint(**c) for c in data["constraints"]
        ]
        # Reconstruct instances
        benchmark.instances = []
        for inst_data in data["instances"]:
            instance = CQCBInstance(
                instance_id=inst_data["instance_id"],
                respondent_id=inst_data["respondent_id"],
                questions=[],  # Will be loaded separately
                responses=inst_data["responses"],
                constraints=benchmark.constraints,
                metadata=inst_data["metadata"],
            )
            benchmark.instances.append(instance)

        return benchmark


def create_cqcb_from_anes():
    """从ANES数据创建CQCB基准"""
    benchmark = CQCBBenchmark("anes_2020")
    benchmark.save_benchmark("data/cache/cqcb_anes_2020.json")
    print(
        f"Created CQCB benchmark with {len(benchmark.instances)} instances and {len(benchmark.constraints)} constraints"
    )
    return benchmark


if __name__ == "__main__":
    create_cqcb_from_anes()
