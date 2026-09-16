package pl.maslak.sepquiz

import android.os.Bundle
import android.util.TypedValue
import android.view.Gravity
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat

class QuizActivity : AppCompatActivity() {

    private lateinit var tryb: String
    private lateinit var pytania: List<Pytanie>
    private lateinit var postepy: Postepy

    private var nr = 0
    private val odpowiedzi = mutableMapOf<String, Int>()   // id pytania -> wybrany indeks
    private var odpowiedziano = false

    private val LITERY = listOf("A", "B", "C", "D")
    private val PROG = 75

    private lateinit var boxOdp: LinearLayout
    private lateinit var boxWyj: LinearLayout
    private lateinit var btnDalej: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_quiz)
        Bank.wczytaj(this)
        postepy = Postepy(this)

        tryb = intent.getStringExtra("tryb") ?: "nauka"
        val zakres = intent.getStringExtra("zakres")
        val dzial = intent.getStringExtra("dzial")
        val ile = intent.getIntExtra("ile", 0)

        var pula = Bank.filtruj(zakres, dzial)
        if (tryb == "bledy") {
            val bledne = postepy.bledne()
            pula = pula.filter { it.id in bledne }
        }
        pula = pula.shuffled()
        if (ile > 0 && ile < pula.size) pula = pula.take(ile)
        pytania = pula

        title = when (tryb) {
            "egzamin" -> "Egzamin próbny"
            "bledy" -> "Powtórka błędów"
            else -> "Tryb nauki"
        }
        supportActionBar?.setDisplayHomeAsUpEnabled(true)

        boxOdp = findViewById(R.id.boxOdpowiedzi)
        boxWyj = findViewById(R.id.boxWyjasnienie)
        btnDalej = findViewById(R.id.btnDalej)
        btnDalej.setOnClickListener { dalej() }

        if (pytania.isEmpty()) { pokazWynik(); return }
        pokazPytanie()
    }

    override fun onSupportNavigateUp(): Boolean { finish(); return true }

    private fun pokazPytanie() {
        val p = pytania[nr]
        odpowiedziano = false

        findViewById<TextView>(R.id.txtPostep).text =
            "Pytanie ${nr + 1} z ${pytania.size}"
        findViewById<ProgressBar>(R.id.pasek).apply {
            max = pytania.size; progress = nr
        }
        findViewById<TextView>(R.id.txtMeta).text =
            "dział ${p.dzial} · ${Bank.dzialy[p.dzial]} · ${p.zakres.joinToString("/")}"
        findViewById<TextView>(R.id.txtPytanie).text = p.tresc

        boxWyj.visibility = View.GONE
        btnDalej.visibility = View.GONE
        findViewById<ScrollView>(R.id.scroll).scrollTo(0, 0)

        boxOdp.removeAllViews()
        p.odpowiedzi.forEachIndexed { i, tresc ->
            val b = Button(this).apply {
                text = "${LITERY[i]})  $tresc"
                gravity = Gravity.START or Gravity.CENTER_VERTICAL
                isAllCaps = false
                setTextSize(TypedValue.COMPLEX_UNIT_SP, 15f)
                setTextColor(ContextCompat.getColor(this@QuizActivity, R.color.tekst))
                setBackgroundResource(R.drawable.tlo_odpowiedzi)
                setPadding(28, 26, 28, 26)
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
                ).apply { topMargin = 14 }
                setOnClickListener { wybierz(i) }
            }
            boxOdp.addView(b)
        }
    }

    private fun wybierz(wybor: Int) {
        if (odpowiedziano) return
        odpowiedziano = true
        val p = pytania[nr]
        val dobrze = wybor == p.poprawna
        odpowiedzi[p.id] = wybor
        postepy.zapiszWynik(p.id, dobrze)

        for (i in 0 until boxOdp.childCount) boxOdp.getChildAt(i).isEnabled = false

        if (tryb == "egzamin") {
            // W egzaminie nie zdradzamy poprawnej — tylko zaznaczamy wybor.
            (boxOdp.getChildAt(wybor) as Button).setBackgroundResource(R.drawable.tlo_odpowiedzi_ok)
        } else {
            (boxOdp.getChildAt(p.poprawna) as Button).setBackgroundResource(R.drawable.tlo_odpowiedzi_ok)
            if (!dobrze) (boxOdp.getChildAt(wybor) as Button)
                .setBackgroundResource(R.drawable.tlo_odpowiedzi_zle)

            findViewById<TextView>(R.id.txtWerdykt).apply {
                text = if (dobrze) "✓ Dobrze" else "✗ Źle"
                setTextColor(ContextCompat.getColor(this@QuizActivity,
                    if (dobrze) R.color.ok else R.color.zle))
            }
            findViewById<TextView>(R.id.txtWyjasnienie).text = p.wyjasnienie
            findViewById<TextView>(R.id.txtPodstawa).text =
                "Podstawa: " + (Bank.zrodla[p.podstawa] ?: p.podstawa)
            boxWyj.visibility = View.VISIBLE
        }

        btnDalej.text = if (nr == pytania.size - 1) "ZAKOŃCZ I POKAŻ WYNIK" else "DALEJ"
        btnDalej.visibility = View.VISIBLE
    }

    private fun dalej() {
        if (nr < pytania.size - 1) { nr++; pokazPytanie() } else pokazWynik()
    }

    private fun pokazWynik() {
        boxOdp.removeAllViews()
        boxWyj.visibility = View.GONE
        btnDalej.visibility = View.GONE
        findViewById<TextView>(R.id.txtMeta).text = ""
        findViewById<ProgressBar>(R.id.pasek).progress = pytania.size

        if (pytania.isEmpty()) {
            findViewById<TextView>(R.id.txtPostep).text = "Brak pytań"
            findViewById<TextView>(R.id.txtPytanie).text =
                "Nie ma błędów do powtórki — rozwiąż najpierw kilka pytań w trybie nauki."
            return
        }

        val dobre = pytania.count { odpowiedzi[it.id] == it.poprawna }
        val proc = dobre * 100 / pytania.size
        findViewById<TextView>(R.id.txtPostep).text = "Koniec"
        findViewById<TextView>(R.id.txtPytanie).apply {
            text = "Wynik: $dobre / ${pytania.size}  ($proc%)"
            setTextColor(ContextCompat.getColor(this@QuizActivity,
                if (proc >= PROG) R.color.ok else R.color.zle))
        }

        val sb = StringBuilder()
        sb.append(if (proc >= PROG) "Powyżej progu $PROG%. Tak trzymaj.\n"
                  else "Poniżej progu $PROG%.\n")

        val zle = pytania.filter { odpowiedzi[it.id] != it.poprawna }
        if (zle.isNotEmpty()) {
            val wgDzialu = zle.groupingBy { it.dzial }.eachCount()
                .toList().sortedByDescending { it.second }
            sb.append("\nBŁĘDY WEDŁUG DZIAŁU\n")
            wgDzialu.forEach { (d, n) -> sb.append("  $d · ${Bank.dzialy[d]}: $n\n") }

            sb.append("\nOMÓWIENIE BŁĘDÓW\n")
            zle.forEach { p ->
                val w = odpowiedzi[p.id]
                sb.append("\n").append(p.id).append(" · dział ").append(p.dzial).append("\n")
                sb.append(p.tresc).append("\n")
                if (w != null) sb.append("  Twoja: ").append(LITERY[w]).append(") ")
                    .append(p.odpowiedzi[w]).append("\n")
                sb.append("  Poprawna: ").append(LITERY[p.poprawna]).append(") ")
                    .append(p.odpowiedzi[p.poprawna]).append("\n")
                sb.append("  ").append(p.wyjasnienie).append("\n")
            }
        } else {
            sb.append("\nKomplet poprawnych odpowiedzi.\n")
        }

        findViewById<TextView>(R.id.txtWynik).apply {
            text = sb.toString()
            visibility = View.VISIBLE
        }
        btnDalej.apply {
            text = "WRÓĆ DO MENU"
            visibility = View.VISIBLE
            setOnClickListener { finish() }
        }
    }
}
