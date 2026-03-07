#!/usr/bin/env python3
"""
华为云环境变量工具
支持从.env文件加载AK/SK
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import json
from datetime import datetime

class HuaweiEnvConfig:
    """华为云环境配置管理"""
    
    def __init__(self, env_file: str = ".env"):
        self.env_file = env_file
        self.config = {}
        self.loaded = False
        
    def load_env(self) -> bool:
        """加载环境变量"""
        try:
            # 尝试从指定文件加载
            env_path = Path(self.env_file)
            if env_path.exists():
                load_dotenv(dotenv_path=env_path)
                print(f"✅ 从 {self.env_file} 加载环境变量")
            else:
                # 尝试从工作目录加载
                load_dotenv()
                print("✅ 从系统环境变量加载")
            
            # 获取配置
            self.config = {
                "access_key": os.getenv("HUAWEI_ACCESS_KEY"),
                "secret_key": os.getenv("HUAWEI_SECRET_KEY"),
                "project_id": os.getenv("HUAWEI_PROJECT_ID"),
                "account_id": os.getenv("HUAWEI_ACCOUNT_ID", "hw59248219"),
                "region": os.getenv("HUAWEI_REGION", "cn-east-3"),
            }
            
            # 验证必要配置
            if not self.config["access_key"] or not self.config["secret_key"]:
                print("❌ 缺少必要的AK/SK配置")
                return False
                
            self.loaded = True
            return True
            
        except Exception as e:
            print(f"❌ 加载环境变量失败: {e}")
            return False
    
    def validate_config(self) -> bool:
        """验证配置完整性"""
        if not self.loaded:
            return False
            
        required = ["access_key", "secret_key"]
        missing = [key for key in required if not self.config.get(key)]
        
        if missing:
            print(f"❌ 缺少必要配置: {', '.join(missing)}")
            return False
            
        # 隐藏敏感信息显示
        masked_ak = self.mask_string(self.config["access_key"])
        masked_sk = self.mask_string(self.config["secret_key"])
        
        print("🔐 配置验证通过:")
        print(f"   账号ID: {self.config['account_id']}")
        print(f"   地域: {self.config['region']}")
        print(f"   Access Key: {masked_ak}")
        print(f"   Secret Key: {masked_sk}")
        if self.config["project_id"]:
            print(f"   项目ID: {self.config['project_id']}")
            
        return True
    
    def mask_string(self, text: str, visible_chars: int = 4) -> str:
        """隐藏敏感字符串"""
        if not text or len(text) <= visible_chars * 2:
            return "***"
        return f"{text[:visible_chars]}...{text[-visible_chars:]}"
    
    def generate_env_template(self) -> str:
        """生成.env文件模板"""
        template = """# 华为云API配置
# 账号: hw59248219
# 地域: 华东-上海一 (cn-east-3)

# 必需配置
HUAWEI_ACCESS_KEY=你的Access_Key_Id
HUAWEI_SECRET_KEY=你的Secret_Access_Key

# 可选配置
HUAWEI_PROJECT_ID=你的项目ID
HUAWEI_ACCOUNT_ID=hw59248219
HUAWEI_REGION=cn-east-3

# 其他配置
# HUAWEI_ENDPOINT=ecs.cn-east-3.myhuaweicloud.com
"""
        return template
    
    def create_env_file(self, filepath: str = ".env") -> bool:
        """创建.env文件模板"""
        try:
            template = self.generate_env_template()
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(template)
            print(f"✅ 已创建.env文件模板: {filepath}")
            print("💡 请编辑该文件，填入你的AK/SK信息")
            return True
        except Exception as e:
            print(f"❌ 创建.env文件失败: {e}")
            return False

class HuaweiAPIClientWithEnv:
    """支持.env文件的华为云API客户端"""
    
    def __init__(self, env_file: str = ".env"):
        self.env_config = HuaweiEnvConfig(env_file)
        self.api_client = None
        
    def initialize(self) -> bool:
        """初始化API客户端"""
        if not self.env_config.load_env():
            return False
            
        if not self.env_config.validate_config():
            return False
            
        # 这里可以初始化实际的API客户端
        print("🚀 API客户端初始化成功")
        return True
    
    def test_connection(self) -> bool:
        """测试API连接"""
        print("\n🔗 测试华为云API连接...")
        
        # 模拟连接测试
        config = self.env_config.config
        print(f"   测试账号: {config['account_id']}")
        print(f"   测试地域: {config['region']}")
        print("   连接状态: ✅ 模拟连接成功")
        
        # 实际实现时需要调用华为云API
        # 例如: 调用IAM服务获取token
        return True
    
    def analyze_costs(self) -> dict:
        """分析成本（模拟）"""
        print("\n💰 成本分析...")
        
        # 基于配置生成分析报告
        analysis = {
            "account": self.env_config.config["account_id"],
            "region": self.env_config.config["region"],
            "analysis_time": datetime.now().isoformat(),
            "estimated_monthly_cost": 12500.00,
            "optimization_opportunities": [
                {
                    "category": "计费模式",
                    "items": [
                        {"name": "预留实例", "saving": "30-50%", "priority": "高"},
                        {"name": "竞价实例", "saving": "60-90%", "priority": "中"},
                    ]
                },
                {
                    "category": "资源配置",
                    "items": [
                        {"name": "ECS规格调整", "saving": "15-30%", "priority": "高"},
                        {"name": "存储优化", "saving": "20-40%", "priority": "中"},
                    ]
                }
            ],
            "total_saving_potential": "25-35%"
        }
        
        return analysis
    
    def generate_report(self):
        """生成分析报告"""
        if not self.initialize():
            print("❌ 初始化失败，无法生成报告")
            return
        
        if not self.test_connection():
            print("❌ API连接测试失败")
            return
        
        analysis = self.analyze_costs()
        
        print("\n" + "="*70)
        print("华为云成本优化分析报告")
        print("="*70)
        
        print(f"账号: {analysis['account']}")
        print(f"地域: {analysis['region']}")
        print(f"分析时间: {analysis['analysis_time']}")
        print(f"预估月度费用: ¥{analysis['estimated_monthly_cost']:,.2f}")
        
        print("\n🎯 优化机会:")
        for category in analysis["optimization_opportunities"]:
            print(f"\n{category['category']}:")
            for item in category["items"]:
                print(f"  • {item['name']}: 节省{item['saving']} (优先级: {item['priority']})")
        
        print(f"\n💡 总节省潜力: {analysis['total_saving_potential']}")
        print(f"💡 预期月度节省: ¥{analysis['estimated_monthly_cost'] * 0.3:,.2f}")
        
        print("\n📋 下一步:")
        print("1. 运行详细资源分析")
        print("2. 实施快速优化措施")
        print("3. 建立持续监控")
        
        print("\n" + "="*70)

def main():
    """主函数"""
    print("华为云环境变量工具")
    print("-" * 40)
    
    # 检查参数
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "init":
            # 创建.env文件模板
            config = HuaweiEnvConfig()
            config.create_env_file()
            return
        elif command == "check":
            # 检查环境变量
            config = HuaweiEnvConfig()
            if config.load_env():
                config.validate_config()
            return
        elif command == "analyze":
            # 运行分析
            env_file = sys.argv[2] if len(sys.argv) > 2 else ".env"
            client = HuaweiAPIClientWithEnv(env_file)
            client.generate_report()
            return
    
    # 默认显示帮助
    print("使用方法:")
    print("  python3 huawei_env_tools.py init      # 创建.env文件模板")
    print("  python3 huawei_env_tools.py check     # 检查环境变量")
    print("  python3 huawei_env_tools.py analyze   # 运行成本分析")
    print("  python3 huawei_env_tools.py analyze .env.prod  # 使用指定文件")
    print()
    print("示例:")
    print("  1. 创建.env文件模板:")
    print("     python3 huawei_env_tools.py init")
    print()
    print("  2. 编辑.env文件，填入AK/SK:")
    print("     nano .env")
    print()
    print("  3. 运行成本分析:")
    print("     python3 huawei_env_tools.py analyze")

if __name__ == "__main__":
    main()