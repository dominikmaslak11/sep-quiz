package pl.maslak.sepquiz

import android.app.AlertDialog
import android.content.Intent
import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private val zakresyKlucze = listOf<String?>(null, "D", "E")
    private lateinit var dzialyKlucze: List<String?>
    private val ileOpcje = listOf(10, 20, 25, 30, 0)   // 0 = wszystkie

    private lateinit var spZakres: Spinner
    private lateinit var spDzial: Spinner
    private lateinit var spIle: Spinner
    private lateinit var txtPula: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        Bank.wczytaj(this)

        spZakres = findViewById(R.id.spZakres)
        spDzial = findViewById(R.id.spDzial)
        spIle = findViewById(R.id.spIle)
        txtPula = findViewById(R.id.txtPula)

        spZakres.adapter = adapter(listOf(
            "Wszystkie pytania",
            "Tylko dozór (D)",
            "Tylko eksploatacja (E)"
        ))

        dzialyKlucze = listOf<String?>(null) + Bank.kolejnoscDzialow.filter { Bank.dzialy.containsKey(it) }
        spDzial.adapter = adapter(dzialyKlucze.map { k ->
            if (k == null) "Wszystkie działy" else "$k · ${Bank.dzialy[k]}"
        })

        spIle.adapter = adapter(ileOpcje.map { if (it == 0) "Wszystkie" else "$it pytań" })
        spIle.setSelection(2)

        val odswiez = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(p: AdapterView<*>?, v: android.view.View?, i: Int, id: Long) = pokazPule()
            override fun onNothingSelected(p: AdapterView<*>?) {}
        }
        spZakres.onItemSelectedListener = odswiez
        spDzial.onItemSelectedListener = odswiez

        findViewById<Button>(R.id.btnNauka).setOnClickListener { start("nauka") }
        findViewById<Button>(R.id.btnEgzamin).setOnClickListener { start("egzamin") }
        findViewById<Button>(R.id.btnBledy).setOnClickListener { start("bledy") }
        findViewById<Button>(R.id.btnReset).setOnClickListener { potwierdzReset() }
    }

    override fun onResume() {
        super.onResume()
        pokazPule()
        val (unikalne, dobrze, razem) = Postepy(this).statystyki()
        findViewById<TextView>(R.id.txtPodsumowanie).text =
            if (razem == 0) "${Bank.pytania.size} pytań w banku. Jeszcze nic nie rozwiązane."
            else "${Bank.pytania.size} pytań w banku · przerobione $unikalne · " +
                 "skuteczność ${dobrze * 100 / razem}% ($dobrze/$razem)"
    }

    private fun adapter(pozycje: List<String>) =
        ArrayAdapter(this, android.R.layout.simple_spinner_item, pozycje).apply {
            setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        }

    private fun wybranyZakres() = zakresyKlucze[spZakres.selectedItemPosition]
    private fun wybranyDzial() = dzialyKlucze[spDzial.selectedItemPosition]

    private fun pokazPule() {
        val n = Bank.filtruj(wybranyZakres(), wybranyDzial()).size
        val bledne = Postepy(this).bledne().size
        txtPula.text = "Pasujących pytań: $n" + if (bledne > 0) "   ·   do powtórki: $bledne" else ""
        findViewById<Button>(R.id.btnBledy).isEnabled = bledne > 0
    }

    private fun start(tryb: String) {
        val pula = Bank.filtruj(wybranyZakres(), wybranyDzial())
        if (pula.isEmpty()) {
            Toast.makeText(this, "Żadne pytanie nie pasuje do filtrów.", Toast.LENGTH_SHORT).show()
            return
        }
        startActivity(Intent(this, QuizActivity::class.java).apply {
            putExtra("tryb", tryb)
            putExtra("zakres", wybranyZakres())
            putExtra("dzial", wybranyDzial())
            putExtra("ile", ileOpcje[spIle.selectedItemPosition])
        })
    }

    private fun potwierdzReset() {
        AlertDialog.Builder(this)
            .setTitle("Wyczyścić postępy?")
            .setMessage("Skasuje to historię odpowiedzi i listę błędów do powtórki. Pytań to nie usuwa.")
            .setPositiveButton("Wyczyść") { _, _ ->
                Postepy(this).wyczysc()
                onResume()
                Toast.makeText(this, "Postępy wyczyszczone.", Toast.LENGTH_SHORT).show()
            }
            .setNegativeButton("Anuluj", null)
            .show()
    }
}
