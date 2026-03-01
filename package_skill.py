import os
import zipfile
import shutil

def package_skill(skill_dir, output_dir=None):
    """将技能文件夹打包为 .skill 文件"""
    skill_name = os.path.basename(skill_dir)
    
    if output_dir is None:
        output_dir = os.path.dirname(os.path.abspath(skill_dir))
    
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, f"{skill_name}.skill")
    
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, skill_dir)
                zipf.write(file_path, arcname)
    
    print(f"[OK] Packaged: {output_file}")
    return output_file

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <技能文件夹> [输出目录]")
        sys.exit(1)
    
    skill_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    package_skill(skill_dir, output_dir)
