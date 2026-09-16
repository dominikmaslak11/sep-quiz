plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "pl.maslak.sepquiz"
    compileSdk = 34

    defaultConfig {
        applicationId = "pl.maslak.sepquiz"
        // minSdk 24 — telefon docelowy to Samsung M21 z Androidem 12 (API 31).
        // NIE podnosic powyzej 31 bez sprawdzenia, na czym aplikacja ma dzialac.
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            signingConfig = signingConfigs.getByName("debug")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
}

dependencies {
    implementation("androidx.appcompat:appcompat:1.6.1")
}
