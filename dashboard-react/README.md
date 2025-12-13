# OOVMTEL Modern Dashboard

Interface moderne, responsive et interactive pour la plateforme d'observabilité industrielle OOVMTEL.

## Caractéristiques

### Deux Parcours Utilisateurs

**Mode Business (Non-Tech)**
- OEE (Overall Equipment Effectiveness) avec décomposition A×P×Q
- Production journalière et tendances
- Statut des équipements en temps réel
- Alertes critiques et KPIs industriels
- Visualisation intuitive avec jauges et graphiques

**Mode Tech**
- Métriques pipeline (metrics rate, logs rate, traces)
- Santé des services (VictoriaMetrics, OpenSearch, Kafka, OTEL)
- Utilisation des ressources (CPU, Memory, Disk)
- Latence et taux d'erreur
- Vue détaillée de chaque composant

### Navigation

- **Vue Globale**: Dashboard agrégé selon le mode utilisateur
- **Grafana**: Accès aux tableaux de bord Grafana
- **OpenSearch**: Analyse des logs et recherche
- **Kafka**: Monitoring du streaming de données

### Fonctionnalités

- Mise à jour temps réel (WebSocket + fallback polling)
- Design responsive (mobile, tablet, desktop)
- Thème sombre optimisé pour environnements industriels
- Drill-down du global vers le détail
- Animations fluides avec Framer Motion

## Installation

```bash
cd dashboard-react
npm install
```

## Développement

```bash
npm run dev
```

L'application sera disponible sur `http://localhost:3001`

## Build Production

```bash
npm run build
```

Les fichiers de production seront générés dans le dossier `dist/`

## Demo Standalone

Pour tester sans installation, ouvrez simplement `demo.html` dans un navigateur.
Cette version utilise React via CDN et ne nécessite aucune configuration.

## Structure du Projet

```
dashboard-react/
├── src/
│   ├── components/          # Composants réutilisables
│   │   ├── ui/
│   │   │   ├── Card.jsx     # Cartes et métriques
│   │   │   ├── Gauge.jsx    # Jauges circulaires
│   │   │   ├── Charts.jsx   # Graphiques Recharts
│   │   │   └── Status.jsx   # Badges et indicateurs
│   │   └── Layout.jsx       # Layout principal
│   ├── pages/
│   │   ├── GlobalView.jsx   # Vue principale
│   │   ├── GrafanaView.jsx  # Vue Grafana
│   │   ├── OpenSearchView.jsx
│   │   ├── KafkaView.jsx
│   │   └── DetailedView.jsx # Vue détaillée service
│   ├── context/
│   │   └── DashboardContext.jsx  # État global
│   ├── hooks/
│   │   └── useRealTimeData.js    # WebSocket/polling
│   ├── styles/
│   │   └── index.css        # Tailwind + custom
│   ├── App.jsx
│   └── main.jsx
├── demo.html                # Version standalone
├── package.json
├── vite.config.js
├── tailwind.config.js
└── README.md
```

## Technologies

- **React 18** - UI library
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations
- **Recharts** - Charts
- **Lucide React** - Icons
- **React Router** - Navigation

## Intégration Backend

Le dashboard se connecte à l'API FastAPI existante:

- `GET /api/metrics` - Métriques unifiées
- `GET /api/services` - Statut des services
- `GET /api/events` - Événements récents
- `WS /ws` - Updates temps réel

## Configuration

Variables d'environnement dans `vite.config.js`:

```js
server: {
  port: 3001,
  proxy: {
    '/api': 'http://localhost:8085',
    '/ws': { target: 'ws://localhost:8085', ws: true }
  }
}
```

## Screenshots

### Mode Business
- OEE Dashboard avec disponibilité, performance, qualité
- Grille d'équipements avec statuts
- Production par produit

### Mode Tech
- Service health overview
- Data pipeline throughput
- Resource utilization
