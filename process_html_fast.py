import os
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, unquote
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def download_image(url, save_path):
    if os.path.exists(save_path):
        return True  # 已存在，跳过（续传支持）
    
    try:
        # 增加重试机制
        for attempt in range(3):
            try:
                response = requests.get(url, timeout=15)
                if response.status_code == 200:
                    with open(save_path, 'wb') as f:
                        f.write(response.content)
                    return True
                else:
                    print(f"    - 状态码错误 {response.status_code}: {url}")
                    break
            except requests.exceptions.ConnectionError:
                if attempt < 2:
                    time.sleep(1)  # 连接重置时稍作等待再重试
                    continue
                raise
    except Exception as e:
        print(f"    - 下载失败 {url}: {e}")
    return False

def process_html_online_images(html_path, output_folder, max_workers=10):
    # 创建输出目录
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    images_dir = os.path.join(output_folder, "images")
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)

    print(f"正在处理 HTML: {html_path} ...")
    
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'lxml')
    
    img_tags = soup.find_all('img')
    online_imgs = []
    
    for i, img in enumerate(img_tags):
        src = img.get('src')
        if src and src.startswith('http'):
            online_imgs.append((i, img, src))

    print(f"发现 {len(online_imgs)} 张在线图片。开始多线程下载 (线程数: {max_workers})...")
    
    downloaded_count = 0
    tasks = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i, img, src in online_imgs:
            try:
                parsed_url = urlparse(src)
                filename = os.path.basename(unquote(parsed_url.path))
                if not filename or '.' not in filename:
                    filename = f"img_{i+1}.png"
                
                img_path = os.path.join(images_dir, filename)
                
                # 避免重名
                counter = 1
                base_name, ext = os.path.splitext(filename)
                while os.path.exists(img_path):
                    img_path = os.path.join(images_dir, f"{base_name}_{counter}{ext}")
                    counter += 1
                
                # 提交任务
                future = executor.submit(download_image, src, img_path)
                tasks.append((future, img, img_path))
                
            except Exception as e:
                print(f"  - 准备任务出错: {e}")

        # 等待所有任务完成
        for future, img, img_path in tasks:
            if future.result():
                rel_path = os.path.relpath(img_path, output_folder).replace("\\", "/")
                img['src'] = rel_path
                downloaded_count += 1

    # 保存新的 HTML
    output_html = os.path.join(output_folder, "index.html")
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(str(soup))
        
    print(f"\n处理完成！共成功处理 {downloaded_count}/{len(online_imgs)} 张图片。")
    print(f"HTML 文件已保存至: {output_html}")

if __name__ == "__main__":
    html_file = "NX12_基于特征加工.html"
    out_dir = "nx12_fbm_html_output_v3"
    # 增加线程数到 20 以提速
    process_html_online_images(html_file, out_dir, max_workers=20)
