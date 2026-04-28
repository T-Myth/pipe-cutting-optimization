import gurobipy as gp
from gurobipy import GRB

def solve_pipe_cutting():
    # 需求
    demand = [15, 28, 21, 30]

    # 二进制位数
    bits_x = 5   # x_i: 0~30 需要 5 位
    bits_p = 3   # a_i,b_i,c_i,d_i: 0~5 需要 3 位

    # 零件长度 (mm)
    lengths = [290, 315, 350, 455]

    # 创建模型
    model = gp.Model("PipeCutting")

    # ========== 1. 定义二进制变量 ==========
    # x_i 的二进制位: X[i][k]   i=0..3, k=0..bits_x-1
    X = {}
    for i in range(4):
        for k in range(bits_x):
            X[i, k] = model.addVar(vtype=GRB.BINARY, name=f"X_{i+1}_{k+1}")

    # a_i, b_i, c_i, d_i 的二进制位
    A = {}; B = {}; C = {}; D = {}
    for i in range(4):
        for l in range(bits_p):
            A[i, l] = model.addVar(vtype=GRB.BINARY, name=f"A_{i+1}_{l+1}")
            B[i, l] = model.addVar(vtype=GRB.BINARY, name=f"B_{i+1}_{l+1}")
            C[i, l] = model.addVar(vtype=GRB.BINARY, name=f"C_{i+1}_{l+1}")
            D[i, l] = model.addVar(vtype=GRB.BINARY, name=f"D_{i+1}_{l+1}")

    # 乘积变量 Pxa = X * A  等
    Pxa = {}; Pxb = {}; Pxc = {}; Pxd = {}
    for i in range(4):
        for k in range(bits_x):
            for l in range(bits_p):
                Pxa[i, k, l] = model.addVar(vtype=GRB.BINARY, name=f"Pxa_{i+1}_{k+1}_{l+1}")
                Pxb[i, k, l] = model.addVar(vtype=GRB.BINARY, name=f"Pxb_{i+1}_{k+1}_{l+1}")
                Pxc[i, k, l] = model.addVar(vtype=GRB.BINARY, name=f"Pxc_{i+1}_{k+1}_{l+1}")
                Pxd[i, k, l] = model.addVar(vtype=GRB.BINARY, name=f"Pxd_{i+1}_{k+1}_{l+1}")

    # 更新模型
    model.update()
    # ========== 2. 目标函数 ==========
    obj = gp.LinExpr()
    for i in range(4):
        x_expr = gp.LinExpr()
        for k in range(bits_x):
            x_expr += (2 ** k) * X[i, k]      # 2^(k) 因为 k 从 0 开始
        obj += (1.0 + 0.1 * (i+1)) * x_expr   # 系数 1.1, 1.2, 1.3, 1.4
    model.setObjective(obj, GRB.MINIMIZE)

    # ========== 3. 约束 ==========
    # 3.1 需求约束
    for p in range(4):   # p=0:290, 1:315, 2:350, 3:455
        demand_expr = gp.LinExpr()
        for i in range(4):
            for k in range(bits_x):
                for l in range(bits_p):
                    coeff = (2 ** k) * (2 ** l)
                    if p == 0:
                        demand_expr += coeff * Pxa[i, k, l]
                    elif p == 1:
                        demand_expr += coeff * Pxb[i, k, l]
                    elif p == 2:
                        demand_expr += coeff * Pxc[i, k, l]
                    else:  # p == 3
                        demand_expr += coeff * Pxd[i, k, l]
        model.addConstr(demand_expr >= demand[p], name=f"demand_{p+1}")

    # 3.2 模式可行性约束（每根钢管）
    for i in range(4):
        # 根数约束: a_i + b_i + c_i + d_i <= 5
        total_pcs = gp.LinExpr()
        for l in range(bits_p):
            total_pcs += (2 ** l) * (A[i, l] + B[i, l] + C[i, l] + D[i, l])
        model.addConstr(total_pcs <= 5, name=f"max_pcs_{i+1}")

        # 长度约束: 290a_i + 315b_i + 350c_i + 455d_i 在 [1750, 1850]
        len_expr = gp.LinExpr()
        for l in range(bits_p):
            len_expr += (2 ** l) * (lengths[0]*A[i, l] + lengths[1]*B[i, l] +
                                    lengths[2]*C[i, l] + lengths[3]*D[i, l])
        model.addConstr(len_expr >= 1750, name=f"len_lb_{i+1}")
        model.addConstr(len_expr <= 1850, name=f"len_ub_{i+1}")

    # 3.3 排序约束: x1 >= x2 >= x3 >= x4
    x_expr = []
    for i in range(4):
        expr = gp.LinExpr()
        for k in range(bits_x):
            expr += (2 ** k) * X[i, k]
        x_expr.append(expr)
    model.addConstr(x_expr[0] >= x_expr[1], name="x1_ge_x2")
    model.addConstr(x_expr[1] >= x_expr[2], name="x2_ge_x3")
    model.addConstr(x_expr[2] >= x_expr[3], name="x3_ge_x4")

    # 3.4 乘积线性化约束: P = X * A 等
    for i in range(4):
        for k in range(bits_x):
            for l in range(bits_p):
                # Pxa
                model.addConstr(Pxa[i, k, l] <= X[i, k], name=f"Pxa_le_X_{i+1}_{k+1}_{l+1}")
                model.addConstr(Pxa[i, k, l] <= A[i, l], name=f"Pxa_le_A_{i+1}_{k+1}_{l+1}")
                model.addConstr(Pxa[i, k, l] >= X[i, k] + A[i, l] - 1, name=f"Pxa_ge_{i+1}_{k+1}_{l+1}")
                # Pxb
                model.addConstr(Pxb[i, k, l] <= X[i, k], name=f"Pxb_le_X_{i+1}_{k+1}_{l+1}")
                model.addConstr(Pxb[i, k, l] <= B[i, l], name=f"Pxb_le_B_{i+1}_{k+1}_{l+1}")
                model.addConstr(Pxb[i, k, l] >= X[i, k] + B[i, l] - 1, name=f"Pxb_ge_{i+1}_{k+1}_{l+1}")
                # Pxc
                model.addConstr(Pxc[i, k, l] <= X[i, k], name=f"Pxc_le_X_{i+1}_{k+1}_{l+1}")
                model.addConstr(Pxc[i, k, l] <= C[i, l], name=f"Pxc_le_C_{i+1}_{k+1}_{l+1}")
                model.addConstr(Pxc[i, k, l] >= X[i, k] + C[i, l] - 1, name=f"Pxc_ge_{i+1}_{k+1}_{l+1}")
                # Pxd
                model.addConstr(Pxd[i, k, l] <= X[i, k], name=f"Pxd_le_X_{i+1}_{k+1}_{l+1}")
                model.addConstr(Pxd[i, k, l] <= D[i, l], name=f"Pxd_le_D_{i+1}_{k+1}_{l+1}")
                model.addConstr(Pxd[i, k, l] >= X[i, k] + D[i, l] - 1, name=f"Pxd_ge_{i+1}_{k+1}_{l+1}")

    # ========== 4. 求解 ==========
    model.setParam('TimeLimit', 300)   # 最大求解时间 300 秒
    model.optimize()

    # ========== 5. 输出结果 ==========
    if model.Status == GRB.OPTIMAL or model.Status == GRB.TIME_LIMIT:
        print("\n========== 最优解 ==========")
        print(f"目标值: {model.ObjVal:.4f}")

        for i in range(4):
            # 计算 x_i
            x_val = 0
            for k in range(bits_x):
                x_val += (2 ** k) * X[i, k].X
            # 计算 a_i, b_i, c_i, d_i
            a_val = b_val = c_val = d_val = 0
            for l in range(bits_p):
                a_val += (2 ** l) * A[i, l].X
                b_val += (2 ** l) * B[i, l].X
                c_val += (2 ** l) * C[i, l].X
                d_val += (2 ** l) * D[i, l].X
            print(f"模式{i+1}: [{int(a_val)},{int(b_val)},{int(c_val)},{int(d_val)}] 使用 {int(x_val)} 次")
    else:
        print("求解失败，状态码:", model.Status)

if __name__ == "__main__":
    solve_pipe_cutting()
