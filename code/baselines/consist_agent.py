#!/usr/bin/env python3
"""
ConsistAgent - Consistency-Constrained Virtual User Agent

This module implements the ConsistAgent method that enforces cross-question
attitude consistency through memory-based constraint decoding.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import random
import json
from pathlib import Path

from .base import BaseMethod, SurveyResult
from data.cqcb_benchmark import ConsistencyConstraint
from models.persona import Persona


@dataclass
class ConsistencyMemory:
    """一致性记忆"""

    responses: Dict[str, Any] = None
    constraints: List[ConsistencyConstraint] = None
    constraint_strength: float = 0.8
    memory_window: int = 10

    def __post_init__(self):
        if self.responses is None:
            self.responses = {}
        if self.constraints is None:
            self.constraints = []


class ConsistAgent(BaseMethod):
    """
    ConsistAgent - 一致性约束的虚拟用户生成方法

    核心思想：通过记忆之前的回答，在生成新回答时确保与已有态度保持一致。
    """

    name = "consist_agent"
    description = "一致性约束解码的虚拟用户"

    def __init__(
        self,
        seed: int = 42,
        config: Optional[Dict] = None,
        constraint_strength: float = 0.8,
        memory_window: int = 10,
    ):
        super().__init__(seed, config)
        self.constraint_strength = constraint_strength
        self.memory_window = memory_window
        self.consistency_memory = ConsistencyMemory(
            constraint_strength=constraint_strength, memory_window=memory_window
        )

        # Load constraints from CQCB benchmark
        self._load_constraints()

    def _load_constraints(self):
        """加载CQCB约束"""
        try:
            constraint_path = Path("data/cache/cqcb_anes_2020.json")
            if constraint_path.exists():
                with open(constraint_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Reconstruct constraints
                self.consistency_memory.constraints = []
                for c_data in data["constraints"]:
                    constraint = ConsistencyConstraint(**c_data)
                    self.consistency_memory.constraints.append(constraint)
            else:
                # Create default constraints if file doesn't exist
                self._create_default_constraints()
        except Exception as e:
            print(f"Warning: Failed to load constraints: {e}")
            self._create_default_constraints()

    def _create_default_constraints(self):
        """创建默认约束"""
        default_constraints = [
            ConsistencyConstraint(
                constraint_id="default_001",
                question_pair=("party_id", "presidential_vote"),
                constraint_type="logical",
                constraint_rule="Party identification should be consistent with presidential vote choice",
                expected_consistency=0.85,
                domain="political",
            ),
            ConsistencyConstraint(
                constraint_id="default_002",
                question_pair=("economy_rating", "country_direction"),
                constraint_type="logical",
                constraint_rule="Economic rating should be consistent with country direction assessment",
                expected_consistency=0.80,
                domain="political",
            ),
        ]
        self.consistency_memory.constraints = default_constraints

    def generate_response(
        self,
        question: str,
        options: List[str],
        persona_info: Optional[Dict] = None,
        context: Optional[str] = None,
    ) -> SurveyResult:
        """
        生成一致性约束的响应

        Args:
            question: 问题文本
            options: 选项列表
            persona_info: Persona信息
            context: 上下文

        Returns:
            SurveyResult: 一致性约束的响应
        """
        # Get question ID from context or extract from question
        question_id = self._extract_question_id(question, context)

        # Check for consistency constraints
        constrained_options = self._apply_consistency_constraints(
            question_id, options, persona_info
        )

        # Apply persona-based preferences
        weighted_options = self._apply_persona_preferences(
            constrained_options, persona_info
        )

        # Select response with weighted probabilities
        response = self._weighted_choice(weighted_options)
        confidence = (
            max(weighted_options.values()) if weighted_options else 1.0 / len(options)
        )

        # Update memory
        if question_id:
            self.consistency_memory.responses[question_id] = response

        return SurveyResult(
            persona_id=persona_info.get("id", "UNKNOWN") if persona_info else "UNKNOWN",
            question_id=question_id,
            response=response,
            confidence=confidence,
            method=self.name,
            metadata={
                "constraint_applied": len(constrained_options) < len(options),
                "constraint_strength": self.constraint_strength,
                "options_considered": len(constrained_options),
            },
        )

    def _extract_question_id(self, question: str, context: Optional[str]) -> str:
        """从问题或上下文中提取问题ID"""
        # Try to extract from context first
        if context and "question_id:" in context:
            try:
                start = context.find("question_id:") + 12
                end = context.find(" ", start)
                if end == -1:
                    end = len(context)
                return context[start:end].strip()
            except:
                pass

        # Try to match common question patterns
        question_patterns = {
            "Who did you vote for President?": "presidential_vote",
            "Which party do you identify with?": "party_id",
            "How would you rate the economy?": "economy_rating",
            "Is the country heading in the right direction?": "country_direction",
            "Do you trust the government?": "trust_government",
            "What is your age group?": "age_group",
            "What is your gender?": "gender",
            "What is your race/ethnicity?": "race",
            "What is your highest education level?": "education",
            "What is your household income?": "income",
            "Which region do you live in?": "region",
        }

        for pattern, q_id in question_patterns.items():
            if pattern in question:
                return q_id

        # Fallback: create ID from first few words
        words = question.split()[:3]
        return "_".join(words).lower().replace("?", "").replace(",", "")

    def _apply_consistency_constraints(
        self, question_id: str, options: List[str], persona_info: Optional[Dict]
    ) -> Dict[str, float]:
        """
        应用一致性约束，过滤和加权选项

        Returns:
            Dict[str, float]: 选项到权重的映射
        """
        if not question_id or not self.consistency_memory.constraints:
            # No constraints, return uniform weights
            return {opt: 1.0 for opt in options}

        # Find relevant constraints
        relevant_constraints = []
        for constraint in self.consistency_memory.constraints:
            if question_id in constraint.question_pair:
                relevant_constraints.append(constraint)

        if not relevant_constraints:
            # No relevant constraints, return uniform weights
            return {opt: 1.0 for opt in options}

        # Apply constraints
        option_weights = {opt: 1.0 for opt in options}

        for constraint in relevant_constraints:
            # Get the other question in the pair
            other_q = (
                constraint.question_pair[0]
                if constraint.question_pair[1] == question_id
                else constraint.question_pair[1]
            )

            # Check if we have a response for the other question
            if other_q in self.consistency_memory.responses:
                other_response = self.consistency_memory.responses[other_q]

                # Apply constraint logic
                for option in options:
                    if not self._is_consistent_with_constraint(
                        option, other_response, constraint
                    ):
                        # Reduce weight for inconsistent options
                        option_weights[option] *= 1.0 - self.constraint_strength

        return option_weights

    def _is_consistent_with_constraint(
        self, response: str, other_response: str, constraint: ConsistencyConstraint
    ) -> bool:
        """检查响应是否与约束一致"""
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

            # Determine which is party and which is vote
            if "party_id" == constraint.question_pair[0]:
                party, vote = other_response, response
            else:
                party, vote = response, other_response

            if party in party_to_candidate and vote in ["Biden", "Trump"]:
                expected = party_to_candidate[party]
                if expected is None:
                    return True  # Independent/Other can vote for anyone
                return vote == expected

        # Economy rating and Country direction consistency
        if (
            "economy_rating" in constraint.question_pair
            and "country_direction" in constraint.question_pair
        ):
            if "economy_rating" == constraint.question_pair[0]:
                economy, direction = other_response, response
            else:
                economy, direction = response, other_response

            if economy == "Better" and direction == "Right":
                return True
            if economy == "Worse" and direction == "Wrong":
                return True
            if economy == "Same":
                return True  # Neutral on economy can have any view on direction

        # Default: assume consistent
        return True

    def _apply_persona_preferences(
        self, option_weights: Dict[str, float], persona_info: Optional[Dict]
    ) -> Dict[str, float]:
        """应用Persona偏好调整权重"""
        if not persona_info:
            return option_weights

        demographics = persona_info.get("demographics", {})
        values = persona_info.get("values", [])

        # Adjust weights based on demographics
        adjusted_weights = option_weights.copy()

        for option, weight in adjusted_weights.items():
            # Education level influence
            education = demographics.get("education", "")
            if "Graduate" in education or "Bachelor" in education:
                if "moderate" in option.lower() or "middle" in option.lower():
                    adjusted_weights[option] *= 1.3

            # Age influence
            age = demographics.get("age_group", "")
            if "60+" in age:
                if "traditional" in option.lower() or "conservative" in option.lower():
                    adjusted_weights[option] *= 1.2
            elif "18-29" in age:
                if "new" in option.lower() or "progressive" in option.lower():
                    adjusted_weights[option] *= 1.2

        return adjusted_weights

    def _weighted_choice(self, weights: Dict[str, float]) -> str:
        """根据权重选择选项"""
        if not weights:
            return ""

        # Normalize weights
        total_weight = sum(weights.values())
        if total_weight == 0:
            # All weights are zero, choose randomly
            return self.rng.choice(list(weights.keys()))

        normalized_weights = [w / total_weight for w in weights.values()]
        options = list(weights.keys())

        # Use random.choices with weights
        chosen = self.rng.choices(options, weights=normalized_weights, k=1)[0]
        return chosen

    def reset_memory(self):
        """重置一致性记忆"""
        self.consistency_memory.responses.clear()


# Register ConsistAgent with MethodFactory
from .base import MethodFactory

MethodFactory.register("consist_agent", ConsistAgent)


if __name__ == "__main__":
    # Test ConsistAgent
    print("Testing ConsistAgent...")

    agent = ConsistAgent(seed=42, constraint_strength=0.9)

    # Simulate a sequence of questions
    questions_and_options = [
        (
            "Which party do you identify with?",
            ["Democrat", "Republican", "Independent", "Other"],
        ),
        ("Who did you vote for President?", ["Biden", "Trump", "Other", "No Vote"]),
        ("Is the country heading in the right direction?", ["Right", "Wrong"]),
    ]

    persona_info = {
        "id": "TEST_001",
        "demographics": {
            "age_group": "30-44",
            "gender": "Female",
            "education": "Bachelor",
            "income": "60k-100k",
            "region": "West",
        },
        "values": ["Innovation", "Freedom", "Equality"],
    }

    for question, options in questions_and_options:
        result = agent.generate_response(question, options, persona_info)
        print(f"Q: {question}")
        print(f"A: {result.response} (confidence: {result.confidence:.3f})")
        print(f"Metadata: {result.metadata}")
        print()
