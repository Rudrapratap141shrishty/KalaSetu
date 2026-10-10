"""
Automated Native Android APK Compilation Pipeline for KalaSetu
Downloads lightweight Google official build tools (aapt2, D8/R8, android.jar),
compiles Java source code to Dalvik classes.dex, links Android resources,
bundles all offline web app assets, and signs the APK with release keystore.
"""

import os
import sys
import shutil
import zipfile
import subprocess
from pathlib import Path
import urllib.request

ROOT_DIR = Path(__file__).resolve().parent
BUILD_TOOLS_DIR = ROOT_DIR / 'android_tools'
BUILD_TOOLS_DIR.mkdir(parents=True, exist_ok=True)

ANDROID_DIR = ROOT_DIR / 'android'
SRC_DIR = ANDROID_DIR / 'app' / 'src' / 'main'
JAVA_SRC = SRC_DIR / 'java' / 'org' / 'kalasetu' / 'app' / 'MainActivity.java'
RES_DIR = SRC_DIR / 'res'
MANIFEST_XML = SRC_DIR / 'AndroidManifest.xml'
ASSETS_DIR = SRC_DIR / 'assets'

OUTPUT_DIR = ROOT_DIR / 'build_output'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

AAPT2_JAR = BUILD_TOOLS_DIR / 'aapt2.jar'
AAPT2_EXE = BUILD_TOOLS_DIR / 'aapt2.exe'
R8_JAR = BUILD_TOOLS_DIR / 'r8.jar'
ANDROID_JAR = BUILD_TOOLS_DIR / 'android-35.jar'

KEYSTORE_PATH = ROOT_DIR / 'kalasetu-release.jks'
UNSIGNED_APK = OUTPUT_DIR / 'app-unsigned.apk'
SIGNED_APK = ROOT_DIR / 'KalaSetu-ArtisanVerse.apk'
STATIC_APK = ROOT_DIR / 'static' / 'apk' / 'KalaSetu-ArtisanVerse.apk'

def download_file(url, target_path, desc):
    if not target_path.exists():
        print(f"[Download] Fetching {desc} from Google repository...")
        urllib.request.urlretrieve(url, target_path)
        print(f"           Saved to {target_path.name}")
    else:
        print(f"[Cache] Found cached {desc}: {target_path.name}")

def setup_build_tools():
    print("\n[Step 1/6] Setting up Android CLI Toolchain...")
    
    # 1. Android API Jar
    android_jar_url = 'https://raw.githubusercontent.com/Sable/android-platforms/master/android-35/android.jar'
    download_file(android_jar_url, ANDROID_JAR, "Android SDK Platform (android.jar)")
    
    # 2. D8 / R8 Dex Compiler
    r8_url = 'https://dl.google.com/dl/android/maven2/com/android/tools/r8/8.2.42/r8-8.2.42.jar'
    download_file(r8_url, R8_JAR, "Google D8/R8 Dex Compiler (r8.jar)")
    
    # 3. AAPT2 Windows Binary
    aapt2_url = 'https://dl.google.com/dl/android/maven2/com/android/tools/build/aapt2/8.2.2-10154469/aapt2-8.2.2-10154469-windows.jar'
    download_file(aapt2_url, AAPT2_JAR, "AAPT2 Resource Compiler")
    
    if not AAPT2_EXE.exists():
        with zipfile.ZipFile(AAPT2_JAR, 'r') as z:
            z.extract('aapt2.exe', BUILD_TOOLS_DIR)
        print(f"           Extracted aapt2.exe")

def bundle_offline_web_app():
    print("\n[Step 2/6] Packaging Offline Mobile Web App Assets...")
    if ASSETS_DIR.exists():
        shutil.rmtree(ASSETS_DIR)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    # Copy HTML, CSS, JS, Manifest, Icons
    shutil.copy2(ROOT_DIR / 'templates' / 'index.html', ASSETS_DIR / 'index.html')
    shutil.copytree(ROOT_DIR / 'static' / 'css', ASSETS_DIR / 'static' / 'css', dirs_exist_ok=True)
    shutil.copytree(ROOT_DIR / 'static' / 'js', ASSETS_DIR / 'static' / 'js', dirs_exist_ok=True)
    shutil.copytree(ROOT_DIR / 'static' / 'icons', ASSETS_DIR / 'static' / 'icons', dirs_exist_ok=True)
    shutil.copy2(ROOT_DIR / 'static' / 'manifest.json', ASSETS_DIR / 'static' / 'manifest.json')
    shutil.copy2(ROOT_DIR / 'static' / 'sw.js', ASSETS_DIR / 'static' / 'sw.js')
    print(f"           Bundled complete application into {ASSETS_DIR}")

def compile_resources():
    print("\n[Step 3/6] Compiling Android Resources with AAPT2...")
    compiled_res_zip = OUTPUT_DIR / 'compiled_res.zip'
    
    # Compile res directory
    cmd_compile = f'"{AAPT2_EXE}" compile --dir "{RES_DIR}" -o "{compiled_res_zip}"'
    subprocess.run(cmd_compile, shell=True, check=True)
    
    # Link resources & manifest
    gen_dir = OUTPUT_DIR / 'gen'
    gen_dir.mkdir(parents=True, exist_ok=True)
    
    cmd_link = (
        f'"{AAPT2_EXE}" link -o "{UNSIGNED_APK}" '
        f'-I "{ANDROID_JAR}" '
        f'--manifest "{MANIFEST_XML}" '
        f'--min-sdk-version 23 '
        f'--target-sdk-version 35 '
        f'--java "{gen_dir}" '
        f'--auto-add-overlay '
        f'"{compiled_res_zip}"'
    )
    subprocess.run(cmd_link, shell=True, check=True)
    print(f"           Generated R.java & base APK package: {UNSIGNED_APK}")

def compile_java_and_dex():
    print("\n[Step 4/6] Compiling Java Code & Converting to Dalvik classes.dex...")
    classes_dir = OUTPUT_DIR / 'classes'
    classes_dir.mkdir(parents=True, exist_ok=True)
    
    r_java = OUTPUT_DIR / 'gen' / 'org' / 'kalasetu' / 'app' / 'R.java'
    
    # Compile Java to Java 8 bytecode .class
    cmd_javac = (
        f'javac --release 8 -cp "{ANDROID_JAR}" '
        f'-d "{classes_dir}" '
        f'"{JAVA_SRC}" "{r_java}"'
    )
    subprocess.run(cmd_javac, shell=True, check=True)
    print("           Compiled Java source files to .class bytecode")
    
    # Convert .class to classes.dex using D8
    class_files = []
    for root, dirs, files in os.walk(classes_dir):
        for file in files:
            if file.endswith('.class'):
                class_files.append(f'"{Path(root) / file}"')
                
    cmd_d8 = (
        f'java -cp "{R8_JAR}" com.android.tools.r8.D8 '
        f'--min-api 23 '
        f'--lib "{ANDROID_JAR}" '
        f'--output "{OUTPUT_DIR}" '
        + " ".join(class_files)
    )
    subprocess.run(cmd_d8, shell=True, check=True)
    print(f"           Generated Dalvik classes.dex in {OUTPUT_DIR}")

def assemble_final_apk():
    print("\n[Step 5/6] Merging classes.dex, Assets, and Resources into APK...")
    classes_dex = OUTPUT_DIR / 'classes.dex'
    
    # Inject classes.dex and assets into unsigned APK
    with zipfile.ZipFile(UNSIGNED_APK, 'a', zipfile.ZIP_DEFLATED) as apk:
        # Add classes.dex
        apk.write(classes_dex, 'classes.dex')
        
        # Add assets
        for root, dirs, files in os.walk(ASSETS_DIR):
            for file in files:
                file_path = Path(root) / file
                arc_name = 'assets/' + str(file_path.relative_to(ASSETS_DIR)).replace('\\', '/')
                apk.write(file_path, arc_name)
                
    print(f"           Assembled package: {UNSIGNED_APK}")

def sign_apk():
    print("\n[Step 6/6] Signing APK with Keystore Certificate...")
    if not KEYSTORE_PATH.exists():
        keytool_cmd = (
            f'keytool -genkeypair -v -keystore "{KEYSTORE_PATH}" '
            f'-alias kalasetu -keyalg RSA -keysize 2048 -validity 10000 '
            f'-storepass kalasetu123 -keypass kalasetu123 '
            f'-dname "CN=KalaSetu, OU=ArtisanVerse, O=KalaSetu, L=Varanasi, ST=UP, C=IN"'
        )
        subprocess.run(keytool_cmd, shell=True, check=True)
        
    # Copy unsigned APK to final signed destination
    shutil.copy2(UNSIGNED_APK, SIGNED_APK)
    
    # Sign APK using jarsigner
    jarsigner_cmd = (
        f'jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 '
        f'-keystore "{KEYSTORE_PATH}" -storepass kalasetu123 -keypass kalasetu123 '
        f'"{SIGNED_APK}" kalasetu'
    )
    subprocess.run(jarsigner_cmd, shell=True, check=True, stdout=subprocess.PIPE)
    
    # Copy to static web distribution path
    STATIC_APK.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SIGNED_APK, STATIC_APK)
    
    apk_size = os.path.getsize(SIGNED_APK) / 1024
    print("\n" + "=" * 65)
    print("  [SUCCESS] Native Android APK Successfully Compiled & Signed!")
    print(f"  -> File: {SIGNED_APK} ({apk_size:.1f} KB)")
    print(f"  -> Web URL: http://localhost:8000/static/apk/KalaSetu-ArtisanVerse.apk")
    print(f"  -> Contains: Native Dalvik bytecode (classes.dex), AndroidManifest,")
    print(f"               Camera Permissions, UPI Intent Handlers, Offline Assets")
    print("=" * 65)

def main():
    print("=" * 65)
    print("  KalaSetu (ArtisanVerse) - Native Android APK Compiler")
    print("=" * 65)
    
    setup_build_tools()
    bundle_offline_web_app()
    compile_resources()
    compile_java_and_dex()
    assemble_final_apk()
    sign_apk()

if __name__ == '__main__':
    main()
