"""关键词过滤器

对文本内容进行敏感词检查和过滤。
"""

import re
from typing import Dict, List, Set, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class KeywordFilter:
    """关键词过滤器"""
    
    def __init__(self, keywords_dir: str = "data/safety_config/keywords"):
        self.keywords_dir = Path(keywords_dir)
        self.keyword_sets: Dict[str, Set[str]] = {}
        self.pattern_cache: Dict[str, re.Pattern] = {}
        self._load_keywords()
    
    def _load_keywords(self):
        """加载敏感词库"""
        try:
            if not self.keywords_dir.exists():
                self._create_default_keywords()
                return
            
            for keyword_file in self.keywords_dir.glob("*.txt"):
                category = keyword_file.stem
                keywords = set()
                
                with open(keyword_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            keywords.add(line)
                
                self.keyword_sets[category] = keywords
                logger.info(f"加载 {category} 敏感词 {len(keywords)} 个")
        
        except Exception as e:
            logger.error(f"加载敏感词库失败: {e}")
            self._create_default_keywords()
    
    def _create_default_keywords(self):
        """创建默认敏感词库"""
        default_keywords = {
            "political": [
                "政治敏感词示例1",
                "政治敏感词示例2"
            ],
            "nsfw": [
                "不适宜内容示例1",
                "不适宜内容示例2"
            ],
            "financial_violations": [
                "保证收益",
                "稳赚不赔", 
                "无风险高收益",
                "内幕消息",
                "操纵市场",
                "非法集资",
                "一定赚钱",
                "必然上涨",
                "绝对安全",
                "零风险"
            ]
        }
        
        # 创建目录
        self.keywords_dir.mkdir(parents=True, exist_ok=True)
        
        # 写入默认词库
        for category, keywords in default_keywords.items():
            keyword_file = self.keywords_dir / f"{category}.txt"
            with open(keyword_file, 'w', encoding='utf-8') as f:
                f.write("# " + category + " 敏感词库\n")
                for keyword in keywords:
                    f.write(keyword + "\n")
        
        # 重新加载
        self._load_keywords()
    
    def check_keywords(self, text: str, categories: Optional[List[str]] = None) -> List[Dict]:
        """检查文本中的敏感词"""
        violations = []
        
        check_categories = categories or list(self.keyword_sets.keys())
        
        for category in check_categories:
            if category not in self.keyword_sets:
                continue
                
            keywords = self.keyword_sets[category]
            
            for keyword in keywords:
                if keyword in text:
                    # 找到所有匹配位置
                    positions = []
                    start = 0
                    while True:
                        pos = text.find(keyword, start)
                        if pos == -1:
                            break
                        positions.append(pos)
                        start = pos + 1
                    
                    if positions:
                        violations.append({
                            "category": category,
                            "keyword": keyword,
                            "positions": positions,
                            "count": len(positions),
                            "severity": self._get_severity(category)
                        })
        
        return violations
    
    def filter_content(self, text: str, replacement: str = "***") -> Dict[str, Any]:
        """过滤文本内容"""
        
        violations = self.check_keywords(text)
        filtered_text = text
        
        # 按关键词长度倒序排列，避免替换冲突
        all_keywords = []
        for violation in violations:
            all_keywords.extend([(violation["keyword"], violation["category"])])
        
        all_keywords.sort(key=lambda x: len(x[0]), reverse=True)
        
        # 执行替换
        for keyword, category in all_keywords:
            if self._should_replace(category):
                filtered_text = filtered_text.replace(keyword, replacement)
        
        return {
            "original_text": text,
            "filtered_text": filtered_text,
            "violations": violations,
            "is_filtered": filtered_text != text
        }
    
    def add_keywords(self, category: str, keywords: List[str]):
        """添加敏感词"""
        if category not in self.keyword_sets:
            self.keyword_sets[category] = set()
        
        self.keyword_sets[category].update(keywords)
        
        # 保存到文件
        self._save_keywords(category)
    
    def remove_keywords(self, category: str, keywords: List[str]):
        """移除敏感词"""
        if category in self.keyword_sets:
            self.keyword_sets[category] -= set(keywords)
            self._save_keywords(category)
    
    def _save_keywords(self, category: str):
        """保存敏感词到文件"""
        try:
            keyword_file = self.keywords_dir / f"{category}.txt"
            with open(keyword_file, 'w', encoding='utf-8') as f:
                f.write(f"# {category} 敏感词库\n")
                for keyword in sorted(self.keyword_sets[category]):
                    f.write(keyword + "\n")
        except Exception as e:
            logger.error(f"保存敏感词库失败 {category}: {e}")
    
    def _get_severity(self, category: str) -> str:
        """获取类别严重程度"""
        severity_mapping = {
            "political": "high",
            "nsfw": "high",
            "financial_violations": "medium",
            "discrimination": "high"
        }
        return severity_mapping.get(category, "low")
    
    def _should_replace(self, category: str) -> bool:
        """判断是否应该替换敏感词"""
        replace_categories = {"political", "nsfw", "discrimination"}
        return category in replace_categories
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取词库统计信息"""
        stats = {}
        total_keywords = 0
        
        for category, keywords in self.keyword_sets.items():
            count = len(keywords)
            stats[category] = count
            total_keywords += count
        
        return {
            "categories": stats,
            "total_keywords": total_keywords,
            "categories_count": len(self.keyword_sets)
        }


# 全局关键词过滤器实例
keyword_filter = KeywordFilter()


def check_sensitive_keywords(text: str, categories: Optional[List[str]] = None) -> List[Dict]:
    """便捷函数：检查敏感词"""
    return keyword_filter.check_keywords(text, categories)


def filter_sensitive_content(text: str, replacement: str = "***") -> Dict[str, Any]:
    """便捷函数：过滤敏感内容"""
    return keyword_filter.filter_content(text, replacement)


if __name__ == "__main__":
    # 测试代码
    test_text = "这个投资保证收益，绝对稳赚不赔。"
    
    violations = check_sensitive_keywords(test_text)
    print(f"发现违规词汇: {len(violations)} 个")
    
    filtered_result = filter_sensitive_content(test_text)
    print(f"过滤后内容: {filtered_result['filtered_text']}")
    print(f"是否被过滤: {filtered_result['is_filtered']}")
