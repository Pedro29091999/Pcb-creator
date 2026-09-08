import os

def write_file(path, content):
    dirname = os.path.dirname(path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"[CREATED] {path}")

def generate_pcb_app():
    print("Initializing Prompt-to-PCB Android App project structure...")

    # 1. Root build.gradle
    write_file("build.gradle", """
plugins {
    id 'com.android.application' version '8.1.4' apply false
    id 'org.jetbrains.kotlin.android' version '1.9.0' apply false
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

    # 3. gradle.properties
    write_file("gradle.properties", """
android.useAndroidX=true
android.enableJetifier=true
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
""")

    # 4. app/build.gradle (Removed redundant org.json dependency)
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
    implementation 'com.squareup.okhttp3:okhttp:4.11.0'
}
""")

    # 5. AndroidManifest.xml
    write_file("app/src/main/AndroidManifest.xml", """
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />
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

    # 6. Strings resource
    write_file("app/src/main/res/values/strings.xml", """
<resources>
    <string name="app_name">PCB Generator AI</string>
</resources>
""")

    # 7. Layout XML
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
        android:layout_marginBottom="12dp" />

    <EditText
        android:id="@+id/etApiKey"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Enter Gemini API Key..."
        android:inputType="textPassword"
        android:textSize="14sp"
        android:padding="8dp"
        android:layout_marginBottom="8dp" />

    <EditText
        android:id="@+id/etPrompt"
        android:layout_width="match_parent"
        android:layout_height="100dp"
        android:hint="Enter circuit blueprint prompt (e.g., 'Design a 5V regulated power supply')..."
        android:gravity="top|start"
        android:inputType="textMultiLine"
        android:background="@android:drawable/edit_text"
        android:padding="8dp"
        android:layout_marginBottom="12dp" />

    <Button
        android:id="@+id/btnGenerate"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Generate &amp; Export Real PCB File"
        android:layout_marginBottom="12dp" />

    <TextView
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Generation &amp; File Output Log:"
        android:textStyle="bold"
        android:layout_marginBottom="4dp" />

    <ScrollView
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:background="#1E1E1E"
        android:padding="8dp">

        <TextView
            android:id="@+id/tvOutput"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="Ready for API key and prompt..."
            android:textColor="#00FF00"
            android:fontFamily="monospace"
            android:textSize="13sp" />
    </ScrollView>

</LinearLayout>
""")

    # 8. MainActivity.kt
    write_file("app/src/main/java/com/example/pcbgenerator/MainActivity.kt", """
package com.example.pcbgenerator

import android.os.Bundle
import android.os.Environment
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.io.IOException

class MainActivity : AppCompatActivity() {

    private val client = OkHttpClient()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val etApiKey = findViewById<EditText>(R.id.etApiKey)
        val etPrompt = findViewById<EditText>(R.id.etPrompt)
        val btnGenerate = findViewById<Button>(R.id.btnGenerate)
        val tvOutput = findViewById<TextView>(R.id.tvOutput)

        btnGenerate.setOnClickListener {
            val apiKey = etApiKey.text.toString().trim()
            val promptText = etPrompt.text.toString().trim()

            if (apiKey.isEmpty() || promptText.isEmpty()) {
                tvOutput.text = "Error: Please provide both an API Key and a circuit prompt."
                return@setOnClickListener
            }

            tvOutput.text = "Sending blueprint request to Gemini API..."
            callGeminiApi(apiKey, promptText, tvOutput)
        }
    }

    private fun callGeminiApi(apiKey: String, userPrompt: String, tvOutput: TextView) {
        val url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$apiKey"
        
        val systemInstruction = "You are an expert electronics and PCB design system. Given a user prompt, generate a formal technical netlist, component layout breakdown, and a mock KiCad schematic file script block."
        
        val jsonBody = JSONObject().apply {
            put("contents", JSONArray().put(
                JSONObject().put("parts", JSONArray().put(
                    JSONObject().put("text", "$systemInstruction\\n\\nUser Request: $userPrompt")
                ))
            ))
        }

        val body = jsonBody.toString().toRequestBody("application/json; charset=utf-8".toMediaType())
        val request = Request.Builder().url(url).post(body).build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                runOnUiThread {
                    tvOutput.text = "Network Error: ${e.message}"
                }
            }

            override fun onResponse(call: Call, response: Response) {
                val responseBody = response.body?.string()
                if (!response.isSuccessful || responseBody == null) {
                    runOnUiThread {
                        tvOutput.text = "API Error: ${response.code} - ${response.message}"
                    }
                    return
                }

                try {
                    val jsonResponse = JSONObject(responseBody)
                    val candidates = jsonResponse.getJSONArray("candidates")
                    val contentObj = candidates.getJSONObject(0).getJSONObject("content")
                    val partsArr = contentObj.getJSONArray("parts")
                    val generatedText = partsArr.getJSONObject(0).getString("text")

                    val filename = "PCB_Blueprint_" + System.currentTimeMillis() + ".kicad_pcb"
                    val savedFile = saveFileToDownloads(filename, generatedText)

                    runOnUiThread {
                        if (savedFile != null) {
                            tvOutput.text = "SUCCESS! File exported and saved:\\n" +
                                    "${savedFile.absolutePath}\\n\\n--- MODEL RESPONSE ---\\n$generatedText"
                        } else {
                            tvOutput.text = "Received response, but failed to save file to local storage."
                        }
                    }
                } catch (e: Exception) {
                    runOnUiThread {
                        tvOutput.text = "Parsing Exception: ${e.message}\\nRaw: $responseBody"
                    }
                }
            }
        })
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

    print("\n[SUCCESS] Android App structure generated successfully!")

if __name__ == "__main__":
    generate_pcb_app()
