import java.util.Properties

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

// Dane do podpisu wydania leza w android/klucz.properties — plik POZA repozytorium.
// Bez niego build release podpisze sie kluczem debugowym (tylko do testow lokalnych).
val klucz = Properties().apply {
    val f = rootProject.file("klucz.properties")
    if (f.exists()) f.inputStream().use { load(it) }
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
        versionCode = 3
        versionName = "1.2"
    }

    signingConfigs {
        create("wydanie") {
            if (klucz.getProperty("storeFile") != null) {
                storeFile = file(klucz.getProperty("storeFile"))
                storePassword = klucz.getProperty("storePassword")
                keyAlias = klucz.getProperty("keyAlias")
                keyPassword = klucz.getProperty("keyPassword")
            }
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            signingConfig = if (klucz.getProperty("storeFile") != null)
                signingConfigs.getByName("wydanie") else signingConfigs.getByName("debug")
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
