import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Frame, Label, Button, Entry
import cv2
import os
import numpy as np
from safetensors import safe_open
import torch
from typing import Optional, Union, Any, Dict

class VideoFrameExtractor:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("视频拆帧工具")
        self.root.geometry("500x300")
        
        # 视频文件路径
        self.video_path = tk.StringVar()
        # 输出目录路径
        self.output_dir = tk.StringVar()
        
        # 移除转换文件路径变量
        # self.convert_path = tk.StringVar()
        
        # 创建界面组件
        self.create_widgets()
    
    def create_widgets(self):
        # 视频文件选择
        tk.Label(self.root, text="视频文件:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Entry(self.root, textvariable=self.video_path, width=40).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.root, text="浏览...", command=self.select_video).grid(row=0, column=2, padx=5, pady=5)
        
        # 输出目录选择
        tk.Label(self.root, text="输出目录:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        tk.Entry(self.root, textvariable=self.output_dir, width=40).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self.root, text="浏览...", command=self.select_output_dir).grid(row=1, column=2, padx=5, pady=5)
        
        # 转换文件选择
        # 移除转换文件相关组件
        # tk.Label(self.root, text="转换文件:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        # tk.Entry(self.root, textvariable=self.convert_path, width=40).grid(row=2, column=1, padx=5, pady=5)
        # tk.Button(self.root, text="浏览...", command=self.select_convert_file).grid(row=2, column=2, padx=5, pady=5)

        # 功能按钮
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        tk.Button(button_frame, text="开始拆帧", command=self.extract_frames, width=15).pack(side=tk.LEFT, padx=5)
        
        # 状态显示
        self.status_label = tk.Label(self.root, text="准备就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=4, column=0, columnspan=3, sticky="we", padx=5, pady=5)
    
    def select_video(self) -> None:
        file_path: str = filedialog.askopenfilename(
            title="选择视频文件",
            filetypes=[("视频文件", "*.mp4 *.avi *.mov *.mkv"), ("所有文件", "*.*")]
        )
        if file_path:
            self.video_path.set(file_path)
    
    def select_output_dir(self) -> None:
        dir_path: str = filedialog.askdirectory(title="选择输出目录")
        if dir_path:
            self.output_dir.set(dir_path)
            
    def extract_frames(self) -> None:
        video_path = self.video_path.get()
        output_dir = self.output_dir.get()
        
        # 验证输入
        if not video_path or not output_dir:
            messagebox.showerror("错误", "请先选择视频文件和输出目录")
            return
        
        if not os.path.exists(video_path):
            messagebox.showerror("错误", "视频文件不存在")
            return
        
        try:
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            # 打开视频文件
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                # 更详细的错误提示
                error_msg = f"无法打开视频文件: {video_path}\n"
                error_msg += "可能原因:\n"
                error_msg += "1. 文件路径包含中文或特殊字符\n"
                error_msg += "2. 视频编码格式不受支持\n"
                error_msg += "3. 文件已损坏\n"
                error_msg += "请尝试:\n"
                error_msg += "1. 将文件移动到纯英文路径\n"
                error_msg += "2. 转换为标准MP4格式(H.264编码)"
                messagebox.showerror("错误", error_msg)
                return
            
            # 获取视频信息
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames == 0:
                messagebox.showerror("错误", "视频帧数为0，可能是无效视频文件")
                return
            
            print(f"视频信息: 总帧数={total_frames}, 宽度={cap.get(cv2.CAP_PROP_FRAME_WIDTH)}, 高度={cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
            self.status_label.config(text=f"正在处理: 0/{total_frames} 帧")
            self.root.update()
            
            # 逐帧处理
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # 确保输出目录存在并可写
                try:
                    os.makedirs(output_dir, exist_ok=True)
                    # 测试目录可写性
                    test_file = os.path.join(output_dir, 'test_write.tmp')
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)
                except Exception as e:
                    print(f"错误: 输出目录 {output_dir} 不可写: {str(e)}")
                    print("建议尝试以下目录之一:")
                    print("1. 桌面目录: C:/Users/你的用户名/Desktop/output_frames")
                    print("2. 当前目录下的子目录: ./output_frames")
                    return
                
                # 保存帧为PNG (统一使用正斜杠)
                output_path = os.path.join(output_dir, f"frame_{frame_count:04d}.png").replace('\\', '/')
                try:
                    # 先测试用Pillow保存图像
                    from PIL import Image
                    pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    pil_img.save(output_path)
                    print(f"已保存帧 {frame_count} 到 {output_path} (使用Pillow)")
                except Exception as e:
                    print(f"错误: 无法保存帧 {frame_count}: {str(e)}")
                    print("可能原因:")
                    print("1. 磁盘空间不足")
                    print("2. 文件权限问题")
                    print("3. 图像编码问题")
                    print("4. 防病毒软件阻止")
                
                frame_count += 1
                if frame_count % 10 == 0:  # 每10帧更新一次状态
                    self.status_label.config(text=f"正在处理: {frame_count}/{total_frames} 帧")
                    self.root.update()
            
            cap.release()
            self.status_label.config(text=f"完成! 共处理 {frame_count} 帧")
            messagebox.showinfo("完成", f"成功提取 {frame_count} 帧到 {output_dir}")
            
        except Exception as e:
            messagebox.showerror("错误", f"处理过程中发生错误: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoFrameExtractor(root)
    root.mainloop()