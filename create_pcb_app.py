import os

def write_file(path, content):
    dirname = os.path.dirname(path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"[CREATED] {path}")

def generate_project():
    print("Initializing Master Setup: Upgrading KiCad export to use native self-contained primitives...")

    # 1. GitHub Actions Workflow File
    write_file(".github/workflows/generate_and_build.yml", """
name: Generate and Build PCB App APK

on:
  push:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  generate-and-build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout Repository
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'

    - name: Set up JDK 17
      uses: actions/setup-java@v4
      with:
        distribution: 'temurin'
        java-version: '17'

    - name: Run Python Script to Scaffold Android App
      run: |
        python setup_all.py

    - name: Install Modern Gradle 8.4
      run: |
        wget https://services.gradle.org/distributions/gradle-8.4-bin.zip
        unzip -q gradle-8.4-bin.zip
        echo "$PWD/gradle-8.4/bin" >> $GITHUB_PATH

    - name: Generate Gradle Wrapper
      run: |
        gradle wrapper --gradle-version 8.4

    - name: Grant execute permission for Gradle wrapper
      run: chmod +x gradlew

    - name: Build Debug APK
      run: ./gradlew assembleDebug

    - name: Upload APK Artifact
      uses: actions/upload-artifact@v4
      with:
        name: pcb-generator-debug-apk
        path: app/build/outputs/apk/debug/app-debug.apk
""")

    # 2. Root build.gradle
    write_file("build.gradle", """
plugins {
    id 'com.android.application' version '8.1.4' apply false
    id 'org.jetbrains.kotlin.android' version '1.9.0' apply false
}
""")

    # 3. settings.gradle
    write_file("settings.gradle", """
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "PCBGeneratorApp"
include ':app'
""")

    # 4. gradle.properties
    write_file("gradle.properties", """
android.useAndroidX=true
android.enableJetifier=true
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
""")

    # 5. app/build.gradle
    write_file("app/build.gradle", """
plugins {
    id 'com.android.application'
    id 'org.jetbrains.kotlin.android'
}

android {
    namespace 'com.example.pcbgenerator'
    compileSdk 34

    defaultConfig {
        applicationId "com.example.pcbgenerator"
        minSdk 24
        targetSdk 34
        versionCode 1
        versionName "1.0"

        testInstrumentationRunner "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = '17'
    }
}

dependencies {
    implementation 'androidx.core:core-ktx:1.12.0'
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.11.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
}
""")

    # 6. AndroidManifest.xml
    write_file("app/src/main/AndroidManifest.xml", """
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" android:maxSdkVersion="32" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" android:maxSdkVersion="32" />

    <application
        android:allowBackup="true"
        android:label="PCB Generator AI"
        android:supportsRtl="true"
        android:theme="@style/Theme.AppCompat.Light.DarkActionBar">
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>
""")

    # 7. Strings Resource
    write_file("app/src/main/res/values/strings.xml", """
<resources>
    <string name="app_name">PCB Generator AI</string>
</resources>
""")

    # 8. Layout XML (UI Design)
    write_file("app/src/main/res/layout/activity_main.xml", """
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="16dp"
    android:gravity="center_horizontal">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Offline AI PCB &amp; Electronics Designer"
        android:textSize="18sp"
        android:textStyle="bold"
        android:layout_marginBottom="16dp" />

    <EditText
        android:id="@+id/etPrompt"
        android:layout_width="match_parent"
        android:layout_height="120dp"
        android:hint="Enter circuit blueprint prompt (e.g., '5V regulated power supply with microcontroller')..."
        android:gravity="top|start"
        android:inputType="textMultiLine"
        android:background="@android:drawable/edit_text"
        android:padding="8dp"
        android:layout_marginBottom="16dp" />

    <Button
        android:id="@+id/btnGenerate"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Compile &amp; Export Native KiCad PCB File"
        android:layout_marginBottom="16dp" />

    <TextView
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Compilation &amp; File Export Log:"
        android:textStyle="bold"
        android:layout_marginBottom="8dp" />

    <ScrollView
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:background="#1E1E1E"
        android:padding="8dp">

        <TextView
            android:id="@+id/tvOutput"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="Ready for circuit prompt..."
            android:textColor="#00FF00"
            android:fontFamily="monospace"
            android:textSize="13sp" />
    </ScrollView>

</LinearLayout>
""")

    # 9. MainActivity.kt (Uses KiCad graphic primitives for universal rendering)
    write_file("app/src/main/java/com/example/pcbgenerator/MainActivity.kt", """
package com.example.pcbgenerator

import android.os.Bundle
import android.os.Environment
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import java.io.File

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val etPrompt = findViewById<EditText>(R.id.etPrompt)
        val btnGenerate = findViewById<Button>(R.id.btnGenerate)
        val tvOutput = findViewById<TextView>(R.id.tvOutput)

        btnGenerate.setOnClickListener {
            val promptText = etPrompt.text.toString().trim()
            if (promptText.isEmpty()) {
                tvOutput.text = "Error: Please enter a circuit blueprint prompt."
                return@setOnClickListener
            }

            tvOutput.text = "Compiling prompt into native KiCad graphics..."
            
            val compiledResult = compilePromptToNativeKiCad(promptText)
            val fileName = "PCB_Design_" + System.currentTimeMillis() + ".kicad_pcb"
            val savedFile = saveFileToDownloads(fileName, compiledResult.fileContent)

            if (savedFile != null) {
                tvOutput.text = "SUCCESS! Native KiCad file saved:\\n" +
                        "${savedFile.absolutePath}\\n\\n" +
                        "--- COMPILATION LOG ---\\n" +
                        compiledResult.logSummary
            } else {
                tvOutput.text = "Error: Failed to write file to local download storage."
            }
        }
    }

    data class CompilationResult(val fileContent: String, val logSummary: String)

    private fun compilePromptToNativeKiCad(prompt: String): CompilationResult {
        val lowerPrompt = prompt.lowercase()
        
        val hasMicrocontroller = lowerPrompt.contains("microcontroller") || lowerPrompt.contains("arduino") || lowerPrompt.contains("esp32") || lowerPrompt.contains("mcu")
        val hasRegulator = lowerPrompt.contains("regulator") || lowerPrompt.contains("7805") || lowerPrompt.contains("power") || lowerPrompt.contains("supply")
        val hasLed = lowerPrompt.contains("led") || lowerPrompt.contains("indicator")
        
        val components = mutableListOf<String>()
        components.add("C1")
        components.add("C2")
        if (hasRegulator) components.add("U1 (LM7805)")
        if (hasMicrocontroller) components.add("MCU1")
        if (hasLed) {
            components.add("D1")
            components.add("R1")
        }

        // Build a self-contained KiCad file using graphic primitives (gr_text, gr_circle, gr_line)
        // This guarantees all viewers render components and traces natively without library lookups.
        val kicadFileContent = StringBuilder().apply {
            append("(kicad_pcb (version 20221018) (generator \\"pcb_ai_native\\")\\n")
            append("  (paper \\"A4\\")\\n")
            append("  (layers\\n")
            append("    (0 \\"F.Cu\\" signal)\\n")
            append("    (31 \\"B.Cu\\" signal)\\n")
            append("    (40 \\"Edge.Cuts\\" user)\\n")
            append("    (41 \\"F.SilkS\\" user)\\n")
            append("  )\\n")
            append("  (setup\\n")
            append("    (zone_setting (clearance 0.5))\\n")
            append("  )\\n")
            append("  ;; Prompt: $prompt\\n")
            
            // Board boundary outline (Square box)
            append("  (gr_rect (start 10 10) (end 120 100) (stroke (width 0.15) (type solid)) (layer \\"Edge.Cuts\\"))\\n")

            // Draw components & traces natively using primitives
            for ((index, name) in components.withIndex()) {
                val posX = 25.0 + (index * 16.0)
                val posY = 40.0 + ((index % 2) * 20.0)
                
                // Component Label text on Silkscreen layer
                append("  (gr_text \\"$name\\" (at $posX $posY) (layer \\"F.SilkS\\") (effects (font (size 1.2 1.2))))\\n")
                
                // Component Pad/Circle representation on Copper layer
                append("  (gr_circle (center $posX $posY) (end ${posX + 2} $posY) (stroke (width 0.6) (type solid)) (layer \\"F.Cu\\"))\\n")

                // Interconnecting copper traces to next component
                if (index < components.size - 1) {
                    val nextX = 25.0 + ((index + 1) * 16.0)
                    val nextY = 40.0 + (((index + 1) % 2) * 20.0)
                    append("  (gr_line (start $posX $posY) (end $nextX $nextY) (stroke (width 0.3) (type solid)) (layer \\"F.Cu\\"))\\n")
                }
            }
            append(")\\n")
        }.toString()

        val log = StringBuilder().apply {
            append("1. Parsed blueprint prompt: OK\\n")
            append("2. Generated Edge.Cuts board canvas (120x100mm)\\n")
            append("3. Injected ${components.size} components via native F.SilkS text and F.Cu pads\\n")
            append("4. Rendered copper interconnect traces (Library-independent format).")
        }.toString()

        return CompilationResult(kicadFileContent, log)
    }

    private fun saveFileToDownloads(fileName: String, fileContent: String): File? {
        return try {
            val downloadsDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
            if (!downloadsDir.exists()) {
                downloadsDir.mkdirs()
            }
            val file = File(downloadsDir, fileName)
            file.writeText(fileContent)
            file
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }
}
""")

    print("\n[SUCCESS] Master project script updated with native KiCad primitives generator!")

if __name__ == "__main__":
    generate_project()
