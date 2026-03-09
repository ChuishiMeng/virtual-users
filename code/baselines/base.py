"""
Baseline 方法基类

所有 Baseline 方法的抽象基类和通用功能
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import random


@dataclass
class SurveyResult:
    """问卷结果"""
    persona_id: str
    question_id: str
    response: str
    confidence: float = 1.0
    method: str = "unknown"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseMethod(ABC):
    """Baseline 方法基类"""
    
    name: str = "base"
    description: str = "Base method class"
    
    def __init__(self, seed: int = 42, config: Optional[Dict] = None):
        self.seed = seed
        self.config = config or {}
        self.rng = random.Random(seed)
        np.random.seed(seed)
    
    @abstractmethod
    def generate_response(
        self,
        question: str,
        options: List[str],
        persona_info: Optional[Dict] = None,
        context: Optional[str] = None
    ) -> SurveyResult:
        """
        生成问卷响应
        
        Args:
            question: 问题文本
            options: 选项列表
            persona_info: Persona 信息（可选）
            context: 额外上下文（可选）
        
        Returns:
            SurveyResult 对象
        """
        pass
    
    def generate_batch(
        self,
        questions: List[Tuple[str, List[str]]],  # [(question, options), ...]
        persona_info: Optional[Dict] = None,
        context: Optional[str] = None
    ) -> List[SurveyResult]:
        """批量生成响应"""
        results = []
        for i, (question, options) in enumerate(questions):
            result = self.generate_response(question, options, persona_info, context)
            result.question_id = f"Q{i+1}"
            results.append(result)
        return results
    
    def set_seed(self, seed: int):
        """设置随机种子"""
        self.seed = seed
        self.rng = random.Random(seed)
        np.random.seed(seed)


class RandomMethod(BaseMethod):
    """
    Random Baseline
    
    均匀随机选择选项（下界参考）
    """
    
    name = "random"
    description = "均匀随机选择"
    
    def generate_response(
        self,
        question: str,
        options: List[str],
        persona_info: Optional[Dict] = None,
        context: Optional[str] = None
    ) -> SurveyResult:
        """随机选择一个选项"""
        response = self.rng.choice(options)
        
        return SurveyResult(
            persona_id=persona_info.get('id', 'UNKNOWN') if persona_info else 'UNKNOWN',
            question_id='',
            response=response,
            confidence=1.0 / len(options),  # 均匀分布的置信度
            method=self.name,
            metadata={'n_options': len(options)}
        )


class ModeMethod(BaseMethod):
    """
    Mode Baseline
    
    总是选择最常见选项（需要先验分布）
    """
    
    name = "mode"
    description = "总是选择最常见选项"
    
    def __init__(self, mode_options: Optional[Dict[str, str]] = None, 
                 seed: int = 42, config: Optional[Dict] = None):
        super().__init__(seed, config)
        # mode_options: {question_id: most_common_option}
        self.mode_options = mode_options or {}
    
    def generate_response(
        self,
        question: str,
        options: List[str],
        persona_info: Optional[Dict] = None,
        context: Optional[str] = None
    ) -> SurveyResult:
        """选择最常见选项"""
        # 如果有预定义的模式，使用它
        question_key = context or question[:50]  # 简化的问题键
        
        if question_key in self.mode_options:
            response = self.mode_options[question_key]
            if response not in options:
                response = self.rng.choice(options)
        else:
            # 默认选择第一个选项（或最后一个，取决于设置）
            response = options[-1] if len(options) > 1 else options[0]
        
        return SurveyResult(
            persona_id=persona_info.get('id', 'UNKNOWN') if persona_info else 'UNKNOWN',
            question_id='',
            response=response,
            confidence=1.0,
            method=self.name,
            metadata={'mode_based': question_key in self.mode_options}
        )


class LLMDirectMethod(BaseMethod):
    """
    LLM-Direct Baseline
    
    无 Persona 直接使用 LLM 生成响应
    """
    
    name = "llm_direct"
    description = "无 Persona 直接生成"
    
    def __init__(self, llm_client=None, seed: int = 42, config: Optional[Dict] = None):
        super().__init__(seed, config)
        self.llm_client = llm_client
        self.temperature = self.config.get('temperature', 0.7)
    
    def generate_response(
        self,
        question: str,
        options: List[str],
        persona_info: Optional[Dict] = None,
        context: Optional[str] = None
    ) -> SurveyResult:
        """直接使用 LLM 生成响应（无 Persona）"""
        
        # 构建提示
        prompt = self._build_prompt(question, options, context)
        
        # 如果有 LLM 客户端，调用它
        if self.llm_client is not None:
            response, confidence = self._call_llm(prompt, options)
        else:
            # 模拟模式：随机选择（用于测试）
            response, confidence = self._simulate_response(options)
        
        return SurveyResult(
            persona_id=persona_info.get('id', 'UNKNOWN') if persona_info else 'UNKNOWN',
            question_id='',
            response=response,
            confidence=confidence,
            method=self.name,
            metadata={'prompt_length': len(prompt)}
        )
    
    def _build_prompt(self, question: str, options: List[str], context: Optional[str]) -> str:
        """构建提示"""
        options_str = "\n".join(f"{i+1}. {opt}" for i, opt in enumerate(options))
        
        prompt = f"""Please answer the following survey question. Select one option from the list below.

Question: {question}

Options:
{options_str}

Please respond with only the option you choose, without any explanation."""
        
        if context:
            prompt = f"Context: {context}\n\n{prompt}"
        
        return prompt
    
    def _call_llm(self, prompt: str, options: List[str]) -> Tuple[str, float]:
        """调用 LLM（子类实现）"""
        # 基类提供默认实现，子类可覆盖
        raise NotImplementedError("Subclass must implement _call_llm")
    
    def _simulate_response(self, options: List[str]) -> Tuple[str, float]:
        """模拟响应（用于测试）"""
        # 使用带有一定偏好的随机选择
        weights = self._get_option_weights(len(options))
        idx = self.rng.choices(range(len(options)), weights=weights)[0]
        return options[idx], weights[idx]
    
    def _get_option_weights(self, n_options: int) -> List[float]:
        """获取选项权重（模拟 LLM 的偏好）"""
        # 简单的偏好分布：中间选项稍高
        if n_options == 2:
            return [0.55, 0.45]
        elif n_options == 3:
            return [0.25, 0.50, 0.25]
        elif n_options == 4:
            return [0.20, 0.35, 0.30, 0.15]
        else:
            # 均匀分布
            return [1.0 / n_options] * n_options


class LLMPromptMethod(LLMDirectMethod):
    """
    LLM-Prompt Baseline
    
    使用简单 Persona 描述生成响应
    """
    
    name = "llm_prompt"
    description = "简单 Persona 描述"
    
    def generate_response(
        self,
        question: str,
        options: List[str],
        persona_info: Optional[Dict] = None,
        context: Optional[str] = None
    ) -> SurveyResult:
        """使用 Persona 信息生成响应"""
        
        # 构建 Persona 提示
        persona_prompt = self._build_persona_prompt(persona_info)
        
        # 构建完整提示
        prompt = self._build_prompt_with_persona(question, options, persona_prompt, context)
        
        if self.llm_client is not None:
            response, confidence = self._call_llm(prompt, options)
        else:
            response, confidence = self._simulate_response_with_persona(options, persona_info)
        
        return SurveyResult(
            persona_id=persona_info.get('id', 'UNKNOWN') if persona_info else 'UNKNOWN',
            question_id='',
            response=response,
            confidence=confidence,
            method=self.name,
            metadata={
                'has_persona': persona_info is not None,
                'prompt_length': len(prompt)
            }
        )
    
    def _build_persona_prompt(self, persona_info: Optional[Dict]) -> str:
        """构建 Persona 提示"""
        if persona_info is None:
            return "You are an average person."
        
        demographics = persona_info.get('demographics', {})
        demo_parts = [f"{k}: {v}" for k, v in demographics.items()]
        
        if demo_parts:
            return f"You are a person with the following characteristics: {', '.join(demo_parts)}."
        else:
            return "You are an average person."
    
    def _build_prompt_with_persona(self, question: str, options: List[str], 
                                   persona_prompt: str, context: Optional[str]) -> str:
        """构建带 Persona 的提示"""
        options_str = "\n".join(f"{i+1}. {opt}" for i, opt in enumerate(options))
        
        prompt = f"""{persona_prompt}

Please answer the following survey question based on your characteristics. Select one option from the list below.

Question: {question}

Options:
{options_str}

Please respond with only the option you choose, without any explanation."""
        
        if context:
            prompt = f"Context: {context}\n\n{prompt}"
        
        return prompt
    
    def _simulate_response_with_persona(self, options: List[str], 
                                        persona_info: Optional[Dict]) -> Tuple[str, float]:
        """基于 Persona 模拟响应"""
        # 这里实现简单的 Persona 基于偏好
        # 实际应用中应该调用真正的 LLM
        
        weights = self._get_persona_based_weights(options, persona_info)
        idx = self.rng.choices(range(len(options)), weights=weights)[0]
        return options[idx], weights[idx]
    
    def _get_persona_based_weights(self, options: List[str], 
                                   persona_info: Optional[Dict]) -> List[float]:
        """基于 Persona 获取选项权重"""
        base_weights = self._get_option_weights(len(options))
        
        if persona_info is None:
            return base_weights
        
        # 根据 Persona 调整权重
        demographics = persona_info.get('demographics', {})
        values = persona_info.get('values', [])
        
        # 简单规则：基于选项文本和人口统计调整
        adjusted_weights = base_weights.copy()
        
        for i, option in enumerate(options):
            # 教育水平影响
            education = demographics.get('education', '')
            if 'Graduate' in education or 'Bachelor' in education:
                if 'moderate' in option.lower() or 'middle' in option.lower():
                    adjusted_weights[i] *= 1.3
            
            # 年龄影响
            age = demographics.get('age_group', '')
            if '60+' in age:
                if 'traditional' in option.lower() or 'conservative' in option.lower():
                    adjusted_weights[i] *= 1.2
            elif '18-29' in age:
                if 'new' in option.lower() or 'progressive' in option.lower():
                    adjusted_weights[i] *= 1.2
        
        # 归一化
        total = sum(adjusted_weights)
        return [w / total for w in adjusted_weights]


class LLMS3PASMethod(LLMPromptMethod):
    """
    LLM-S³ PAS Method
    
    官方基准方法（参考 LLM-S³ Benchmark）
    """
    
    name = "llm_s3_pas"
    description = "LLM-S³ PAS 官方基准"
    
    def __init__(self, llm_client=None, seed: int = 42, config: Optional[Dict] = None):
        super().__init__(llm_client, seed, config)
        # PAS 特定配置
        self.use_context_augmentation = self.config.get('use_context_augmentation', True)
        self.use_distribution_matching = self.config.get('use_distribution_matching', False)
    
    def generate_response(
        self,
        question: str,
        options: List[str],
        persona_info: Optional[Dict] = None,
        context: Optional[str] = None
    ) -> SurveyResult:
        """使用 LLM-S³ PAS 方法生成响应"""
        
        # PAS 特定：使用上下文增强
        if self.use_context_augmentation and context is None:
            context = self._generate_context(persona_info)
        
        # 调用父类方法
        result = super().generate_response(question, options, persona_info, context)
        result.method = self.name
        
        # 添加 PAS 特定元数据
        result.metadata['pas_context_augmentation'] = self.use_context_augmentation
        
        return result
    
    def _generate_context(self, persona_info: Optional[Dict]) -> str:
        """生成上下文增强信息"""
        if persona_info is None:
            return ""
        
        demographics = persona_info.get('demographics', {})
        
        # 简单的上下文生成
        context_parts = []
        
        if 'region' in demographics:
            context_parts.append(f"living in the {demographics['region']} region")
        if 'education' in demographics:
            context_parts.append(f"with {demographics['education']} education")
        if 'income' in demographics:
            context_parts.append(f"in the {demographics['income']} income bracket")
        
        if context_parts:
            return f"Context: A respondent " + ", ".join(context_parts) + "."
        return ""


class MethodFactory:
    """方法工厂"""
    
    _methods = {
        'random': RandomMethod,
        'mode': ModeMethod,
        'llm_direct': LLMDirectMethod,
        'llm_prompt': LLMPromptMethod,
        'llm_s3_pas': LLMS3PASMethod,
    }
    
    @classmethod
    def create(cls, method_name: str, llm_client=None, 
               seed: int = 42, config: Optional[Dict] = None) -> BaseMethod:
        """创建方法实例"""
        if method_name not in cls._methods:
            raise ValueError(f"Unknown method: {method_name}. Available: {list(cls._methods.keys())}")
        
        method_class = cls._methods[method_name]
        
        # Random, Mode, and ConsistAgent don't need llm_client
        if method_name in ['random', 'mode', 'consist_agent']:
            if method_name == 'mode':
                return method_class(seed=seed, config=config)
            return method_class(seed=seed, config=config)
        return method_class(llm_client=llm_client, seed=seed, config=config)
    
    @classmethod
    def register(cls, name: str, method_class: type):
        """注册新方法"""
        cls._methods[name] = method_class
    
    @classmethod
    def list_methods(cls) -> List[str]:
        """列出所有可用方法"""
        return list(cls._methods.keys())


if __name__ == "__main__":
    # 测试 Baseline 方法
    print("测试 Baseline 方法...")
    
    # 测试问题
    question = "Who do you plan to vote for in the upcoming election?"
    options = ["Candidate A", "Candidate B", "Undecided", "Will not vote"]
    persona_info = {
        'id': 'TEST_001',
        'demographics': {
            'age_group': '30-44',
            'gender': 'Female',
            'education': 'Bachelor',
            'income': '60k-100k',
            'region': 'West'
        },
        'values': ['Innovation', 'Freedom', 'Equality']
    }
    
    # 测试各个方法
    methods = ['random', 'mode', 'llm_direct', 'llm_prompt', 'llm_s3_pas']
    
    for method_name in methods:
        print(f"\n--- {method_name} ---")
        method = MethodFactory.create(method_name, seed=42)
        result = method.generate_response(question, options, persona_info)
        print(f"响应: {result.response}")
        print(f"置信度: {result.confidence:.3f}")
        print(f"元数据: {result.metadata}")
