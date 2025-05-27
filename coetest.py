import numpy as np
import json
from scipy.interpolate import lagrange

# 生成样本数据
x = np.array([0, 1, 2, 3])
y = np.array([1, 3, 2, 5])

# 生成拉格朗日插值多项式
poly = lagrange(x, y)

# 提取多项式的系数
coefficients = poly.coefficients.tolist()  # 转换为列表格式

# 保存系数到JSON文件
j = json.dumps(coefficients)


# 还原多项式
restored_poly = np.poly1d(json.loads(j))

# 验证还原的多项式
print("还原的多项式:", restored_poly)
