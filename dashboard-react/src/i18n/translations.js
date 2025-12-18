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
        kafka: 'Kafka',
        observability: 'Observabilité',
        security: 'Sécurité & Conformité'
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
    },

    // Observability & Remediation
    observability: {
      title: 'Observabilité & Remédiation',
      description: 'Surveillance des SLOs, gestion des incidents et automatisation de la remédiation',
      tabs: {
        overview: 'Vue d\'ensemble',
        incidents: 'Incidents',
        runbooks: 'Runbooks',
        history: 'Historique'
      },
      // Metrics
      sloCompliance: 'Conformité SLO',
      activeIncidents: 'Incidents Actifs',
      mttr: 'MTTR Moyen',
      mttd: 'MTTD Moyen',
      automationRate: 'Taux d\'Automatisation',
      // SLO
      sloStatus: 'Statut des SLOs',
      current: 'Actuel',
      target: 'Objectif',
      errorBudget: 'Budget d\'Erreur',
      remaining: 'restant',
      // Incidents
      allActiveIncidents: 'Tous les Incidents Actifs',
      noActiveIncidents: 'Aucun Incident Actif',
      allSystemsOperational: 'Tous les systèmes fonctionnent normalement',
      allSeverities: 'Toutes les sévérités',
      critical: 'Critique',
      warning: 'Avertissement',
      allServices: 'Tous les services',
      viewRunbook: 'Voir Runbook',
      remediationActions: 'Actions de Remédiation',
      runNextStep: 'Exécuter Suivant',
      pauseRemediation: 'Pause',
      escalate: 'Escalader',
      // Runbooks
      remediationRunbooks: 'Runbooks de Remédiation',
      createRunbook: 'Créer Runbook',
      executions: 'exécutions',
      avgMTTR: 'MTTR Moyen',
      triggers: 'Déclencheurs',
      steps: 'Étapes',
      automated: 'Automatisé',
      manual: 'Manuel',
      executeRunbook: 'Exécuter le Runbook',
      // History
      remediationHistory: 'Historique des Remédiations',
      last24h: 'Dernières 24h',
      last7d: '7 derniers jours',
      last30d: '30 derniers jours',
      runbook: 'Runbook',
      service: 'Service',
      trigger: 'Déclencheur',
      duration: 'Durée',
      status: 'Statut',
      progress: 'Progression',
      // Charts
      mttrTrend: 'Tendance MTTR/MTTD',
      incidentTrend: 'Tendance des Incidents',
      minutes: 'Minutes',
      autoResolved: 'Auto-résolu',
      manualResolved: 'Résolu manuellement',
      // Actions
      quickActions: 'Actions Rapides'
    },

    // Welcome & Onboarding
    welcome: {
      badge: 'Plateforme Unifiée d\'Observabilité',
      title: 'Bienvenue sur Synapsix',
      subtitle: 'Votre centre de commande unifié pour l\'observabilité industrielle',
      selectPersona: 'Choisissez votre profil',
      selectPersonaDescription: 'Sélectionnez le profil qui correspond le mieux à votre rôle pour une expérience personnalisée',
      skip: 'Passer',
      getStarted: 'Commencer',
      showGuide: 'Afficher le guide de démarrage'
    },

    // Personas
    personas: {
      operations_manager: {
        title: 'Responsable des Opérations',
        description: 'Surveillez la production, l\'OEE et les performances des équipements'
      },
      plant_director: {
        title: 'Directeur d\'Usine',
        description: 'Vue exécutive avec impact financier et KPIs stratégiques'
      },
      devops_engineer: {
        title: 'Ingénieur DevOps',
        description: 'Monitoring infrastructure, pipelines et services'
      },
      security_analyst: {
        title: 'Analyste Sécurité',
        description: 'Posture de sécurité, vulnérabilités et conformité'
      },
      compliance_officer: {
        title: 'Responsable Conformité',
        description: 'Audits, politiques et conformité réglementaire'
      },
      data_analyst: {
        title: 'Analyste Data',
        description: 'Qualité des données, pipelines et analyses avancées'
      }
    },

    // Guide steps
    guide: {
      step1: {
        title: 'Choisissez votre profil',
        description: 'Sélectionnez le profil qui correspond à votre rôle'
      },
      step2: {
        title: 'Explorez le Command Center',
        description: 'Vue globale de tous vos systèmes'
      },
      step3: {
        title: 'Naviguez vers les vues détaillées',
        description: 'Technique, Sécurité, Business ou Conformité'
      },
      step4: {
        title: 'Utilisez l\'assistant IA',
        description: 'Posez des questions en langage naturel'
      }
    },

    // Command Center
    commandCenter: {
      title: 'Command Center',
      subtitle: 'Vue unifiée de tous vos systèmes',
      overallHealth: 'Santé Globale',
      systemHealth: 'Santé Système',
      allSystemsOperational: 'Tous les systèmes opérationnels',
      securityScore: 'Score Sécurité',
      complianceScore: 'Score Conformité',
      technicalView: 'Vue Technique',
      technicalDescription: 'Infrastructure, services et pipelines',
      securityView: 'Vue Sécurité',
      securityDescription: 'Vulnérabilités, menaces et conformité',
      complianceView: 'Vue Conformité',
      complianceDescription: 'Audits, politiques et rapports',
      businessView: 'Vue Business',
      businessDescription: 'KPIs, OEE et impact financier',
      recentAlerts: 'Alertes Récentes',
      dataSources: 'Sources de Données',
      dataFlow: 'Flux de Données',
      askAI: 'Demander à l\'IA'
    },

    // Technical View
    technicalView: {
      title: 'Vue Technique',
      subtitle: 'Infrastructure, services et pipelines de données',
      dataSources: 'Sources de Données',
      resourceUsage: 'Utilisation des Ressources',
      services: 'Services',
      pipelineThroughput: 'Débit du Pipeline'
    },

    // Business KPI View
    businessKPI: {
      title: 'KPIs Business',
      subtitle: 'Performance de production et impact financier'
    },

    // AI Assistant
    assistant: {
      title: 'Assistant IA',
      subtitle: 'Posez vos questions en langage naturel',
      welcome: 'Comment puis-je vous aider ?',
      welcomeDescription: 'Je peux analyser vos données, générer des rapports et vous aider à résoudre des problèmes',
      placeholder: 'Posez une question sur vos données...'
    },

    // Security & Compliance
    security: {
      title: 'Sécurité & Conformité',
      description: 'Gestion des risques, audit de conformité et insights IA',
      tabs: {
        overview: 'Vue d\'ensemble',
        compliance: 'Conformité',
        vulnerabilities: 'Vulnérabilités',
        aiInsights: 'Insights IA',
        audit: 'Audit',
        policies: 'Politiques'
      },
      // Metrics
      overallScore: 'Score Global',
      criticalVulns: 'Vulnérabilités Critiques',
      openVulns: 'Vulnérabilités Ouvertes',
      aiAlerts: 'Alertes IA',
      activePolicies: 'Politiques Actives',
      // Compliance
      complianceOverview: 'Aperçu Conformité',
      complianceFrameworks: 'Cadres de Conformité',
      compliant: 'Conforme',
      partial: 'Partiel',
      nonCompliant: 'Non Conforme',
      controls: 'Contrôles',
      passed: 'Réussis',
      failed: 'Échoués',
      nextAudit: 'Prochain Audit',
      lastAudit: 'Dernier Audit',
      auditTimeline: 'Calendrier des Audits',
      generateReport: 'Générer Rapport',
      // Vulnerabilities
      allVulnerabilities: 'Toutes les Vulnérabilités',
      recentVulnerabilities: 'Vulnérabilités Récentes',
      vulnDistribution: 'Distribution des Vulnérabilités',
      allSeverities: 'Toutes les sévérités',
      critical: 'Critique',
      high: 'Élevée',
      medium: 'Moyenne',
      low: 'Faible',
      allStatuses: 'Tous les statuts',
      statusOpen: 'Ouvert',
      statusInProgress: 'En cours',
      statusPatched: 'Corrigé',
      viewDetails: 'Voir Détails',
      // Security
      securityTrend: 'Tendance Sécurité',
      securityScore: 'Score de Sécurité',
      threatsDetected: 'Menaces Détectées',
      threatsBlocked: 'Menaces Bloquées',
      exportReport: 'Exporter Rapport',
      runScan: 'Lancer Scan',
      // AI Insights
      latestAIInsights: 'Derniers Insights IA',
      aiSecurityInsights: 'Insights Sécurité IA',
      poweredByAI: 'Propulsé par l\'IA',
      confidence: 'Confiance',
      aiType: {
        anomaly: 'Anomalie',
        prediction: 'Prédiction',
        optimization: 'Optimisation'
      },
      aiCapabilities: {
        anomalyDetection: 'Détection d\'Anomalies',
        anomalyDesc: 'Détection en temps réel des comportements suspects',
        predictive: 'Analyse Prédictive',
        predictiveDesc: 'Anticipation des risques et menaces futures',
        optimization: 'Optimisation',
        optimizationDesc: 'Recommandations pour améliorer la sécurité'
      },
      // Audit
      auditTrail: 'Journal d\'Audit',
      auditId: 'ID',
      action: 'Action',
      user: 'Utilisateur',
      resource: 'Ressource',
      ipAddress: 'Adresse IP',
      timestamp: 'Horodatage',
      // Policies
      securityPolicies: 'Politiques de Sécurité',
      managePolicies: 'Gérer Politiques',
      compliance: 'Conformité',
      violations: 'violations',
      avgCompliance: 'Conformité Moyenne',
      enforced: 'Appliquées',
      totalViolations: 'Total Violations',
      policyStatus: {
        enforced: 'Appliquée',
        partial: 'Partielle',
        disabled: 'Désactivée'
      }
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
        kafka: 'Kafka',
        observability: 'Observability',
        security: 'Security & Compliance'
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
    },

    // Observability & Remediation
    observability: {
      title: 'Observability & Remediation',
      description: 'SLO monitoring, incident management and remediation automation',
      tabs: {
        overview: 'Overview',
        incidents: 'Incidents',
        runbooks: 'Runbooks',
        history: 'History'
      },
      // Metrics
      sloCompliance: 'SLO Compliance',
      activeIncidents: 'Active Incidents',
      mttr: 'Avg MTTR',
      mttd: 'Avg MTTD',
      automationRate: 'Automation Rate',
      // SLO
      sloStatus: 'SLO Status',
      current: 'Current',
      target: 'Target',
      errorBudget: 'Error Budget',
      remaining: 'remaining',
      // Incidents
      allActiveIncidents: 'All Active Incidents',
      noActiveIncidents: 'No Active Incidents',
      allSystemsOperational: 'All systems are operating normally',
      allSeverities: 'All severities',
      critical: 'Critical',
      warning: 'Warning',
      allServices: 'All services',
      viewRunbook: 'View Runbook',
      remediationActions: 'Remediation Actions',
      runNextStep: 'Run Next Step',
      pauseRemediation: 'Pause',
      escalate: 'Escalate',
      // Runbooks
      remediationRunbooks: 'Remediation Runbooks',
      createRunbook: 'Create Runbook',
      executions: 'executions',
      avgMTTR: 'Avg MTTR',
      triggers: 'Triggers',
      steps: 'Steps',
      automated: 'Automated',
      manual: 'Manual',
      executeRunbook: 'Execute Runbook',
      // History
      remediationHistory: 'Remediation History',
      last24h: 'Last 24h',
      last7d: 'Last 7 days',
      last30d: 'Last 30 days',
      runbook: 'Runbook',
      service: 'Service',
      trigger: 'Trigger',
      duration: 'Duration',
      status: 'Status',
      progress: 'Progress',
      // Charts
      mttrTrend: 'MTTR/MTTD Trend',
      incidentTrend: 'Incident Trend',
      minutes: 'Minutes',
      autoResolved: 'Auto-resolved',
      manualResolved: 'Manually resolved',
      // Actions
      quickActions: 'Quick Actions'
    },

    // Welcome & Onboarding
    welcome: {
      badge: 'Unified Observability Platform',
      title: 'Welcome to Synapsix',
      subtitle: 'Your unified command center for industrial observability',
      selectPersona: 'Choose your profile',
      selectPersonaDescription: 'Select the profile that best matches your role for a personalized experience',
      skip: 'Skip',
      getStarted: 'Get Started',
      showGuide: 'Show quick start guide'
    },

    // Personas
    personas: {
      operations_manager: {
        title: 'Operations Manager',
        description: 'Monitor production, OEE and equipment performance'
      },
      plant_director: {
        title: 'Plant Director',
        description: 'Executive view with financial impact and strategic KPIs'
      },
      devops_engineer: {
        title: 'DevOps Engineer',
        description: 'Infrastructure monitoring, pipelines and services'
      },
      security_analyst: {
        title: 'Security Analyst',
        description: 'Security posture, vulnerabilities and compliance'
      },
      compliance_officer: {
        title: 'Compliance Officer',
        description: 'Audits, policies and regulatory compliance'
      },
      data_analyst: {
        title: 'Data Analyst',
        description: 'Data quality, pipelines and advanced analytics'
      }
    },

    // Guide steps
    guide: {
      step1: {
        title: 'Choose your profile',
        description: 'Select the profile that matches your role'
      },
      step2: {
        title: 'Explore the Command Center',
        description: 'Global view of all your systems'
      },
      step3: {
        title: 'Navigate to detailed views',
        description: 'Technical, Security, Business or Compliance'
      },
      step4: {
        title: 'Use the AI assistant',
        description: 'Ask questions in natural language'
      }
    },

    // Command Center
    commandCenter: {
      title: 'Command Center',
      subtitle: 'Unified view of all your systems',
      overallHealth: 'Overall Health',
      systemHealth: 'System Health',
      allSystemsOperational: 'All systems operational',
      securityScore: 'Security Score',
      complianceScore: 'Compliance Score',
      technicalView: 'Technical View',
      technicalDescription: 'Infrastructure, services and pipelines',
      securityView: 'Security View',
      securityDescription: 'Vulnerabilities, threats and compliance',
      complianceView: 'Compliance View',
      complianceDescription: 'Audits, policies and reports',
      businessView: 'Business View',
      businessDescription: 'KPIs, OEE and financial impact',
      recentAlerts: 'Recent Alerts',
      dataSources: 'Data Sources',
      dataFlow: 'Data Flow',
      askAI: 'Ask AI'
    },

    // Technical View
    technicalView: {
      title: 'Technical View',
      subtitle: 'Infrastructure, services and data pipelines',
      dataSources: 'Data Sources',
      resourceUsage: 'Resource Usage',
      services: 'Services',
      pipelineThroughput: 'Pipeline Throughput'
    },

    // Business KPI View
    businessKPI: {
      title: 'Business KPIs',
      subtitle: 'Production performance and financial impact'
    },

    // AI Assistant
    assistant: {
      title: 'AI Assistant',
      subtitle: 'Ask questions in natural language',
      welcome: 'How can I help you?',
      welcomeDescription: 'I can analyze your data, generate reports and help you troubleshoot issues',
      placeholder: 'Ask a question about your data...'
    },

    // Security & Compliance
    security: {
      title: 'Security & Compliance',
      description: 'Risk management, compliance auditing and AI insights',
      tabs: {
        overview: 'Overview',
        compliance: 'Compliance',
        vulnerabilities: 'Vulnerabilities',
        aiInsights: 'AI Insights',
        audit: 'Audit',
        policies: 'Policies'
      },
      // Metrics
      overallScore: 'Overall Score',
      criticalVulns: 'Critical Vulnerabilities',
      openVulns: 'Open Vulnerabilities',
      aiAlerts: 'AI Alerts',
      activePolicies: 'Active Policies',
      // Compliance
      complianceOverview: 'Compliance Overview',
      complianceFrameworks: 'Compliance Frameworks',
      compliant: 'Compliant',
      partial: 'Partial',
      nonCompliant: 'Non-Compliant',
      controls: 'Controls',
      passed: 'Passed',
      failed: 'Failed',
      nextAudit: 'Next Audit',
      lastAudit: 'Last Audit',
      auditTimeline: 'Audit Timeline',
      generateReport: 'Generate Report',
      // Vulnerabilities
      allVulnerabilities: 'All Vulnerabilities',
      recentVulnerabilities: 'Recent Vulnerabilities',
      vulnDistribution: 'Vulnerability Distribution',
      allSeverities: 'All severities',
      critical: 'Critical',
      high: 'High',
      medium: 'Medium',
      low: 'Low',
      allStatuses: 'All statuses',
      statusOpen: 'Open',
      statusInProgress: 'In Progress',
      statusPatched: 'Patched',
      viewDetails: 'View Details',
      // Security
      securityTrend: 'Security Trend',
      securityScore: 'Security Score',
      threatsDetected: 'Threats Detected',
      threatsBlocked: 'Threats Blocked',
      exportReport: 'Export Report',
      runScan: 'Run Scan',
      // AI Insights
      latestAIInsights: 'Latest AI Insights',
      aiSecurityInsights: 'AI Security Insights',
      poweredByAI: 'Powered by AI',
      confidence: 'Confidence',
      aiType: {
        anomaly: 'Anomaly',
        prediction: 'Prediction',
        optimization: 'Optimization'
      },
      aiCapabilities: {
        anomalyDetection: 'Anomaly Detection',
        anomalyDesc: 'Real-time detection of suspicious behaviors',
        predictive: 'Predictive Analysis',
        predictiveDesc: 'Anticipate future risks and threats',
        optimization: 'Optimization',
        optimizationDesc: 'Recommendations to improve security'
      },
      // Audit
      auditTrail: 'Audit Trail',
      auditId: 'ID',
      action: 'Action',
      user: 'User',
      resource: 'Resource',
      ipAddress: 'IP Address',
      timestamp: 'Timestamp',
      // Policies
      securityPolicies: 'Security Policies',
      managePolicies: 'Manage Policies',
      compliance: 'Compliance',
      violations: 'violations',
      avgCompliance: 'Average Compliance',
      enforced: 'Enforced',
      totalViolations: 'Total Violations',
      policyStatus: {
        enforced: 'Enforced',
        partial: 'Partial',
        disabled: 'Disabled'
      }
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
        kafka: 'Kafka',
        observability: 'Observabiliteit',
        security: 'Beveiliging & Compliance'
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
    },

    // Observability & Remediation
    observability: {
      title: 'Observabiliteit & Remediatie',
      description: 'SLO monitoring, incidentbeheer en remediatie automatisering',
      tabs: {
        overview: 'Overzicht',
        incidents: 'Incidenten',
        runbooks: 'Runbooks',
        history: 'Geschiedenis'
      },
      // Metrics
      sloCompliance: 'SLO Naleving',
      activeIncidents: 'Actieve Incidenten',
      mttr: 'Gem. MTTR',
      mttd: 'Gem. MTTD',
      automationRate: 'Automatiseringsgraad',
      // SLO
      sloStatus: 'SLO Status',
      current: 'Huidig',
      target: 'Doel',
      errorBudget: 'Foutbudget',
      remaining: 'resterend',
      // Incidents
      allActiveIncidents: 'Alle Actieve Incidenten',
      noActiveIncidents: 'Geen Actieve Incidenten',
      allSystemsOperational: 'Alle systemen werken normaal',
      allSeverities: 'Alle ernst',
      critical: 'Kritiek',
      warning: 'Waarschuwing',
      allServices: 'Alle services',
      viewRunbook: 'Bekijk Runbook',
      remediationActions: 'Remediatie Acties',
      runNextStep: 'Volgende Stap',
      pauseRemediation: 'Pauzeren',
      escalate: 'Escaleren',
      // Runbooks
      remediationRunbooks: 'Remediatie Runbooks',
      createRunbook: 'Runbook Maken',
      executions: 'uitvoeringen',
      avgMTTR: 'Gem. MTTR',
      triggers: 'Triggers',
      steps: 'Stappen',
      automated: 'Geautomatiseerd',
      manual: 'Handmatig',
      executeRunbook: 'Runbook Uitvoeren',
      // History
      remediationHistory: 'Remediatie Geschiedenis',
      last24h: 'Laatste 24u',
      last7d: 'Laatste 7 dagen',
      last30d: 'Laatste 30 dagen',
      runbook: 'Runbook',
      service: 'Service',
      trigger: 'Trigger',
      duration: 'Duur',
      status: 'Status',
      progress: 'Voortgang',
      // Charts
      mttrTrend: 'MTTR/MTTD Trend',
      incidentTrend: 'Incident Trend',
      minutes: 'Minuten',
      autoResolved: 'Auto-opgelost',
      manualResolved: 'Handmatig opgelost',
      // Actions
      quickActions: 'Snelle Acties'
    },

    // Welcome & Onboarding
    welcome: {
      badge: 'Geïntegreerd Observabiliteitsplatform',
      title: 'Welkom bij Synapsix',
      subtitle: 'Uw geïntegreerde commandocentrum voor industriële observabiliteit',
      selectPersona: 'Kies uw profiel',
      selectPersonaDescription: 'Selecteer het profiel dat het beste bij uw rol past voor een gepersonaliseerde ervaring',
      skip: 'Overslaan',
      getStarted: 'Aan de slag',
      showGuide: 'Toon snelstartgids'
    },

    // Personas
    personas: {
      operations_manager: {
        title: 'Operations Manager',
        description: 'Monitor productie, OEE en apparatuurprestaties'
      },
      plant_director: {
        title: 'Fabrieksdirecteur',
        description: 'Executive weergave met financiële impact en strategische KPIs'
      },
      devops_engineer: {
        title: 'DevOps Engineer',
        description: 'Infrastructuurmonitoring, pipelines en services'
      },
      security_analyst: {
        title: 'Beveiligingsanalist',
        description: 'Beveiligingshouding, kwetsbaarheden en compliance'
      },
      compliance_officer: {
        title: 'Compliance Officer',
        description: 'Audits, beleid en regelgevende compliance'
      },
      data_analyst: {
        title: 'Data Analist',
        description: 'Datakwaliteit, pipelines en geavanceerde analyses'
      }
    },

    // Guide steps
    guide: {
      step1: {
        title: 'Kies uw profiel',
        description: 'Selecteer het profiel dat bij uw rol past'
      },
      step2: {
        title: 'Verken het Command Center',
        description: 'Globaal overzicht van al uw systemen'
      },
      step3: {
        title: 'Navigeer naar gedetailleerde weergaven',
        description: 'Technisch, Beveiliging, Business of Compliance'
      },
      step4: {
        title: 'Gebruik de AI-assistent',
        description: 'Stel vragen in natuurlijke taal'
      }
    },

    // Command Center
    commandCenter: {
      title: 'Command Center',
      subtitle: 'Geïntegreerd overzicht van al uw systemen',
      overallHealth: 'Totale Gezondheid',
      systemHealth: 'Systeemgezondheid',
      allSystemsOperational: 'Alle systemen operationeel',
      securityScore: 'Beveiligingsscore',
      complianceScore: 'Compliance Score',
      technicalView: 'Technische Weergave',
      technicalDescription: 'Infrastructuur, services en pipelines',
      securityView: 'Beveiligingsweergave',
      securityDescription: 'Kwetsbaarheden, bedreigingen en compliance',
      complianceView: 'Compliance Weergave',
      complianceDescription: 'Audits, beleid en rapporten',
      businessView: 'Business Weergave',
      businessDescription: 'KPIs, OEE en financiële impact',
      recentAlerts: 'Recente Alerts',
      dataSources: 'Databronnen',
      dataFlow: 'Datastroom',
      askAI: 'Vraag AI'
    },

    // Technical View
    technicalView: {
      title: 'Technische Weergave',
      subtitle: 'Infrastructuur, services en datapipelines',
      dataSources: 'Databronnen',
      resourceUsage: 'Resourcegebruik',
      services: 'Services',
      pipelineThroughput: 'Pipeline Doorvoer'
    },

    // Business KPI View
    businessKPI: {
      title: 'Business KPIs',
      subtitle: 'Productieprestaties en financiële impact'
    },

    // AI Assistant
    assistant: {
      title: 'AI Assistent',
      subtitle: 'Stel vragen in natuurlijke taal',
      welcome: 'Hoe kan ik u helpen?',
      welcomeDescription: 'Ik kan uw data analyseren, rapporten genereren en u helpen problemen op te lossen',
      placeholder: 'Stel een vraag over uw data...'
    },

    // Security & Compliance
    security: {
      title: 'Beveiliging & Compliance',
      description: 'Risicobeheer, compliance-auditing en AI-inzichten',
      tabs: {
        overview: 'Overzicht',
        compliance: 'Compliance',
        vulnerabilities: 'Kwetsbaarheden',
        aiInsights: 'AI Inzichten',
        audit: 'Audit',
        policies: 'Beleid'
      },
      // Metrics
      overallScore: 'Totaalscore',
      criticalVulns: 'Kritieke Kwetsbaarheden',
      openVulns: 'Open Kwetsbaarheden',
      aiAlerts: 'AI Alerts',
      activePolicies: 'Actief Beleid',
      // Compliance
      complianceOverview: 'Compliance Overzicht',
      complianceFrameworks: 'Compliance Kaders',
      compliant: 'Conform',
      partial: 'Gedeeltelijk',
      nonCompliant: 'Niet Conform',
      controls: 'Controles',
      passed: 'Geslaagd',
      failed: 'Gefaald',
      nextAudit: 'Volgende Audit',
      lastAudit: 'Laatste Audit',
      auditTimeline: 'Audit Tijdlijn',
      generateReport: 'Rapport Genereren',
      // Vulnerabilities
      allVulnerabilities: 'Alle Kwetsbaarheden',
      recentVulnerabilities: 'Recente Kwetsbaarheden',
      vulnDistribution: 'Kwetsbaarheid Verdeling',
      allSeverities: 'Alle ernst',
      critical: 'Kritiek',
      high: 'Hoog',
      medium: 'Gemiddeld',
      low: 'Laag',
      allStatuses: 'Alle statussen',
      statusOpen: 'Open',
      statusInProgress: 'In Behandeling',
      statusPatched: 'Gepatcht',
      viewDetails: 'Details Bekijken',
      // Security
      securityTrend: 'Beveiligingstrend',
      securityScore: 'Beveiligingsscore',
      threatsDetected: 'Bedreigingen Gedetecteerd',
      threatsBlocked: 'Bedreigingen Geblokkeerd',
      exportReport: 'Rapport Exporteren',
      runScan: 'Scan Starten',
      // AI Insights
      latestAIInsights: 'Laatste AI Inzichten',
      aiSecurityInsights: 'AI Beveiligingsinzichten',
      poweredByAI: 'Aangedreven door AI',
      confidence: 'Vertrouwen',
      aiType: {
        anomaly: 'Anomalie',
        prediction: 'Voorspelling',
        optimization: 'Optimalisatie'
      },
      aiCapabilities: {
        anomalyDetection: 'Anomaliedetectie',
        anomalyDesc: 'Real-time detectie van verdacht gedrag',
        predictive: 'Predictieve Analyse',
        predictiveDesc: 'Anticipeer op toekomstige risico\'s en bedreigingen',
        optimization: 'Optimalisatie',
        optimizationDesc: 'Aanbevelingen om beveiliging te verbeteren'
      },
      // Audit
      auditTrail: 'Auditspoor',
      auditId: 'ID',
      action: 'Actie',
      user: 'Gebruiker',
      resource: 'Resource',
      ipAddress: 'IP Adres',
      timestamp: 'Tijdstempel',
      // Policies
      securityPolicies: 'Beveiligingsbeleid',
      managePolicies: 'Beleid Beheren',
      compliance: 'Compliance',
      violations: 'overtredingen',
      avgCompliance: 'Gemiddelde Compliance',
      enforced: 'Afgedwongen',
      totalViolations: 'Totaal Overtredingen',
      policyStatus: {
        enforced: 'Afgedwongen',
        partial: 'Gedeeltelijk',
        disabled: 'Uitgeschakeld'
      }
    }
  }
}

export default translations
