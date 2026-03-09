"""
配置管理模块

管理实验配置、路径、超参数等
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from pathlib import Path
import json
import yaml


@dataclass
class ModelConfig:
    """LLM 模型配置"""
    name: str = "glm-5"  # GLM-5 模型
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 0.9
    seed: int = 42


@dataclass
class DataConfig:
    """数据集配置"""
    name: str = "anes_2020"
    data_dir: str = "data/raw"
    cache_dir: str = "data/cache"
    sample_size: Optional[int] = None  # None 表示使用全部数据
    train_ratio: float = 0.8
    random_seed: int = 42


@dataclass
class PersonaConfig:
    """Persona 生成配置"""
    pool_size: int = 300  # Persona 池大小
    diversity_weight: float = 0.5  # 多样性权重
    include_demographics: bool = True
    include_psychographics: bool = True
    include_values: bool = True
    max_retries: int = 3


@dataclass
class RetrievalConfig:
    """知识检索配置"""
    enabled: bool = True
    top_k: int = 5
    rerank: bool = True
    embedding_model: str = "text-embedding-ada-002"
    index_type: str = "faiss"  # faiss, annoy, bm25


@dataclass
class EvaluationConfig:
    """评估配置"""
    metrics: List[str] = field(default_factory=lambda: [
        "kl_divergence", "js_distance", "wasserstein_distance",
        "accuracy", "top3_accuracy", "cohen_kappa",
        "self_consistency", "entropy"
    ])
    n_bootstrap: int = 1000  # Bootstrap 次数
    confidence_level: float = 0.95
    significance_level: float = 0.05
    bonferroni_correction: bool = True


@dataclass
class ExperimentConfig:
    """实验主配置"""
    name: str = "virtual_survey_experiment"
    output_dir: str = "results"
    log_dir: str = "logs"
    n_repeats: int = 5  # 每个配置重复次数
    parallel: bool = True
    n_workers: int = 4
    save_intermediate: bool = True
    
    # 子配置
    model: ModelConfig = field(default_factory=ModelConfig)
    data: DataConfig = field(default_factory=DataConfig)
    persona: PersonaConfig = field(default_factory=PersonaConfig)
    retrieval: RetrievalConfig = field(default_factory=RetrievalConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    
    @classmethod
    def from_yaml(cls, path: str) -> 'ExperimentConfig':
        """从 YAML 文件加载配置"""
        with open(path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        return cls.from_dict(config_dict)
    
    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'ExperimentConfig':
        """从字典创建配置"""
        return cls(
            name=d.get('name', 'experiment'),
            output_dir=d.get('output_dir', 'results'),
            log_dir=d.get('log_dir', 'logs'),
            n_repeats=d.get('n_repeats', 5),
            parallel=d.get('parallel', True),
            n_workers=d.get('n_workers', 4),
            save_intermediate=d.get('save_intermediate', True),
            model=ModelConfig(**d.get('model', {})),
            data=DataConfig(**d.get('data', {})),
            persona=PersonaConfig(**d.get('persona', {})),
            retrieval=RetrievalConfig(**d.get('retrieval', {})),
            evaluation=EvaluationConfig(**d.get('evaluation', {})),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        from dataclasses import asdict
        return asdict(self)
    
    def save_yaml(self, path: str):
        """保存为 YAML 文件"""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, allow_unicode=True)


# 预定义配置
DATASET_CONFIGS = {
    "anes_2020": {
        "name": "ANES 2020",
        "domain": "政治态度",
        "sample_size": 8280,
        "n_questions": 45,
        "task_type": "FAS",
        "url": "https://electionstudies.org/"
    },
    "gss_2018": {
        "name": "GSS 2018",
        "domain": "社会调查",
        "sample_size": 2348,
        "n_questions": 52,
        "task_type": "PAS",
        "url": "https://gss.norc.org/"
    },
    "acs": {
        "name": "American Community Survey",
        "domain": "人口普查",
        "sample_size": 3500,
        "n_questions": 38,
        "task_type": "PAS+FAS",
        "url": "https://www.census.gov/programs-surveys/acs"
    },
    "recs": {
        "name": "RECS",
        "domain": "能源消费",
        "sample_size": 5600,
        "n_questions": 41,
        "task_type": "FAS",
        "url": "https://www.eia.gov/consumption/residential/"
    },
    "nhts": {
        "name": "NHTS",
        "domain": "出行调查",
        "sample_size": 5000,
        "n_questions": 44,
        "task_type": "PAS",
        "url": "https://nhts.ornl.gov/"
    }
}

BASELINE_CONFIGS = {
    "random": {
        "name": "Random",
        "type": "lower_bound",
        "description": "均匀随机选择",
        "requires_llm": False
    },
    "mode": {
        "name": "Mode",
        "type": "lower_bound",
        "description": "总是选最常见选项",
        "requires_llm": False
    },
    "llm_direct": {
        "name": "LLM-Direct",
        "type": "baseline",
        "description": "无 Persona 直接生成",
        "requires_llm": True
    },
    "llm_prompt": {
        "name": "LLM-Prompt",
        "type": "baseline",
        "description": "简单 Persona 描述",
        "requires_llm": True
    },
    "llm_s3_pas": {
        "name": "LLM-S³ PAS",
        "type": "reference",
        "description": "官方基准方法",
        "requires_llm": True
    }
}


def get_default_config() -> ExperimentConfig:
    """获取默认配置"""
    return ExperimentConfig()


if __name__ == "__main__":
    # 测试配置
    config = get_default_config()
    print("默认配置:")
    print(json.dumps(config.to_dict(), indent=2, ensure_ascii=False, default=str))
    
    # 保存配置示例
    config.save_yaml("config/default.yaml")
    print("\n配置已保存到 config/default.yaml")
