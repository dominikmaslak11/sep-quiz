package pl.maslak.sepquiz

import android.content.Context
import org.json.JSONObject

/**
 * Postepy trzymane w SharedPreferences jako JSON: { "I-01": {"razem":3,"dobrze":2}, ... }
 * Dzieki temu format jest czytelny i daje sie porownac z wersja pythonowa.
 */
class Postepy(ctx: Context) {
    private val prefs = ctx.getSharedPreferences("postepy", Context.MODE_PRIVATE)

    private fun dane(): JSONObject =
        JSONObject(prefs.getString("pytania", "{}") ?: "{}")

    fun zapiszWynik(id: String, dobrze: Boolean) {
        val d = dane()
        val w = if (d.has(id)) d.getJSONObject(id) else JSONObject().put("razem", 0).put("dobrze", 0)
        w.put("razem", w.getInt("razem") + 1)
        if (dobrze) w.put("dobrze", w.getInt("dobrze") + 1)
        d.put(id, w)
        prefs.edit().putString("pytania", d.toString()).apply()
    }

    /** Pytania, ktore choc raz poszly zle i nie zostaly jeszcze opanowane. */
    fun bledne(): Set<String> {
        val d = dane()
        return d.keys().asSequence()
            .filter { k -> d.getJSONObject(k).let { it.getInt("dobrze") < it.getInt("razem") } }
            .toSet()
    }

    fun statystyki(): Triple<Int, Int, Int> {
        val d = dane()
        var razem = 0; var dobrze = 0; var unikalne = 0
        d.keys().forEach { k ->
            val o = d.getJSONObject(k)
            razem += o.getInt("razem"); dobrze += o.getInt("dobrze"); unikalne++
        }
        return Triple(unikalne, dobrze, razem)
    }

    fun wyczysc() = prefs.edit().clear().apply()
}
