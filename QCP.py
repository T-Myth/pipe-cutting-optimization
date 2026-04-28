import gurobipy as gp
from gurobipy import GRB

model = gp.Model("PipeCutting")

# 整数变量
x = [model.addVar(lb=0, ub=30, vtype=GRB.INTEGER, name=f"x_{i+1}") for i in range(4)]

# 每个模式的零件数量
a = [model.addVar(lb=0, ub=5, vtype=GRB.INTEGER, name=f"a_{i+1}") for i in range(4)]
b = [model.addVar(lb=0, ub=5, vtype=GRB.INTEGER, name=f"b_{i+1}") for i in range(4)]
c = [model.addVar(lb=0, ub=5, vtype=GRB.INTEGER, name=f"c_{i+1}") for i in range(4)]
d = [model.addVar(lb=0, ub=5, vtype=GRB.INTEGER, name=f"d_{i+1}") for i in range(4)]

# 目标
obj = 1.1*x[0] + 1.2*x[1] + 1.3*x[2] + 1.4*x[3]
model.setObjective(obj, GRB.MINIMIZE)

# 需求约束：使用二次表达式
demand = [15, 28, 21, 30]
model.addConstr(gp.quicksum(x[i]*a[i] for i in range(4)) >= demand[0])
model.addConstr(gp.quicksum(x[i]*b[i] for i in range(4)) >= demand[1])
model.addConstr(gp.quicksum(x[i]*c[i] for i in range(4)) >= demand[2])
model.addConstr(gp.quicksum(x[i]*d[i] for i in range(4)) >= demand[3])

# 模式可行性
for i in range(4):
    model.addConstr(a[i] + b[i] + c[i] + d[i] <= 5)
    # 长度约束
    length = 290*a[i] + 315*b[i] + 350*c[i] + 455*d[i]
    model.addConstr(length <= 1850)
    model.addConstr(length >= 1750)

# 排序
model.addConstr(x[0] >= x[1])
model.addConstr(x[1] >= x[2])
model.addConstr(x[2] >= x[3])

# 求解
model.optimize()

# 输出
if model.Status == GRB.OPTIMAL:
    print(f"目标值: {model.ObjVal}")
    for i in range(4):
        print(f"模式{i+1}: [{int(a[i].X)},{int(b[i].X)},{int(c[i].X)},{int(d[i].X)}] 使用 {int(x[i].X)} 次")
else:
    print("未找到最优解")