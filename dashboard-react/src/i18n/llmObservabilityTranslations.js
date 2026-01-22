// LLM Observability Translations (FR/EN/NL/DE)
// To be merged with main translations

export const llmObservabilityTranslations = {
  // ===========================================
  // FRENCH (FR)
  // ===========================================
  fr: {
    llmObservability: {
      // Page titles
      title: 'Observabilit\u00e9 LLM',
      subtitle: 'Surveillance des mod\u00e8les de langage',
      dashboard: 'Dashboard LLM',

      // Metrics labels
      metrics: {
        latency: 'Latence',
        latencyAvg: 'Latence Moyenne',
        latencyP50: 'Latence P50',
        latencyP95: 'Latence P95',
        latencyP99: 'Latence P99',
        tokens: 'Tokens',
        tokensPrompt: 'Tokens Prompt',
        tokensCompletion: 'Tokens Compl\u00e9tion',
        tokensTotal: 'Tokens Total',
        tokensPerRequest: 'Tokens / Requ\u00eate',
        cost: 'Co\u00fbt',
        costTotal: 'Co\u00fbt Total',
        costHourly: 'Co\u00fbt / Heure',
        costDaily: 'Co\u00fbt / Jour',
        requests: 'Requ\u00eates',
        requestsTotal: 'Requ\u00eates Totales',
        requestsPerMinute: 'Requ\u00eates / Minute',
        requestsActive: 'Requ\u00eates Actives',
        successRate: 'Taux de Succ\u00e8s',
        errorRate: 'Taux d\'Erreur',
        provider: 'Fournisseur',
        model: 'Mod\u00e8le'
      },

      // Units
      units: {
        ms: 'ms',
        seconds: 's',
        tokens: 'tokens',
        usd: '$',
        percent: '%',
        perMinute: '/min',
        perHour: '/h'
      },

      // Status
      status: {
        healthy: 'Op\u00e9rationnel',
        degraded: 'D\u00e9grad\u00e9',
        down: 'Indisponible',
        unknown: 'Inconnu',
        enabled: 'Activ\u00e9',
        disabled: 'D\u00e9sactiv\u00e9'
      },

      // Alerts
      alerts: {
        title: 'Alertes LLM',
        noAlerts: 'Aucune alerte active',
        latencyWarning: 'Latence \u00e9lev\u00e9e d\u00e9tect\u00e9e',
        latencyCritical: 'Latence critique !',
        errorRateWarning: 'Taux d\'erreur \u00e9lev\u00e9',
        errorRateCritical: 'Taux d\'erreur critique !',
        costExceeded: 'Budget horaire d\u00e9pass\u00e9',
        tokenLimit: 'Limite de tokens atteinte',
        rateLimit: 'Limite de requ\u00eates proche',
        providerDown: 'Fournisseur indisponible'
      },

      // Alert severity
      severity: {
        critical: 'Critique',
        warning: 'Attention',
        info: 'Information'
      },

      // Providers
      providers: {
        mistral: 'Mistral AI',
        claude: 'Anthropic Claude',
        openai: 'OpenAI GPT',
        ollama: 'Ollama (Local)',
        azure: 'Azure OpenAI',
        unknown: 'Inconnu'
      },

      // Time windows
      timeWindow: {
        last5min: '5 derni\u00e8res minutes',
        last15min: '15 derni\u00e8res minutes',
        last1hour: 'Derni\u00e8re heure',
        last6hours: '6 derni\u00e8res heures',
        last24hours: '24 derni\u00e8res heures',
        custom: 'P\u00e9riode personnalis\u00e9e'
      },

      // Actions
      actions: {
        refresh: 'Actualiser',
        export: 'Exporter',
        configure: 'Configurer',
        viewDetails: 'Voir d\u00e9tails',
        acknowledge: 'Acquitter',
        dismiss: 'Ignorer'
      },

      // Error messages
      errors: {
        moduleNotAvailable: 'Module d\'observabilit\u00e9 LLM non disponible',
        noData: 'Aucune donn\u00e9e disponible',
        loadError: 'Erreur de chargement des m\u00e9triques',
        connectionError: 'Erreur de connexion au collecteur'
      },

      // Help text
      help: {
        latencyP95: '95% des requ\u00eates sont plus rapides que cette valeur',
        tokensUsage: 'Consommation de tokens pour la p\u00e9riode',
        costEstimate: 'Co\u00fbt estim\u00e9 bas\u00e9 sur les tarifs du fournisseur',
        errorRate: 'Pourcentage de requ\u00eates en \u00e9chec'
      },

      // Dashboard sections
      sections: {
        overview: 'Vue d\'ensemble',
        performance: 'Performance',
        usage: 'Utilisation',
        costs: 'Co\u00fbts',
        errors: 'Erreurs',
        byProvider: 'Par fournisseur',
        byModel: 'Par mod\u00e8le'
      }
    }
  },

  // ===========================================
  // ENGLISH (EN)
  // ===========================================
  en: {
    llmObservability: {
      title: 'LLM Observability',
      subtitle: 'Language model monitoring',
      dashboard: 'LLM Dashboard',

      metrics: {
        latency: 'Latency',
        latencyAvg: 'Average Latency',
        latencyP50: 'P50 Latency',
        latencyP95: 'P95 Latency',
        latencyP99: 'P99 Latency',
        tokens: 'Tokens',
        tokensPrompt: 'Prompt Tokens',
        tokensCompletion: 'Completion Tokens',
        tokensTotal: 'Total Tokens',
        tokensPerRequest: 'Tokens / Request',
        cost: 'Cost',
        costTotal: 'Total Cost',
        costHourly: 'Cost / Hour',
        costDaily: 'Cost / Day',
        requests: 'Requests',
        requestsTotal: 'Total Requests',
        requestsPerMinute: 'Requests / Minute',
        requestsActive: 'Active Requests',
        successRate: 'Success Rate',
        errorRate: 'Error Rate',
        provider: 'Provider',
        model: 'Model'
      },

      units: {
        ms: 'ms',
        seconds: 's',
        tokens: 'tokens',
        usd: '$',
        percent: '%',
        perMinute: '/min',
        perHour: '/h'
      },

      status: {
        healthy: 'Healthy',
        degraded: 'Degraded',
        down: 'Down',
        unknown: 'Unknown',
        enabled: 'Enabled',
        disabled: 'Disabled'
      },

      alerts: {
        title: 'LLM Alerts',
        noAlerts: 'No active alerts',
        latencyWarning: 'High latency detected',
        latencyCritical: 'Critical latency!',
        errorRateWarning: 'High error rate',
        errorRateCritical: 'Critical error rate!',
        costExceeded: 'Hourly budget exceeded',
        tokenLimit: 'Token limit reached',
        rateLimit: 'Rate limit approaching',
        providerDown: 'Provider unavailable'
      },

      severity: {
        critical: 'Critical',
        warning: 'Warning',
        info: 'Information'
      },

      providers: {
        mistral: 'Mistral AI',
        claude: 'Anthropic Claude',
        openai: 'OpenAI GPT',
        ollama: 'Ollama (Local)',
        azure: 'Azure OpenAI',
        unknown: 'Unknown'
      },

      timeWindow: {
        last5min: 'Last 5 minutes',
        last15min: 'Last 15 minutes',
        last1hour: 'Last hour',
        last6hours: 'Last 6 hours',
        last24hours: 'Last 24 hours',
        custom: 'Custom period'
      },

      actions: {
        refresh: 'Refresh',
        export: 'Export',
        configure: 'Configure',
        viewDetails: 'View details',
        acknowledge: 'Acknowledge',
        dismiss: 'Dismiss'
      },

      errors: {
        moduleNotAvailable: 'LLM Observability module not available',
        noData: 'No data available',
        loadError: 'Error loading metrics',
        connectionError: 'Collector connection error'
      },

      help: {
        latencyP95: '95% of requests are faster than this value',
        tokensUsage: 'Token consumption for the period',
        costEstimate: 'Estimated cost based on provider rates',
        errorRate: 'Percentage of failed requests'
      },

      sections: {
        overview: 'Overview',
        performance: 'Performance',
        usage: 'Usage',
        costs: 'Costs',
        errors: 'Errors',
        byProvider: 'By provider',
        byModel: 'By model'
      }
    }
  },

  // ===========================================
  // DUTCH (NL)
  // ===========================================
  nl: {
    llmObservability: {
      title: 'LLM Observability',
      subtitle: 'Taalmodel monitoring',
      dashboard: 'LLM Dashboard',

      metrics: {
        latency: 'Latentie',
        latencyAvg: 'Gemiddelde Latentie',
        latencyP50: 'P50 Latentie',
        latencyP95: 'P95 Latentie',
        latencyP99: 'P99 Latentie',
        tokens: 'Tokens',
        tokensPrompt: 'Prompt Tokens',
        tokensCompletion: 'Completion Tokens',
        tokensTotal: 'Totaal Tokens',
        tokensPerRequest: 'Tokens / Verzoek',
        cost: 'Kosten',
        costTotal: 'Totale Kosten',
        costHourly: 'Kosten / Uur',
        costDaily: 'Kosten / Dag',
        requests: 'Verzoeken',
        requestsTotal: 'Totaal Verzoeken',
        requestsPerMinute: 'Verzoeken / Minuut',
        requestsActive: 'Actieve Verzoeken',
        successRate: 'Succespercentage',
        errorRate: 'Foutpercentage',
        provider: 'Provider',
        model: 'Model'
      },

      units: {
        ms: 'ms',
        seconds: 's',
        tokens: 'tokens',
        usd: '$',
        percent: '%',
        perMinute: '/min',
        perHour: '/u'
      },

      status: {
        healthy: 'Gezond',
        degraded: 'Verminderd',
        down: 'Offline',
        unknown: 'Onbekend',
        enabled: 'Ingeschakeld',
        disabled: 'Uitgeschakeld'
      },

      alerts: {
        title: 'LLM Waarschuwingen',
        noAlerts: 'Geen actieve waarschuwingen',
        latencyWarning: 'Hoge latentie gedetecteerd',
        latencyCritical: 'Kritieke latentie!',
        errorRateWarning: 'Hoog foutpercentage',
        errorRateCritical: 'Kritiek foutpercentage!',
        costExceeded: 'Uurbudget overschreden',
        tokenLimit: 'Tokenlimiet bereikt',
        rateLimit: 'Verzoekenimiet nadert',
        providerDown: 'Provider niet beschikbaar'
      },

      severity: {
        critical: 'Kritiek',
        warning: 'Waarschuwing',
        info: 'Informatie'
      },

      providers: {
        mistral: 'Mistral AI',
        claude: 'Anthropic Claude',
        openai: 'OpenAI GPT',
        ollama: 'Ollama (Lokaal)',
        azure: 'Azure OpenAI',
        unknown: 'Onbekend'
      },

      timeWindow: {
        last5min: 'Laatste 5 minuten',
        last15min: 'Laatste 15 minuten',
        last1hour: 'Laatste uur',
        last6hours: 'Laatste 6 uur',
        last24hours: 'Laatste 24 uur',
        custom: 'Aangepaste periode'
      },

      actions: {
        refresh: 'Vernieuwen',
        export: 'Exporteren',
        configure: 'Configureren',
        viewDetails: 'Details bekijken',
        acknowledge: 'Bevestigen',
        dismiss: 'Negeren'
      },

      errors: {
        moduleNotAvailable: 'LLM Observability module niet beschikbaar',
        noData: 'Geen gegevens beschikbaar',
        loadError: 'Fout bij laden van metrics',
        connectionError: 'Collector verbindingsfout'
      },

      help: {
        latencyP95: '95% van de verzoeken is sneller dan deze waarde',
        tokensUsage: 'Tokengebruik voor de periode',
        costEstimate: 'Geschatte kosten op basis van providertarieven',
        errorRate: 'Percentage mislukte verzoeken'
      },

      sections: {
        overview: 'Overzicht',
        performance: 'Prestaties',
        usage: 'Gebruik',
        costs: 'Kosten',
        errors: 'Fouten',
        byProvider: 'Per provider',
        byModel: 'Per model'
      }
    }
  },

  // ===========================================
  // GERMAN (DE)
  // ===========================================
  de: {
    llmObservability: {
      title: 'LLM Observability',
      subtitle: 'Sprachmodell-\u00dcberwachung',
      dashboard: 'LLM Dashboard',

      metrics: {
        latency: 'Latenz',
        latencyAvg: 'Durchschnittliche Latenz',
        latencyP50: 'P50 Latenz',
        latencyP95: 'P95 Latenz',
        latencyP99: 'P99 Latenz',
        tokens: 'Tokens',
        tokensPrompt: 'Prompt Tokens',
        tokensCompletion: 'Completion Tokens',
        tokensTotal: 'Gesamt Tokens',
        tokensPerRequest: 'Tokens / Anfrage',
        cost: 'Kosten',
        costTotal: 'Gesamtkosten',
        costHourly: 'Kosten / Stunde',
        costDaily: 'Kosten / Tag',
        requests: 'Anfragen',
        requestsTotal: 'Gesamtanfragen',
        requestsPerMinute: 'Anfragen / Minute',
        requestsActive: 'Aktive Anfragen',
        successRate: 'Erfolgsrate',
        errorRate: 'Fehlerrate',
        provider: 'Anbieter',
        model: 'Modell'
      },

      units: {
        ms: 'ms',
        seconds: 's',
        tokens: 'Tokens',
        usd: '$',
        percent: '%',
        perMinute: '/Min',
        perHour: '/Std'
      },

      status: {
        healthy: 'Gesund',
        degraded: 'Beeintr\u00e4chtigt',
        down: 'Offline',
        unknown: 'Unbekannt',
        enabled: 'Aktiviert',
        disabled: 'Deaktiviert'
      },

      alerts: {
        title: 'LLM Warnungen',
        noAlerts: 'Keine aktiven Warnungen',
        latencyWarning: 'Hohe Latenz erkannt',
        latencyCritical: 'Kritische Latenz!',
        errorRateWarning: 'Hohe Fehlerrate',
        errorRateCritical: 'Kritische Fehlerrate!',
        costExceeded: 'St\u00fcndliches Budget \u00fcberschritten',
        tokenLimit: 'Token-Limit erreicht',
        rateLimit: 'Anfragelimit naht',
        providerDown: 'Anbieter nicht verf\u00fcgbar'
      },

      severity: {
        critical: 'Kritisch',
        warning: 'Warnung',
        info: 'Information'
      },

      providers: {
        mistral: 'Mistral AI',
        claude: 'Anthropic Claude',
        openai: 'OpenAI GPT',
        ollama: 'Ollama (Lokal)',
        azure: 'Azure OpenAI',
        unknown: 'Unbekannt'
      },

      timeWindow: {
        last5min: 'Letzte 5 Minuten',
        last15min: 'Letzte 15 Minuten',
        last1hour: 'Letzte Stunde',
        last6hours: 'Letzte 6 Stunden',
        last24hours: 'Letzte 24 Stunden',
        custom: 'Benutzerdefinierter Zeitraum'
      },

      actions: {
        refresh: 'Aktualisieren',
        export: 'Exportieren',
        configure: 'Konfigurieren',
        viewDetails: 'Details anzeigen',
        acknowledge: 'Best\u00e4tigen',
        dismiss: 'Verwerfen'
      },

      errors: {
        moduleNotAvailable: 'LLM Observability Modul nicht verf\u00fcgbar',
        noData: 'Keine Daten verf\u00fcgbar',
        loadError: 'Fehler beim Laden der Metriken',
        connectionError: 'Collector-Verbindungsfehler'
      },

      help: {
        latencyP95: '95% der Anfragen sind schneller als dieser Wert',
        tokensUsage: 'Token-Verbrauch f\u00fcr den Zeitraum',
        costEstimate: 'Gesch\u00e4tzte Kosten basierend auf Anbietertarifen',
        errorRate: 'Prozentsatz fehlgeschlagener Anfragen'
      },

      sections: {
        overview: '\u00dcbersicht',
        performance: 'Leistung',
        usage: 'Nutzung',
        costs: 'Kosten',
        errors: 'Fehler',
        byProvider: 'Nach Anbieter',
        byModel: 'Nach Modell'
      }
    }
  }
}

export default llmObservabilityTranslations
