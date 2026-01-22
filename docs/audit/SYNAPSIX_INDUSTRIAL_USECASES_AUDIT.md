# Audit Synapsix - Cas d'Usage Industriels

**Date:** 2026-01-22
**Version auditee:** 1.1.0
**Modules concernes:** `llm_observability`, `llm/prompts`, `dashboard-react`, `simulators`

---

## Table des matieres

1. [Synthese executive](#synthese-executive)
2. [Panorama des cas d'usage industriels](#panorama-des-cas-dusage-industriels)
3. [Analyse detaillee par cas d'usage](#analyse-detaillee-par-cas-dusage)
4. [Architecture de normalisation des donnees](#architecture-de-normalisation-des-donnees)
5. [Interface utilisateur industrielle](#interface-utilisateur-industrielle)
6. [Simulateurs et generation de donnees](#simulateurs-et-generation-de-donnees)
7. [Points forts](#points-forts)
8. [Axes d'amelioration](#axes-damelioration)
9. [Recommandations strategiques](#recommandations-strategiques)
10. [Conclusion](#conclusion)

---

## Synthese executive

### Score global des cas d'usage industriels: **7.8/10**

| Categorie | Score | Commentaire |
|-----------|-------|-------------|
| Couverture fonctionnelle | 8/10 | 5 cas d'usage majeurs couverts |
| Normalisation donnees | 9/10 | Excellente architecture multi-sources |
| Interface utilisateur | 8/10 | Dashboard ISA-95 bien concu |
| Integration LLM | 7/10 | Prompts specialises, contexte enrichi |
| Simulation/Tests | 7/10 | Simulateurs complets mais limites |
| Documentation | 7/10 | Bonne mais peut etre enrichie |

### Resume

La plateforme SYNAPSIX offre une couverture solide des cas d'usage industriels majeurs avec:
- **5 cas d'usage principaux** implementes et fonctionnels
- **4 sources de donnees industrielles** supportees (SCADA, MES, PLM, OPC-UA)
- **Conformite ISA-95** pour la hierarchie des equipements
- **Integration LLM** avec prompts specialises par domaine

---

## Panorama des cas d'usage industriels

### Cas d'usage implementes

| # | Cas d'usage | Module | Statut | Maturite |
|---|-------------|--------|--------|----------|
| 1 | Analytics conversationnelle | `prompts.py` | Actif | Production |
| 2 | Analyse cause racine (RCA) | `prompts.py` | Actif | Production |
| 3 | Maintenance predictive | `prompts.py`, `dashboard` | Actif | Production |
| 4 | Interpretation d'alarmes | `prompts.py`, `normalizer` | Actif | Production |
| 5 | Analyse OEE/TRS | `prompts.py`, `dashboard` | Actif | Production |

### Sources de donnees industrielles

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SYNAPSIX Data Sources                            │
├──────────────┬──────────────┬──────────────┬───────────────────────┤
│    SCADA     │     MES      │     PLM      │       OPC-UA          │
│  (Niveau 2)  │  (Niveau 3)  │  (Niveau 4)  │    (Multi-niveau)     │
├──────────────┼──────────────┼──────────────┼───────────────────────┤
│ - Mesures    │ - Production │ - Documents  │ - Nodes temps reel    │
│ - Alarmes    │ - Qualite    │ - Revisions  │ - Subscriptions       │
│ - Etats      │ - Temps cycle│ - BOM        │ - Status codes        │
│ - Capteurs   │ - Defauts    │ - Approbation│ - Namespaces          │
└──────────────┴──────────────┴──────────────┴───────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │   Industrial Data Normalizer  │
              │    (Format unifie)            │
              └───────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │     LLM Context Enrichment    │
              │   + OpenTelemetry Metrics     │
              └───────────────────────────────┘
```

---

## Analyse detaillee par cas d'usage

### 1. Analytics Conversationnelle (NLP Queries)

**Fichier:** `web-app/modules/llm/prompts.py:105-129`

**Description:** Permet aux operateurs de poser des questions en langage naturel sur les metriques de production.

**Implementation:**
```python
METRICS_QUERY_PROMPT_FR = """Analyse la requete suivante sur les metriques de production.

Donnees disponibles:
{metrics_context}

Question: {query}

Fournis une reponse claire avec:
1. La valeur demandee avec son unite
2. Une comparaison avec les seuils normaux si pertinent
3. Une tendance si des donnees historiques sont disponibles
4. Une recommandation si la valeur est anormale"""
```

**Evaluation:**
| Critere | Score | Detail |
|---------|-------|--------|
| Completude du prompt | 8/10 | Bien structure, bilingue |
| Contexte fourni | 7/10 | Metriques disponibles, manque historique detaille |
| Qualite des reponses attendues | 8/10 | Format clair et actionnable |

**Points forts:**
- Structure de reponse guidee (valeur, comparaison, tendance, recommandation)
- Support bilingue FR/EN
- Integration du contexte metrique temps reel

**Ameliorations suggeres:**
- Ajouter des exemples few-shot pour ameliorer la qualite
- Integrer les seuils critiques specifiques par equipement
- Supporter les requetes multi-metriques

---

### 2. Analyse Cause Racine (Root Cause Analysis)

**Fichier:** `web-app/modules/llm/prompts.py:171-209`

**Description:** Analyse systematique des incidents avec la methode des 5 Pourquoi.

**Implementation:**
```python
ROOT_CAUSE_ANALYSIS_PROMPT_FR = """Effectue une analyse de cause racine pour l'incident suivant.

Incident: {incident_title}
Description: {incident_description}
Severite: {severity}
Detecte le: {detected_at}

Metriques au moment de l'incident:
{metrics_context}

Timeline des evenements:
{timeline}

Analyse en utilisant la methode des 5 Pourquoi et fournis:
1. La cause racine identifiee
2. Les facteurs contributifs
3. La chaine causale complete
4. Les actions correctives immediates
5. Les actions preventives pour eviter la recurrence"""
```

**Evaluation:**
| Critere | Score | Detail |
|---------|-------|--------|
| Methodologie | 9/10 | Methode 5 Pourquoi bien structuree |
| Contexte fourni | 8/10 | Timeline + metriques + description |
| Output actionnable | 9/10 | Actions correctives et preventives |

**Points forts:**
- Methodologie eprouvee (5 Pourquoi)
- Integration de la timeline des evenements
- Separation actions correctives vs preventives

**Ameliorations suggeres:**
- Ajouter un template pour incidents recurrents
- Integrer l'historique des incidents similaires
- Supporter l'export vers systeme CMMS

---

### 3. Maintenance Predictive

**Fichier:** `web-app/modules/llm/prompts.py:211-251`

**Description:** Prediction des besoins de maintenance basee sur l'analyse des donnees capteurs et historique.

**Implementation:**
```python
PREDICTIVE_MAINTENANCE_PROMPT_FR = """Analyse les donnees de l'equipement pour predire les besoins de maintenance.

Equipement: {equipment_name}
Type: {equipment_type}

Metriques actuelles:
{current_metrics}

Historique des 30 derniers jours:
{historical_metrics}

Historique de maintenance:
{maintenance_history}

Fournis:
1. Score de sante global (0-100)
2. Duree de vie residuelle estimee (RUL)
3. Anomalies detectees
4. Probabilite de panne dans les 7/30 prochains jours
5. Recommandations de maintenance priorisees"""
```

**Integration Dashboard (IndustrialObservabilityView.jsx):**
- Indicateur de sante par equipement (0-100%)
- RUL (Remaining Useful Life) en heures
- Alertes de maintenance urgente (RUL < 200h)
- Historique 24h des metriques

**Evaluation:**
| Critere | Score | Detail |
|---------|-------|--------|
| Completude des donnees | 8/10 | Metriques + historique + maintenance |
| Indicateurs cles | 9/10 | Health score, RUL, probabilite panne |
| Visualisation | 8/10 | Dashboard avec jauges et historique |

**Points forts:**
- Score de sante normalise (0-100)
- RUL (Remaining Useful Life) calcule et affiche
- Priorisation des recommandations

**Ameliorations suggeres:**
- Implementer un modele ML pour affiner les predictions RUL
- Ajouter des courbes de degradation par type d'equipement
- Integrer la GMAO pour automatiser les ordres de travail

---

### 4. Interpretation d'Alarmes

**Fichier:** `web-app/modules/llm/prompts.py:297-331`

**Description:** Analyse et correlation des alarmes actives avec recommandations.

**Implementation:**
```python
ALARM_INTERPRETATION_PROMPT_FR = """Interprete les alarmes actives et fournis des recommandations.

Alarmes actives:
{alarms}

Contexte des equipements:
{equipment_context}

Metriques actuelles:
{metrics_context}

Pour chaque alarme, fournis:
1. Signification et cause probable
2. Niveau de criticite reel
3. Actions immediates requises
4. Impact potentiel sur la production
5. Correlations avec d'autres alarmes"""
```

**Support dans IndustrialDataNormalizer:**
- Classification des severites: INFO, WARNING, CRITICAL, EMERGENCY
- Correlation d'evenements inter-sources (methode `correlate_events`)
- Fenetre temporelle configurable pour correlation

**Evaluation:**
| Critere | Score | Detail |
|---------|-------|--------|
| Categorisation alarmes | 8/10 | 4 niveaux de severite |
| Correlation | 8/10 | Multi-sources, fenetre temporelle |
| Recommandations | 7/10 | Actions immediates, manque SOP |

**Points forts:**
- Correlation multi-sources (SCADA + MES + OPC-UA)
- Impact production evalue
- Categorisation claire des severites

**Ameliorations suggeres:**
- Lier aux procedures operationnelles standard (SOP)
- Ajouter la detection de patterns d'alarmes
- Implementer l'acquittement intelligent

---

### 5. Analyse OEE/TRS

**Fichier:** `web-app/modules/llm/prompts.py:253-295`

**Description:** Analyse des indicateurs de performance globale des equipements.

**Implementation:**
```python
OEE_ANALYSIS_PROMPT_FR = """Analyse les indicateurs OEE/TRS pour la periode demandee.

Donnees OEE:
- OEE global: {oee}%
- Disponibilite: {availability}%
- Performance: {performance}%
- Qualite: {quality}%

Production:
- Produits fabriques: {production_count}
- Defauts: {defects_count}
- Temps de cycle moyen: {cycle_time}s

Question: {query}

Fournis une analyse incluant:
1. Interpretation des valeurs actuelles
2. Identification du facteur limitant (disponibilite, performance ou qualite)
3. Comparaison avec les objectifs standard (OEE World Class: 85%)
4. Pistes d'amelioration prioritaires
5. Impact financier estime des pertes"""
```

**Metriques Prometheus (MES Simulator):**
- `mes_oee_percent` - OEE par workstation
- `mes_quality_rate_percent` - Taux qualite
- `mes_cycle_time_seconds` - Temps de cycle (histogramme)
- `mes_production_count_total` - Compteur production
- `mes_defects_total` - Compteur defauts

**Evaluation:**
| Critere | Score | Detail |
|---------|-------|--------|
| Metriques OEE | 9/10 | Disponibilite, Performance, Qualite |
| Benchmark | 8/10 | Reference World Class (85%) |
| Analyse financiere | 7/10 | Impact estime mais simplifie |

**Points forts:**
- Decomposition complete OEE (D x P x Q)
- Reference benchmark World Class
- Identification facteur limitant

**Ameliorations suggeres:**
- Ajouter les 6 grandes pertes (TPM)
- Calculer le cout reel des pertes
- Integrer les objectifs specifiques par ligne

---

## Architecture de normalisation des donnees

**Fichier:** `web-app/modules/llm_observability/industrial_data_normalizer.py`

### Structure NormalizedIndustrialEvent

```python
@dataclass
class NormalizedIndustrialEvent:
    # Identification
    event_id: str                           # UUID unique
    timestamp: NormalizedTimestamp          # UTC + source + server time
    source: IndustrialDataSource            # SCADA, MES, PLM, OPCUA
    event_type: EventType                   # MEASUREMENT, ALARM, etc.

    # Localisation
    location: NormalizedLocation            # Site/Area/Line/Equipment/Component

    # Donnees
    tag_id: Optional[str]                   # Identifiant tag
    tag_name: Optional[str]                 # Nom affichable
    value: Optional[NormalizedValue]        # Valeur + unite + qualite

    # Contexte
    description: Optional[str]
    category: Optional[str]
    subcategory: Optional[str]

    # Relations
    related_events: List[str]               # Events lies
    parent_event: Optional[str]             # Event parent

    # Metadata
    metadata: Dict[str, Any]
    raw_data: Optional[Dict[str, Any]]      # Donnees brutes preservees

    # Tracing
    correlation_id: Optional[str]           # Pour OpenTelemetry
```

### Normalizers par source

| Source | Normalizer | Events supportes |
|--------|------------|------------------|
| SCADA | `SCADANormalizer` | MEASUREMENT, ALARM, STATE_CHANGE |
| MES | `MESNormalizer` | PRODUCTION_START/END, QUALITY_CHECK, DOWNTIME, MATERIAL_CONSUMED |
| PLM | `PLMNormalizer` | DOCUMENT_CHANGE, REVISION, APPROVAL, BOM_UPDATE |
| OPC-UA | `OPCUANormalizer` | NODE_UPDATE, SUBSCRIPTION_DATA |

### Points forts de l'architecture

1. **Schema unifie** - Toutes les sources normalisees vers un format commun
2. **Qualite preservee** - Indicateurs GOOD/UNCERTAIN/BAD/INTERPOLATED/STALE
3. **Hierarchie ISA-95** - Support complet enterprise/site/area/work_center/work_unit
4. **Tracabilite** - correlation_id pour OpenTelemetry
5. **Buffer intelligent** - Trimming par taille (10000) et age (1h)

### Points faibles identifies

1. **Thread-safety** - Singleton non thread-safe (ligne 892-895)
2. **Imports locaux** - `import uuid` repete dans chaque normalizer
3. **Validation** - Pas de validation Pydantic des entrees
4. **Types manquants** - ERP et CMMS declares mais non implementes

---

## Interface utilisateur industrielle

**Fichier:** `dashboard-react/src/pages/IndustrialObservabilityView.jsx`

### Hierarchie ISA-95 implementee

| Niveau | Description | Icone | Couleur |
|--------|-------------|-------|---------|
| 0 | Process - Capteurs, actionneurs | Radio | Rouge/Orange |
| 1 | Controle - PLC, DCS | CircuitBoard | Orange/Ambre |
| 2 | Supervision - SCADA, HMI | Eye | Jaune/Lime |
| 3 | MES/MOM - Execution, qualite | Factory | Vert/Emeraude |
| 4 | ERP/Business - Planification | BarChart3 | Bleu/Cyan |

### Types d'equipements supportes

| Type | Icone | Metriques |
|------|-------|-----------|
| MOTOR | Zap | temperature, vibration, current, rpm |
| PUMP | RefreshCw | flow, pressure, temperature, power |
| CONVEYOR | ArrowRight | speed, load, alignment, tension |
| ROBOT | Box | cycle_time, accuracy, temperature, torque |
| FURNACE | Thermometer | temperature, pressure, gas_flow, power |
| PRESS | ArrowDown | force, position, cycle_time, oil_temp |
| CNC | Settings | spindle_speed, feed_rate, tool_wear, vibration |
| COMPRESSOR | Gauge | pressure, temperature, flow, power |

### KPIs affiches

1. **Equipements Totaux** - Nombre total
2. **Sante Moyenne** - Moyenne health score avec tendance
3. **En Etat Optimal** - Compteur status optimal
4. **Alertes Actives** - Nombre d'alertes
5. **Degradation** - Equipements degrades + critiques
6. **Maintenance Urgente** - RUL < 200h

### Modes d'affichage

- **Grille** - Cartes equipements en grid responsive
- **Liste** - Vue tabulaire
- **Hierarchie** - Groupement par niveau ISA-95

### Points forts UI

1. **Design moderne** - Tailwind CSS, animations Framer Motion
2. **Temps reel** - Auto-refresh configurable (5s)
3. **Filtres avances** - Par niveau ISA-95, par statut
4. **Detail equipement** - Modal avec historique 24h (Recharts)
5. **Actions integrees** - Creer OT, voir Grafana, exporter

### Points faibles UI

1. **Donnees mockees** - `generateEquipmentData()` genere des donnees factices
2. **Pas d'API reelle** - Aucun appel backend pour les donnees
3. **Historique simule** - Les charts 24h sont generes aleatoirement
4. **Pas de persistence** - Les filtres ne sont pas sauvegardes

---

## Simulateurs et generation de donnees

**Fichier:** `simulators/industrial_simulator.py`

### Simulateurs disponibles

| Type | Classe | Debit | Metriques Prometheus |
|------|--------|-------|---------------------|
| SCADA | `SCADASimulator` | 100 pts/s | temperature, pressure, flow, level, vibration, power |
| MES | `MESSimulator` | Variable | production_count, cycle_time, oee, quality_rate, defects |
| PLM | `PLMSimulator` | Variable | changes_total, approval_time, active_revisions |
| OPC-UA | `OPCUASimulator` | Variable | nodes_total, read_latency, subscription_count |

### Zones de production simulees

**SCADA Areas:**
- zone_a: reactor_001/002, mixer_001, pump_001/002
- zone_b: furnace_001, conveyor_001, press_001, robot_001
- zone_c: tank_001/002, compressor_001, filter_001
- utilities: boiler_001, chiller_001, air_handler_001
- packaging: filler_001, labeler_001, palletizer_001

**MES Workstations:**
- ws_assembly_01/02
- ws_welding_01
- ws_paint_01
- ws_qc_01

### Caracteristiques de simulation

1. **Drift realiste** - Les valeurs derivent de 5% avec occasionnellement 20%
2. **Qualite variable** - 2% des mesures en qualite "uncertain" ou "bad"
3. **Alarmes generees** - Quand valeur > 130% de la base
4. **Temps de cycle** - Varies de +-30% autour de la base par produit

### Points forts simulateurs

1. **Multi-type** - SCADA, MES, PLM, OPC-UA en un seul binaire
2. **Metriques Prometheus** - Exposition native sur :8080
3. **Health checks** - Endpoints /health et /ready
4. **Configurable** - Variables d'environnement pour debit et type

### Points faibles simulateurs

1. **Pas de scenarios** - Pas de simulation de pannes planifiees
2. **Correlations limitees** - Les sources ne sont pas correlees entre elles
3. **Pas de mode batch** - Ne peut pas rejouer des scenarios historiques
4. **Single-threaded** - Un seul type de simulateur a la fois

---

## Points forts

### 1. Architecture de normalisation exemplaire
- Format unifie pour 4 sources industrielles
- Support complet ISA-95
- Qualite de donnees tracee
- Correlation d'evenements

### 2. Couverture fonctionnelle complete
- 5 cas d'usage majeurs implementes
- Prompts bilingues FR/EN
- Methodes eprouvees (5 Pourquoi, OEE)

### 3. Interface utilisateur moderne
- Dashboard temps reel
- Visualisation par hierarchie ISA-95
- KPIs pertinents (health, RUL, alertes)
- Design responsive et anime

### 4. Integration OpenTelemetry native
- Metriques standardisees
- Correlation traces/metriques/logs
- Export Prometheus

### 5. Simulateurs realistes
- 4 types de donnees industrielles
- Drift et variations realistes
- Exposition Prometheus

---

## Axes d'amelioration

### Court terme (1-2 sprints)

| Action | Priorite | Effort | Impact |
|--------|----------|--------|--------|
| Connecter dashboard a l'API reelle | Haute | Moyen | Haut |
| Ajouter validation Pydantic aux normalizers | Haute | Faible | Moyen |
| Fix thread-safety du singleton normalizer | Haute | Faible | Moyen |
| Implementer normalizers ERP/CMMS | Moyenne | Moyen | Moyen |

### Moyen terme (3-4 sprints)

| Action | Priorite | Effort | Impact |
|--------|----------|--------|--------|
| Modele ML pour prediction RUL | Haute | Haut | Haut |
| Integration GMAO (ordres de travail) | Haute | Moyen | Haut |
| Scenarios de simulation (pannes) | Moyenne | Moyen | Moyen |
| Detection patterns d'alarmes | Moyenne | Moyen | Moyen |

### Long terme (5+ sprints)

| Action | Priorite | Effort | Impact |
|--------|----------|--------|--------|
| Digital Twin integration | Haute | Tres Haut | Tres Haut |
| Analyse video/image (defauts) | Moyenne | Haut | Haut |
| NLP avance (voix operateur) | Basse | Haut | Moyen |
| Export vers systemes tiers (SAP, Oracle) | Moyenne | Moyen | Moyen |

---

## Recommandations strategiques

### 1. Prioriser l'integration backend du dashboard

Le dashboard React est impressionnant mais fonctionne avec des donnees mockees. L'integration avec les vraies APIs est critique pour la valeur business.

**Actions:**
- Creer les endpoints REST pour les equipements
- Implementer WebSocket pour les mises a jour temps reel
- Persister les preferences utilisateur

### 2. Enrichir les prompts avec des exemples few-shot

Les prompts actuels sont bien structures mais pourraient beneficier d'exemples concrets pour ameliorer la qualite des reponses LLM.

**Actions:**
- Ajouter 2-3 exemples par type de prompt
- Inclure des cas limites
- Documenter les formats de sortie attendus

### 3. Implementer un modele de prediction RUL

Le RUL (Remaining Useful Life) actuel est simule. Un vrai modele predictif apporterait une valeur considerable.

**Technologies suggerees:**
- scikit-learn pour les modeles simples
- TensorFlow/PyTorch pour LSTM sur series temporelles
- Integration avec MLflow pour le versioning

### 4. Ajouter des scenarios de simulation

Les simulateurs actuels generent des donnees aleatoires. Des scenarios predefinnis permettraient de tester les cas d'usage de bout en bout.

**Scenarios a implementer:**
- Degradation progressive d'un moteur
- Pic de defauts qualite
- Panne cascade (alarmes correlees)
- Maintenance planifiee

### 5. Renforcer la securite IEC 62443

La plateforme mentionne un mode "Secure" IEC 62443 mais l'implementation n'est pas visible dans les cas d'usage.

**Actions:**
- Audit de conformite IEC 62443
- Segmentation reseau OT/IT
- Authentification forte pour les operateurs
- Logging des acces aux donnees sensibles

---

## Conclusion

La plateforme SYNAPSIX offre une base solide pour l'observabilite industrielle avec une couverture fonctionnelle adequate des cas d'usage majeurs. Les points forts incluent une architecture de normalisation exemplaire, des prompts LLM bien structures, et une interface utilisateur moderne.

Les axes d'amelioration principaux concernent:
1. L'integration du dashboard avec les donnees reelles
2. L'implementation de modeles predictifs pour le RUL
3. L'enrichissement des scenarios de simulation
4. La conformite securitaire IEC 62443

Avec ces ameliorations, la plateforme serait en mesure de fournir une valeur business significative aux operateurs industriels.

---

## Annexes

### A. Cartographie des fichiers audites

| Fichier | Lignes | Role |
|---------|--------|------|
| `web-app/modules/llm/prompts.py` | 562 | Prompts industriels |
| `web-app/modules/llm_observability/industrial_data_normalizer.py` | 904 | Normalisation donnees |
| `dashboard-react/src/pages/IndustrialObservabilityView.jsx` | 780 | Interface utilisateur |
| `simulators/industrial_simulator.py` | 527 | Generation donnees |
| **Total** | **2,773** | |

### B. Metriques Prometheus industrielles

**SCADA:**
- `scada_temperature_celsius`
- `scada_pressure_bar`
- `scada_flow_rate_m3h`
- `scada_level_percent`
- `scada_vibration_mms`
- `scada_power_kw`
- `scada_alarms_total`

**MES:**
- `mes_production_count_total`
- `mes_cycle_time_seconds`
- `mes_oee_percent`
- `mes_quality_rate_percent`
- `mes_defects_total`
- `mes_downtime_seconds_total`

**PLM:**
- `plm_changes_total`
- `plm_approval_time_hours`
- `plm_active_revisions`

**OPC-UA:**
- `opcua_nodes_total`
- `opcua_read_latency_ms`
- `opcua_subscription_count`

### C. Variables d'environnement

```bash
# Simulateur
OTEL_ENDPOINT=http://otel-collector:4318
SIMULATOR_TYPE=scada|mes|plm|opcua
METRICS_PORT=8080
DATA_RATE_PER_SEC=100

# Normalisation
LLM_TRACING_ENABLED=true
LLM_TRACING_INCLUDE_PROMPT=false
```

---

*Rapport genere par Claude - Audit Synapsix Cas d'Usage Industriels*
