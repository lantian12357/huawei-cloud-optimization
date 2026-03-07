#!/usr/bin/env python3
"""
华为云简单真实分析脚本
不使用pandas，直接生成CSV和Markdown报告
"""

import os
import sys
import csv
import json
from datetime import datetime, timezone
from typing import List, Dict
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from huawei_simple_api_client import HuaweiSimpleAPIClient


class SimpleHuaweiAnalyzer:
    """简单华为云分析器"""
    
    def __init__(self, env_file: str = "config/.env"):
        """初始化分析器"""
        print("🚀 初始化华为云简单分析器...")
        
        try:
            # 初始化API客户端
            self.api_client = HuaweiSimpleAPIClient(env_file)
            
            # 测试API连接
            if not self.api_client.test_connection():
                print("⚠️ API连接测试失败，将使用模拟数据")
            
            self.analysis_date = datetime.now().strftime("%Y-%m-%d")
            
            # 商务折扣配置
            self.discount_rates = {
                "包年包月": 0.15,  # 15%折扣
                "按需计费": 0.10,  # 10%折扣
            }
            
            # 规格价格表
            self.flavor_prices = {
                "c6.large.2": {"monthly": 400.00, "hourly": 0.56},
                "c6.xlarge.2": {"monthly": 800.00, "hourly": 1.12},
                "c6.2xlarge.2": {"monthly": 1600.00, "hourly": 2.24},
                "c6.4xlarge.2": {"monthly": 3200.00, "hourly": 4.48},
                "r6.large.2": {"monthly": 450.00, "hourly": 0.63},
                "r6.xlarge.2": {"monthly": 900.00, "hourly": 1.26},
                "r6.2xlarge.2": {"monthly": 1800.00, "hourly": 2.52},
            }
            
            print("✅ 华为云简单分析器初始化完成")
            
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            raise
    
    def get_real_ecs_instances(self, limit: int = 100) -> List[Dict]:
        """获取真实的ECS实例数据"""
        return self.api_client.get_real_ecs_instances(limit)
    
    def get_monitoring_data(self, instance_id: str, days: int = 30) -> Dict:
        """获取监控数据"""
        return self.api_client.get_monitoring_data(instance_id, days)
    
    def calculate_current_cost(self, instance: Dict) -> float:
        """计算当前成本（考虑商务折扣）"""
        flavor = instance["flavor"]
        billing_mode = instance["billing_mode"]
        
        # 查找规格价格
        if flavor not in self.flavor_prices:
            print(f"⚠️ 未知规格: {flavor}，使用默认价格")
            # 根据规格名称估算价格
            base_price = self._estimate_price_from_flavor(flavor)
            hourly_price = self._estimate_hourly_price(base_price)
        else:
            base_price = self.flavor_prices[flavor]["monthly"]
            hourly_price = self.flavor_prices[flavor]["hourly"]
        
        # 应用商务折扣
        discount_rate = self.discount_rates.get(billing_mode, 0.0)
        
        if billing_mode == "包年包月":
            discounted_price = base_price * (1 - discount_rate)
        else:  # 按需计费
            # 假设实例运行了完整月份
            hours_in_month = 24 * 30  # 30天
            base_price = hourly_price * hours_in_month
            discounted_price = base_price * (1 - discount_rate)
        
        return round(discounted_price, 2)
    
    def _estimate_price_from_flavor(self, flavor: str) -> float:
        """根据规格名称估算价格"""
        flavor_lower = flavor.lower()
        
        if "large" in flavor_lower and "xlarge" not in flavor_lower and "2xlarge" not in flavor_lower:
            return 400.00
        elif "xlarge" in flavor_lower and "2xlarge" not in flavor_lower:
            return 800.00
        elif "2xlarge" in flavor_lower and "4xlarge" not in flavor_lower:
            return 1600.00
        elif "4xlarge" in flavor_lower:
            return 3200.00
        elif "8xlarge" in flavor_lower:
            return 6400.00
        else:
            return 500.00  # 默认
    
    def _estimate_hourly_price(self, monthly_price: float) -> float:
        """根据月价估算小时价格"""
        # 假设每月720小时（30天×24小时）
        return round(monthly_price / 720, 2)
    
    def calculate_running_days(self, created_str: str) -> int:
        """计算运行天数"""
        try:
            # 处理时间格式
            if 'Z' in created_str:
                created_str = created_str.replace('Z', '+00:00')
            
            created = datetime.fromisoformat(created_str)
            now = datetime.now(timezone.utc)
            
            # 确保created有时区信息
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            
            running_days = (now - created).days
            return max(running_days, 1)
            
        except Exception as e:
            print(f"⚠️ 计算运行天数失败: {e}，使用默认值")
            return 365  # 默认一年
    
    def suggest_optimized_flavor(self, instance: Dict, monitoring: Dict) -> Dict:
        """建议优化规格（基于真实使用率）"""
        flavor = instance["flavor"]
        cpu_peak = monitoring["cpu_peak"]
        mem_peak = monitoring["mem_peak"]
        
        # 根据使用率建议优化
        if cpu_peak < 30 and mem_peak < 40:
            # 使用率低，考虑降配
            if "2xlarge" in flavor:
                suggested = flavor.replace("2xlarge", "xlarge")
                optimization = "降配"
                reason = f"CPU峰值{cpu_peak}% < 30%，内存峰值{mem_peak}% < 40%，可降配"
            elif "xlarge" in flavor:
                suggested = flavor.replace("xlarge", "large")
                optimization = "降配"
                reason = f"CPU峰值{cpu_peak}% < 30%，内存峰值{mem_peak}% < 40%，可降配"
            elif "large" in flavor:
                suggested = flavor  # 已是最小规格
                optimization = "保持"
                reason = f"CPU峰值{cpu_peak}%，内存峰值{mem_peak}%，已是最小规格"
            else:
                suggested = flavor
                optimization = "保持"
                reason = f"CPU峰值{cpu_peak}%，内存峰值{mem_peak}%，规格未知"
                
        elif cpu_peak > 80 or mem_peak > 85:
            # 使用率高，考虑升配
            if "large" in flavor:
                suggested = flavor.replace("large", "xlarge")
                optimization = "升配"
                reason = f"CPU峰值{cpu_peak}% > 80% 或 内存峰值{mem_peak}% > 85%，需升配"
            elif "xlarge" in flavor:
                suggested = flavor.replace("xlarge", "2xlarge")
                optimization = "升配"
                reason = f"CPU峰值{cpu_peak}% > 80% 或 内存峰值{mem_peak}% > 85%，需升配"
            else:
                suggested = flavor
                optimization = "保持"
                reason = f"CPU峰值{cpu_peak}%，内存峰值{mem_peak}%，规格未知"
                
        else:
            # 使用率适中，保持当前规格
            suggested = flavor
            optimization = "保持"
            reason = f"CPU峰值{cpu_peak}%，内存峰值{mem_peak}%，使用率适中"
        
        return {
            "suggested_flavor": suggested,
            "optimization_type": optimization,
            "reason": reason
        }
    
    def calculate_potential_saving(self, instance: Dict, current_cost: float, 
                                  suggested_flavor: str) -> float:
        """计算潜在节省（考虑商务折扣）"""
        if suggested_flavor == instance["flavor"]:
            return 0.0
        
        # 计算优化后成本
        if suggested_flavor not in self.flavor_prices:
            print(f"⚠️ 未知优化规格: {suggested_flavor}，无法计算节省")
            return 0.0
        
        billing_mode = instance["billing_mode"]
        discount_rate = self.discount_rates.get(billing_mode, 0.0)
        
        if billing_mode == "包年包月":
            base_new_price = self.flavor_prices[suggested_flavor]["monthly"]
            new_cost = base_new_price * (1 - discount_rate)
        else:  # 按需计费
            hours_in_month = 24 * 30
            hourly_price = self.flavor_prices[suggested_flavor]["hourly"]
            base_new_price = hourly_price * hours_in_month
            new_cost = base_new_price * (1 - discount_rate)
        
        saving = current_cost - new_cost
        return round(max(saving, 0.0), 2)
    
    def analyze_instances(self, limit: int = 100) -> List[Dict]:
        """分析实例"""
        print("📊 分析ECS实例...")
        
        # 获取真实实例数据
        instances = self.get_real_ecs_instances(limit)
        
        if not instances:
            print("❌ 未获取到ECS实例数据")
            return []
        
        analyzed_instances = []
        
        for instance in instances:
            print(f"📋 分析实例: {instance['name']} ({instance['id']})")
            
            # 获取监控数据
            monitoring = self.get_monitoring_data(instance["id"])
            
            # 计算当前成本（考虑折扣）
            current_cost = self.calculate_current_cost(instance)
            
            # 计算运行天数
            running_days = self.calculate_running_days(instance["created"])
            
            # 建议优化规格
            optimization = self.suggest_optimized_flavor(instance, monitoring)
            
            # 计算潜在节省
            potential_saving = self.calculate_potential_saving(
                instance, current_cost, optimization["suggested_flavor"]
            )
            
            # 计算折扣前成本（用于参考）
            discount_rate = self.discount_rates.get(instance["billing_mode"], 0.0)
            base_cost = round(current_cost / (1 - discount_rate), 2) if discount_rate < 1 else current_cost
            
            # 计算节省比例
            saving_ratio = (potential_saving / current_cost * 100) if current_cost > 0 else 0
            
            # 构建分析结果
            analyzed_instance = {
                "实例名称": instance["name"],
                "实例ID": instance["id"],
                "规格": instance["flavor"],
                "CPU核心数": instance["cpu_cores"],
                "内存(GB)": instance["memory_gb"],
                "最近30天CPU峰值(%)": monitoring["cpu_peak"],
                "最近30天内存峰值(%)": monitoring["mem_peak"],
                "最近30天磁盘峰值(%)": monitoring["disk_peak"],
                "付费方式": instance["billing_mode"],
                "折扣前成本(元/月)": base_cost,
                "商务折扣率": f"{discount_rate*100:.1f}%",
                "当前成本(元/月)": current_cost,
                "创建时间": instance["created"][:10] if len(instance["created"]) >= 10 else instance["created"],
                "运行时长(天)": running_days,
                "建议优化规格": optimization["suggested_flavor"],
                "优化类型": optimization["optimization_type"],
                "优化原因": optimization["reason"],
                "可节省成本(元/月)": potential_saving,
                "节省比例": f"{saving_ratio:.1f}%" if potential_saving > 0 else "0%",
                "状态": instance["status"],
                "数据来源": monitoring.get("source", "API"),
                "分析日期": self.analysis_date,
            }
            
            analyzed_instances.append(analyzed_instance)
        
        # 计算总计
        if analyzed_instances:
            total_current_cost = sum(inst["当前成本(元/月)"] for inst in analyzed_instances)
            total_potential_saving = sum(inst["可节省成本(元/月)"] for inst in analyzed_instances)
            total_saving_ratio = (total_potential_saving / total_current_cost * 100) if total_current_cost > 0 else 0
            
            print(f"\n💰 成本统计:")
            print(f"   实例总数: {len(analyzed_instances)} 个")
            print(f"   当前总成本: ¥{total_current_cost:.2f}/月")
            print(f"   潜在总节省: ¥{total_potential_saving:.2f}/月")
            print(f"   节省比例: {total_saving_ratio:.1f}%")
            
            # 统计优化类型
            optimization_counts = {}
            for inst in analyzed_instances:
                opt_type = inst["优化类型"]
                optimization_counts[opt_type] = optimization_counts.get(opt_type, 0) + 1
            
            print(f"\n🔧 优化建议统计:")
            for opt_type, count in optimization_counts.items():
                print(f"   {opt_type}: {count} 个实例")
        
        return analyzed_instances
    
    def save_to_csv(self, instances: List[Dict], output_dir: str = "reports"):
        """保存为CSV文件"""
        if not instances:
            print("❌ 没有数据可保存")
            return
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = os.path.join(output_dir, f"huawei_simple_analysis_{timestamp}.csv")
        
        # 获取所有字段
        fieldnames = list(instances[0].keys())
        
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(instances)
        
        print(f"✅ CSV文件已保存: {csv_file}")
        return csv_file
    
    def save_to_markdown(self, instances: List[Dict], output_dir: str = "reports"):
        """保存为Markdown文件"""
        if not instances:
            print("❌ 没有数据可保存")
            return
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        md_file = os.path.join(output_dir, f"huawei_simple_analysis_{timestamp}.md")
        
        # 计算总计
        total_current_cost = sum(inst["当前成本(元/月)"] for inst in instances)
        total_potential_saving = sum(inst["可节省成本(元/月)"] for inst in instances)
        total_saving_ratio = (total_potential_saving / total_current_cost * 100) if total_current_cost > 0 else 0
        
        # 统计优化类型
        optimization_counts = {}
        for inst in instances:
            opt_type = inst["优化类型"]
            optimization_counts[opt_type] = optimization_counts.get(opt_type, 0) + 1
        
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"# 华为云服务器简单优化分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**数据来源**: 华为云API\n")
            f.write(f"**分析账号**: {self.api_client.account_id}\n")
            f.write(f"**分析区域**: {self.api_client.region}\n\n")
            
            f.write("## 📊 汇总统计\n\n")
            f.write(f"- **实例总数**: {len(instances)} 个\n")
            f.write(f"- **当前总成本**: ¥{total_current_cost:.2f}/月\n")
            f.write(f"- **潜在总节省**: ¥{total_potential_saving:.2f}/月\n")
            f.write(f"- **节省比例**: {total_saving_ratio:.1f}%\n\n")
            
            f.write("## 🔧 优化建议统计\n\n")
            for opt_type, count in optimization_counts.items():
                f.write(f"- **{opt_type}**: {count} 个实例\n")
            
            f.write("\n## 📋 详细数据\n\n")
            
            # 创建表格
            headers = list(instances[0].keys())
            f.write("| " + " | ".join(headers) + " |\n")
            f.write("|" + "---|" * len(headers) + "\n")
            
            for inst in instances:
                row_values = []
                for header in headers:
                    value = inst[header]
                    if isinstance(value, float):
                        row_values.append(f"{value:.2f}")
                    else:
                        row_values.append(str(value))
                f.write("| " + " | ".join(row_values) + " |\n")
        
        print(f"✅ Markdown文件已保存: {md_file}")
        return md_file
    
    def save_to_json(self, instances: List[Dict], output_dir: str = "reports"):
        """保存为JSON文件"""
        if not instances:
            print("❌ 没有数据可保存")
            return
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = os.path.join(output_dir, f"huawei_simple_analysis_{timestamp}.json")
        
        # 计算总计
        total_current_cost = sum(inst["当前成本(元/月)"] for inst in instances)
        total_potential_saving = sum(inst["可节省成本(元/月)"] for inst in instances)
        
        data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "account_id": self.api_client.account_id,
                "region": self.api_client.region,
                "instance_count": len(instances),
                "total_cost": total_current_cost,
                "total_saving": total_potential_saving,
                "saving_ratio": (total_potential_saving / total_current_cost * 100) if total_current_cost > 0 else 0
            },
            "instances": instances
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON文件已保存: {json_file}")
        return json_file


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 华为云简单真实数据优化分析系统")
    print("=" * 60)
    
    try:
        # 初始化分析器
        analyzer = SimpleHuaweiAnalyzer()
        
        # 分析实例
        instances = analyzer.analyze_instances(limit=50)
        
        if not instances:
            print("❌ 未分析到任何实例，退出")
            return
        
        # 保存到文件
        csv_file = analyzer.save_to_csv(instances)
        md_file = analyzer.save_to_markdown(instances)
        json_file = analyzer.save_to_json(instances)
        
        print("\n" + "=" * 60)
        print("✅ 华为云简单真实数据优化分析完成！")
        print("=" * 60)
        
        # 显示关键统计
        total_current_cost = sum(inst["当前成本(元/月)"] for inst in instances)
        total_potential_saving = sum(inst["可节省成本(元/月)"] for inst in instances)
        
        print(f"\n📊 关键统计:")
        print(f"   实例总数: {len(instances)} 个")
        print(f"   当前总成本: ¥{total_current_cost:.2f}/月")
        print(f"   潜在总节省: ¥{total_potential_saving:.2f}/月")
        
        # 显示前5个实例
        print("\n📋 前5个实例详情:")
        for i, inst in enumerate(instances[:5], 1):
            print(f"  {i}. {inst['实例名称']} ({inst['规格']})")
            print(f"     成本: ¥{inst['当前成本(元/月)']}/月, 节省: ¥{inst['可节省成本(元/月)']}/月")
            print(f"     优化: {inst['优化类型']} → {inst['建议优化规格']}")
        
        print(f"\n📁 报告文件:")
        print(f"   CSV: {csv_file}")
        print(f"   Markdown: {md_file}")
        print(f"   JSON: {json_file}")
        
    except Exception as e:
        print(f"\n❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()