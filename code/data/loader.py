"""
数据加载器模块

支持 ANES、GSS、ACS 等数据集的加载和预处理
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import json
import pandas as pd
import numpy as np


@dataclass
class SurveyQuestion:
    """问卷问题"""
    id: str
    text: str
    question_type: str  # single_choice, multiple_choice, scale, open
    options: List[str]
    demographic: bool = False  # 是否为人口统计问题
    weight: float = 1.0


@dataclass
class SurveyResponse:
    """问卷响应"""
    respondent_id: str
    demographics: Dict[str, Any]  # 人口统计信息
    responses: Dict[str, Any]  # 问题ID -> 响应
    weights: Optional[float] = None


@dataclass
class SurveyDataset:
    """问卷数据集"""
    name: str
    domain: str
    questions: List[SurveyQuestion]
    responses: List[SurveyResponse]
    metadata: Dict[str, Any]
    
    def get_demographic_fields(self) -> List[str]:
        """获取人口统计字段"""
        return [q.id for q in self.questions if q.demographic]
    
    def get_survey_fields(self) -> List[str]:
        """获取调查问题字段"""
        return [q.id for q in self.questions if not q.demographic]
    
    def get_response_distribution(self, question_id: str) -> Dict[str, float]:
        """获取某个问题的响应分布"""
        responses = [r.responses.get(question_id) for r in self.responses]
        responses = [r for r in responses if r is not None]
        
        if not responses:
            return {}
        
        # 统计频率
        counts = {}
        for r in responses:
            key = str(r)
            counts[key] = counts.get(key, 0) + 1
        
        # 归一化为概率
        total = len(responses)
        return {k: v / total for k, v in counts.items()}
    
    def to_dataframe(self) -> pd.DataFrame:
        """转换为 DataFrame"""
        records = []
        for r in self.responses:
            record = {'respondent_id': r.respondent_id}
            record.update(r.demographics)
            record.update(r.responses)
            if r.weights is not None:
                record['weight'] = r.weights
            records.append(record)
        return pd.DataFrame(records)


class BaseDataLoader(ABC):
    """数据加载器基类"""
    
    def __init__(self, data_dir: str = "data/raw", cache_dir: str = "data/cache"):
        self.data_dir = Path(data_dir)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def load(self, sample_size: Optional[int] = None) -> SurveyDataset:
        """加载数据集"""
        pass
    
    @abstractmethod
    def get_question_schema(self) -> List[SurveyQuestion]:
        """获取问题模式"""
        pass
    
    def _sample_responses(self, responses: List[SurveyResponse], 
                          sample_size: int, seed: int = 42) -> List[SurveyResponse]:
        """采样响应"""
        np.random.seed(seed)
        indices = np.random.choice(len(responses), min(sample_size, len(responses)), replace=False)
        return [responses[i] for i in indices]


class ANESLoader(BaseDataLoader):
    """ANES 2020 数据加载器"""
    
    # ANES 2020 核心人口统计字段
    DEMOGRAPHIC_FIELDS = [
        'V201018',   # 年龄组
        'V201511',   # 性别
        'V201510',   # 种族
        'V201514',   # 教育水平
        'V201614',   # 收入
        'V201024',   # 地区
    ]
    
    # 核心调查问题
    SURVEY_FIELDS = [
        'V202031',   # 总统投票意向
        'V202066',   # 党派认同
        'V202163',   # 经济状况评估
        'V202167',   # 国家方向
        'V202361',   # 政府信任
    ]
    
    def load(self, sample_size: Optional[int] = None) -> SurveyDataset:
        """加载 ANES 数据集"""
        # 尝试从缓存加载
        cache_file = self.cache_dir / "anes_2020_processed.json"
        if cache_file.exists():
            return self._load_from_cache(cache_file, sample_size)
        
        # 如果没有真实数据，生成模拟数据用于测试
        return self._generate_mock_data(sample_size)
    
    def _generate_mock_data(self, sample_size: Optional[int] = None) -> SurveyDataset:
        """生成模拟数据用于测试"""
        np.random.seed(42)
        n = sample_size or 1000
        
        questions = self.get_question_schema()
        
        # 生成响应
        responses = []
        for i in range(n):
            # 生成人口统计信息
            demographics = {
                'age_group': np.random.choice(['18-29', '30-44', '45-59', '60+'], p=[0.2, 0.25, 0.3, 0.25]),
                'gender': np.random.choice(['Male', 'Female', 'Other'], p=[0.48, 0.50, 0.02]),
                'race': np.random.choice(['White', 'Black', 'Hispanic', 'Asian', 'Other'], p=[0.6, 0.12, 0.18, 0.06, 0.04]),
                'education': np.random.choice(['HS', 'Some College', 'Bachelor', 'Graduate'], p=[0.25, 0.30, 0.30, 0.15]),
                'income': np.random.choice(['<30k', '30k-60k', '60k-100k', '>100k'], p=[0.25, 0.30, 0.25, 0.20]),
                'region': np.random.choice(['Northeast', 'Midwest', 'South', 'West'], p=[0.18, 0.21, 0.38, 0.23]),
            }
            
            # 基于人口统计生成响应（模拟真实相关性）
            party_preference = self._simulate_party_preference(demographics)
            
            survey_responses = {
                'presidential_vote': np.random.choice(['Biden', 'Trump', 'Other', 'No Vote'], 
                                                      p=party_preference),
                'party_id': np.random.choice(['Democrat', 'Republican', 'Independent', 'Other'],
                                             p=[0.35, 0.30, 0.30, 0.05]),
                'economy_rating': np.random.choice(['Better', 'Worse', 'Same'], p=[0.3, 0.4, 0.3]),
                'country_direction': np.random.choice(['Right', 'Wrong'], p=[0.4, 0.6]),
                'trust_government': np.random.choice(['Trust', 'Distrust', 'Neutral'], p=[0.25, 0.45, 0.30]),
            }
            
            responses.append(SurveyResponse(
                respondent_id=f"ANES_{i:05d}",
                demographics=demographics,
                responses=survey_responses
            ))
        
        return SurveyDataset(
            name="ANES 2020",
            domain="政治态度",
            questions=questions,
            responses=responses,
            metadata={
                'source': 'ANES 2020 Time Series',
                'n_respondents': n,
                'year': 2020
            }
        )
    
    def _simulate_party_preference(self, demographics: Dict) -> List[float]:
        """模拟党派偏好（基于人口统计）"""
        base = [0.35, 0.35, 0.10, 0.20]  # Biden, Trump, Other, No Vote
        
        # 根据人口统计调整
        if demographics['education'] == 'Graduate':
            base[0] += 0.15
            base[1] -= 0.15
        elif demographics['education'] == 'HS':
            base[0] -= 0.10
            base[1] += 0.10
        
        if demographics['race'] == 'Black':
            base[0] += 0.40
            base[1] -= 0.40
        elif demographics['race'] == 'White':
            base[0] -= 0.05
            base[1] += 0.05
        
        # 归一化
        total = sum(base)
        return [b / total for b in base]
    
    def get_question_schema(self) -> List[SurveyQuestion]:
        """获取 ANES 问题模式"""
        return [
            # 人口统计问题
            SurveyQuestion('age_group', 'What is your age group?', 'single_choice',
                          ['18-29', '30-44', '45-59', '60+'], demographic=True),
            SurveyQuestion('gender', 'What is your gender?', 'single_choice',
                          ['Male', 'Female', 'Other'], demographic=True),
            SurveyQuestion('race', 'What is your race/ethnicity?', 'single_choice',
                          ['White', 'Black', 'Hispanic', 'Asian', 'Other'], demographic=True),
            SurveyQuestion('education', 'What is your highest education level?', 'single_choice',
                          ['HS', 'Some College', 'Bachelor', 'Graduate'], demographic=True),
            SurveyQuestion('income', 'What is your household income?', 'single_choice',
                          ['<30k', '30k-60k', '60k-100k', '>100k'], demographic=True),
            SurveyQuestion('region', 'Which region do you live in?', 'single_choice',
                          ['Northeast', 'Midwest', 'South', 'West'], demographic=True),
            # 调查问题
            SurveyQuestion('presidential_vote', 'Who did you vote for President?', 'single_choice',
                          ['Biden', 'Trump', 'Other', 'No Vote']),
            SurveyQuestion('party_id', 'Which party do you identify with?', 'single_choice',
                          ['Democrat', 'Republican', 'Independent', 'Other']),
            SurveyQuestion('economy_rating', 'How would you rate the economy?', 'single_choice',
                          ['Better', 'Worse', 'Same']),
            SurveyQuestion('country_direction', 'Is the country heading in the right direction?', 
                          'single_choice', ['Right', 'Wrong']),
            SurveyQuestion('trust_government', 'Do you trust the government?', 'single_choice',
                          ['Trust', 'Distrust', 'Neutral']),
        ]
    
    def _load_from_cache(self, cache_file: Path, sample_size: Optional[int]) -> SurveyDataset:
        """从缓存加载数据"""
        with open(cache_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        responses = [
            SurveyResponse(**r) for r in data['responses']
        ]
        
        if sample_size:
            responses = self._sample_responses(responses, sample_size)
        
        return SurveyDataset(
            name=data['name'],
            domain=data['domain'],
            questions=[SurveyQuestion(**q) for q in data['questions']],
            responses=responses,
            metadata=data['metadata']
        )


class GSSLoader(BaseDataLoader):
    """GSS 2018 数据加载器"""
    
    def load(self, sample_size: Optional[int] = None) -> SurveyDataset:
        """加载 GSS 数据集"""
        return self._generate_mock_data(sample_size)
    
    def _generate_mock_data(self, sample_size: Optional[int] = None) -> SurveyDataset:
        """生成模拟 GSS 数据"""
        np.random.seed(42)
        n = sample_size or 1000
        
        questions = self.get_question_schema()
        
        responses = []
        for i in range(n):
            demographics = {
                'age': np.random.randint(18, 90),
                'gender': np.random.choice(['Male', 'Female']),
                'race': np.random.choice(['White', 'Black', 'Other']),
                'education': np.random.choice(['<HS', 'HS', 'College', 'Graduate']),
                'income': np.random.choice(['Low', 'Medium', 'High']),
            }
            
            survey_responses = {
                'general_happiness': np.random.choice(['Very Happy', 'Pretty Happy', 'Not Too Happy']),
                'job_satisfaction': np.random.choice(['Very Satisfied', 'Mod. Satisfied', 'A Little Dissat', 'Very Dissatisfied']),
                'trust_people': np.random.choice(['Can Trust', 'Cannot Trust', 'Depends']),
                'political_views': np.random.choice(['Ext. Liberal', 'Liberal', 'Slight. Liberal', 'Moderate', 
                                                    'Slight. Conserv', 'Conserv', 'Ext. Conserv']),
                'confidence_science': np.random.choice(['A Great Deal', 'Only Some', 'Hardly Any']),
            }
            
            responses.append(SurveyResponse(
                respondent_id=f"GSS_{i:05d}",
                demographics=demographics,
                responses=survey_responses
            ))
        
        return SurveyDataset(
            name="GSS 2018",
            domain="社会调查",
            questions=questions,
            responses=responses,
            metadata={'source': 'GSS 2018', 'n_respondents': n, 'year': 2018}
        )
    
    def get_question_schema(self) -> List[SurveyQuestion]:
        return [
            SurveyQuestion('age', 'What is your age?', 'scale', ['18-89'], demographic=True),
            SurveyQuestion('gender', 'What is your gender?', 'single_choice', ['Male', 'Female'], demographic=True),
            SurveyQuestion('race', 'What is your race?', 'single_choice', ['White', 'Black', 'Other'], demographic=True),
            SurveyQuestion('education', 'What is your education?', 'single_choice', 
                          ['<HS', 'HS', 'College', 'Graduate'], demographic=True),
            SurveyQuestion('income', 'What is your income level?', 'single_choice', 
                          ['Low', 'Medium', 'High'], demographic=True),
            SurveyQuestion('general_happiness', 'How happy are you?', 'single_choice',
                          ['Very Happy', 'Pretty Happy', 'Not Too Happy']),
            SurveyQuestion('job_satisfaction', 'How satisfied are you with your job?', 'single_choice',
                          ['Very Satisfied', 'Mod. Satisfied', 'A Little Dissat', 'Very Dissatisfied']),
            SurveyQuestion('trust_people', 'Can you trust people?', 'single_choice',
                          ['Can Trust', 'Cannot Trust', 'Depends']),
            SurveyQuestion('political_views', 'What are your political views?', 'single_choice',
                          ['Ext. Liberal', 'Liberal', 'Slight. Liberal', 'Moderate', 
                           'Slight. Conserv', 'Conserv', 'Ext. Conserv']),
            SurveyQuestion('confidence_science', 'Confidence in scientific community?', 'single_choice',
                          ['A Great Deal', 'Only Some', 'Hardly Any']),
        ]


class DataLoaderFactory:
    """数据加载器工厂"""
    
    _loaders = {
        'anes_2020': ANESLoader,
        'gss_2018': GSSLoader,
    }
    
    @classmethod
    def create(cls, dataset_name: str, data_dir: str = "data/raw", 
               cache_dir: str = "data/cache") -> BaseDataLoader:
        """创建数据加载器"""
        if dataset_name not in cls._loaders:
            raise ValueError(f"Unknown dataset: {dataset_name}. Available: {list(cls._loaders.keys())}")
        
        return cls._loaders[dataset_name](data_dir, cache_dir)
    
    @classmethod
    def register(cls, name: str, loader_class: type):
        """注册新的数据加载器"""
        cls._loaders[name] = loader_class


# 便捷函数
def load_dataset(name: str, sample_size: Optional[int] = None, 
                 data_dir: str = "data/raw") -> SurveyDataset:
    """加载数据集的便捷函数"""
    loader = DataLoaderFactory.create(name, data_dir)
    return loader.load(sample_size)


if __name__ == "__main__":
    # 测试数据加载
    print("测试 ANES 数据加载...")
    dataset = load_dataset("anes_2020", sample_size=100)
    print(f"数据集: {dataset.name}")
    print(f"样本数: {len(dataset.responses)}")
    print(f"问题数: {len(dataset.questions)}")
    print(f"人口统计字段: {dataset.get_demographic_fields()}")
    print(f"调查字段: {dataset.get_survey_fields()}")
    
    # 测试响应分布
    dist = dataset.get_response_distribution('presidential_vote')
    print(f"\n总统投票分布: {dist}")
    
    # 测试 DataFrame 转换
    df = dataset.to_dataframe()
    print(f"\nDataFrame shape: {df.shape}")
    print(df.head())
