#!/usr/bin/env python3
"""
华为云简单分析脚本 - 直接使用华为云SDK获取真实数据
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# 尝试导入华为云SDK
try:
    from huaweicloudsdkcore.auth.credentials import BasicCredentials
    from huaweicloudsdkecs.v2 import EcsClient, ListServersDetailsRequest
    from huaweicloudsdkecs.v2.region.ecs_region import EcsRegion
    from huaweicloudsdkces.v1 import CesClient, ListMetricsRequest, BatchListMetricDataRequest
    from huaweicloudsdkces.v1.region.ces_region import CesRegion
    from huaweicloudsdkbss.v2 import BssClient, ListCustomerselfResourceRecordDetailsRequest
    from huaweicloudsdkbss.v2.region.bss_region import BssRegion
    print("✅ 华为云SDK导入成功")
except ImportError as e:
    print(f"❌ 华为云SDK导入失败: {e}")
    print("请安装华为云SDK: pip3 install huaweicloudsdkcore huaweicloudsdkecs huaweicloudsdkces huaweicloudsdkbss")
    sys.exit(1)

def load_huawei_config():
    """加载华为云配置"""
    # 优先从 /root/.openclaw/.env 加载
    primary_env_path = Path("/root/.openclaw/.env")
    if primary_env_path.exists():
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=primary_env_path, override=True)
        print(f"✅ 从 {primary_env_path} 加载环境变量")
    else:
        print("❌ 未找到配置文件 /root/.openclaw/.env")
        return None
    
    config = {
        "access_key": os.getenv("HUAWEI_ACCESS_KEY"),
        "secret_key": os.getenv("HUAWEI_SECRET_KEY"),
        "project_id": os.getenv("HUAWEI_PROJECT_ID"),
        "account_id": os.getenv("HUAWEI_ACCOUNT_ID", "hw59248219"),
        "region": os.getenv("HUAWEI_REGION", "cn-east-3"),
    }
    
    # 验证配置
    if not config["access_key"] or not config["secret_key"]:
        print("❌ 缺少必要的AK/SK配置")
        return None
    
    if not config["project_id"]:
        print("❌ 缺少项目ID配置")
        return None
    
    print(f"✅ 配置验证通过:")
    print(f"   账号ID: {config['account_id']}")
    print(f"   地域: {config['region']}")
    print(f"   项目ID: {config['project_id']}")
    print(f"   Access Key: {config['access_key'][:8]}...{config['access_key'][-4:]}")
    print(f"   Secret Key: {config['secret_key'][:8]}...{config['secret_key'][-4:]}")
    
    return config

def create_ecs_client(config):
    """创建ECS客户端"""
    try:
        credentials = BasicCredentials(
            ak=config["access_key"],
            sk=config["secret_key"],
            project_id=config["project_id"]
        )
        
        client = EcsClient.new_builder() \
            .with_credentials(credentials) \
            .with_region(EcsRegion.value_of(config["region"])) \
            .build()
        
        print(f"✅ ECS客户端创建成功 (区域: {config['region']})")
        return client
    except Exception as e:
        print(f"❌ ECS客户端创建失败: {e}")
        return None

def get_ecs_instances(client):
    """获取ECS实例列表"""
    try:
        request = ListServersDetailsRequest()
        request.limit = 100  # 每页100个实例
        request.offset = 0
        
        response = client.list_servers_details(request)
        if response.servers:
            print(f"✅ 成功获取到 {len(response.servers)} 个ECS实例")
            return response.servers
        else:
            print("⚠️  API返回空实例列表")
            return []
    except Exception as e:
        print(f"❌ 获取ECS实例失败: {e}")
        return []

def analyze_instance(instance):
    """分析单个实例"""
    instance_info = {
        "id": instance.id,
        "name": instance.name,
        "status": instance.status,
        "created": instance.created,
        "flavor": {
            "id": instance.flavor.id if instance.flavor else "未知",
            "name": instance.flavor.name if instance.flavor else "未知",
        },
        "image": {
            "id": instance.image.id if instance.image else "未知",
        },
        "metadata": instance.metadata if instance.metadata else {},
        "addresses": instance.addresses if instance.addresses else {},
        "security_groups": [sg.name for sg in instance.security_groups] if instance.security_groups else [],
    }
    
    return instance_info

def generate_markdown_report(instances, config):
    """生成Markdown报告"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"huawei_ecs_report_{timestamp}.md"
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"# 华为云ECS实例详细报告\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**账号ID**: {config['account_id']}\n")
        f.write(f"**地域**: {config['region']}\n")
        f.write(f"**项目ID**: {config['project_id']}\n")
        f.write(f"**实例总数**: {len(instances)}\n\n")
        
        f.write("## 实例详情\n\n")
        
        if not instances:
            f.write("⚠️ 未找到ECS实例\n")
            return report_file
        
        # 按状态统计
        status_count = {}
        for instance in instances:
            status = instance.get("status", "未知")
            status_count[status] = status_count.get(status, 0) + 1
        
        f.write("### 实例状态统计\n")
        for status, count in status_count.items():
            f.write(f"- {status}: {count} 台\n")
        f.write("\n")
        
        # 详细实例列表
        f.write("### 详细实例列表\n")
        f.write("| 序号 | 实例名称 | 实例ID | 状态 | 规格 | 创建时间 | 安全组 |\n")
        f.write("|------|----------|--------|------|------|----------|--------|\n")
        
        for i, instance in enumerate(instances, 1):
            name = instance.get("name", "未命名")
            instance_id = instance.get("id", "未知")[:12] + "..."
            status = instance.get("status", "未知")
            flavor = instance.get("flavor", {}).get("name", "未知")
            created = instance.get("created", "未知")
            security_groups = ", ".join(instance.get("security_groups", []))[:30]
            
            f.write(f"| {i} | {name} | {instance_id} | {status} | {flavor} | {created} | {security_groups} |\n")
        
        f.write("\n")
        
        # 规格统计
        f.write("### 实例规格统计\n")
        flavor_count = {}
        for instance in instances:
            flavor = instance.get("flavor", {}).get("name", "未知")
            flavor_count[flavor] = flavor_count.get(flavor, 0) + 1
        
        for flavor, count in sorted(flavor_count.items(), key=lambda x: x[1], reverse=True):
            f.write(f"- {flavor}: {count} 台\n")
        
        f.write("\n")
        
        # 建议
        f.write("## 优化建议\n\n")
        f.write("### 1. 运行状态分析\n")
        active_count = status_count.get("ACTIVE", 0)
        stopped_count = status_count.get("SHUTOFF", 0)
        total_count = len(instances)
        
        if stopped_count > 0:
            f.write(f"- **停止的实例**: {stopped_count} 台 ({stopped_count/total_count*100:.1f}%)\n")
            f.write("  - 建议: 检查是否需要长期停止的实例，考虑删除或调整规格\n")
        
        f.write(f"- **运行的实例**: {active_count} 台 ({active_count/total_count*100:.1f}%)\n")
        f.write("  - 建议: 监控资源使用率，优化规格配置\n")
        
        f.write("\n### 2. 规格优化建议\n")
        f.write("- 对于低负载实例: 考虑降配到更小规格\n")
        f.write("- 对于高负载实例: 监控性能，考虑升配\n")
        f.write("- 统一规格: 标准化实例规格，便于管理和成本控制\n")
        
        f.write("\n### 3. 成本优化建议\n")
        f.write("- 包年包月: 长期运行的实例建议使用包年包月计费\n")
        f.write("- 自动伸缩: 根据负载自动调整实例数量\n")
        f.write("- 资源标签: 使用标签管理资源，便于成本分摊\n")
    
    print(f"✅ Markdown报告已生成: {report_file}")
    return report_file

def main():
    """主函数"""
    print("🚀 开始华为云ECS实例分析...")
    
    # 加载配置
    config = load_huawei_config()
    if not config:
        print("❌ 配置加载失败，请检查环境变量")
        return
    
    # 创建客户端
    ecs_client = create_ecs_client(config)
    if not ecs_client:
        print("❌ 客户端创建失败")
        return
    
    # 获取实例
    print("🔍 获取ECS实例列表...")
    instances_raw = get_ecs_instances(ecs_client)
    
    if not instances_raw:
        print("⚠️ 未获取到ECS实例，可能原因:")
        print("   1. 当前区域没有实例")
        print("   2. API权限不足")
        print("   3. 网络连接问题")
        return
    
    # 分析实例
    print("📊 分析实例信息...")
    instances = []
    for instance_raw in instances_raw:
        instance_info = analyze_instance(instance_raw)
        instances.append(instance_info)
    
    # 生成报告
    print("📝 生成详细报告...")
    report_file = generate_markdown_report(instances, config)
    
    print(f"\n🎉 分析完成!")
    print(f"📄 报告文件: {report_file}")
    print(f"📊 分析实例数: {len(instances)}")
    
    # 显示摘要
    print("\n📋 实例摘要:")
    status_count = {}
    for instance in instances:
        status = instance.get("status", "未知")
        status_count[status] = status_count.get(status, 0) + 1
    
    for status, count in status_count.items():
        print(f"  - {status}: {count} 台")

if __name__ == "__main__":
    main()