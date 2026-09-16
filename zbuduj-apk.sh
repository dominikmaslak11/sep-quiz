#!/usr/bin/env bash
# Buduje APK od zera. Wymaga Android SDK i JDK 21.
set -euo pipefail
cd "$(dirname "$0")"

export JAVA_HOME=${JAVA_HOME:-/usr/lib/jvm/java-21-openjdk-amd64}
export ANDROID_HOME=${ANDROID_HOME:-$HOME/Android/Sdk}

# pytania.json jest jednym zrodlem prawdy — przed kazdym budowaniem odswiez kopie w assets
python3 pytania.py
cp pytania.json android/app/src/main/assets/pytania.json

echo "sdk.dir=$ANDROID_HOME" > android/local.properties

# AGP 8.5.2 wymaga Gradle 8.9. Systemowy /usr/bin/gradle to 4.4.1 i nie czyta
# settings.gradle.kts, a 9.3.1 jest za nowy — dlatego szukamy konkretnie 8.9.
GRADLE=$(find "$HOME/.gradle/wrapper/dists" -path '*gradle-8.9/bin/gradle' -type f 2>/dev/null | head -1)
[ -x "$GRADLE" ] || { echo "Nie znalazlem gradle 8.9."; exit 1; }

(cd android && "$GRADLE" assembleDebug --console=plain)

cp android/app/build/outputs/apk/debug/app-debug.apk SEP-Quiz-G1-v1.0.apk
echo
echo "Gotowe: $(pwd)/SEP-Quiz-G1-v1.0.apk"
echo "Instalacja przez USB:  adb install -r SEP-Quiz-G1-v1.0.apk"
