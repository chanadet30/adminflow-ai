export default function Landing() {
  return (
    <div className="min-h-screen bg-white flex flex-col">

      {/* HERO */}
      <section className="flex flex-col items-center justify-center text-center px-6 py-24">
        <h1 className="text-5xl font-bold mb-6">
          AdminFlow
        </h1>

        <p className="text-xl text-gray-600 mb-8 max-w-2xl">
          Automatise tes emails et factures avec l’IA. Gagne des heures chaque semaine.
        </p>

        <a
          href="/dashboard"
          className="bg-indigo-600 text-white px-8 py-4 rounded-xl text-lg shadow hover:scale-105 transition"
        >
          Essayer gratuitement
        </a>
      </section>

      {/* FEATURES */}
      <section className="grid md:grid-cols-3 gap-8 px-10 py-20 bg-gray-50">
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <h3 className="font-semibold mb-2">📧 Emails intelligents</h3>
          <p className="text-gray-600">
            Analyse automatique et réponses prêtes à envoyer.
          </p>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm">
          <h3 className="font-semibold mb-2">📄 Factures automatiques</h3>
          <p className="text-gray-600">
            Extraction des données et organisation instantanée.
          </p>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm">
          <h3 className="font-semibold mb-2">⚡ Gain de temps</h3>
          <p className="text-gray-600">
            Automatise tes tâches administratives en un clic.
          </p>
        </div>
      </section>

      {/* PRICING */}
      <section className="py-20 text-center">
        <h2 className="text-3xl font-bold mb-10">
          Tarification simple
        </h2>

        <div className="flex flex-col md:flex-row justify-center gap-6">

          {/* FREE */}
          <div className="border p-8 rounded-xl w-80">
            <h3 className="text-xl font-semibold mb-4">Gratuit</h3>
            <p className="mb-4">Essai limité</p>
            <p className="text-3xl font-bold mb-6">0€</p>
          </div>

          {/* PREMIUM */}
          <div className="border-2 border-indigo-600 p-8 rounded-xl w-80">
            <h3 className="text-xl font-semibold mb-4">Premium</h3>
            <p className="mb-4">Accès complet</p>
            <p className="text-3xl font-bold mb-6">9€/mois</p>

            <a
              href="/dashboard"
              className="bg-indigo-600 text-white px-6 py-3 rounded-lg"
            >
              Commencer
            </a>
          </div>

        </div>
      </section>

    </div>
  );
}