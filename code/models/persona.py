"""
Persona 生成器模块

基于人口统计信息生成虚拟用户 Persona
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import json
import random
import numpy as np
from pathlib import Path


@dataclass
class Persona:
    """虚拟用户 Persona"""
    id: str
    demographics: Dict[str, str]  # 人口统计信息
    psychographics: Dict[str, Any]  # 心理特征
    values: List[str]  # 价值观
    decision_style: str  # 决策风格
    knowledge_domains: List[str]  # 知识领域
    confidence_threshold: float = 0.5  # 置信度阈值（低于此值回答"不知道"）
    
    def to_prompt(self, format_type: str = "detailed") -> str:
        """将 Persona 转换为提示词"""
        if format_type == "simple":
            return self._to_simple_prompt()
        elif format_type == "detailed":
            return self._to_detailed_prompt()
        else:
            return self._to_structured_prompt()
    
    def _to_simple_prompt(self) -> str:
        """简单格式提示"""
        demo_str = ", ".join(f"{k}: {v}" for k, v in self.demographics.items())
        return f"You are a {demo_str}."
    
    def _to_detailed_prompt(self) -> str:
        """详细格式提示"""
        demo_str = "\n".join(f"- {k}: {v}" for k, v in self.demographics.items())
        values_str = ", ".join(self.values)
        
        return f"""You are a survey respondent with the following characteristics:

Demographics:
{demo_str}

Psychographics:
- Personality traits: {', '.join(self.psychographics.get('personality', ['Moderate']))}
- Values: {values_str}
- Decision style: {self.decision_style}

When answering survey questions:
1. Stay true to your demographic and psychographic profile
2. Answer based on your values and experiences
3. If you genuinely don't know or have no opinion, say so
4. Be consistent with your established characteristics"""

    def _to_structured_prompt(self) -> str:
        """结构化格式提示（JSON）"""
        return json.dumps({
            "demographics": self.demographics,
            "psychographics": self.psychographics,
            "values": self.values,
            "decision_style": self.decision_style
        }, ensure_ascii=False, indent=2)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'demographics': self.demographics,
            'psychographics': self.psychographics,
            'values': self.values,
            'decision_style': self.decision_style,
            'knowledge_domains': self.knowledge_domains,
            'confidence_threshold': self.confidence_threshold
        }
    
    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'Persona':
        """从字典创建"""
        return cls(**d)


class PersonaGenerator:
    """Persona 生成器"""
    
    # 预定义的人格特质
    PERSONALITY_TRAITS = [
        "Openness", "Conscientiousness", "Extraversion", 
        "Agreeableness", "Neuroticism"
    ]
    
    # 预定义价值观
    VALUES_POOL = [
        "Freedom", "Equality", "Security", "Tradition", 
        "Innovation", "Sustainability", "Community", "Individualism",
        "Success", "Family", "Health", "Wealth"
    ]
    
    # 决策风格
    DECISION_STYLES = [
        "Rational", "Emotional", "Impulsive", "Deliberate", 
        "Intuitive", "Analytical"
    ]
    
    def __init__(self, seed: int = 42, config: Optional[Dict] = None):
        self.seed = seed
        self.config = config or {}
        self.rng = random.Random(seed)
        np.random.seed(seed)
    
    def generate_personas(
        self, 
        n: int,
        demographic_distributions: Optional[Dict[str, Dict[str, float]]] = None,
        ensure_diversity: bool = True
    ) -> List[Persona]:
        """
        生成 Persona 池
        
        Args:
            n: 生成数量
            demographic_distributions: 人口统计分布 {field: {value: probability}}
            ensure_diversity: 是否确保多样性
        """
        personas = []
        
        for i in range(n):
            # 生成人口统计信息
            if demographic_distributions:
                demographics = self._sample_from_distribution(demographic_distributions)
            else:
                demographics = self._generate_default_demographics()
            
            # 生成心理特征
            psychographics = self._generate_psychographics(demographics)
            
            # 生成价值观
            values = self._generate_values(demographics, psychographics)
            
            # 生成决策风格
            decision_style = self.rng.choice(self.DECISION_STYLES)
            
            # 生成知识领域
            knowledge_domains = self._generate_knowledge_domains(demographics)
            
            # 置信度阈值
            confidence_threshold = self.rng.uniform(0.3, 0.7)
            
            persona = Persona(
                id=f"PERSONA_{i:05d}",
                demographics=demographics,
                psychographics=psychographics,
                values=values,
                decision_style=decision_style,
                knowledge_domains=knowledge_domains,
                confidence_threshold=confidence_threshold
            )
            
            personas.append(persona)
        
        if ensure_diversity:
            personas = self._ensure_diversity(personas)
        
        return personas
    
    def generate_persona_from_demographics(
        self, 
        demographics: Dict[str, str]
    ) -> Persona:
        """基于人口统计生成单个 Persona"""
        psychographics = self._generate_psychographics(demographics)
        values = self._generate_values(demographics, psychographics)
        
        return Persona(
            id=f"PERSONA_CUSTOM_{self.rng.randint(10000, 99999)}",
            demographics=demographics,
            psychographics=psychographics,
            values=values,
            decision_style=self.rng.choice(self.DECISION_STYLES),
            knowledge_domains=self._generate_knowledge_domains(demographics),
            confidence_threshold=self.rng.uniform(0.3, 0.7)
        )
    
    def _generate_default_demographics(self) -> Dict[str, str]:
        """生成默认人口统计"""
        return {
            'age_group': self.rng.choices(
                ['18-29', '30-44', '45-59', '60+'],
                weights=[0.2, 0.25, 0.3, 0.25]
            )[0],
            'gender': self.rng.choices(
                ['Male', 'Female', 'Other'],
                weights=[0.48, 0.50, 0.02]
            )[0],
            'race': self.rng.choices(
                ['White', 'Black', 'Hispanic', 'Asian', 'Other'],
                weights=[0.6, 0.12, 0.18, 0.06, 0.04]
            )[0],
            'education': self.rng.choices(
                ['HS', 'Some College', 'Bachelor', 'Graduate'],
                weights=[0.25, 0.30, 0.30, 0.15]
            )[0],
            'income': self.rng.choices(
                ['<30k', '30k-60k', '60k-100k', '>100k'],
                weights=[0.25, 0.30, 0.25, 0.20]
            )[0],
            'region': self.rng.choices(
                ['Northeast', 'Midwest', 'South', 'West'],
                weights=[0.18, 0.21, 0.38, 0.23]
            )[0]
        }
    
    def _sample_from_distribution(self, distributions: Dict[str, Dict[str, float]]) -> Dict[str, str]:
        """从给定分布采样"""
        result = {}
        for field, dist in distributions.items():
            values = list(dist.keys())
            probs = list(dist.values())
            # 归一化
            total = sum(probs)
            probs = [p / total for p in probs]
            result[field] = self.rng.choices(values, weights=probs)[0]
        return result
    
    def _generate_psychographics(self, demographics: Dict[str, str]) -> Dict[str, Any]:
        """生成心理特征"""
        # 基于人口统计生成相关心理特征
        personality = []
        
        # 教育水平影响开放性
        if demographics.get('education') in ['Bachelor', 'Graduate']:
            personality.extend(['Openness', 'Analytical'])
        else:
            personality.extend(self.rng.sample(self.PERSONALITY_TRAITS, 2))
        
        # 年龄影响
        age = demographics.get('age_group', '')
        if '60+' in age:
            personality.append('Tradition-oriented')
        elif '18-29' in age:
            personality.append('Innovation-oriented')
        
        return {
            'personality': list(set(personality)),
            'risk_tolerance': self.rng.choice(['Low', 'Medium', 'High']),
            'social_orientation': self.rng.choice(['Individualist', 'Collectivist', 'Mixed'])
        }
    
    def _generate_values(self, demographics: Dict[str, str], psychographics: Dict) -> List[str]:
        """生成价值观"""
        n_values = self.rng.randint(2, 4)
        values = []
        
        # 基于人口统计调整权重
        weights = {v: 1.0 for v in self.VALUES_POOL}
        
        # 教育水平
        if demographics.get('education') == 'Graduate':
            weights['Innovation'] *= 2
            weights['Success'] *= 1.5
        
        # 收入水平
        if demographics.get('income') in ['60k-100k', '>100k']:
            weights['Security'] *= 1.5
            weights['Wealth'] *= 1.5
        
        # 年龄
        if '60+' in demographics.get('age_group', ''):
            weights['Tradition'] *= 2
            weights['Family'] *= 1.5
        elif '18-29' in demographics.get('age_group', ''):
            weights['Innovation'] *= 1.5
            weights['Freedom'] *= 1.5
        
        # 加权采样
        value_list = list(weights.keys())
        value_weights = list(weights.values())
        
        for _ in range(n_values):
            value = self.rng.choices(value_list, weights=value_weights)[0]
            if value not in values:
                values.append(value)
        
        return values
    
    def _generate_knowledge_domains(self, demographics: Dict[str, str]) -> List[str]:
        """生成知识领域"""
        domains = ['General']
        
        # 基于教育
        education = demographics.get('education', '')
        if education == 'Graduate':
            domains.append('Academic')
        if education in ['Bachelor', 'Graduate']:
            domains.append('Professional')
        
        # 基于年龄
        age = demographics.get('age_group', '')
        if '60+' in age:
            domains.append('Life Experience')
        elif '18-29' in age:
            domains.append('Technology')
        
        return domains
    
    def _ensure_diversity(self, personas: List[Persona]) -> List[Persona]:
        """确保 Persona 池的多样性"""
        # 计算每个属性的唯一值数量
        attribute_counts = {}
        for p in personas:
            for k, v in p.demographics.items():
                if k not in attribute_counts:
                    attribute_counts[k] = {}
                attribute_counts[k][v] = attribute_counts[k].get(v, 0) + 1
        
        # 简单的多样性检查
        # 在实际应用中可以使用更复杂的聚类或优化方法
        return personas


class PersonaPool:
    """Persona 池管理器"""
    
    def __init__(self, personas: List[Persona]):
        self.personas = personas
        self._index = {p.id: p for p in personas}
    
    def get_persona(self, persona_id: str) -> Optional[Persona]:
        """获取指定 Persona"""
        return self._index.get(persona_id)
    
    def sample_personas(self, n: int, demographics_filter: Optional[Dict] = None) -> List[Persona]:
        """采样 Persona"""
        pool = self.personas
        
        if demographics_filter:
            pool = [
                p for p in pool 
                if all(p.demographics.get(k) == v for k, v in demographics_filter.items())
            ]
        
        return random.sample(pool, min(n, len(pool)))
    
    def get_demographic_distribution(self) -> Dict[str, Dict[str, float]]:
        """获取人口统计分布"""
        dist = {}
        
        for p in self.personas:
            for k, v in p.demographics.items():
                if k not in dist:
                    dist[k] = {}
                dist[k][v] = dist[k].get(v, 0) + 1
        
        # 归一化
        for k in dist:
            total = sum(dist[k].values())
            dist[k] = {v: c / total for v, c in dist[k].items()}
        
        return dist
    
    def save(self, path: str):
        """保存 Persona 池"""
        data = {
            'personas': [p.to_dict() for p in self.personas],
            'metadata': {
                'n_personas': len(self.personas),
                'demographic_distribution': self.get_demographic_distribution()
            }
        }
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load(cls, path: str) -> 'PersonaPool':
        """加载 Persona 池"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        personas = [Persona.from_dict(p) for p in data['personas']]
        return cls(personas)


if __name__ == "__main__":
    # 测试 Persona 生成
    print("测试 Persona 生成器...")
    
    generator = PersonaGenerator(seed=42)
    
    # 生成 10 个 Persona
    personas = generator.generate_personas(10)
    
    print(f"\n生成了 {len(personas)} 个 Persona")
    
    for p in personas[:3]:
        print(f"\n--- {p.id} ---")
        print(f"人口统计: {p.demographics}")
        print(f"价值观: {p.values}")
        print(f"决策风格: {p.decision_style}")
        print(f"\n提示词:\n{p.to_prompt('simple')}")
    
    # 测试 PersonaPool
    pool = PersonaPool(personas)
    print(f"\n人口统计分布: {pool.get_demographic_distribution()}")
    
    # 保存和加载
    pool.save("data/cache/persona_pool_test.json")
    loaded_pool = PersonaPool.load("data/cache/persona_pool_test.json")
    print(f"\n加载的 Persona 数量: {len(loaded_pool.personas)}")
