# Documentation OOVMTEL

Plateforme d'observabilité industrielle haute performance pour environnements IT/OT critiques.

## Navigation Rapide

| Section | Description |
|---------|-------------|
| [Architecture](architecture/README.md) | Architecture technique et modes de déploiement |
| [Audits](audits/README.md) | Audits UX et observabilité |
| [Modules](GAME_CHANGER_MODULES.md) | Modules game-changer (NLP, RCA, Predictive) |

---

## Architecture

Documentation technique détaillée de la plateforme.

| Document | Description |
|----------|-------------|
| [Vue d'ensemble](architecture/SYSTEM_OVERVIEW.md) | Architecture globale et capacités |
| [Modes de déploiement](architecture/DEPLOYMENT_MODES.md) | Standard, Direct-OTLP, Sécurisé |
| [Pipelines OTEL](architecture/OTEL_PIPELINES.md) | Configuration OpenTelemetry |
| [Ports et réseau](architecture/NETWORK_PORTS.md) | Tableau des ports |
| [Stockage](architecture/STORAGE.md) | Volumes et persistance |

**Documents spécialisés :**
- [Architecture sécurisée IEC 62443](SECURE_ARCHITECTURE.md)
- [Architecture Direct-OTLP](DIRECT_OTLP_ARCHITECTURE.md)

---

## Audits

Évaluation de la plateforme et recommandations.

| Document | Score | Description |
|----------|-------|-------------|
| [Audit UX](audits/UX_AUDIT.md) | 7.2/10 | Expérience utilisateur, parcours, clarté |
| [Audit Observabilité](audits/OBSERVABILITY_AUDIT.md) | 8.5/10 | Stack technique, performance |

---

## Analyses

Études de marché et opportunités.

| Document | Description |
|----------|-------------|
| [Analyse parcours utilisateur](USER_JOURNEY_ANALYSIS.md) | Parcours par persona |
| [Analyse maturité solutions](SOLUTION_MATURITY_ANALYSIS.md) | Comparaison avec le marché |
| [Analyse gaps marché](MARKET_GAPS_ANALYSIS.md) | Opportunités de différenciation |
| [Opportunités no-code](NOCODE_OPPORTUNITY_ANALYSIS.md) | Potentiel no-code |
| [Alternatives Kafka](KAFKA_ALTERNATIVES_ANALYSIS.md) | Comparaison message brokers |

---

## Modules

Documentation des modules avancés.

| Document | Description |
|----------|-------------|
| [Modules Game-Changer](GAME_CHANGER_MODULES.md) | NLP, RCA, Predictive, Remediation, HPC |
| [LLM Observability](LLM_OBSERVABILITY.md) | Monitoring des modèles LLM |
| [Améliorations HPC](HPC_IMPROVEMENTS.md) | Module calcul haute performance |

---

## Démarrage Rapide

```bash
# Mode Standard (avec Kafka)
docker compose up -d

# Mode Direct-OTLP (léger)
docker compose -f docker-compose.direct-otlp.yml up -d

# Mode Sécurisé (IEC 62443)
./scripts/start.sh secure
```

## Accès aux Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Unified View | http://localhost:8085 | - |
| Grafana | http://localhost:3000 | admin / admin123 |
| OpenObserve | http://localhost:5080 | root@example.com / Complexpass#123 |
| OpenSearch Dashboards | http://localhost:5601 | - |
| Kafka UI | http://localhost:8090 | - |

---

## Références Externes

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [VictoriaMetrics Docs](https://docs.victoriametrics.com/)
- [OpenObserve Docs](https://openobserve.ai/docs/)
- [OpenSearch Documentation](https://opensearch.org/docs/)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [IEC 62443 Standard](https://www.iec.ch/cyber-security)
