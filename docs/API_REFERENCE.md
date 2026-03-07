# API参考文档

## 华为云API端点

### 基础服务
- **IAM (身份认证)**: `https://iam.myhuaweicloud.com`
- **ECS (弹性云服务器)**: `https://ecs.{region}.myhuaweicloud.com`
- **EVS (云硬盘)**: `https://evs.{region}.myhuaweicloud.com`
- **VPC (虚拟私有云)**: `https://vpc.{region}.myhuaweicloud.com`
- **EIP (弹性公网IP)**: `https://vpc.{region}.myhuaweicloud.com`

### 监控服务
- **CES (云监控)**: `https://ces.{region}.myhuaweicloud.com`

### 计费服务
- **BSS (费用中心)**: `https://bss.myhuaweicloud.com`

## 主要API接口

### 1. IAM认证
```python
# 获取Token
POST /v3/auth/tokens
Content-Type: application/json

{
  "auth": {
    "identity": {
      "methods": ["password"],
      "password": {
        "user": {
          "name": "access_key",
          "password": "secret_key",
          "domain": {
            "name": "access_key"
          }
        }
      }
    },
    "scope": {
      "project": {
        "name": "region_name"
      }
    }
  }
}
```

### 2. ECS实例管理
```python
# 查询ECS实例列表
GET /v1/{project_id}/cloudservers/detail

# 查询ECS规格详情
GET /v1/{project_id}/cloudservers/flavors

# 查询ECS监控数据
GET /v1/{project_id}/metric-data
```

### 3. 监控数据查询
```python
# 查询指标数据
POST /V1.0/{project_id}/metric-data
Content-Type: application/json

{
  "namespace": "SYS.ECS",
  "metric_name": "cpu_util",
  "from": "2026-02-01T00:00:00Z",
  "to": "2026-03-01T00:00:00Z",
  "period": "300",
  "filter": "average",
  "dimensions": [
    {
      "name": "instance_id",
      "value": "i-xxxxxxxx"
    }
  ]
}
```

### 4. 账单查询
```python
# 查询资源消费记录
POST /v2/bills/customer-bills/monthly-sum
Content-Type: application/json

{
  "bill_cycle": "2026-02",
  "service_type_code": "hws.service.type.ec2",
  "resource_type_code": "hws.resource.type.vm"
}
```

## 项目中的API封装

### HuaweiCloudAPI类
```python
class HuaweiCloudAPI:
    """华为云API客户端"""
    
    def __init__(self, access_key, secret_key, project_id=None):
        self.access_key = access_key
        self.secret_key = secret_key
        self.project_id = project_id
        self.region = "cn-east-3"
        self.token = None
        
    def _get_auth_token(self) -> str:
        """获取IAM认证token"""
        # 实现细节...
        
    def get_ecs_instances(self) -> List[Dict]:
        """获取ECS实例列表"""
        # 实现细节...
        
    def get_monitoring_data(self, instance_id, metric_name, days=30) -> Dict:
        """获取监控数据"""
        # 实现细节...
        
    def get_billing_data(self, resource_id, resource_type="ecs") -> Dict:
        """获取账单数据"""
        # 实现细节...
```

### 数据格式

#### ECS实例数据格式
```json
{
  "id": "i-001",
  "name": "web-server-01",
  "spec": "c6.2xlarge.2",
  "cpu": 8,
  "memory": 16,
  "status": "ACTIVE",
  "billing_mode": "prePaid",
  "created_at": "2025-01-15T10:30:00Z",
  "flavor_id": "c6.2xlarge.2",
  "image_id": "img-001",
  "vpc_id": "vpc-001",
  "subnet_id": "subnet-001",
  "security_groups": ["sg-001"],
  "volume_ids": ["vol-001"],
  "eip_id": "eip-001"
}
```

#### 监控数据格式
```json
{
  "cpu_util": {
    "max": 35.2,
    "avg": 18.7,
    "min": 5.1
  },
  "mem_util": {
    "max": 62.8,
    "avg": 45.3,
    "min": 32.1
  }
}
```

#### 账单数据格式
```json
{
  "monthly_cost": 1250.00,
  "discount_rate": 0.85,
  "actual_cost": 1062.50,
  "billing_mode": "prePaid",
  "resource_type": "ecs"
}
```

## 错误处理

### 常见错误码
- **400**: 请求参数错误
- **401**: 认证失败
- **403**: 权限不足
- **404**: 资源不存在
- **429**: 请求频率限制
- **500**: 服务器内部错误

### 重试机制
```python
def api_call_with_retry(func, max_retries=3, delay=1):
    """带重试的API调用"""
    for attempt in range(max_retries):
        try:
            return func()
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(delay * (2 ** attempt))  # 指数退避
```

## 性能优化

### 批量请求
```python
# 批量获取监控数据
def get_batch_monitoring_data(instance_ids, metric_names):
    """批量获取监控数据，减少API调用次数"""
    # 实现细节...
```

### 缓存机制
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_flavor_info(flavor_id):
    """缓存规格信息，避免重复查询"""
    # 实现细节...
```

## 安全注意事项

### 敏感信息保护
1. **API密钥**: 存储在环境变量或配置文件中，不提交到代码仓库
2. **Token管理**: Token有效期内复用，避免频繁获取
3. **请求签名**: 使用华为云SDK的签名机制

### 访问控制
1. **最小权限原则**: 使用具有只读权限的IAM用户
2. **网络隔离**: 在VPC内访问内部端点
3. **审计日志**: 记录所有API调用

## 扩展接口

### 自定义指标
```python
def get_custom_metrics(instance_id, custom_queries):
    """获取自定义监控指标"""
    # 实现细节...
```

### 实时告警
```python
def setup_real_time_alerts(instance_id, thresholds):
    """设置实时告警"""
    # 实现细节...
```

### 成本预测
```python
def predict_future_costs(historical_data, growth_rate):
    """预测未来成本"""
    # 实现细节...
```

## 调试工具

### API调试脚本
```python
# scripts/debug_api.py
import requests
import json

def debug_api_call(url, headers, data=None):
    """调试API调用"""
    print(f"URL: {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    if data:
        print(f"Data: {json.dumps(data, indent=2)}")
    
    response = requests.post(url, headers=headers, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    return response
```

### 性能监控
```python
import time
from functools import wraps

def time_api_call(func):
    """计时装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f} seconds")
        return result
    return wrapper
```

---

**最后更新**: 2026-03-07  
**版本**: v1.0.0