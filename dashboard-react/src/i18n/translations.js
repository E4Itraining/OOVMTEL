// Synapsix Dashboard - Multilingual translations (FR/EN/NL/DE)

export const LANGUAGES = {
  FR: 'fr',
  EN: 'en',
  NL: 'nl',
  DE: 'de'
}

export const LANGUAGE_LABELS = {
  [LANGUAGES.FR]: 'Français',
  [LANGUAGES.EN]: 'English',
  [LANGUAGES.NL]: 'Nederlands',
  [LANGUAGES.DE]: 'Deutsch'
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
      persona: 'Profil',
      changePersona: 'Changer de profil',
      main: {
        home: 'Accueil',
        globalView: 'Vue Globale',
        commandCenter: 'Centre de Commande',
        technicalView: 'Vue Technique',
        businessKPI: 'KPIs Métier',
        aiAssistant: 'Assistant IA',
        impactAnalysis: 'Impact & Préconisations',
        impactChain: 'Chaîne d\'Impact IT/OT',
        simulators: 'Lanceur Simulateurs',
        industrialObs: 'Observabilité Industrielle',
        correlation: 'Corrélation IT-OT-IA',
        cybersecurityOT: 'Cybersécurité OT/IT',
        grafana: 'Grafana',
        opensearch: 'OpenSearch',
        kafka: 'Kafka',
        observability: 'Observabilité',
        aiObservability: 'Observabilité IA',
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
      },
      // Métriques OT (Operational Technology)
      ot: {
        title: 'Zone OT (Operational Technology)',
        health: 'Santé Zone OT',
        globalHealth: 'Santé Globale OT',
        // Systèmes
        systems: {
          scada: {
            name: 'SCADA',
            fullName: 'Supervisory Control and Data Acquisition',
            connectedDevices: 'Équipements connectés',
            dataPoints: 'Points de données/s',
            alarms: 'Alarmes actives'
          },
          mes: {
            name: 'MES',
            fullName: 'Manufacturing Execution System',
            activeOrders: 'Ordres actifs',
            completed: 'Complétés aujourd\'hui',
            pending: 'En attente',
            efficiency: 'Efficacité'
          },
          plm: {
            name: 'PLM',
            fullName: 'Product Lifecycle Management',
            activeProducts: 'Produits actifs',
            revisions: 'Révisions en attente',
            qualityHolds: 'Blocages qualité'
          },
          opcua: {
            name: 'OPC-UA',
            fullName: 'OPC Unified Architecture',
            servers: 'Serveurs connectés',
            subscriptions: 'Abonnements actifs',
            tags: 'Tags surveillés',
            latency: 'Latence'
          }
        },
        // Métriques industrielles
        industrial: {
          title: 'Métriques Industrielles',
          mtbf: 'MTBF',
          mtbfFull: 'Temps moyen entre pannes',
          mttr: 'MTTR',
          mttrFull: 'Temps moyen de réparation',
          trs: 'TRS Détaillé',
          trsFull: 'Taux de Rendement Synthétique',
          disponibilite: 'Disponibilité',
          performance: 'Performance',
          qualite: 'Qualité'
        },
        // Zones de production
        zones: {
          title: 'Zones de Production',
          lines: 'lignes',
          oee: 'OEE'
        },
        // Chaîne logique-métier
        dependencyChain: {
          title: 'Chaîne Logique-Métier',
          impactCritical: 'Impact Critique',
          impactMedium: 'Impact Modéré',
          impactLow: 'Impact Faible'
        },
        // Impacts
        impacts: {
          title: 'Impacts Actifs sur Production',
          severity: 'Sévérité',
          critical: 'Critique',
          warning: 'Modéré',
          affectedLines: 'Lignes affectées',
          lostProduction: 'Production perdue',
          estimatedCost: 'Coût estimé',
          duration: 'Durée',
          rootCause: 'Cause racine'
        }
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

    // Welcome/Onboarding Page
    welcome: {
      title: 'Bienvenue sur Synapsix',
      subtitle: 'Plateforme d\'Observabilité Industrielle',
      tagline: 'Propulsé par l\'IA',
      selectPersona: 'Sélectionnez votre profil pour personnaliser votre expérience',
      continue: 'Continuer',
      skip: 'Passer cette étape',
      hint: 'Vous pouvez changer de profil à tout moment dans les paramètres'
    },

    // Personas - Industrial context (Business / Tech / Sécurité / Juridique / GreenOps)
    personas: {
      // ═══════════════════════════════════════════════════════════════════════════
      // BUSINESS - Vision métier et stratégique
      // ═══════════════════════════════════════════════════════════════════════════
      dirigeant: {
        title: 'Dirigeant / CEO',
        description: 'Vision stratégique 360°, gouvernance et pilotage global de l\'entreprise',
        feature1: 'Tableaux de bord exécutifs',
        feature2: 'ROI et impact business',
        feature3: 'Indicateurs de risques stratégiques'
      },
      cfo: {
        title: 'Directeur Financier / CFO',
        description: 'Pilotage financier, ROI des investissements IT et optimisation des coûts',
        feature1: 'Analyse coûts IT / OPEX / CAPEX',
        feature2: 'ROI des projets digitaux',
        feature3: 'Budget et prévisions'
      },
      directeurProduction: {
        title: 'Directeur Production / COO',
        description: 'Supervision des opérations, performance industrielle et excellence opérationnelle',
        feature1: 'OEE et rendement machines',
        feature2: 'Alertes équipements critiques',
        feature3: 'Planification maintenance'
      },

      // ═══════════════════════════════════════════════════════════════════════════
      // TECH - Technique et data
      // ═══════════════════════════════════════════════════════════════════════════
      dsi: {
        title: 'DSI / CTO',
        description: 'Direction des Systèmes d\'Information, transformation digitale et innovation',
        feature1: 'Gouvernance IT et architecture',
        feature2: 'Performance infrastructure',
        feature3: 'Roadmap technologique'
      },
      dataMlops: {
        title: 'Data Engineer / MLOps',
        description: 'Pipelines de données, modèles ML et qualité des données industrielles',
        feature1: 'Qualité et drift données',
        feature2: 'Performance modèles ML',
        feature3: 'Monitoring pipelines'
      },
      devopsSre: {
        title: 'DevOps / SRE',
        description: 'Fiabilité, disponibilité et automatisation de l\'infrastructure',
        feature1: 'SLOs et fiabilité',
        feature2: 'Gestion des incidents',
        feature3: 'Observabilité full-stack'
      },

      // ═══════════════════════════════════════════════════════════════════════════
      // SÉCURITÉ - Cybersécurité
      // ═══════════════════════════════════════════════════════════════════════════
      rssi: {
        title: 'RSSI / CISO',
        description: 'Responsable de la Sécurité des Systèmes d\'Information',
        feature1: 'Posture de sécurité',
        feature2: 'Gestion des vulnérabilités',
        feature3: 'Conformité NIS 2 / ISO 27001'
      },
      analyteSoc: {
        title: 'Analyste SOC',
        description: 'Surveillance des menaces, détection et réponse aux incidents de sécurité',
        feature1: 'Alertes et incidents sécurité',
        feature2: 'Analyse forensique',
        feature3: 'Threat intelligence'
      },

      // ═══════════════════════════════════════════════════════════════════════════
      // JURIDIQUE - Conformité et régulations
      // ═══════════════════════════════════════════════════════════════════════════
      dpo: {
        title: 'DPO',
        description: 'Data Protection Officer - Protection des données personnelles et vie privée',
        feature1: 'Conformité RGPD',
        feature2: 'Registre des traitements',
        feature3: 'Droits des personnes'
      },
      responsableConformite: {
        title: 'Responsable Conformité',
        description: 'Conformité réglementaire EU : NIS2, AI Act, DORA et normes sectorielles',
        feature1: 'AI Act & régulations EU',
        feature2: 'Audits et certifications',
        feature3: 'Gestion des risques juridiques'
      },

      // ═══════════════════════════════════════════════════════════════════════════
      // GREENOPS - Durabilité et environnement
      // ═══════════════════════════════════════════════════════════════════════════
      responsableRse: {
        title: 'Responsable RSE / Sustainability',
        description: 'Responsabilité Sociétale, impact environnemental et reporting ESG/CSRD',
        feature1: 'Empreinte carbone',
        feature2: 'KPIs durabilité',
        feature3: 'Reporting CSRD / ESG'
      },
      greenItManager: {
        title: 'Green IT Manager',
        description: 'Efficience énergétique IT, PUE datacenter et numérique responsable',
        feature1: 'PUE et consommation énergétique',
        feature2: 'Cloud carbon footprint',
        feature3: 'Optimisation ressources'
      }
    },

    // Impact Analysis
    impactAnalysis: {
      title: 'Impact & Préconisations',
      subtitle: 'Analyse des impacts et recommandations IA personnalisées',
      summary: {
        totalImpacts: 'Impacts identifiés',
        criticalItems: 'Éléments critiques',
        estimatedSavings: 'Économies potentielles',
        riskReduction: 'Réduction des risques',
        actionItems: 'Actions recommandées'
      },
      categories: {
        financial: 'Financier',
        operational: 'Opérationnel',
        security: 'Sécurité',
        compliance: 'Conformité',
        performance: 'Performance'
      },
      priority: {
        critical: 'Critique',
        high: 'Haute',
        medium: 'Moyenne',
        low: 'Basse'
      },
      aiInsight: 'Analyse IA',
      recommendations: 'Préconisations',
      affectedSystems: 'Systèmes impactés',
      timeToImplement: 'Délai de mise en œuvre',
      roi: 'Retour sur investissement',
      createAction: 'Créer une action',
      viewDetails: 'Voir les détails',
      exportReport: 'Exporter le rapport'
    },

    // Command Center
    commandCenter: {
      title: 'Centre de Commande',
      subtitle: 'Vue d\'ensemble de la santé système et des alertes',
      quickAccess: 'Accès rapide',
      keyMetrics: 'Métriques clés',
      quickNav: {
        technical: {
          title: 'Vue Technique',
          description: 'Infrastructure, services et pipelines'
        },
        business: {
          title: 'KPIs Métier',
          description: 'OEE, production et impact financier'
        },
        security: {
          title: 'Sécurité',
          description: 'Vulnérabilités et conformité'
        },
        observability: {
          title: 'Observabilité',
          description: 'Incidents et remédiation'
        }
      },
      systemHealth: {
        title: 'Santé Système',
        subtitle: 'État des services backend',
        overall: 'Score Global',
        servicesHealthy: 'services opérationnels',
        backendServices: 'Services Backend'
      },
      alerts: {
        title: 'Alertes',
        active: 'actives',
        noAlerts: 'Aucune alerte active'
      },
      aiAssistant: {
        title: 'Assistant IA',
        description: 'Posez vos questions en langage naturel'
      }
    },

    // Technical View
    technicalView: {
      title: 'Vue Technique',
      subtitle: 'Infrastructure, services backend et pipelines de données',
      pipeline: {
        title: 'Pipeline de Données',
        subtitle: 'Flux de collecte vers stockage'
      },
      backends: {
        title: 'Services Backend'
      },
      throughput: {
        title: 'Débit',
        subtitle: 'Métriques, logs et traces par heure'
      }
    },

    // Business KPI View
    businessKPI: {
      title: 'KPIs Métier',
      subtitle: 'Performance de production, qualité et impact financier',
      period: {
        today: 'Aujourd\'hui',
        week: 'Semaine',
        month: 'Mois'
      },
      oee: {
        title: 'OEE Global',
        subtitle: 'Efficacité Globale des Équipements',
        components: 'Composantes OEE',
        componentsSubtitle: 'Disponibilité × Performance × Qualité',
        trend: 'Tendance OEE',
        trendSubtitle: 'Évolution sur les dernières 24 heures'
      },
      financial: {
        title: 'Impact Financier',
        subtitle: 'Revenus et coûts de production'
      },
      production: {
        byProduct: 'Production par Produit',
        distribution: 'Distribution de la production'
      },
      equipment: {
        status: 'État des Équipements',
        statusSubtitle: 'Lignes de production'
      },
      maintenance: {
        title: 'Maintenance',
        subtitle: 'Planification et historique'
      }
    },

    // AI Assistant
    aiAssistant: {
      title: 'Assistant IA',
      subtitle: 'Posez vos questions en langage naturel',
      online: 'En ligne',
      welcome: 'Comment puis-je vous aider ?',
      welcomeDescription: 'Je peux analyser vos données, générer des rapports et répondre à vos questions sur la production, l\'infrastructure et la sécurité.',
      suggestions: 'Suggestions',
      quickActions: 'Actions rapides',
      placeholder: 'Posez votre question...'
    },

    // Security & Compliance
    security: {
      title: 'Sécurité & Conformité',
      description: 'Gestion des risques, audit de conformité et insights IA',
      tabs: {
        overview: 'Vue d\'ensemble',
        compliance: 'Conformité',
        euRegulations: 'Régulations EU',
        vulnerabilities: 'Vulnérabilités',
        aiInsights: 'Insights IA',
        audit: 'Audit',
        policies: 'Politiques',
        video: 'Vidéosurveillance'
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
      },
      // Video Surveillance
      video: {
        cameras: 'Caméras',
        online: 'En ligne',
        offline: 'Hors ligne',
        recording: 'Enregistrement',
        lastMotion: 'Dernier mouvement',
        alerts: 'alertes',
        totalAlerts: 'Alertes Totales',
        liveFeeds: 'Flux en Direct',
        allCameras: 'Toutes les caméras',
        onlineOnly: 'En ligne uniquement',
        withAlerts: 'Avec alertes',
        fullscreen: 'Plein écran',
        recentEvents: 'Événements Récents',
        viewRecording: 'Voir enregistrement',
        storage: 'Stockage',
        of: 'sur',
        retention: 'Rétention',
        days: 'jours',
        bandwidth: 'Bande passante'
      },
      // EU Regulations (AI Act & NIS 2)
      euReg: {
        inProgress: 'En cours',
        aiActDesc: 'Règlement européen sur l\'intelligence artificielle',
        nis2Desc: 'Directive européenne sur la cybersécurité des réseaux et systèmes d\'information',
        aiSystems: 'Systèmes IA',
        highRisk: 'Haut risque',
        requirements: 'Exigences',
        compliantReq: 'Conformes',
        aiActTitle: 'AI Act - Classification des systèmes IA',
        assessRisk: 'Évaluer le risque',
        unacceptable: 'Inacceptable',
        highRiskCat: 'Haut risque',
        limited: 'Risque limité',
        minimal: 'Risque minimal',
        systems: 'systèmes',
        aiInventory: 'Inventaire des systèmes IA',
        provider: 'Fournisseur',
        useCases: 'Cas d\'usage',
        aiActRequirements: 'Exigences AI Act',
        deadline: 'Échéance',
        nis2Title: 'NIS 2 - Cybersécurité',
        entityType: 'Type d\'entité',
        essential: 'Entité essentielle',
        sector: 'Secteur',
        manufacturing: 'Industrie manufacturière',
        notifyDelay: 'Délai notification',
        authority: 'Autorité compétente',
        nis2Requirements: 'Exigences NIS 2',
        nis2Incidents: 'Incidents NIS 2',
        resolved: 'Résolu',
        active: 'Actif',
        reportedToANSSI: 'Signalé à l\'ANSSI',
        detection: 'Détection',
        resolution: 'Résolution',
        impact: 'Impact',
        risk: {
          minimal: 'Risque minimal',
          limited: 'Risque limité',
          high: 'Haut risque',
          unacceptable: 'Inacceptable'
        },
        priority: {
          critical: 'Critique',
          high: 'Élevée',
          medium: 'Moyenne'
        },
        impactLevel: {
          low: 'Faible',
          medium: 'Moyen',
          high: 'Élevé'
        }
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
      persona: 'Profile',
      changePersona: 'Change profile',
      main: {
        home: 'Home',
        globalView: 'Global View',
        commandCenter: 'Command Center',
        technicalView: 'Technical View',
        businessKPI: 'Business KPIs',
        aiAssistant: 'AI Assistant',
        impactAnalysis: 'Impact & Recommendations',
        impactChain: 'IT/OT Impact Chain',
        simulators: 'Simulator Launcher',
        industrialObs: 'Industrial Observability',
        correlation: 'IT-OT-AI Correlation',
        cybersecurityOT: 'OT/IT Cybersecurity',
        aiObservability: 'AI Observability',
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
      },
      // OT (Operational Technology) Metrics
      ot: {
        title: 'OT Zone (Operational Technology)',
        health: 'OT Zone Health',
        globalHealth: 'OT Global Health',
        // Systems
        systems: {
          scada: {
            name: 'SCADA',
            fullName: 'Supervisory Control and Data Acquisition',
            connectedDevices: 'Connected devices',
            dataPoints: 'Data points/s',
            alarms: 'Active alarms'
          },
          mes: {
            name: 'MES',
            fullName: 'Manufacturing Execution System',
            activeOrders: 'Active orders',
            completed: 'Completed today',
            pending: 'Pending',
            efficiency: 'Efficiency'
          },
          plm: {
            name: 'PLM',
            fullName: 'Product Lifecycle Management',
            activeProducts: 'Active products',
            revisions: 'Pending revisions',
            qualityHolds: 'Quality holds'
          },
          opcua: {
            name: 'OPC-UA',
            fullName: 'OPC Unified Architecture',
            servers: 'Connected servers',
            subscriptions: 'Active subscriptions',
            tags: 'Monitored tags',
            latency: 'Latency'
          }
        },
        // Industrial metrics
        industrial: {
          title: 'Industrial Metrics',
          mtbf: 'MTBF',
          mtbfFull: 'Mean Time Between Failures',
          mttr: 'MTTR',
          mttrFull: 'Mean Time To Repair',
          trs: 'OEE Detailed',
          trsFull: 'Overall Equipment Effectiveness',
          disponibilite: 'Availability',
          performance: 'Performance',
          qualite: 'Quality'
        },
        // Production zones
        zones: {
          title: 'Production Zones',
          lines: 'lines',
          oee: 'OEE'
        },
        // Business logic chain
        dependencyChain: {
          title: 'Business Logic Chain',
          impactCritical: 'Critical Impact',
          impactMedium: 'Medium Impact',
          impactLow: 'Low Impact'
        },
        // Impacts
        impacts: {
          title: 'Active Production Impacts',
          severity: 'Severity',
          critical: 'Critical',
          warning: 'Moderate',
          affectedLines: 'Affected lines',
          lostProduction: 'Lost production',
          estimatedCost: 'Estimated cost',
          duration: 'Duration',
          rootCause: 'Root cause'
        }
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

    // Welcome/Onboarding Page
    welcome: {
      title: 'Welcome to Synapsix',
      subtitle: 'Industrial Observability Platform',
      tagline: 'Powered by AI',
      selectPersona: 'Select your profile to personalize your experience',
      continue: 'Continue',
      skip: 'Skip this step',
      hint: 'You can change your profile anytime in settings'
    },

    // Personas - Industrial context (Business / Tech / Security / Legal / GreenOps)
    personas: {
      // ═══════════════════════════════════════════════════════════════════════════
      // BUSINESS - Business vision and strategy
      // ═══════════════════════════════════════════════════════════════════════════
      dirigeant: {
        title: 'Executive / CEO',
        description: '360° strategic vision, governance and global company management',
        feature1: 'Executive dashboards',
        feature2: 'ROI and business impact',
        feature3: 'Strategic risk indicators'
      },
      cfo: {
        title: 'CFO',
        description: 'Financial management, IT investment ROI and cost optimization',
        feature1: 'IT costs / OPEX / CAPEX analysis',
        feature2: 'Digital projects ROI',
        feature3: 'Budget and forecasts'
      },
      directeurProduction: {
        title: 'Production Director / COO',
        description: 'Operations supervision, industrial performance and operational excellence',
        feature1: 'OEE and machine performance',
        feature2: 'Critical equipment alerts',
        feature3: 'Maintenance planning'
      },

      // ═══════════════════════════════════════════════════════════════════════════
      // TECH - Technical and data
      // ═══════════════════════════════════════════════════════════════════════════
      dsi: {
        title: 'CIO / CTO',
        description: 'Information Systems Direction, digital transformation and innovation',
        feature1: 'IT governance and architecture',
        feature2: 'Infrastructure performance',
        feature3: 'Technology roadmap'
      },
      dataMlops: {
        title: 'Data Engineer / MLOps',
        description: 'Data pipelines, ML models and industrial data quality',
        feature1: 'Data quality and drift',
        feature2: 'ML model performance',
        feature3: 'Pipeline monitoring'
      },
      devopsSre: {
        title: 'DevOps / SRE',
        description: 'Reliability, availability and infrastructure automation',
        feature1: 'SLOs and reliability',
        feature2: 'Incident management',
        feature3: 'Full-stack observability'
      },

      // ═══════════════════════════════════════════════════════════════════════════
      // SECURITY - Cybersecurity
      // ═══════════════════════════════════════════════════════════════════════════
      rssi: {
        title: 'CISO',
        description: 'Chief Information Security Officer',
        feature1: 'Security posture',
        feature2: 'Vulnerability management',
        feature3: 'NIS 2 / ISO 27001 compliance'
      },
      analyteSoc: {
        title: 'SOC Analyst',
        description: 'Threat monitoring, detection and security incident response',
        feature1: 'Security alerts and incidents',
        feature2: 'Forensic analysis',
        feature3: 'Threat intelligence'
      },

      // ═══════════════════════════════════════════════════════════════════════════
      // LEGAL - Compliance and regulations
      // ═══════════════════════════════════════════════════════════════════════════
      dpo: {
        title: 'DPO',
        description: 'Data Protection Officer - Personal data protection and privacy',
        feature1: 'GDPR compliance',
        feature2: 'Processing registry',
        feature3: 'Data subject rights'
      },
      responsableConformite: {
        title: 'Compliance Officer',
        description: 'EU regulatory compliance: NIS2, AI Act, DORA and industry standards',
        feature1: 'AI Act & EU regulations',
        feature2: 'Audits and certifications',
        feature3: 'Legal risk management'
      },

      // ═══════════════════════════════════════════════════════════════════════════
      // GREENOPS - Sustainability and environment
      // ═══════════════════════════════════════════════════════════════════════════
      responsableRse: {
        title: 'CSR / Sustainability Manager',
        description: 'Corporate Social Responsibility, environmental impact and ESG/CSRD reporting',
        feature1: 'Carbon footprint',
        feature2: 'Sustainability KPIs',
        feature3: 'CSRD / ESG reporting'
      },
      greenItManager: {
        title: 'Green IT Manager',
        description: 'IT energy efficiency, datacenter PUE and responsible digital',
        feature1: 'PUE and energy consumption',
        feature2: 'Cloud carbon footprint',
        feature3: 'Resource optimization'
      }
    },

    // Impact Analysis
    impactAnalysis: {
      title: 'Impact & Recommendations',
      subtitle: 'Impact analysis and personalized AI recommendations',
      summary: {
        totalImpacts: 'Identified impacts',
        criticalItems: 'Critical items',
        estimatedSavings: 'Potential savings',
        riskReduction: 'Risk reduction',
        actionItems: 'Recommended actions'
      },
      categories: {
        financial: 'Financial',
        operational: 'Operational',
        security: 'Security',
        compliance: 'Compliance',
        performance: 'Performance'
      },
      priority: {
        critical: 'Critical',
        high: 'High',
        medium: 'Medium',
        low: 'Low'
      },
      aiInsight: 'AI Analysis',
      recommendations: 'Recommendations',
      affectedSystems: 'Affected systems',
      timeToImplement: 'Time to implement',
      roi: 'Return on investment',
      createAction: 'Create action',
      viewDetails: 'View details',
      exportReport: 'Export report'
    },

    // Command Center
    commandCenter: {
      title: 'Command Center',
      subtitle: 'System health overview and alerts',
      quickAccess: 'Quick Access',
      keyMetrics: 'Key Metrics',
      quickNav: {
        technical: {
          title: 'Technical View',
          description: 'Infrastructure, services and pipelines'
        },
        business: {
          title: 'Business KPIs',
          description: 'OEE, production and financial impact'
        },
        security: {
          title: 'Security',
          description: 'Vulnerabilities and compliance'
        },
        observability: {
          title: 'Observability',
          description: 'Incidents and remediation'
        }
      },
      systemHealth: {
        title: 'System Health',
        subtitle: 'Backend services status',
        overall: 'Overall Score',
        servicesHealthy: 'services healthy',
        backendServices: 'Backend Services'
      },
      alerts: {
        title: 'Alerts',
        active: 'active',
        noAlerts: 'No active alerts'
      },
      aiAssistant: {
        title: 'AI Assistant',
        description: 'Ask questions in natural language'
      }
    },

    // Technical View
    technicalView: {
      title: 'Technical View',
      subtitle: 'Infrastructure, backend services and data pipelines',
      pipeline: {
        title: 'Data Pipeline',
        subtitle: 'Collection to storage flow'
      },
      backends: {
        title: 'Backend Services'
      },
      throughput: {
        title: 'Throughput',
        subtitle: 'Metrics, logs and traces per hour'
      }
    },

    // Business KPI View
    businessKPI: {
      title: 'Business KPIs',
      subtitle: 'Production performance, quality and financial impact',
      period: {
        today: 'Today',
        week: 'Week',
        month: 'Month'
      },
      oee: {
        title: 'Overall OEE',
        subtitle: 'Overall Equipment Effectiveness',
        components: 'OEE Components',
        componentsSubtitle: 'Availability × Performance × Quality',
        trend: 'OEE Trend',
        trendSubtitle: 'Evolution over the last 24 hours'
      },
      financial: {
        title: 'Financial Impact',
        subtitle: 'Revenue and production costs'
      },
      production: {
        byProduct: 'Production by Product',
        distribution: 'Production distribution'
      },
      equipment: {
        status: 'Equipment Status',
        statusSubtitle: 'Production lines'
      },
      maintenance: {
        title: 'Maintenance',
        subtitle: 'Planning and history'
      }
    },

    // AI Assistant
    aiAssistant: {
      title: 'AI Assistant',
      subtitle: 'Ask questions in natural language',
      online: 'Online',
      welcome: 'How can I help you?',
      welcomeDescription: 'I can analyze your data, generate reports and answer your questions about production, infrastructure and security.',
      suggestions: 'Suggestions',
      quickActions: 'Quick actions',
      placeholder: 'Ask your question...'
    },

    // Security & Compliance
    security: {
      title: 'Security & Compliance',
      description: 'Risk management, compliance auditing and AI insights',
      tabs: {
        overview: 'Overview',
        compliance: 'Compliance',
        euRegulations: 'EU Regulations',
        vulnerabilities: 'Vulnerabilities',
        aiInsights: 'AI Insights',
        audit: 'Audit',
        policies: 'Policies',
        video: 'Video Surveillance'
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
      },
      // Video Surveillance
      video: {
        cameras: 'Cameras',
        online: 'Online',
        offline: 'Offline',
        recording: 'Recording',
        lastMotion: 'Last motion',
        alerts: 'alerts',
        totalAlerts: 'Total Alerts',
        liveFeeds: 'Live Feeds',
        allCameras: 'All cameras',
        onlineOnly: 'Online only',
        withAlerts: 'With alerts',
        fullscreen: 'Fullscreen',
        recentEvents: 'Recent Events',
        viewRecording: 'View Recording',
        storage: 'Storage',
        of: 'of',
        retention: 'Retention',
        days: 'days',
        bandwidth: 'Bandwidth'
      },
      // EU Regulations (AI Act & NIS 2)
      euReg: {
        inProgress: 'In Progress',
        aiActDesc: 'European regulation on artificial intelligence',
        nis2Desc: 'European directive on network and information systems security',
        aiSystems: 'AI Systems',
        highRisk: 'High Risk',
        requirements: 'Requirements',
        compliantReq: 'Compliant',
        aiActTitle: 'AI Act - AI Systems Classification',
        assessRisk: 'Assess Risk',
        unacceptable: 'Unacceptable',
        highRiskCat: 'High Risk',
        limited: 'Limited Risk',
        minimal: 'Minimal Risk',
        systems: 'systems',
        aiInventory: 'AI Systems Inventory',
        provider: 'Provider',
        useCases: 'Use Cases',
        aiActRequirements: 'AI Act Requirements',
        deadline: 'Deadline',
        nis2Title: 'NIS 2 - Cybersecurity',
        entityType: 'Entity Type',
        essential: 'Essential Entity',
        sector: 'Sector',
        manufacturing: 'Manufacturing',
        notifyDelay: 'Notification Delay',
        authority: 'Competent Authority',
        nis2Requirements: 'NIS 2 Requirements',
        nis2Incidents: 'NIS 2 Incidents',
        resolved: 'Resolved',
        active: 'Active',
        reportedToANSSI: 'Reported to ANSSI',
        detection: 'Detection',
        resolution: 'Resolution',
        impact: 'Impact',
        risk: {
          minimal: 'Minimal Risk',
          limited: 'Limited Risk',
          high: 'High Risk',
          unacceptable: 'Unacceptable'
        },
        priority: {
          critical: 'Critical',
          high: 'High',
          medium: 'Medium'
        },
        impactLevel: {
          low: 'Low',
          medium: 'Medium',
          high: 'High'
        }
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
      persona: 'Profiel',
      changePersona: 'Profiel wijzigen',
      main: {
        home: 'Home',
        globalView: 'Globaal Overzicht',
        commandCenter: 'Commandocentrum',
        technicalView: 'Technisch Overzicht',
        businessKPI: 'Zakelijke KPIs',
        aiAssistant: 'AI Assistent',
        impactAnalysis: 'Impact & Aanbevelingen',
        impactChain: 'IT/OT Impactketen',
        simulators: 'Simulator Launcher',
        industrialObs: 'Industriele Observabiliteit',
        correlation: 'IT-OT-AI Correlatie',
        cybersecurityOT: 'OT/IT Cyberbeveiliging',
        aiObservability: 'AI Observabiliteit',
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

    // Welcome/Onboarding Page
    welcome: {
      title: 'Welkom bij Synapsix',
      subtitle: 'Industrieel Observabiliteitsplatform',
      tagline: 'Aangedreven door AI',
      selectPersona: 'Selecteer uw profiel om uw ervaring te personaliseren',
      continue: 'Doorgaan',
      skip: 'Deze stap overslaan',
      hint: 'U kunt uw profiel op elk moment wijzigen in instellingen'
    },

    // Personas
    personas: {
      operationsManager: {
        title: 'Operations Manager',
        description: 'Toezicht op productielijnen en apparatuurbeheer',
        feature1: 'Realtime OEE tracking',
        feature2: 'Kritieke apparatuurwaarschuwingen',
        feature3: 'Onderhoudsplanning'
      },
      plantDirector: {
        title: 'Fabrieksdirecteur',
        description: 'Strategische visie en financiele KPIs',
        feature1: 'Executive dashboards',
        feature2: 'Productie financiele impact',
        feature3: 'Trends en voorspellingen'
      },
      devopsEngineer: {
        title: 'DevOps Engineer',
        description: 'Infrastructuur en datapipelines',
        feature1: 'Service gezondheid',
        feature2: 'Pipeline monitoring',
        feature3: 'Prestatieanalyse'
      },
      securityAnalyst: {
        title: 'Beveiligingsanalist',
        description: 'Bedreigingen en kwetsbaarheden monitoring',
        feature1: 'Beveiligingswaarschuwingen',
        feature2: 'Anomaliedetectie',
        feature3: 'Toegangsauditing'
      },
      complianceOfficer: {
        title: 'Compliance Officer',
        description: 'Wettelijke naleving en beleid',
        feature1: 'Compliance status',
        feature2: 'Audit rapporten',
        feature3: 'Beleidsbeheer'
      },
      dataAnalyst: {
        title: 'Data Analist',
        description: 'Metrieken en loganalyse',
        feature1: 'Data exploratie',
        feature2: 'Patroondetectie',
        feature3: 'Export en rapporten'
      }
    },

    // Command Center
    commandCenter: {
      title: 'Commandocentrum',
      subtitle: 'Overzicht systeemgezondheid en waarschuwingen',
      quickAccess: 'Snelle Toegang',
      keyMetrics: 'Belangrijke Metrieken',
      quickNav: {
        technical: {
          title: 'Technisch Overzicht',
          description: 'Infrastructuur, services en pipelines'
        },
        business: {
          title: 'Zakelijke KPIs',
          description: 'OEE, productie en financiele impact'
        },
        security: {
          title: 'Beveiliging',
          description: 'Kwetsbaarheden en compliance'
        },
        observability: {
          title: 'Observabiliteit',
          description: 'Incidenten en remediatie'
        }
      },
      systemHealth: {
        title: 'Systeemgezondheid',
        subtitle: 'Backend services status',
        overall: 'Totaalscore',
        servicesHealthy: 'services gezond',
        backendServices: 'Backend Services'
      },
      alerts: {
        title: 'Waarschuwingen',
        active: 'actief',
        noAlerts: 'Geen actieve waarschuwingen'
      },
      aiAssistant: {
        title: 'AI Assistent',
        description: 'Stel vragen in natuurlijke taal'
      }
    },

    // Technical View
    technicalView: {
      title: 'Technisch Overzicht',
      subtitle: 'Infrastructuur, backend services en datapipelines',
      pipeline: {
        title: 'Datapipeline',
        subtitle: 'Collectie naar opslag stroom'
      },
      backends: {
        title: 'Backend Services'
      },
      throughput: {
        title: 'Doorvoer',
        subtitle: 'Metrieken, logs en traces per uur'
      }
    },

    // Business KPI View
    businessKPI: {
      title: 'Zakelijke KPIs',
      subtitle: 'Productieprestaties, kwaliteit en financiele impact',
      period: {
        today: 'Vandaag',
        week: 'Week',
        month: 'Maand'
      },
      oee: {
        title: 'Totale OEE',
        subtitle: 'Algehele Apparatuur Effectiviteit',
        components: 'OEE Componenten',
        componentsSubtitle: 'Beschikbaarheid × Prestatie × Kwaliteit',
        trend: 'OEE Trend',
        trendSubtitle: 'Evolutie over de laatste 24 uur'
      },
      financial: {
        title: 'Financiele Impact',
        subtitle: 'Omzet en productiekosten'
      },
      production: {
        byProduct: 'Productie per Product',
        distribution: 'Productieverdeling'
      },
      equipment: {
        status: 'Apparatuurstatus',
        statusSubtitle: 'Productielijnen'
      },
      maintenance: {
        title: 'Onderhoud',
        subtitle: 'Planning en geschiedenis'
      }
    },

    // AI Assistant
    aiAssistant: {
      title: 'AI Assistent',
      subtitle: 'Stel vragen in natuurlijke taal',
      online: 'Online',
      welcome: 'Hoe kan ik u helpen?',
      welcomeDescription: 'Ik kan uw gegevens analyseren, rapporten genereren en uw vragen over productie, infrastructuur en beveiliging beantwoorden.',
      suggestions: 'Suggesties',
      quickActions: 'Snelle acties',
      placeholder: 'Stel uw vraag...'
    },

    // Security & Compliance
    security: {
      title: 'Beveiliging & Compliance',
      description: 'Risicobeheer, compliance-auditing en AI-inzichten',
      tabs: {
        overview: 'Overzicht',
        compliance: 'Compliance',
        euRegulations: 'EU Regelgeving',
        vulnerabilities: 'Kwetsbaarheden',
        aiInsights: 'AI Inzichten',
        audit: 'Audit',
        policies: 'Beleid',
        video: 'Videobewaking'
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
      },
      // Video Surveillance
      video: {
        cameras: 'Camera\'s',
        online: 'Online',
        offline: 'Offline',
        recording: 'Opname',
        lastMotion: 'Laatste beweging',
        alerts: 'waarschuwingen',
        totalAlerts: 'Totaal Waarschuwingen',
        liveFeeds: 'Live Feeds',
        allCameras: 'Alle camera\'s',
        onlineOnly: 'Alleen online',
        withAlerts: 'Met waarschuwingen',
        fullscreen: 'Volledig scherm',
        recentEvents: 'Recente Gebeurtenissen',
        viewRecording: 'Bekijk Opname',
        storage: 'Opslag',
        of: 'van',
        retention: 'Bewaartijd',
        days: 'dagen',
        bandwidth: 'Bandbreedte'
      },
      // EU Regulations (AI Act & NIS 2)
      euReg: {
        inProgress: 'In Behandeling',
        aiActDesc: 'Europese verordening inzake kunstmatige intelligentie',
        nis2Desc: 'Europese richtlijn over netwerk- en informatiesysteembeveiliging',
        aiSystems: 'AI Systemen',
        highRisk: 'Hoog Risico',
        requirements: 'Vereisten',
        compliantReq: 'Conform',
        aiActTitle: 'AI Act - AI Systeem Classificatie',
        assessRisk: 'Risico Beoordelen',
        unacceptable: 'Onacceptabel',
        highRiskCat: 'Hoog Risico',
        limited: 'Beperkt Risico',
        minimal: 'Minimaal Risico',
        systems: 'systemen',
        aiInventory: 'AI Systemen Inventaris',
        provider: 'Aanbieder',
        useCases: 'Toepassingen',
        aiActRequirements: 'AI Act Vereisten',
        deadline: 'Deadline',
        nis2Title: 'NIS 2 - Cyberbeveiliging',
        entityType: 'Entiteitstype',
        essential: 'Essentiële Entiteit',
        sector: 'Sector',
        manufacturing: 'Productie',
        notifyDelay: 'Meldingstermijn',
        authority: 'Bevoegde Autoriteit',
        nis2Requirements: 'NIS 2 Vereisten',
        nis2Incidents: 'NIS 2 Incidenten',
        resolved: 'Opgelost',
        active: 'Actief',
        reportedToANSSI: 'Gemeld bij ANSSI',
        detection: 'Detectie',
        resolution: 'Oplossing',
        impact: 'Impact',
        risk: {
          minimal: 'Minimaal Risico',
          limited: 'Beperkt Risico',
          high: 'Hoog Risico',
          unacceptable: 'Onacceptabel'
        },
        priority: {
          critical: 'Kritiek',
          high: 'Hoog',
          medium: 'Gemiddeld'
        },
        impactLevel: {
          low: 'Laag',
          medium: 'Gemiddeld',
          high: 'Hoog'
        }
      }
    }
  },

  // ===========================================
  // GERMAN (DE)
  // ===========================================
  [LANGUAGES.DE]: {
    // App branding
    app: {
      name: 'Synapsix',
      tagline: 'Industrielle Observability',
      description: 'Einheitliches industrielles Observability-Dashboard'
    },

    // Common actions
    common: {
      back: 'Zurück',
      refresh: 'Aktualisieren',
      save: 'Speichern',
      cancel: 'Abbrechen',
      close: 'Schließen',
      search: 'Suchen',
      filter: 'Filtern',
      export: 'Exportieren',
      settings: 'Einstellungen',
      notifications: 'Benachrichtigungen',
      loading: 'Laden...',
      error: 'Fehler',
      success: 'Erfolg',
      warning: 'Warnung',
      info: 'Information',
      viewAll: 'Alle anzeigen',
      viewMore: 'Mehr anzeigen',
      viewLess: 'Weniger anzeigen'
    },

    // Connection status
    connection: {
      realtime: 'Echtzeit',
      offline: 'Offline',
      connected: 'Verbunden',
      disconnected: 'Getrennt',
      reconnecting: 'Verbindung wird wiederhergestellt...'
    },

    // User modes/profiles
    profiles: {
      title: 'Benutzerprofil',
      business: {
        name: 'Business',
        label: 'Business-Pfad',
        description: 'Geschäftsansicht und Produktionsindikatoren'
      },
      tech: {
        name: 'Tech',
        label: 'Technischer Pfad',
        description: 'Technische Ansicht und Systemmetriken'
      },
      modeLabel: {
        business: 'Business-Modus',
        tech: 'Tech-Modus'
      }
    },

    // Navigation - Main menu
    nav: {
      persona: 'Profil',
      changePersona: 'Profil wechseln',
      main: {
        home: 'Startseite',
        globalView: 'Globale Ansicht',
        commandCenter: 'Kommandozentrale',
        technicalView: 'Technische Ansicht',
        businessKPI: 'Business-KPIs',
        aiAssistant: 'KI-Assistent',
        impactAnalysis: 'Impact & Empfehlungen',
        impactChain: 'IT/OT Impact-Kette',
        simulators: 'Simulator Launcher',
        industrialObs: 'Industrielle Observability',
        correlation: 'IT-OT-KI Korrelation',
        cybersecurityOT: 'OT/IT Cybersicherheit',
        aiObservability: 'KI Observability',
        grafana: 'Grafana',
        opensearch: 'OpenSearch',
        kafka: 'Kafka',
        observability: 'Observability',
        security: 'Sicherheit & Compliance'
      },
      // Home page submenus
      home: {
        title: 'Dashboard',
        overview: 'Übersicht',
        quickStats: 'Schnellstatistiken',
        recentActivity: 'Letzte Aktivität',
        favorites: 'Favoriten'
      },
      // Business profile menu items
      business: {
        title: 'Business-Menü',
        production: 'Produktion',
        quality: 'Qualität',
        performance: 'Leistung',
        equipment: 'Ausrüstung',
        alarms: 'Alarme',
        reports: 'Berichte',
        kpis: 'KPIs',
        trends: 'Trends',
        analytics: 'Analytik'
      },
      // Tech profile menu items
      tech: {
        title: 'Technisches Menü',
        metrics: 'Metriken',
        logs: 'Logs',
        traces: 'Traces',
        infrastructure: 'Infrastruktur',
        services: 'Dienste',
        databases: 'Datenbanken',
        monitoring: 'Überwachung',
        alerts: 'Warnungen',
        performance: 'Leistung'
      }
    },

    // Business metrics
    metrics: {
      business: {
        oee: 'Gesamt-OEE',
        oeeDescription: 'Gesamtanlageneffektivität',
        availability: 'Verfügbarkeit',
        performance: 'Leistung',
        quality: 'Qualität',
        qualityRate: 'Qualitätsrate',
        productionToday: 'Produktion heute',
        cycleTime: 'Zykluszeit',
        defectsToday: 'Defekte heute',
        criticalAlarms: 'Kritische Alarme',
        equipmentStatus: 'Anlagenstatus',
        productionByProduct: 'Produktion nach Produkt',
        oeeTrend: 'OEE-Trend (24h)',
        running: 'Läuft',
        stopped: 'Gestoppt',
        maintenance: 'Wartung',
        error: 'Fehler'
      },
      tech: {
        metricsRate: 'Metriken/s',
        logsRate: 'Logs/s',
        tracesRate: 'Traces/s',
        latencyP95: 'Latenz P95',
        errorRate: 'Fehlerrate',
        kafkaThroughput: 'Kafka-Durchsatz',
        cpu: 'CPU',
        memory: 'Speicher',
        disk: 'Festplatte',
        activeSeries: 'Aktive Serien',
        storage: 'Speicherplatz',
        queryLatency: 'Abfragelatenz',
        documents: 'Dokumente',
        health: 'Zustand',
        nodes: 'Knoten',
        topics: 'Topics',
        partitions: 'Partitionen',
        consumerLag: 'Consumer-Lag'
      }
    },

    // Service pages
    services: {
      grafana: {
        title: 'Grafana',
        description: 'Visualisierung und Dashboards',
        dashboards: 'Dashboards',
        explore: 'Erkunden',
        alerting: 'Alerting'
      },
      opensearch: {
        title: 'OpenSearch',
        description: 'Log-Suche und -Analyse',
        discover: 'Entdecken',
        indices: 'Indizes',
        queries: 'Abfragen'
      },
      kafka: {
        title: 'Kafka',
        description: 'Daten-Streaming',
        topics: 'Topics',
        consumers: 'Consumers',
        producers: 'Producers'
      },
      victoriametrics: {
        title: 'VictoriaMetrics',
        description: 'Metrikenspeicherung'
      }
    },

    // Time and date
    time: {
      lastUpdate: 'Letzte Aktualisierung',
      now: 'Jetzt',
      today: 'Heute',
      yesterday: 'Gestern',
      thisWeek: 'Diese Woche',
      thisMonth: 'Dieser Monat',
      custom: 'Benutzerdefiniert'
    },

    // Errors and messages
    messages: {
      noData: 'Keine Daten verfügbar',
      loadingError: 'Ladefehler',
      connectionLost: 'Verbindung verloren',
      tryAgain: 'Erneut versuchen'
    },

    // Observability & Remediation
    observability: {
      title: 'Observability & Behebung',
      description: 'SLO-Überwachung, Vorfallmanagement und Behebungsautomatisierung',
      tabs: {
        overview: 'Übersicht',
        incidents: 'Vorfälle',
        runbooks: 'Runbooks',
        history: 'Verlauf'
      },
      // Metrics
      sloCompliance: 'SLO-Compliance',
      activeIncidents: 'Aktive Vorfälle',
      mttr: 'Durchschn. MTTR',
      mttd: 'Durchschn. MTTD',
      automationRate: 'Automatisierungsgrad',
      // SLO
      sloStatus: 'SLO-Status',
      current: 'Aktuell',
      target: 'Ziel',
      errorBudget: 'Fehlerbudget',
      remaining: 'verbleibend',
      // Incidents
      allActiveIncidents: 'Alle aktiven Vorfälle',
      noActiveIncidents: 'Keine aktiven Vorfälle',
      allSystemsOperational: 'Alle Systeme arbeiten normal',
      allSeverities: 'Alle Schweregrade',
      critical: 'Kritisch',
      warning: 'Warnung',
      allServices: 'Alle Dienste',
      viewRunbook: 'Runbook anzeigen',
      remediationActions: 'Behebungsmaßnahmen',
      runNextStep: 'Nächsten Schritt ausführen',
      pauseRemediation: 'Pause',
      escalate: 'Eskalieren',
      // Runbooks
      remediationRunbooks: 'Behebungs-Runbooks',
      createRunbook: 'Runbook erstellen',
      executions: 'Ausführungen',
      avgMTTR: 'Durchschn. MTTR',
      triggers: 'Auslöser',
      steps: 'Schritte',
      automated: 'Automatisiert',
      manual: 'Manuell',
      executeRunbook: 'Runbook ausführen',
      // History
      remediationHistory: 'Behebungsverlauf',
      last24h: 'Letzte 24h',
      last7d: 'Letzte 7 Tage',
      last30d: 'Letzte 30 Tage',
      runbook: 'Runbook',
      service: 'Dienst',
      trigger: 'Auslöser',
      duration: 'Dauer',
      status: 'Status',
      progress: 'Fortschritt',
      // Charts
      mttrTrend: 'MTTR/MTTD-Trend',
      incidentTrend: 'Vorfalltrend',
      minutes: 'Minuten',
      autoResolved: 'Automatisch behoben',
      manualResolved: 'Manuell behoben',
      // Actions
      quickActions: 'Schnellaktionen'
    },

    // Welcome/Onboarding Page
    welcome: {
      title: 'Willkommen bei Synapsix',
      subtitle: 'Industrielle Observability-Plattform',
      tagline: 'KI-gestützt',
      selectPersona: 'Wählen Sie Ihr Profil, um Ihre Erfahrung zu personalisieren',
      continue: 'Weiter',
      skip: 'Diesen Schritt überspringen',
      hint: 'Sie können Ihr Profil jederzeit in den Einstellungen ändern'
    },

    // Personas
    personas: {
      operationsManager: {
        title: 'Betriebsleiter',
        description: 'Überwachung der Produktionslinien und Anlagenverwaltung',
        feature1: 'OEE-Tracking in Echtzeit',
        feature2: 'Kritische Anlagenwarnungen',
        feature3: 'Wartungsplanung'
      },
      plantDirector: {
        title: 'Werksleiter',
        description: 'Strategische Vision und finanzielle KPIs',
        feature1: 'Executive-Dashboards',
        feature2: 'Finanzielle Auswirkungen der Produktion',
        feature3: 'Trends und Prognosen'
      },
      devopsEngineer: {
        title: 'DevOps-Ingenieur',
        description: 'Infrastruktur und Datenpipelines',
        feature1: 'Service-Zustand',
        feature2: 'Pipeline-Überwachung',
        feature3: 'Leistungsanalyse'
      },
      securityAnalyst: {
        title: 'Sicherheitsanalyst',
        description: 'Überwachung von Bedrohungen und Schwachstellen',
        feature1: 'Sicherheitswarnungen',
        feature2: 'Anomalieerkennung',
        feature3: 'Zugriffsaudits'
      },
      complianceOfficer: {
        title: 'Compliance-Beauftragter',
        description: 'Regulatorische Compliance und Richtlinien',
        feature1: 'Compliance-Status',
        feature2: 'Audit-Berichte',
        feature3: 'Richtlinienverwaltung'
      },
      dataAnalyst: {
        title: 'Datenanalyst',
        description: 'Analyse von Metriken und Logs',
        feature1: 'Datenexploration',
        feature2: 'Mustererkennung',
        feature3: 'Export und Berichte'
      }
    },

    // Command Center
    commandCenter: {
      title: 'Kommandozentrale',
      subtitle: 'Übersicht über Systemzustand und Warnungen',
      quickAccess: 'Schnellzugriff',
      keyMetrics: 'Wichtige Metriken',
      quickNav: {
        technical: {
          title: 'Technische Ansicht',
          description: 'Infrastruktur, Dienste und Pipelines'
        },
        business: {
          title: 'Business-KPIs',
          description: 'OEE, Produktion und finanzielle Auswirkungen'
        },
        security: {
          title: 'Sicherheit',
          description: 'Schwachstellen und Compliance'
        },
        observability: {
          title: 'Observability',
          description: 'Vorfälle und Behebung'
        }
      },
      systemHealth: {
        title: 'Systemzustand',
        subtitle: 'Backend-Dienste-Status',
        overall: 'Gesamtbewertung',
        servicesHealthy: 'Dienste funktionsfähig',
        backendServices: 'Backend-Dienste'
      },
      alerts: {
        title: 'Warnungen',
        active: 'aktiv',
        noAlerts: 'Keine aktiven Warnungen'
      },
      aiAssistant: {
        title: 'KI-Assistent',
        description: 'Stellen Sie Fragen in natürlicher Sprache'
      }
    },

    // Technical View
    technicalView: {
      title: 'Technische Ansicht',
      subtitle: 'Infrastruktur, Backend-Dienste und Datenpipelines',
      pipeline: {
        title: 'Datenpipeline',
        subtitle: 'Erfassung bis Speicherung'
      },
      backends: {
        title: 'Backend-Dienste'
      },
      throughput: {
        title: 'Durchsatz',
        subtitle: 'Metriken, Logs und Traces pro Stunde'
      }
    },

    // Business KPI View
    businessKPI: {
      title: 'Business-KPIs',
      subtitle: 'Produktionsleistung, Qualität und finanzielle Auswirkungen',
      period: {
        today: 'Heute',
        week: 'Woche',
        month: 'Monat'
      },
      oee: {
        title: 'Gesamt-OEE',
        subtitle: 'Gesamtanlageneffektivität',
        components: 'OEE-Komponenten',
        componentsSubtitle: 'Verfügbarkeit × Leistung × Qualität',
        trend: 'OEE-Trend',
        trendSubtitle: 'Entwicklung der letzten 24 Stunden'
      },
      financial: {
        title: 'Finanzielle Auswirkungen',
        subtitle: 'Umsatz und Produktionskosten'
      },
      production: {
        byProduct: 'Produktion nach Produkt',
        distribution: 'Produktionsverteilung'
      },
      equipment: {
        status: 'Anlagenstatus',
        statusSubtitle: 'Produktionslinien'
      },
      maintenance: {
        title: 'Wartung',
        subtitle: 'Planung und Verlauf'
      }
    },

    // AI Assistant
    aiAssistant: {
      title: 'KI-Assistent',
      subtitle: 'Stellen Sie Fragen in natürlicher Sprache',
      online: 'Online',
      welcome: 'Wie kann ich Ihnen helfen?',
      welcomeDescription: 'Ich kann Ihre Daten analysieren, Berichte erstellen und Ihre Fragen zu Produktion, Infrastruktur und Sicherheit beantworten.',
      suggestions: 'Vorschläge',
      quickActions: 'Schnellaktionen',
      placeholder: 'Stellen Sie Ihre Frage...'
    },

    // Security & Compliance
    security: {
      title: 'Sicherheit & Compliance',
      description: 'Risikomanagement, Compliance-Audits und KI-Erkenntnisse',
      tabs: {
        overview: 'Übersicht',
        compliance: 'Compliance',
        euRegulations: 'EU-Vorschriften',
        vulnerabilities: 'Schwachstellen',
        aiInsights: 'KI-Erkenntnisse',
        audit: 'Audit',
        policies: 'Richtlinien',
        video: 'Videoüberwachung'
      },
      // Metrics
      overallScore: 'Gesamtbewertung',
      criticalVulns: 'Kritische Schwachstellen',
      openVulns: 'Offene Schwachstellen',
      aiAlerts: 'KI-Warnungen',
      activePolicies: 'Aktive Richtlinien',
      // Compliance
      complianceOverview: 'Compliance-Übersicht',
      complianceFrameworks: 'Compliance-Frameworks',
      compliant: 'Konform',
      partial: 'Teilweise',
      nonCompliant: 'Nicht konform',
      controls: 'Kontrollen',
      passed: 'Bestanden',
      failed: 'Fehlgeschlagen',
      nextAudit: 'Nächstes Audit',
      lastAudit: 'Letztes Audit',
      auditTimeline: 'Audit-Zeitplan',
      generateReport: 'Bericht erstellen',
      // Vulnerabilities
      allVulnerabilities: 'Alle Schwachstellen',
      recentVulnerabilities: 'Aktuelle Schwachstellen',
      vulnDistribution: 'Schwachstellenverteilung',
      allSeverities: 'Alle Schweregrade',
      critical: 'Kritisch',
      high: 'Hoch',
      medium: 'Mittel',
      low: 'Niedrig',
      allStatuses: 'Alle Status',
      statusOpen: 'Offen',
      statusInProgress: 'In Bearbeitung',
      statusPatched: 'Behoben',
      viewDetails: 'Details anzeigen',
      // Security
      securityTrend: 'Sicherheitstrend',
      securityScore: 'Sicherheitsbewertung',
      threatsDetected: 'Erkannte Bedrohungen',
      threatsBlocked: 'Blockierte Bedrohungen',
      exportReport: 'Bericht exportieren',
      runScan: 'Scan starten',
      // AI Insights
      latestAIInsights: 'Neueste KI-Erkenntnisse',
      aiSecurityInsights: 'KI-Sicherheitserkenntnisse',
      poweredByAI: 'KI-gestützt',
      confidence: 'Konfidenz',
      aiType: {
        anomaly: 'Anomalie',
        prediction: 'Vorhersage',
        optimization: 'Optimierung'
      },
      aiCapabilities: {
        anomalyDetection: 'Anomalieerkennung',
        anomalyDesc: 'Echtzeit-Erkennung verdächtigen Verhaltens',
        predictive: 'Prädiktive Analyse',
        predictiveDesc: 'Antizipation zukünftiger Risiken und Bedrohungen',
        optimization: 'Optimierung',
        optimizationDesc: 'Empfehlungen zur Verbesserung der Sicherheit'
      },
      // Audit
      auditTrail: 'Audit-Trail',
      auditId: 'ID',
      action: 'Aktion',
      user: 'Benutzer',
      resource: 'Ressource',
      ipAddress: 'IP-Adresse',
      timestamp: 'Zeitstempel',
      // Policies
      securityPolicies: 'Sicherheitsrichtlinien',
      managePolicies: 'Richtlinien verwalten',
      compliance: 'Compliance',
      violations: 'Verstöße',
      avgCompliance: 'Durchschnittliche Compliance',
      enforced: 'Durchgesetzt',
      totalViolations: 'Gesamtverstöße',
      policyStatus: {
        enforced: 'Durchgesetzt',
        partial: 'Teilweise',
        disabled: 'Deaktiviert'
      },
      // Video Surveillance
      video: {
        cameras: 'Kameras',
        online: 'Online',
        offline: 'Offline',
        recording: 'Aufnahme',
        lastMotion: 'Letzte Bewegung',
        alerts: 'Warnungen',
        totalAlerts: 'Gesamtwarnungen',
        liveFeeds: 'Live-Feeds',
        allCameras: 'Alle Kameras',
        onlineOnly: 'Nur online',
        withAlerts: 'Mit Warnungen',
        fullscreen: 'Vollbild',
        recentEvents: 'Aktuelle Ereignisse',
        viewRecording: 'Aufnahme ansehen',
        storage: 'Speicher',
        of: 'von',
        retention: 'Aufbewahrung',
        days: 'Tage',
        bandwidth: 'Bandbreite'
      },
      // EU Regulations (AI Act & NIS 2)
      euReg: {
        inProgress: 'In Bearbeitung',
        aiActDesc: 'Europäische Verordnung über künstliche Intelligenz',
        nis2Desc: 'Europäische Richtlinie über Netz- und Informationssicherheit',
        aiSystems: 'KI-Systeme',
        highRisk: 'Hohes Risiko',
        requirements: 'Anforderungen',
        compliantReq: 'Konform',
        aiActTitle: 'AI Act - KI-Systemklassifizierung',
        assessRisk: 'Risiko bewerten',
        unacceptable: 'Inakzeptabel',
        highRiskCat: 'Hohes Risiko',
        limited: 'Begrenztes Risiko',
        minimal: 'Minimales Risiko',
        systems: 'Systeme',
        aiInventory: 'KI-Systeme Inventar',
        provider: 'Anbieter',
        useCases: 'Anwendungsfälle',
        aiActRequirements: 'AI Act Anforderungen',
        deadline: 'Frist',
        nis2Title: 'NIS 2 - Cybersicherheit',
        entityType: 'Entitätstyp',
        essential: 'Wesentliche Entität',
        sector: 'Sektor',
        manufacturing: 'Produktion',
        notifyDelay: 'Meldefrist',
        authority: 'Zuständige Behörde',
        nis2Requirements: 'NIS 2 Anforderungen',
        nis2Incidents: 'NIS 2 Vorfälle',
        resolved: 'Gelöst',
        active: 'Aktiv',
        reportedToANSSI: 'An ANSSI gemeldet',
        detection: 'Erkennung',
        resolution: 'Lösung',
        impact: 'Auswirkung',
        risk: {
          minimal: 'Minimales Risiko',
          limited: 'Begrenztes Risiko',
          high: 'Hohes Risiko',
          unacceptable: 'Inakzeptabel'
        },
        priority: {
          critical: 'Kritisch',
          high: 'Hoch',
          medium: 'Mittel'
        },
        impactLevel: {
          low: 'Niedrig',
          medium: 'Mittel',
          high: 'Hoch'
        }
      }
    }
  }
}

export default translations
