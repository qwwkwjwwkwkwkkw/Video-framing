# 视频拆帧工具

## 功能描述
- 从视频文件中提取每一帧图像
- 支持常见视频格式(MP4/AVI/MOV/MKV)
- 输出为PNG格式图片

## 使用说明
1. 运行`video_frame_extractor.exe`
2. 点击"浏览..."选择视频文件
3. 选择输出目录
4. 点击"开始拆帧"按钮

## 打包说明
```bash
pyinstaller --onefile --windowed video_frame_extractor.py
```

## 依赖库
- Python 3.8+
- OpenCV (cv2)
- NumPy
- tkinter

## 注意事项
- 确保输出目录有足够空间
- 大视频文件处理可能需要较长时间
