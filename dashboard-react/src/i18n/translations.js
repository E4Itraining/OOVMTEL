// Synapsix Dashboard - Multilingual translations (FR/EN/NL)

export const LANGUAGES = {
  FR: 'fr',
  EN: 'en',
  NL: 'nl'
}

export const LANGUAGE_LABELS = {
  [LANGUAGES.FR]: 'Français',
  [LANGUAGES.EN]: 'English',
  [LANGUAGES.NL]: 'Nederlands'
}

export const translations = {
  // ===========================================
  // FRENCH (FR)
  // ===========================================
  [LANGUAGES.FR]: {
    // App branding
    app: {
      name: 'Synapsix',
      tagline: 'Observabilité Industrielle',
      description: 'Dashboard unifié d\'observabilité industrielle'
    },

    // Common actions
    common: {
      back: 'Retour',
      refresh: 'Rafraîchir',
      save: 'Enregistrer',
      cancel: 'Annuler',
      close: 'Fermer',
      search: 'Rechercher',
      filter: 'Filtrer',
      export: 'Exporter',
      settings: 'Paramètres',
      notifications: 'Notifications',
      loading: 'Chargement...',
      error: 'Erreur',
      success: 'Succès',
      warning: 'Attention',
      info: 'Information',
      viewAll: 'Voir tout',
      viewMore: 'Voir plus',
      viewLess: 'Voir moins'
    },

    // Connection status
    connection: {
      realtime: 'Temps réel',
      offline: 'Hors ligne',
      connected: 'Connecté',
      disconnected: 'Déconnecté',
      reconnecting: 'Reconnexion...'
    },

    // User modes/profiles
    profiles: {
      title: 'Parcours Utilisateur',
      business: {
        name: 'Business',
        label: 'Parcours Business',
        description: 'Vue métier et indicateurs de production'
      },
      tech: {
        name: 'Tech',
        label: 'Parcours Technique',
        description: 'Vue technique et métriques système'
      },
      modeLabel: {
        business: 'Mode Business',
        tech: 'Mode Tech'
      }
    },

    // Navigation - Main menu
    nav: {
      main: {
        home: 'Accueil',
        globalView: 'Vue Globale',
        grafana: 'Grafana',
        opensearch: 'OpenSearch',
        kafka: 'Kafka'
      },
      // Home page submenus
      home: {
        title: 'Tableau de bord',
        overview: 'Vue d\'ensemble',
        quickStats: 'Statistiques rapides',
        recentActivity: 'Activité récente',
        favorites: 'Favoris'
      },
      // Business profile menu items
      business: {
        title: 'Menu Business',
        production: 'Production',
        quality: 'Qualité',
        performance: 'Performance',
        equipment: 'Équipements',
        alarms: 'Alarmes',
        reports: 'Rapports',
        kpis: 'KPIs',
        trends: 'Tendances',
        analytics: 'Analytique'
      },
      // Tech profile menu items
      tech: {
        title: 'Menu Technique',
        metrics: 'Métriques',
        logs: 'Logs',
        traces: 'Traces',
        infrastructure: 'Infrastructure',
        services: 'Services',
        databases: 'Bases de données',
        monitoring: 'Monitoring',
        alerts: 'Alertes',
        performance: 'Performance'
      }
    },

    // Business metrics
    metrics: {
      business: {
        oee: 'OEE Global',
        oeeDescription: 'Efficacité globale des équipements',
        availability: 'Disponibilité',
        performance: 'Performance',
        quality: 'Qualité',
        qualityRate: 'Taux Qualité',
        productionToday: 'Production Jour',
        cycleTime: 'Temps Cycle',
        defectsToday: 'Défauts Jour',
        criticalAlarms: 'Alarmes Critiques',
        equipmentStatus: 'Statut Équipements',
        productionByProduct: 'Production par Produit',
        oeeTrend: 'Tendance OEE (24h)',
        running: 'En marche',
        stopped: 'Arrêt',
        maintenance: 'Maintenance',
        error: 'Erreur'
      },
      tech: {
        metricsRate: 'Métriques/s',
        logsRate: 'Logs/s',
        tracesRate: 'Traces/s',
        latencyP95: 'Latence P95',
        errorRate: 'Taux d\'erreur',
        kafkaThroughput: 'Débit Kafka',
        cpu: 'CPU',
        memory: 'Mémoire',
        disk: 'Disque',
        activeSeries: 'Séries actives',
        storage: 'Stockage',
        queryLatency: 'Latence requêtes',
        documents: 'Documents',
        health: 'Santé',
        nodes: 'Nœuds',
        topics: 'Topics',
        partitions: 'Partitions',
        consumerLag: 'Lag consommateurs'
      }
    },

    // Service pages
    services: {
      grafana: {
        title: 'Grafana',
        description: 'Visualisation et dashboards',
        dashboards: 'Dashboards',
        explore: 'Explorer',
        alerting: 'Alerting'
      },
      opensearch: {
        title: 'OpenSearch',
        description: 'Recherche et analyse de logs',
        discover: 'Découvrir',
        indices: 'Index',
        queries: 'Requêtes'
      },
      kafka: {
        title: 'Kafka',
        description: 'Streaming de données',
        topics: 'Topics',
        consumers: 'Consommateurs',
        producers: 'Producteurs'
      },
      victoriametrics: {
        title: 'VictoriaMetrics',
        description: 'Stockage de métriques'
      }
    },

    // Time and date
    time: {
      lastUpdate: 'Dernière mise à jour',
      now: 'Maintenant',
      today: 'Aujourd\'hui',
      yesterday: 'Hier',
      thisWeek: 'Cette semaine',
      thisMonth: 'Ce mois',
      custom: 'Personnalisé'
    },

    // Errors and messages
    messages: {
      noData: 'Aucune donnée disponible',
      loadingError: 'Erreur de chargement',
      connectionLost: 'Connexion perdue',
      tryAgain: 'Réessayer'
    }
  },

  // ===========================================
  // ENGLISH (EN)
  // ===========================================
  [LANGUAGES.EN]: {
    // App branding
    app: {
      name: 'Synapsix',
      tagline: 'Industrial Observability',
      description: 'Unified industrial observability dashboard'
    },

    // Common actions
    common: {
      back: 'Back',
      refresh: 'Refresh',
      save: 'Save',
      cancel: 'Cancel',
      close: 'Close',
      search: 'Search',
      filter: 'Filter',
      export: 'Export',
      settings: 'Settings',
      notifications: 'Notifications',
      loading: 'Loading...',
      error: 'Error',
      success: 'Success',
      warning: 'Warning',
      info: 'Information',
      viewAll: 'View all',
      viewMore: 'View more',
      viewLess: 'View less'
    },

    // Connection status
    connection: {
      realtime: 'Real-time',
      offline: 'Offline',
      connected: 'Connected',
      disconnected: 'Disconnected',
      reconnecting: 'Reconnecting...'
    },

    // User modes/profiles
    profiles: {
      title: 'User Profile',
      business: {
        name: 'Business',
        label: 'Business Path',
        description: 'Business view and production indicators'
      },
      tech: {
        name: 'Tech',
        label: 'Technical Path',
        description: 'Technical view and system metrics'
      },
      modeLabel: {
        business: 'Business Mode',
        tech: 'Tech Mode'
      }
    },

    // Navigation - Main menu
    nav: {
      main: {
        home: 'Home',
        globalView: 'Global View',
        grafana: 'Grafana',
        opensearch: 'OpenSearch',
        kafka: 'Kafka'
      },
      // Home page submenus
      home: {
        title: 'Dashboard',
        overview: 'Overview',
        quickStats: 'Quick Stats',
        recentActivity: 'Recent Activity',
        favorites: 'Favorites'
      },
      // Business profile menu items
      business: {
        title: 'Business Menu',
        production: 'Production',
        quality: 'Quality',
        performance: 'Performance',
        equipment: 'Equipment',
        alarms: 'Alarms',
        reports: 'Reports',
        kpis: 'KPIs',
        trends: 'Trends',
        analytics: 'Analytics'
      },
      // Tech profile menu items
      tech: {
        title: 'Technical Menu',
        metrics: 'Metrics',
        logs: 'Logs',
        traces: 'Traces',
        infrastructure: 'Infrastructure',
        services: 'Services',
        databases: 'Databases',
        monitoring: 'Monitoring',
        alerts: 'Alerts',
        performance: 'Performance'
      }
    },

    // Business metrics
    metrics: {
      business: {
        oee: 'Overall OEE',
        oeeDescription: 'Overall Equipment Effectiveness',
        availability: 'Availability',
        performance: 'Performance',
        quality: 'Quality',
        qualityRate: 'Quality Rate',
        productionToday: 'Today\'s Production',
        cycleTime: 'Cycle Time',
        defectsToday: 'Today\'s Defects',
        criticalAlarms: 'Critical Alarms',
        equipmentStatus: 'Equipment Status',
        productionByProduct: 'Production by Product',
        oeeTrend: 'OEE Trend (24h)',
        running: 'Running',
        stopped: 'Stopped',
        maintenance: 'Maintenance',
        error: 'Error'
      },
      tech: {
        metricsRate: 'Metrics/s',
        logsRate: 'Logs/s',
        tracesRate: 'Traces/s',
        latencyP95: 'Latency P95',
        errorRate: 'Error Rate',
        kafkaThroughput: 'Kafka Throughput',
        cpu: 'CPU',
        memory: 'Memory',
        disk: 'Disk',
        activeSeries: 'Active Series',
        storage: 'Storage',
        queryLatency: 'Query Latency',
        documents: 'Documents',
        health: 'Health',
        nodes: 'Nodes',
        topics: 'Topics',
        partitions: 'Partitions',
        consumerLag: 'Consumer Lag'
      }
    },

    // Service pages
    services: {
      grafana: {
        title: 'Grafana',
        description: 'Visualization and dashboards',
        dashboards: 'Dashboards',
        explore: 'Explore',
        alerting: 'Alerting'
      },
      opensearch: {
        title: 'OpenSearch',
        description: 'Log search and analysis',
        discover: 'Discover',
        indices: 'Indices',
        queries: 'Queries'
      },
      kafka: {
        title: 'Kafka',
        description: 'Data streaming',
        topics: 'Topics',
        consumers: 'Consumers',
        producers: 'Producers'
      },
      victoriametrics: {
        title: 'VictoriaMetrics',
        description: 'Metrics storage'
      }
    },

    // Time and date
    time: {
      lastUpdate: 'Last update',
      now: 'Now',
      today: 'Today',
      yesterday: 'Yesterday',
      thisWeek: 'This week',
      thisMonth: 'This month',
      custom: 'Custom'
    },

    // Errors and messages
    messages: {
      noData: 'No data available',
      loadingError: 'Loading error',
      connectionLost: 'Connection lost',
      tryAgain: 'Try again'
    }
  },

  // ===========================================
  // DUTCH (NL)
  // ===========================================
  [LANGUAGES.NL]: {
    // App branding
    app: {
      name: 'Synapsix',
      tagline: 'Industriële Observabiliteit',
      description: 'Uniforme industriële observability dashboard'
    },

    // Common actions
    common: {
      back: 'Terug',
      refresh: 'Vernieuwen',
      save: 'Opslaan',
      cancel: 'Annuleren',
      close: 'Sluiten',
      search: 'Zoeken',
      filter: 'Filteren',
      export: 'Exporteren',
      settings: 'Instellingen',
      notifications: 'Meldingen',
      loading: 'Laden...',
      error: 'Fout',
      success: 'Succes',
      warning: 'Waarschuwing',
      info: 'Informatie',
      viewAll: 'Alles bekijken',
      viewMore: 'Meer bekijken',
      viewLess: 'Minder bekijken'
    },

    // Connection status
    connection: {
      realtime: 'Real-time',
      offline: 'Offline',
      connected: 'Verbonden',
      disconnected: 'Verbinding verbroken',
      reconnecting: 'Opnieuw verbinden...'
    },

    // User modes/profiles
    profiles: {
      title: 'Gebruikersprofiel',
      business: {
        name: 'Business',
        label: 'Business Pad',
        description: 'Bedrijfsweergave en productie-indicatoren'
      },
      tech: {
        name: 'Tech',
        label: 'Technisch Pad',
        description: 'Technische weergave en systeemmetrieken'
      },
      modeLabel: {
        business: 'Business Modus',
        tech: 'Tech Modus'
      }
    },

    // Navigation - Main menu
    nav: {
      main: {
        home: 'Home',
        globalView: 'Globaal Overzicht',
        grafana: 'Grafana',
        opensearch: 'OpenSearch',
        kafka: 'Kafka'
      },
      // Home page submenus
      home: {
        title: 'Dashboard',
        overview: 'Overzicht',
        quickStats: 'Snelle Statistieken',
        recentActivity: 'Recente Activiteit',
        favorites: 'Favorieten'
      },
      // Business profile menu items
      business: {
        title: 'Business Menu',
        production: 'Productie',
        quality: 'Kwaliteit',
        performance: 'Prestatie',
        equipment: 'Apparatuur',
        alarms: 'Alarmen',
        reports: 'Rapporten',
        kpis: 'KPIs',
        trends: 'Trends',
        analytics: 'Analyses'
      },
      // Tech profile menu items
      tech: {
        title: 'Technisch Menu',
        metrics: 'Metrieken',
        logs: 'Logs',
        traces: 'Traces',
        infrastructure: 'Infrastructuur',
        services: 'Services',
        databases: 'Databases',
        monitoring: 'Monitoring',
        alerts: 'Alerts',
        performance: 'Prestatie'
      }
    },

    // Business metrics
    metrics: {
      business: {
        oee: 'Totale OEE',
        oeeDescription: 'Algehele Apparatuur Effectiviteit',
        availability: 'Beschikbaarheid',
        performance: 'Prestatie',
        quality: 'Kwaliteit',
        qualityRate: 'Kwaliteitspercentage',
        productionToday: 'Productie Vandaag',
        cycleTime: 'Cyclustijd',
        defectsToday: 'Defecten Vandaag',
        criticalAlarms: 'Kritieke Alarmen',
        equipmentStatus: 'Apparatuurstatus',
        productionByProduct: 'Productie per Product',
        oeeTrend: 'OEE Trend (24u)',
        running: 'Actief',
        stopped: 'Gestopt',
        maintenance: 'Onderhoud',
        error: 'Fout'
      },
      tech: {
        metricsRate: 'Metrieken/s',
        logsRate: 'Logs/s',
        tracesRate: 'Traces/s',
        latencyP95: 'Latentie P95',
        errorRate: 'Foutpercentage',
        kafkaThroughput: 'Kafka Doorvoer',
        cpu: 'CPU',
        memory: 'Geheugen',
        disk: 'Schijf',
        activeSeries: 'Actieve Series',
        storage: 'Opslag',
        queryLatency: 'Query Latentie',
        documents: 'Documenten',
        health: 'Gezondheid',
        nodes: 'Nodes',
        topics: 'Topics',
        partitions: 'Partities',
        consumerLag: 'Consumer Lag'
      }
    },

    // Service pages
    services: {
      grafana: {
        title: 'Grafana',
        description: 'Visualisatie en dashboards',
        dashboards: 'Dashboards',
        explore: 'Verkennen',
        alerting: 'Alerting'
      },
      opensearch: {
        title: 'OpenSearch',
        description: 'Log zoeken en analyse',
        discover: 'Ontdekken',
        indices: 'Indexen',
        queries: 'Queries'
      },
      kafka: {
        title: 'Kafka',
        description: 'Data streaming',
        topics: 'Topics',
        consumers: 'Consumers',
        producers: 'Producers'
      },
      victoriametrics: {
        title: 'VictoriaMetrics',
        description: 'Metriekenopslag'
      }
    },

    // Time and date
    time: {
      lastUpdate: 'Laatste update',
      now: 'Nu',
      today: 'Vandaag',
      yesterday: 'Gisteren',
      thisWeek: 'Deze week',
      thisMonth: 'Deze maand',
      custom: 'Aangepast'
    },

    // Errors and messages
    messages: {
      noData: 'Geen gegevens beschikbaar',
      loadingError: 'Laadfout',
      connectionLost: 'Verbinding verloren',
      tryAgain: 'Opnieuw proberen'
    }
  }
}

export default translations
