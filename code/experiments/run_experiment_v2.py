#!/usr/bin/env python3
"""
Virtual Users Research - Main Experiment Runner v2
Version: v3 with ACS (Attitude Consistency Score)

This script runs the complete virtual user experiment pipeline including:
1. Load configuration
2. Download and prepare data
3. Generate Persona pool
4. Run baseline methods (including ConsistAgent)
5. Evaluate results with both traditional metrics and ACS
6. Save and report results
"""

import argparse
import yaml
import json
import os
import sys
from pathlib import Path
import logging
from typing import Dict, List, Any

# Add the code directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from models.persona import PersonaGenerator, PersonaPool
from baselines.base import MethodFactory
from eval import Evaluator, print_evaluation_results
from evaluation.acs_metric import calculate_acs_score, ACSResult
from baselines.consist_agent import ConsistAgent
from data.loader import load_dataset, SurveyDataset


def setup_logging(config: Dict[str, Any]) -> logging.Logger:
    """Setup logging configuration"""
    log_dir = Path(config.get("log_dir", "logs"))
    log_dir.mkdir(parents=True, exist_ok=True)

    logging_config = config.get("logging", {})
    log_level = getattr(logging, logging_config.get("level", "INFO"))

    logger = logging.getLogger("virtual_users")
    logger.setLevel(log_level)

    # File handler
    if logging_config.get("file", True):
        file_handler = logging.FileHandler(log_dir / "experiment_v2.log")
        file_formatter = logging.Formatter(
            logging_config.get(
                "format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Console handler
    if logging_config.get("console", True):
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter("%(levelname)s - %(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger


def load_configuration(config_path: str) -> Dict[str, Any]:
    """Load YAML configuration file"""
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config


def generate_persona_pool(
    config: Dict[str, Any], logger: logging.Logger
) -> PersonaPool:
    """Generate Persona pool based on configuration"""
    logger.info("Generating Persona pool...")

    persona_config = config.get("persona", {})
    pool_size = persona_config.get("pool_size", 300)
    seed = config.get("data", {}).get("seed", 42)

    generator = PersonaGenerator(seed=seed)
    personas = generator.generate_personas(
        n=pool_size, ensure_diversity=persona_config.get("diversity_weight", 0.5) > 0
    )

    pool = PersonaPool(personas)
    logger.info(f"Generated {len(personas)} personas")

    return pool


def run_baseline_methods(
    config: Dict[str, Any],
    dataset: SurveyDataset,
    persona_pool: PersonaPool,
    logger: logging.Logger,
) -> Dict[str, List[Dict[str, Any]]]:
    """Run all baseline methods and collect responses"""
    logger.info("Running baseline methods...")

    baselines = config.get(
        "baselines",
        ["random", "mode", "llm_direct", "llm_prompt", "llm_s3_pas", "consist_agent"],
    )
    questions = [q.__dict__ for q in dataset.questions]
    real_responses = [r.responses for r in dataset.responses]

    all_results = {}

    for method_name in baselines:
        logger.info(f"Running {method_name} method...")

        # Create method instance
        method = MethodFactory.create(
            method_name, seed=config.get("data", {}).get("seed", 42)
        )

        # For ConsistAgent, we need to reset memory between personas
        if method_name == "consist_agent":
            # Reset memory for each persona
            pass

        # Generate responses for each persona
        virtual_responses = []
        personas_to_use = persona_pool.personas[
            : config.get("data", {}).get("sample_size", len(persona_pool.personas))
        ]

        for persona in personas_to_use:
            if hasattr(method, "reset_memory"):
                method.reset_memory()

            method_responses = {}

            for question in questions:
                q_id = question["id"]
                q_text = question["text"]
                q_options = question.get("options", [])
                q_type = question.get("type", "single_choice")

                # Prepare options for the method
                if q_type == "likert_scale":
                    # For Likert scale, create numeric options
                    options = [str(i) for i in range(1, 6)]  # 1-5 scale
                else:
                    options = q_options

                # Generate response
                result = method.generate_response(
                    question=q_text,
                    options=options,
                    persona_info=persona.to_dict(),
                    context=f"question_id:{q_id}",
                )

                method_responses[q_id] = result.response

            virtual_responses.append(method_responses)

        all_results[method_name] = virtual_responses
        logger.info(
            f"Completed {method_name} method with {len(virtual_responses)} responses"
        )

    return all_results


def evaluate_results(
    config: Dict[str, Any],
    dataset: SurveyDataset,
    baseline_results: Dict[str, List[Dict[str, Any]]],
    logger: logging.Logger,
) -> Dict[str, Any]:
    """Evaluate all baseline results with both traditional metrics and ACS"""
    logger.info("Evaluating results...")

    # Convert SurveyQuestion objects to dict and map question_type to type for eval.py compatibility
    questions = []
    for q in dataset.questions:
        q_dict = q.__dict__.copy()
        if 'question_type' in q_dict:
            q_dict['type'] = q_dict['question_type']
            del q_dict['question_type']
        questions.append(q_dict)
    real_responses = [r.responses for r in dataset.responses]

    evaluator = Evaluator()
    all_evaluations = {}

    for method_name, virtual_responses in baseline_results.items():
        logger.info(f"Evaluating {method_name} method...")

        # Traditional evaluation
        traditional_eval = evaluator.evaluate_all(
            real_responses, virtual_responses, questions
        )

        # ACS evaluation
        try:
            acs_result = calculate_acs_score(virtual_responses)
            acs_eval = {
                "acs_overall": acs_result.overall_score,
                "acs_domain_scores": acs_result.domain_scores,
                "acs_constraint_scores": acs_result.constraint_scores,
            }
        except Exception as e:
            logger.warning(f"ACS evaluation failed for {method_name}: {e}")
            acs_eval = {
                "acs_overall": 0.0,
                "acs_domain_scores": {},
                "acs_constraint_scores": {},
            }

        # Combine evaluations
        combined_eval = {"traditional": traditional_eval, "acs": acs_eval}

        all_evaluations[method_name] = combined_eval
        logger.info(f"Completed evaluation for {method_name}")

    return all_evaluations


def save_results(
    config: Dict[str, Any],
    evaluations: Dict[str, Any],
    baseline_results: Dict[str, Any],
    logger: logging.Logger,
):
    """Save evaluation results and detailed responses"""
    output_dir = Path(config.get("output_dir", "results"))
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save evaluation summary
    eval_summary = {"config": config, "evaluations": evaluations}

    with open(output_dir / "evaluation_summary_v2.json", "w", encoding="utf-8") as f:
        json.dump(eval_summary, f, ensure_ascii=False, indent=2)

    # Save detailed results if requested
    if config.get("evaluation", {}).get("save_detailed_results", True):
        detailed_results = {"config": config, "baseline_responses": baseline_results}

        with open(output_dir / "detailed_results_v2.json", "w", encoding="utf-8") as f:
            json.dump(detailed_results, f, ensure_ascii=False, indent=2)

    logger.info(f"Results saved to {output_dir}")


def print_summary(evaluations: Dict[str, Any]):
    """Print experiment summary"""
    print("\n" + "=" * 60)
    print("EXPERIMENT SUMMARY (v2 with ACS)")
    print("=" * 60)

    for method_name, eval_result in evaluations.items():
        agg = eval_result["traditional"].get("aggregate", {})
        acs = eval_result["acs"]

        print(f"\n{method_name.upper()}:")
        print(
            f"  Average Distribution Similarity: {agg.get('avg_distribution_similarity', 0):.4f}"
        )
        print(f"  Average KL Divergence: {agg.get('avg_kl_divergence', 0):.4f}")
        print(f"  Average Kappa Coefficient: {agg.get('avg_kappa', 0):.4f}")
        print(f"  ACS Overall Score: {acs.get('acs_overall', 0):.4f}")


def main():
    """Main experiment runner"""
    parser = argparse.ArgumentParser(
        description="Run Virtual Users Research Experiment v2"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/default.yaml",
        help="Path to configuration file",
    )
    parser.add_argument("--dataset", type=str, help="Override dataset name from config")
    parser.add_argument(
        "--n_personas", type=int, help="Override number of personas from config"
    )
    parser.add_argument(
        "--temperature", type=float, help="Override temperature from config"
    )
    parser.add_argument(
        "--n_repeats", type=int, help="Override number of repeats from config"
    )

    args = parser.parse_args()

    # Load configuration
    config = load_configuration(args.config)

    # Override config with command line arguments if provided
    if args.dataset:
        config["data"]["name"] = args.dataset
    if args.n_personas:
        config["persona"]["pool_size"] = args.n_personas
    if args.temperature:
        config["model"]["temperature"] = args.temperature
    if args.n_repeats:
        config["n_repeats"] = args.n_repeats

    # Setup logging
    logger = setup_logging(config)
    logger.info("Starting Virtual Users Research Experiment v2 (with ACS)")

    try:
        # Load dataset
        data_config = config.get("data", {})
        dataset = load_dataset(
            name=data_config.get("name", "anes_2020"),
            sample_size=data_config.get("sample_size"),
            data_dir=data_config.get("data_dir", "data/raw"),
        )

        # Generate Persona pool
        persona_pool = generate_persona_pool(config, logger)

        # Run baseline methods
        baseline_results = run_baseline_methods(config, dataset, persona_pool, logger)

        # Evaluate results
        evaluations = evaluate_results(config, dataset, baseline_results, logger)

        # Save results
        save_results(config, evaluations, baseline_results, logger)

        # Print summary
        logger.info("Experiment completed successfully!")
        print_summary(evaluations)

    except Exception as e:
        logger.error(f"Experiment failed with error: {e}")
        raise


if __name__ == "__main__":
    main()
