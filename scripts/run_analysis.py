#!/usr/bin/env python3
"""
华为云优化分析 - 简化运行脚本
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.huawei_cloud_optimization_project import main

if __name__ == "__main__":
    print("🚀 华为云服务器优化分析")
    print("=" * 50)
    
    # 检查配置文件
    env_file = project_root / "config" / ".env"
    if not env_file.exists():
        print(f"❌ 配置文件不存在: {env_file}")
        print(f"💡 请先复制模板文件:")
        print(f"  cp config/.env.example config/.env")
        print(f"💡 然后编辑config/.env文件，填入你的华为云AK/SK")
        sys.exit(1)
    
    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=env_file)
    
    # 检查必要的环境变量
    required_vars = ["HUAWEI_ACCESS_KEY", "HUAWEI_SECRET_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ 缺少必要的环境变量: {', '.join(missing_vars)}")
        print(f"💡 请检查 {env_file} 文件")
        sys.exit(1)
    
    print("✅ 配置文件检查通过")
    print(f"📁 报告将保存到: {project_root / 'reports'}")
    print()
    
    # 运行主分析
    try:
        main()
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)