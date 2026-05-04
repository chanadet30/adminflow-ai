"use client";

export default function Home() {
  return (
    <div className="min-h-screen bg-white">

      {/* HERO */}
      <section className="text-center py-20 px-6">
        <h1 className="text-5xl font-bold mb-6">
          Gagne du temps sur tes emails
        </h1>

        <p className="text-gray-600 mb-8 text-lg">
          Analyse automatiquement tes emails et obtiens une réponse claire en quelques secondes.
        </p>

        <a
          href="/dashboard"
          className="bg-indigo-600 text-white px-6 py-3 rounded text-lg hover:bg-indigo-700"
        >
          🚀 Commencer gratuitement
        </a>
      </section>

      {/* FEATURES */}
      <section className="grid md:grid-cols-3 gap-8 px-10 py-20 bg-gray-50">

        <div>
          <h3 className="font-bold text-lg mb-2">⚡ Rapide</h3>
          <p className="text-gray-600">
            Analyse instantanée de tes emails
          </p>
        </div>

        <div>
          <h3 className="font-bold text-lg mb-2">🤖 Intelligent</h3>
          <p className="text-gray-600">
            Résumés clairs et exploitables
          </p>
        </div>

        <div>
          <h3 className="font-bold text-lg mb-2">💎 Premium</h3>
          <p className="text-gray-600">
            Analyses illimitées pour aller plus loin
          </p>
        </div>

      </section>

      {/* PRICING */}
      <section className="text-center py-20">

        <h2 className="text-3xl font-bold mb-10">
          Simple et transparent
        </h2>

        <div className="flex justify-center gap-10">

          <div className="border p-6 rounded w-60">
            <h3 className="font-bold mb-2">Gratuit</h3>
            <p className="text-2xl mb-4">0€</p>
            <p className="text-gray-600 mb-4">
              3 analyses
            </p>
            <a href="/dashboard" className="text-indigo-600">
              Commencer
            </a>
          </div>

          <div className="border p-6 rounded w-60 bg-indigo-50">
            <h3 className="font-bold mb-2">Premium</h3>
            <p className="text-2xl mb-4">9€/mois</p>
            <p className="text-gray-600 mb-4">
              Illimité
            </p>
            <a
              href="/dashboard"
              className="bg-indigo-600 text-white px-4 py-2 rounded"
            >
              Passer Premium
            </a>
          </div>

        </div>

      </section>

    </div>
  );
}