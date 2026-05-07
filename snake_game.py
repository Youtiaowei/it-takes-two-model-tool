import tkinter as tk
import random

# ------------------- 常量 -------------------
GRID_SIZE = 20          # 每个格子边长（像素）
GRID_WIDTH = 30         # 水平格子数
GRID_HEIGHT = 30        # 垂直格子数
CANVAS_WIDTH = GRID_WIDTH * GRID_SIZE
CANVAS_HEIGHT = GRID_HEIGHT * GRID_SIZE

# 颜色
COLOR_BG = "#2E2E2E"           # 背景深灰
COLOR_GRID = "#3D3D3D"         # 网格线
COLOR_SNAKE = "#4CAF50"        # 蛇身绿色
COLOR_SNAKE_HEAD = "#8BC34A"   # 蛇头浅绿
COLOR_FOOD = "#FF5656"         # 食物红色
COLOR_SCORE = "#FFFFFF"        # 分数白色
COLOR_OVERLAY = "#1E1E1E"      # 遮罩深色
COLOR_OVERLAY_TEXT = "#FFD700" # 文字金色

# 移动方向
DIRECTIONS = {
    "Up": (0, -1),
    "Down": (0, 1),
    "Left": (-1, 0),
    "Right": (1, 0)
}
OPPOSITE = {
    "Up": "Down",
    "Down": "Up",
    "Left": "Right",
    "Right": "Left"
}

# ------------------- 游戏类 -------------------
class SnakeGame:
    def __init__(self, master):
        self.master = master
        master.title("贪吃蛇")
        master.resizable(False, False)
        master.configure(bg=COLOR_BG)

        self.canvas = tk.Canvas(
            master,
            width=CANVAS_WIDTH + 2,   # 两边留 1px 边框
            height=CANVAS_HEIGHT + 2,
            highlightthickness=0,
            bg=COLOR_BG
        )
        self.canvas.pack(padx=10, pady=10)

        # 键盘绑定
        master.bind("<KeyPress>", self.key_press)
        master.bind("<KeyPress-r>", self.restart)
        master.bind("<KeyPress-R>", self.restart)

        # 游戏状态
        self.snake = []          # 蛇身格子坐标列表
        self.food = None         # 食物坐标 (x, y)
        self.direction = "Right" # 当前方向
        self.next_dir = "Right"  # 下一个有效方向
        self.score = 0
        self.running = False
        self.game_over_flag = False

        # UI 元素
        self.score_text = None
        self.overlay_rect = None
        self.overlay_text = None

        # 绘制初始界面
        self.draw_grid()
        self.initialize_game()

    # ---------- 绘图辅助 ----------
    def draw_grid(self):
        """绘制网格线"""
        for x in range(0, CANVAS_WIDTH + 1, GRID_SIZE):
            self.canvas.create_line(
                x + 1, 1, x + 1, CANVAS_HEIGHT + 1,
                fill=COLOR_GRID, width=1
            )
        for y in range(0, CANVAS_HEIGHT + 1, GRID_SIZE):
            self.canvas.create_line(
                1, y + 1, CANVAS_WIDTH + 1, y + 1,
                fill=COLOR_GRID, width=1
            )

    def draw_square(self, x, y, color, outline=None):
        """在网格 (x,y) 处绘制一个方块，坐标以格子为单位"""
        px = x * GRID_SIZE + 1
        py = y * GRID_SIZE + 1
        self.canvas.create_rectangle(
            px, py,
            px + GRID_SIZE, py + GRID_SIZE,
            fill=color,
            outline=outline or color,
            width=1,
            tags="square"
        )

    # ---------- 游戏初始化 ----------
    def initialize_game(self):
        # 蛇的初始位置（中央）
        self.snake = [
            (GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2),
            (GRID_WIDTH // 2,     GRID_HEIGHT // 2),
            (GRID_WIDTH // 2 + 1, GRID_HEIGHT // 2)
        ]
        self.direction = "Right"
        self.next_dir = "Right"
        self.score = 0
        self.game_over_flag = False
        self.running = False

        # 删除旧食物、旧覆盖
        self.canvas.delete("food")
        self.canvas.delete("overlay")
        self.canvas.delete("score")

        # 生成新食物
        self.generate_food()
        self.draw_all()
        self.update_score_display()

        # 移除游戏结束遮罩
        if self.overlay_rect:
            self.canvas.delete(self.overlay_rect)
            self.overlay_rect = None
        if self.overlay_text:
            self.canvas.delete(self.overlay_text)
            self.overlay_text = None

    def start_game(self):
        if not self.running and not self.game_over_flag:
            self.running = True
            self.next_turn()

    # ---------- 键盘控制 ----------
    def key_press(self, event):
        key = event.keysym
        if key in DIRECTIONS:
            opp = OPPOSITE[key]
            # 禁止原地掉头
            if opp != self.direction:
                self.next_dir = key
        # 如果游戏未开始，按任何方向键开始
        if not self.running and not self.game_over_flag:
            self.start_game()

    # ---------- 逻辑更新 ----------
    def next_turn(self):
        if not self.running:
            return

        # 应用方向
        self.direction = self.next_dir
        dx, dy = DIRECTIONS[self.direction]

        # 新蛇头位置
        head_x, head_y = self.snake[-1]
        new_head = (head_x + dx, head_y + dy)

        # 检查是否吃到食物
        if new_head == self.food:
            # 蛇长增加（不删除尾）
            self.snake.append(new_head)
            self.score += 10
            self.update_score_display()
            self.generate_food()
        else:
            # 正常移动：头进、尾出
            self.snake.append(new_head)
            self.snake.pop(0)

        # 重新绘制
        self.draw_all()

        # 碰撞检测
        if self.check_collision(new_head):
            self.game_over()
            return

        # 继续下一帧
        self.master.after(120, self.next_turn)   # 速度 120ms

    def check_collision(self, head):
        # 墙壁碰撞
        x, y = head
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
            return True
        # 自身碰撞（排除蛇头本身）
        if head in self.snake[:-1]:
            return True
        return False

    # ---------- 食物 ----------
    def generate_food(self):
        while True:
            fx = random.randint(0, GRID_WIDTH - 1)
            fy = random.randint(0, GRID_HEIGHT - 1)
            if (fx, fy) not in self.snake:
                self.food = (fx, fy)
                break

    # ---------- 绘制 ----------
    def draw_all(self):
        # 清除之前的所有方块（保留网格）
        self.canvas.delete("square")
        self.canvas.delete("food")
        self.canvas.delete("score")

        # 绘制蛇身
        for idx, segment in enumerate(self.snake):
            color = COLOR_SNAKE_HEAD if idx == len(self.snake) - 1 else COLOR_SNAKE
            # 蛇身稍微圆角效果：用矩形模拟
            px = segment[0] * GRID_SIZE + 2
            py = segment[1] * GRID_SIZE + 2
            self.canvas.create_rectangle(
                px, py,
                px + GRID_SIZE - 2, py + GRID_SIZE - 2,
                fill=color,
                outline="",
                tags="square"
            )

        # 绘制食物（圆形）
        if self.food:
            fx, fy = self.food
            cx = fx * GRID_SIZE + 1 + GRID_SIZE // 2
            cy = fy * GRID_SIZE + 1 + GRID_SIZE // 2
            radius = GRID_SIZE // 2 - 2
            self.canvas.create_oval(
                cx - radius, cy - radius,
                cx + radius, cy + radius,
                fill=COLOR_FOOD,
                outline="",
                tags="food"
            )

        # 绘制分数
        self.update_score_display()

    def update_score_display(self):
        # 删除旧的分数文字
        self.canvas.delete("score_text")
        self.canvas.create_text(
            CANVAS_WIDTH // 2 + 1, 10,
            text=f"分数: {self.score}",
            fill=COLOR_SCORE,
            font=("微软雅黑", 16, "bold"),
            anchor="n",
            tags="score_text"
        )

    # ---------- 游戏结束 ----------
    def game_over(self):
        self.running = False
        self.game_over_flag = True

        # 半透明遮罩
        self.overlay_rect = self.canvas.create_rectangle(
            1, 1,
            CANVAS_WIDTH + 1, CANVAS_HEIGHT + 1,
            fill=COLOR_OVERLAY,
            stipple="gray25",   # 半透明纹理效果
            tags="overlay"
        )

        # 游戏结束文字
        self.overlay_text = self.canvas.create_text(
            CANVAS_WIDTH // 2 + 1, CANVAS_HEIGHT // 2 - 20,
            text="游戏结束",
            fill=COLOR_OVERLAY_TEXT,
            font=("微软雅黑", 30, "bold"),
            anchor="center",
            tags="overlay"
        )
        # 分数
        self.canvas.create_text(
            CANVAS_WIDTH // 2 + 1, CANVAS_HEIGHT // 2 + 20,
            text=f"最终得分: {self.score}",
            fill=COLOR_OVERLAY_TEXT,
            font=("微软雅黑", 18, "bold"),
            anchor="center",
            tags="overlay"
        )
        # 提示
        self.canvas.create_text(
            CANVAS_WIDTH // 2 + 1, CANVAS_HEIGHT // 2 + 60,
            text="按 R 键重新开始",
            fill=COLOR_OVERLAY_TEXT,
            font=("微软雅黑", 14),
            anchor="center",
            tags="overlay"
        )

    # ---------- 重新开始 ----------
    def restart(self, event=None):
        self.canvas.delete("overlay")
        self.initialize_game()
        # 玩家按方向键后再开始

# ------------------- 主程序 -------------------
if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
