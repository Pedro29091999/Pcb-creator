import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"[CREATED] {path}")

def generate_pcb_app():
    print("Initializing Prompt-to-PCB Android App project structure...")

    # 1. Root build.gradle
    write_file("build.gradle", """
buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath "com.android.tools.build:gradle:8.1.4"
        classpath "org.jetbrains.kotlin:kotlin-gradle-plugin:1.9.0"
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

task clean(type: Delete) {
    delete rootProject.buildDir
}
""")

    # 2. settings.gradle
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

    # 3. app/build.gradle
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

    # 4. AndroidManifest.xml
    write_file("app/src/main/AndroidManifest.xml", """
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="PCB Generator AI"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.AppCompat.Light.DarkActionBar">
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="intent.action.MAIN" />
                <category android:name="category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>
""")

    # 5. Strings resource
    write_file("app/src/main/res/values/strings.xml", """
<resources>
    <string name="app_name">PCB Generator AI</string>
</resources>
""")

    # 6. Layout XML (UI with Prompt Input & Output Log)
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
        android:text="AI PCB &amp; Electronics Designer"
        android:textSize="20sp"
        android:textStyle="bold"
        android:layout_marginBottom="16dp" />

    <EditText
        android:id="@+id/etPrompt"
        android:layout_width="match_parent"
        android:layout_height="120dp"
        android:hint="Enter your blueprint or circuit prompt (e.g., '5V regulated power supply with LM7805')..."
        android:gravity="top|start"
        android:inputType="textMultiLine"
        android:background="@android:drawable/edit_text"
        android:padding="8dp"
        android:layout_marginBottom="16dp" />

    <Button
        android:id="@+id/btnGenerate"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Generate PCB Schematic &amp; Netlist"
        android:layout_marginBottom="16dp" />

    <TextView
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Generated Output / Blueprints:"
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
            android:text="Ready for prompt..."
            android:textColor="#00FF00"
            android:fontFamily="monospace"
            android:textSize="14sp" />
    </ScrollView>

</LinearLayout>
""")

    # 7. MainActivity.kt (Logic to handle prompt-to-PCB generation simulation)
    write_file("app/src/main/java/com/example/pcbgenerator/MainActivity.kt", """
package com.example.pcbgenerator

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

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
                tvOutput.text = "Error: Please enter a prompt or blueprint description."
                return@setOnClickListener
            }

            // Simulated AI PCB Generation Logic (Netlist & Routing layout specs)
            val resultLog = StringBuilder()
            resultLog.append("Analyzing prompt: \\\"$promptText\\\"...\\n")
            resultLog.append("[1/3] Parsing electronic components... OK\\n")
            resultLog.append("[2/3] Generating Netlist & Schematic routing... OK\\n")
            resultLog.append("[3/3] Exporting Gerber layout blueprint...\\n\\n")
            resultLog.append("--- GENERATED CIRCUIT SPEC ---\\n")
            resultLog.append("Components detected: Microcontroller, Resistors, Capacitors\\n")
            resultLog.append("Estimated PCB Size: 50mm x 40mm (Double Layer)\\n")
            resultLog.append("Status: Ready to export to KiCad / EasyEDA format.")

            tvOutput.text = resultLog.toString()
        }
    }
}
""")

    # 8. Gradle Wrapper Properties (needed for build)
    write_file("gradle/wrapper/gradle-wrapper.properties", """
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-8.4-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
""")

    # 9. GitHub Actions Workflow File (.github/workflows/build_apk.yml)
    write_file(".github/workflows/build_apk.yml", """
name: Build PCB AI App APK

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build-apk:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout Repository
      uses: actions/checkout@v4

    - name: Set up JDK 17
      uses: actions/setup-java@v4
      with:
        distribution: 'temurin'
        java-version: '17'
        cache: 'gradle'

    - name: Download Gradle Wrapper (if missing)
      run: gradle wrapper --gradle-version 8.4

    - name: Grant execute permission for Gradle wrapper
      run: chmod +x gradlew || true

    - name: Build Debug APK
      run: ./gradlew assembleDebug

    - name: Upload APK Artifact
      uses: actions/upload-artifact@v4
      with:
        name: pcb-generator-debug-apk
        path: app/build/outputs/apk/debug/app-debug.apk
""")

    print("\n[SUCCESS] Entire Android App and GitHub Actions workflow generated successfully!")

if __name__ == "__main__":
    generate_pcb_app()
