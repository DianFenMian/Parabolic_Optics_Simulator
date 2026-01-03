import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.widgets import Slider, Button, RadioButtons

# 设置中文支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

class ParabolaOptics:
    def __init__(self, focus=1.0):
        self.focus = focus  # 焦距
        self.directrix = -focus  # 准线方程 y = -focus
        
    def parabola_y(self, x):
        """计算抛物线的y坐标，标准形式：y = x²/(4f)"""
        return x**2 / (4 * self.focus)
    
    def get_tangent_slope(self, x):
        """计算抛物线在点(x, y)处的切线斜率"""
        return x / (2 * self.focus)
    
    def reflect_ray(self, ray_start, ray_dir):
        """计算光线在抛物线上的反射"""
        # 光线参数方程：x = ray_start[0] + t * ray_dir[0]
        #               y = ray_start[1] + t * ray_dir[1]
        
        # 快速检查：如果光线从焦点出发且x方向合理，直接计算交点
        if np.allclose(ray_start, np.array([0, self.focus])):
            # 光线从焦点出发，找到其指向的抛物线上的点
            # 使用光线方向和抛物线方程求解
            # 设光线方向向量为(dx, dy)，则光线参数方程为：x = 0 + t*dx, y = f + t*dy
            # 代入抛物线方程：y = x²/(4f)
            # 得到：f + t*dy = (t*dx)²/(4f)
            # 整理得：(dx²/(4f))t² - dy*t - f = 0
            dx = ray_dir[0]
            dy = ray_dir[1]
            
            a = dx**2 / (4 * self.focus)
            b = -dy
            c = -self.focus
            
            discriminant = b**2 - 4 * a * c
            if discriminant < 0:
                return None  # 无交点
            
            t = (-b + np.sqrt(discriminant)) / (2 * a)  # 取正t值
            if t < 0:
                t = (-b - np.sqrt(discriminant)) / (2 * a)
                if t < 0:
                    return None  # 光线方向不对
            
            intersection = np.array([0 + t*dx, self.focus + t*dy])
        elif ray_dir[0] == 0:
            # 处理垂直入射的特殊情况
            x = ray_start[0]
            y_parabola = self.parabola_y(x)
            if ray_dir[1] == 0:
                return None  # 水平光线不会与抛物线相交
            t = (y_parabola - ray_start[1]) / ray_dir[1]
            if t <= 0:
                return None  # 光线方向不对
            intersection = np.array([x, y_parabola])
        else:
            # 解光线与抛物线的交点
            a = ray_dir[0]**2
            b = 2 * ray_start[0] * ray_dir[0] - 4 * self.focus * ray_dir[1]
            c = ray_start[0]**2 - 4 * self.focus * ray_start[1]
            
            discriminant = b**2 - 4 * a * c
            if discriminant < 0:
                return None  # 无交点
            
            t = (-b - np.sqrt(discriminant)) / (2 * a)  # 取最近的交点
            if t < 0:
                return None  # 光线方向不对
            
            intersection = np.array([ray_start[0] + t * ray_dir[0], 
                                    ray_start[1] + t * ray_dir[1]])
        
        # 计算切线斜率和法线斜率
        tangent_slope = self.get_tangent_slope(intersection[0])
        normal_slope = -1 / tangent_slope if tangent_slope != 0 else np.inf
        
        # 入射光线方向向量
        incident = np.array(ray_dir)
        incident = incident / np.linalg.norm(incident)  # 归一化
        
        # 法线向量
        if normal_slope == np.inf:
            normal = np.array([0, 1])
        else:
            normal = np.array([1, normal_slope])
            normal = normal / np.linalg.norm(normal)  # 归一化
        
        # 使用反射定律：反射光线 = 入射光线 - 2*(入射光线·法线)*法线
        reflected = incident - 2 * np.dot(incident, normal) * normal
        
        return intersection, reflected, t
    
    def generate_parallel_rays(self, num_rays=5, x_range=(-3, 3)):
        """生成从上到下入射的平行光线"""
        rays = []
        # 从上方远处垂直向下入射，x坐标在抛物线开口范围内
        x_positions = np.linspace(x_range[0], x_range[1], num_rays)
        for x in x_positions:
            ray_start = np.array([x, 10])  # 从上方远处开始
            ray_dir = np.array([0, -1])  # 方向向下
            rays.append((ray_start, ray_dir))
        return rays
    
    def generate_focal_rays(self, num_rays=5):
        """生成从焦点出发的入射光线，直接射向抛物线上的点"""
        rays = []
        # 在抛物线上选择不同x坐标的点
        x_values = np.linspace(-3, 3, num_rays)  # x范围覆盖抛物线开口
        for x in x_values:
            # 计算抛物线上该x坐标的点
            y_parabola = self.parabola_y(x)
            # 光线从焦点指向抛物线上的点
            ray_start = np.array([0, self.focus])  # 焦点坐标
            # 计算光线方向向量：从焦点指向抛物线上的点
            ray_dir = np.array([x - 0, y_parabola - self.focus])
            # 归一化方向向量
            ray_dir = ray_dir / np.linalg.norm(ray_dir)
            rays.append((ray_start, ray_dir))
        return rays

# 全局变量存储光线类型
current_ray_type = 'parallel'

def update(val):
    """更新图形"""
    focus = s_focus.val
    num_rays = int(s_num_rays.val)
    ray_type = current_ray_type
    
    # 更新抛物线
    optics.focus = focus
    x = np.linspace(-8, 8, 400)
    y = optics.parabola_y(x)
    parabola_plot.set_data(x, y)
    
    # 更新焦点位置
    focus_plot.set_data([0], [focus])
    
    # 更新准线
    directrix_plot.set_data([-8, 8], [-focus, -focus])
    
    # 清除旧的光线
    for line in ray_lines:
        line.remove()
    ray_lines.clear()
    
    # 生成新的光线
    if ray_type == 'parallel':
        rays = optics.generate_parallel_rays(num_rays=num_rays)
    else:
        rays = optics.generate_focal_rays(num_rays=num_rays)
    
    # 绘制光线
    for ray_start, ray_dir in rays:
        result = optics.reflect_ray(ray_start, ray_dir)
        if result:
            intersection, reflected, t = result
            
            # 入射光线：从起始点到交点
            t_incident = np.linspace(0, t, 50)  # 只绘制到交点
            x_incident = ray_start[0] + t_incident * ray_dir[0]
            y_incident = ray_start[1] + t_incident * ray_dir[1]
            line1, = ax.plot(x_incident, y_incident, 'b-', alpha=0.6)
            ray_lines.append(line1)
            
            # 反射光线：从交点出发
            t_reflected = np.linspace(0, 12, 50)
            x_reflected = intersection[0] + t_reflected * reflected[0]
            y_reflected = intersection[1] + t_reflected * reflected[1]
            line2, = ax.plot(x_reflected, y_reflected, 'r-', alpha=0.8)
            ray_lines.append(line2)
    
    fig.canvas.draw_idle()

# 光线类型选择处理函数
def set_ray_type(label):
    global current_ray_type
    if label == '平行入射光线':
        current_ray_type = 'parallel'
    else:
        current_ray_type = 'focal'
    update(None)

# 初始化抛物线光学系统
optics = ParabolaOptics()

# 创建图形
fig, ax = plt.subplots(figsize=(10, 8))
plt.subplots_adjust(left=0.1, bottom=0.35)

# 绘制初始抛物线
x = np.linspace(-8, 8, 400)
y = optics.parabola_y(x)
parabola_plot, = ax.plot(x, y, 'k-', linewidth=2, label='抛物线')

# 绘制焦点
focus_plot, = ax.plot([0], [optics.focus], 'ro', markersize=8, label='焦点')

# 绘制准线
directrix_plot, = ax.plot([-8, 8], [-optics.focus, -optics.focus], 'k--', label='准线')

# 光线类型选择
ray_type_var = RadioButtons(plt.axes([0.1, 0.25, 0.3, 0.1]), 
                               ('平行入射光线', '焦点发射光线'), 
                               active=0)

# 创建滑块
ax_focus = plt.axes([0.1, 0.15, 0.65, 0.03])
s_focus = Slider(ax_focus, '焦距', 0.5, 5.0, valinit=1.0)

ax_num_rays = plt.axes([0.1, 0.1, 0.65, 0.03])
s_num_rays = Slider(ax_num_rays, '光线数量', 1, 15, valinit=5, valstep=1)

# 重置按钮
ax_reset = plt.axes([0.8, 0.05, 0.1, 0.04])
button = Button(ax_reset, '重置', hovercolor='0.975')

# 光线线条列表
ray_lines = []

# 连接事件
ray_type_var.on_clicked(set_ray_type)
s_focus.on_changed(update)
s_num_rays.on_changed(update)

# 重置函数
def reset(event):
    s_focus.reset()
    s_num_rays.reset()
    ray_type_var.set_active(0)
    global current_ray_type
    current_ray_type = 'parallel'
    update(None)

button.on_clicked(reset)

# 主程序入口
if __name__ == "__main__":
    # 设置图形属性
    ax.set_aspect('equal')
    ax.set_xlim(-10, 10)
    ax.set_ylim(-2, 8)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('抛物线光学性质演示')
    ax.legend()
    
    # 初始绘制光线
    update(None)
    
    # 显示图形
    plt.show()