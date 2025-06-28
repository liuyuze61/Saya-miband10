import re
import json
import sys

def convert_script(input_file, output_file):
    scenes = []
    current_scene = {"background": "", "dialogues": []}
    current_fg = None
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        
        # 处理背景设置
        bg_match = re.search(r'<BACKGROUND SRC="([^"]+)"', line)
        if bg_match:
            current_scene["background"] = bg_match.group(1).split('//')[0].strip()
            continue
        
        # 处理立绘设置
        bustup_match = re.search(r'<BUSTUP NAME="([^"]+)" face="([^"]+)"', line)
        if bustup_match:
            current_fg = f"{bustup_match.group(1)}_{bustup_match.group(2)}"
            continue
        
        # 处理语音对话
        voice_match = re.search(r'<voice NAME="([^"]+)"[^>]*>([^<]+)', line)
        if voice_match:
            character = voice_match.group(1)
            text = voice_match.group(2).strip()
            if text.endswith('<k>'):
                text = text[:-3].strip()
            
            dialogue = {"character": character, "text": text}
            if current_fg:
                dialogue["fg"] = current_fg
            current_scene["dialogues"].append(dialogue)
            continue
        
        # 处理普通文本行
        if line and not line.startswith(('<', '//', '#')) and not re.match(r'^\s*$', line):
            text = line
            if text.endswith('<k>'):
                text = text[:-3].strip()
            
            dialogue = {"character": "", "text": text.strip()}
            if current_fg:
                dialogue["fg"] = current_fg
            current_scene["dialogues"].append(dialogue)
            continue
        
        # 处理场景分割
        if line == '<clear>':
            if current_scene["dialogues"]:
                scenes.append(current_scene)
            current_scene = {"background": "", "dialogues": []}
            current_fg = None
    
    # 添加最后一个场景
    if current_scene["dialogues"]:
        scenes.append(current_scene)
    
    # 保存为JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(scenes, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script_converter.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    convert_script(input_file, output_file)