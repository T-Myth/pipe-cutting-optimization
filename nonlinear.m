%先找到所有可能的模式，遍历搜索
% 定义约束条件
A = [1, 1, 1, 1; 
    290, 315, 350, 455;
    -290,-315,-350,-455];
b = [5; 1850;-1750];
% 初始化切割模式矩阵
results_matrix = [];
% 循环遍历所有结果
for x1 = 0:5,for x2 = 0:5,for x3 = 0:5,for x4 = 0:5
    x = [x1 x2 x3 x4]'; % 组合向量
    % 检查是否满足所有约束条件
    if all(A*x <= b)
        results_matrix = [results_matrix;x'];
    end
end; end; end; end
%定义决策变量，分别为四种模式下四种产品生产数，xij 为第 i 中模型生成的第 j 种产品个数，NMi 为第 i 中模式使用次数，xj 为二元变量，表示选择第 j 种模式，共 22 个决策变量
A = [ones(1,11),zeros(1,11);
    eye(11),-1*eye(11);
    -30*eye(11),eye(11);
    zeros(1,11),-1*results_matrix(:,1)';
    zeros(1,11),-1*results_matrix(:,2)';
    zeros(1,11),-1*results_matrix(:,3)';
    zeros(1,11),-1*results_matrix(:,4)';];
b = [4;zeros(22,1);-15;-28;-21;-30];
lb = zeros(1,22);
ub = [ones(1,11) 30*ones(1,11)];
%定义所有决策变量为整数
Intcon = 1:22;
options = optimoptions('ga', ...
 'PopulationSize', 50, ... % 种群大小
 'MaxGenerations', 100, ... % 最大迭代次数
 'Display', 'iter', ... % 显示每次迭代的信息
 'PlotFcn', @gaplotbestf); % 绘制最优适应度值的图形
%调用 GA
[x, fval] = ga(@fitness,22, A,b,[],[],lb,ub,[],Intcon,options);
I = x(1:11);
N = x(12:end);
indicesI = find(I);
indicesN = find(N);
disp(['一共选择了',num2str(sum(I)),'种切割模式'])
for i = 1:sum(I)
 disp(['选择的第',num2str(i),'种切割方案：',num2str(results_matrix(indicesI(i),:)),' 该模式使用了',num2str(N(indicesN(i))),'次']);
end
disp(['切割成本：',num2str(fval)]);

function obj = fitness(x)
obj=0;
% 创建一个示例数组
A = x(12:end);
% 找到最大值和其索引
[maxValue, maxIndex] = max(A);
obj = maxValue*1.1 + obj;
% 删除最大值
A(maxIndex) = [];
% 找到最大值和其索引
[maxValue, maxIndex] = max(A);
obj = maxValue*1.2 + obj;
% 删除最大值
A(maxIndex) = [];
% 找到最大值和其索引
[maxValue, maxIndex] = max(A);
obj = maxValue*1.3 + obj;
% 删除最大值
A(maxIndex) = [];
% 找到最大值和其索引
[maxValue, ~] = max(A);
obj = maxValue*1.4 + obj;
end
