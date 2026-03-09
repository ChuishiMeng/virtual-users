#!/usr/bin/env python3
"""
Ablation Study Runner for ConsistAgent
Tests: constraint strength (α) and memory window size
"""

import argparse
import json
import os
import sys
from pathlib import Path
import logging
from typing import Dict, List, Any

# Add code directory to path
sys.path.append(str(Path(__file__).parent.parent))

from models.persona import PersonaGenerator, PersonaPool
from data.loader import load_dataset
from baselines.consist_agent import ConsistAgent
from evaluation.acs_metric import calculate_acs_score
from eval import Evaluator


def setup_logging() -> logging.Logger:
    """Setup logging"""
    logger = logging.getLogger("ablation_study")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
    logger.addHandler(handler)
    return logger


def run_ablation_alpha(
    alpha_values: List[float],
    dataset,
    persona_pool,
    logger: logging.Logger,
    output_dir: Path,
) -> Dict[str, Any]:
    """Run ablation study on constraint strength (alpha)"""
    logger.info("=" * 60)
    logger.info("ABLATION STUDY: Constraint Strength (α)")
    logger.info("=" * 60)

    results = {}
    # Convert questions to format expected by evaluator
    questions = []
    for q in dataset.questions:
        q_dict = q.__dict__.copy()
        if 'question_type' in q_dict:
            q_dict['type'] = q_dict['question_type']
            del q_dict['question_type']
        questions.append(q_dict)
    real_responses = [r.responses for r in dataset.responses]
    evaluator = Evaluator()

    for alpha in alpha_values:
        logger.info(f"\nRunning with α = {alpha}...")

        # Create ConsistAgent with this alpha
        method = ConsistAgent(seed=42, constraint_strength=alpha, memory_window=10)

        # Generate responses
        virtual_responses = []
        personas_to_use = persona_pool.personas[: len(real_responses)]

        for persona in personas_to_use:
            method.reset_memory()
            method_responses = {}

            for question in questions:
                q_id = question["id"]
                q_text = question["text"]
                q_options = question.get("options", [])
                q_type = question.get("type") or question.get("question_type", "single_choice")

                if q_type == "likert_scale":
                    options = [str(i) for i in range(1, 6)]
                else:
                    options = q_options

                result = method.generate_response(
                    question=q_text,
                    options=options,
                    persona_info=persona.to_dict(),
                    context=f"question_id:{q_id}",
                )
                method_responses[q_id] = result.response

            virtual_responses.append(method_responses)

        # Evaluate
        traditional_eval = evaluator.evaluate_all(real_responses, virtual_responses, questions)
        acs_result = calculate_acs_score(virtual_responses)

        results[f"alpha_{alpha}"] = {
            "alpha": alpha,
            "distribution_similarity": traditional_eval["aggregate"]["avg_distribution_similarity"],
            "kl_divergence": traditional_eval["aggregate"]["avg_kl_divergence"],
            "acs_overall": acs_result.overall_score,
            "acs_domain_scores": acs_result.domain_scores,
        }

        logger.info(f"  Distribution Similarity: {results[f'alpha_{alpha}']['distribution_similarity']:.4f}")
        logger.info(f"  KL Divergence: {results[f'alpha_{alpha}']['kl_divergence']:.4f}")
        logger.info(f"  ACS Overall: {results[f'alpha_{alpha}']['acs_overall']:.4f}")

    # Save results
    with open(output_dir / "ablation_alpha.json", "w") as f:
        json.dump(results, f, indent=2)

    return results


def run_ablation_memory(
    memory_values: List[int],
    dataset,
    persona_pool,
    logger: logging.Logger,
    output_dir: Path,
) -> Dict[str, Any]:
    """Run ablation study on memory window size"""
    logger.info("\n" + "=" * 60)
    logger.info("ABLATION STUDY: Memory Window Size")
    logger.info("=" * 60)

    results = {}
    # Convert questions to format expected by evaluator
    questions = []
    for q in dataset.questions:
        q_dict = q.__dict__.copy()
        if 'question_type' in q_dict:
            q_dict['type'] = q_dict['question_type']
            del q_dict['question_type']
        questions.append(q_dict)
    real_responses = [r.responses for r in dataset.responses]
    evaluator = Evaluator()

    for memory in memory_values:
        logger.info(f"\nRunning with memory_window = {memory}...")

        # Create ConsistAgent with this memory window
        method = ConsistAgent(seed=42, constraint_strength=0.8, memory_window=memory)

        # Generate responses
        virtual_responses = []
        personas_to_use = persona_pool.personas[: len(real_responses)]

        for persona in personas_to_use:
            method.reset_memory()
            method_responses = {}

            for question in questions:
                q_id = question["id"]
                q_text = question["text"]
                q_options = question.get("options", [])
                q_type = question.get("type") or question.get("question_type", "single_choice")

                if q_type == "likert_scale":
                    options = [str(i) for i in range(1, 6)]
                else:
                    options = q_options

                result = method.generate_response(
                    question=q_text,
                    options=options,
                    persona_info=persona.to_dict(),
                    context=f"question_id:{q_id}",
                )
                method_responses[q_id] = result.response

            virtual_responses.append(method_responses)

        # Evaluate
        traditional_eval = evaluator.evaluate_all(real_responses, virtual_responses, questions)
        acs_result = calculate_acs_score(virtual_responses)

        results[f"memory_{memory}"] = {
            "memory_window": memory,
            "distribution_similarity": traditional_eval["aggregate"]["avg_distribution_similarity"],
            "kl_divergence": traditional_eval["aggregate"]["avg_kl_divergence"],
            "acs_overall": acs_result.overall_score,
            "acs_domain_scores": acs_result.domain_scores,
        }

        logger.info(f"  Distribution Similarity: {results[f'memory_{memory}']['distribution_similarity']:.4f}")
        logger.info(f"  KL Divergence: {results[f'memory_{memory}']['kl_divergence']:.4f}")
        logger.info(f"  ACS Overall: {results[f'memory_{memory}']['acs_overall']:.4f}")

    # Save results
    with open(output_dir / "ablation_memory.json", "w") as f:
        json.dump(results, f, indent=2)

    return results


def run_gss_validation(
    logger: logging.Logger,
    output_dir: Path,
) -> Dict[str, Any]:
    """Run validation on GSS 2018 dataset"""
    logger.info("\n" + "=" * 60)
    logger.info("GSS 2018 VALIDATION")
    logger.info("=" * 60)

    try:
        # Load GSS dataset
        dataset = load_dataset(name="gss_2018", sample_size=8)
        logger.info(f"Loaded GSS 2018: {len(dataset.questions)} questions, {len(dataset.responses)} responses")

        # Generate personas
        generator = PersonaGenerator(seed=42)
        personas = generator.generate_personas(n=8, ensure_diversity=True)
        persona_pool = PersonaPool(personas)

        # Run ConsistAgent
        method = ConsistAgent(seed=42, constraint_strength=0.8, memory_window=10)
        # Convert questions to format expected by evaluator
        questions = []
        for q in dataset.questions:
            q_dict = q.__dict__.copy()
            if 'question_type' in q_dict:
                q_dict['type'] = q_dict['question_type']
                del q_dict['question_type']
            questions.append(q_dict)
        real_responses = [r.responses for r in dataset.responses]

        virtual_responses = []
        for persona in persona_pool.personas:
            method.reset_memory()
            method_responses = {}

            for question in questions:
                q_id = question["id"]
                q_text = question["text"]
                q_options = question.get("options", [])
                q_type = question.get("type") or question.get("question_type", "single_choice")

                if q_type == "likert_scale":
                    options = [str(i) for i in range(1, 6)]
                else:
                    options = q_options

                result = method.generate_response(
                    question=q_text,
                    options=options,
                    persona_info=persona.to_dict(),
                    context=f"question_id:{q_id}",
                )
                method_responses[q_id] = result.response

            virtual_responses.append(method_responses)

        # Evaluate
        evaluator = Evaluator()
        traditional_eval = evaluator.evaluate_all(real_responses, virtual_responses, questions)
        acs_result = calculate_acs_score(virtual_responses)

        results = {
            "dataset": "gss_2018",
            "distribution_similarity": traditional_eval["aggregate"]["avg_distribution_similarity"],
            "kl_divergence": traditional_eval["aggregate"]["avg_kl_divergence"],
            "acs_overall": acs_result.overall_score,
            "acs_domain_scores": acs_result.domain_scores,
        }

        logger.info(f"  Distribution Similarity: {results['distribution_similarity']:.4f}")
        logger.info(f"  KL Divergence: {results['kl_divergence']:.4f}")
        logger.info(f"  ACS Overall: {results['acs_overall']:.4f}")

        # Save results
        with open(output_dir / "gss_validation.json", "w") as f:
            json.dump(results, f, indent=2)

        return results

    except Exception as e:
        logger.error(f"GSS validation failed: {e}")
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Run ablation studies for ConsistAgent")
    parser.add_argument("--output_dir", type=str, default="results/ablation", help="Output directory")
    parser.add_argument("--skip_alpha", action="store_true", help="Skip alpha ablation")
    parser.add_argument("--skip_memory", action="store_true", help="Skip memory ablation")
    parser.add_argument("--skip_gss", action="store_true", help="Skip GSS validation")
    args = parser.parse_args()

    # Setup
    logger = setup_logging()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load ANES dataset for ablation studies
    logger.info("Loading ANES 2020 dataset...")
    dataset = load_dataset(name="anes_2020", sample_size=8)
    logger.info(f"Loaded ANES 2020: {len(dataset.questions)} questions, {len(dataset.responses)} responses")

    # Generate personas
    logger.info("Generating persona pool...")
    generator = PersonaGenerator(seed=42)
    personas = generator.generate_personas(n=8, ensure_diversity=True)
    persona_pool = PersonaPool(personas)

    # Run ablation studies
    all_results = {}

    if not args.skip_alpha:
        alpha_values = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
        all_results["alpha"] = run_ablation_alpha(alpha_values, dataset, persona_pool, logger, output_dir)

    if not args.skip_memory:
        memory_values = [5, 10, 15, 20]
        all_results["memory"] = run_ablation_memory(memory_values, dataset, persona_pool, logger, output_dir)

    if not args.skip_gss:
        all_results["gss"] = run_gss_validation(logger, output_dir)

    # Save combined results
    with open(output_dir / "ablation_summary.json", "w") as f:
        json.dump(all_results, f, indent=2)

    logger.info("\n" + "=" * 60)
    logger.info("ABLATION STUDIES COMPLETE")
    logger.info(f"Results saved to: {output_dir}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
