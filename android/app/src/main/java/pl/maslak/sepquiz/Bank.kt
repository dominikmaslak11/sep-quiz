package pl.maslak.sepquiz

import android.content.Context
import org.json.JSONObject

/** Jedno pytanie z banku. */
data class Pytanie(
    val id: String,
    val dzial: String,
    val zakres: List<String>,
    val tresc: String,
    val odpowiedzi: List<String>,
    val poprawna: Int,
    val wyjasnienie: String,
    val podstawa: String
)

/**
 * Bank pytan wczytywany raz z assets/pytania.json.
 * Ten sam plik, ktorego uzywa wersja pythonowa — jedno zrodlo prawdy.
 */
object Bank {
    lateinit var pytania: List<Pytanie>; private set
    lateinit var dzialy: Map<String, String>; private set
    lateinit var zrodla: Map<String, String>; private set
    private var wczytany = false

    fun wczytaj(ctx: Context) {
        if (wczytany) return
        val json = ctx.assets.open("pytania.json").bufferedReader().use { it.readText() }
        val root = JSONObject(json)

        dzialy = root.getJSONObject("dzialy").let { o ->
            o.keys().asSequence().associateWith { k -> o.getString(k) }
        }
        zrodla = root.getJSONObject("zrodla").let { o ->
            o.keys().asSequence().associateWith { k -> o.getString(k) }
        }

        val tab = root.getJSONArray("pytania")
        pytania = (0 until tab.length()).map { i ->
            val p = tab.getJSONObject(i)
            val odp = p.getJSONArray("odpowiedzi").let { a -> (0 until a.length()).map { a.getString(it) } }
            val zak = p.getJSONArray("zakres").let { a -> (0 until a.length()).map { a.getString(it) } }
            Pytanie(
                id = p.getString("id"),
                dzial = p.getString("dzial"),
                zakres = zak,
                tresc = p.getString("pytanie"),
                odpowiedzi = odp,
                poprawna = p.getInt("poprawna"),
                wyjasnienie = p.getString("wyjasnienie"),
                podstawa = p.getString("podstawa")
            )
        }
        wczytany = true
    }

    /** Kolejnosc dzialow taka jak w programie egzaminu, nie alfabetyczna. */
    val kolejnoscDzialow = listOf("I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X")

    fun filtruj(zakres: String?, dzial: String?): List<Pytanie> =
        pytania.filter { (zakres == null || zakres in it.zakres) && (dzial == null || it.dzial == dzial) }
}
