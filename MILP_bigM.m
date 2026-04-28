clear; clc;

% ----- 1. 生成所有可能的切割模式 -----
A_mode = [1, 1, 1, 1; 290, 315, 350, 455; -290, -315, -350, -455];
b_mode = [5; 1850; -1750];
results_matrix = [];
for x1 = 0:5, for x2 = 0:5, for x3 = 0:5, for x4 = 0:5
    x = [x1; x2; x3; x4];
    if all(A_mode * x <= b_mode)
        results_matrix = [results_matrix; x'];
    end
end; end; end; end
n = size(results_matrix, 1);  % 应为 11

% ----- 2. 决策变量定义 -----
% 顺序：I(1:n), N(1:n), z1(1:n), z2(1:n), z3(1:n), t1, t2, t3, t4
nVars = 5*n + 4;          % 59
I_idx  = 1:n;
N_idx  = n+1:2*n;
z1_idx = 2*n+1:3*n;
z2_idx = 3*n+1:4*n;
z3_idx = 4*n+1:5*n;
t_idx  = 5*n+1 : 5*n+4;   % t1..t4

lb = zeros(1, nVars);
ub = ones(1, nVars);
ub(N_idx) = 30;
ub(t_idx) = 30;
IntCon = [1:5*n, t_idx];   % 所有变量取整数

% ----- 3. 构建不等式约束 A*x <= b -----
A = [];
b_vec = [];
M = 100;   % 大 M，远大于 30 即可

% --- 原始约束 ---
% sum(I) <= 4
row = zeros(1,nVars); row(I_idx) = 1; A = [A; row]; b_vec = [b_vec; 4];
% I_i - N_i <= 0  (选用则次数≥1)
for i = 1:n
    row = zeros(1,nVars); row(I_idx(i)) = 1; row(N_idx(i)) = -1; A = [A; row]; b_vec = [b_vec; 0];
end
% -30 I_i + N_i <= 0  (不选则为0)
for i = 1:n
    row = zeros(1,nVars); row(I_idx(i)) = -30; row(N_idx(i)) = 1; A = [A; row]; b_vec = [b_vec; 0];
end
% 产品需求约束
demand = [15; 28; 21; 30];
for p = 1:4
    row = zeros(1,nVars);
    for i = 1:n
        row(N_idx(i)) = -results_matrix(i, p);
    end
    A = [A; row]; b_vec = [b_vec; -demand(p)];
end

% --- z 的逻辑约束 ---
% sum(z1)=1, sum(z2)=2, sum(z3)=3
row = zeros(1,nVars); row(z1_idx)=1; A=[A; row]; b_vec=[b_vec; 1];
A=[A; -row]; b_vec=[b_vec; -1];
row = zeros(1,nVars); row(z2_idx)=1; A=[A; row]; b_vec=[b_vec; 2];
A=[A; -row]; b_vec=[b_vec; -2];
row = zeros(1,nVars); row(z3_idx)=1; A=[A; row]; b_vec=[b_vec; 3];
A=[A; -row]; b_vec=[b_vec; -3];

% z1 <= z2 <= z3
for i = 1:n
    row = zeros(1,nVars); row(z1_idx(i)) = 1; row(z2_idx(i)) = -1; A=[A; row]; b_vec=[b_vec; 0];
    row = zeros(1,nVars); row(z2_idx(i)) = 1; row(z3_idx(i)) = -1; A=[A; row]; b_vec=[b_vec; 0];
end

% --- 用 t 表示前四大 (正确方向：t >= 对应表达式) ---
% t1 >= N_i  →  N_i - t1 <= 0
for i = 1:n
    row = zeros(1,nVars); row(N_idx(i)) = 1; row(t_idx(1)) = -1; A=[A; row]; b_vec=[b_vec; 0];
end

% t2 >= N_i - M*z1_i  →  N_i - M*z1_i - t2 <= 0
for i = 1:n
    row = zeros(1,nVars); row(N_idx(i)) = 1; row(z1_idx(i)) = -M; row(t_idx(2)) = -1; A=[A; row]; b_vec=[b_vec; 0];
end

% t3 >= N_i - M*z2_i  →  N_i - M*z2_i - t3 <= 0
for i = 1:n
    row = zeros(1,nVars); row(N_idx(i)) = 1; row(z2_idx(i)) = -M; row(t_idx(3)) = -1; A=[A; row]; b_vec=[b_vec; 0];
end

% t4 >= N_i - M*z3_i  →  N_i - M*z3_i - t4 <= 0
for i = 1:n
    row = zeros(1,nVars); row(N_idx(i)) = 1; row(z3_idx(i)) = -M; row(t_idx(4)) = -1; A=[A; row]; b_vec=[b_vec; 0];
end

% 保证 t 非增 (可选，极小化时一般自动满足)
row = zeros(1,nVars); row(t_idx(1)) = -1; row(t_idx(2)) = 1; A=[A; row]; b_vec=[b_vec; 0];
row = zeros(1,nVars); row(t_idx(2)) = -1; row(t_idx(3)) = 1; A=[A; row]; b_vec=[b_vec; 0];
row = zeros(1,nVars); row(t_idx(3)) = -1; row(t_idx(4)) = 1; A=[A; row]; b_vec=[b_vec; 0];

% ----- 4. 目标函数 -----
f = zeros(1, nVars);
f(t_idx) = [1.1, 1.2, 1.3, 1.4];

% ----- 5. 求解 -----
options = optimoptions('intlinprog', 'Display', 'final');
[x_opt, fval, exitflag] = intlinprog(f, IntCon, A, b_vec, [], [], lb, ub, options);

% ----- 6. 输出结果 -----
if exitflag == 1
    I = round(x_opt(I_idx));
    N = round(x_opt(N_idx));
    z1 = round(x_opt(z1_idx));
    z2 = round(x_opt(z2_idx));
    z3 = round(x_opt(z3_idx));
    t = x_opt(t_idx);

    fprintf('\n========== 优化结果 ==========\n');
    fprintf('最优加权和：%.4f\n', fval);
    fprintf('选用的模式数：%d\n', sum(I));
    disp('使用的模式及次数：');
    for i = 1:n
        if I(i)
            fprintf('模式 %2d：产品 %s，使用 %2d 次\n', i, mat2str(results_matrix(i,:)), N(i));
        end
    end
    fprintf('理论前四大次数：%.0f, %.0f, %.0f, %.0f\n', t);
    fprintf('实际排序次数：%s\n', mat2str(sort(N, 'descend')'));
else
    disp('未找到可行解，请检查约束。');
end
